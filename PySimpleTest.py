import sys
import os
import shutil
from .helper import *
import time
import copy
import getpass
import datetime
import atexit
import traceback
import threading
import ctypes
import colorama

def base_name(file_path):
	filename = os.path.basename(file_path)
	pos = filename.rfind(".")
	if pos == -1:
		return filename
	else:
		return filename[:pos]

def expand_name(file_path):
	filename = os.path.basename(file_path)
	pos = filename.rfind(".")
	if pos == -1 or pos == len(filename)-1:
		return ""
	else:
		return filename[pos+1:]

# assistant functions
def parse_argv(args = {}):
	for i in range(len(sys.argv)):
		if len(sys.argv[i])>=1 and sys.argv[i][0] == "-" and i+1 <= len(sys.argv)-1:
			args[sys.argv[i]] = sys.argv[i+1]

	return args

def __delete_escape(content):
	pos = 0
	while pos != -1:
		pos = content.find("\033[")
		if pos == -1:
			break
		pos_end = content.find("m", pos)
		content = content[:pos] + content[pos_end+1:]
	return content

class ExpandList:
	def __init__(self, target_list = []):
		self.__list = copy.deepcopy(target_list)

	def __getitem__(self, i):
		while i >= len(self.__list):
			self.__list.append({"number":0, "total": 0, "passed":0, "failed":0})
		return self.__list[i]

	def __len__(self):
		return len(self.__list)

# log system
__log_filename = ""
__info_filename = ""
__linfo_filename = ""
__rel_path = ""
__script_total_line = 0
__last_is_end_section = False
__current_section = ExpandList()
_current_level = 0
__indent = ""
__log_use_indent = True
__print_use_indent = True

# control logic
__first_use = True
__code_dict = {}
__color_on = True
__voice_on = False
__gui_on = False
__start_time = None
__speak_engine = None
__is_gui_init = False
__gui_init_code = """
from . import progressbar
import tkinter
import tkinter.messagebox
__root = tkinter.Tk()
__root.withdraw()
"""

__is_voice_init = False
__voice_init_code = """
import pyttsx3
"""

# header info
header_info = {}
header_info["title"] = ""
header_info["version"] = ""
header_info["author"] = getpass.getuser()
header_info["url"] = ""

# tail info
tailer_info = {}

# turn on cmd color
colorama.init()

# configuration
def color_on():
	global __color_on
	__color_on = True

def color_off():
	global __color_on
	__color_on = False

def voice_on():
	global __voice_on
	global __is_voice_init

	__voice_on = True
	if not __is_voice_init:
		__is_voice_init = True
		exec(__voice_init_code, globals(), globals())

def voice_off():
	global __voice_on
	__voice_on = False

def gui_on():
	global __gui_on
	global __is_gui_init

	__gui_on = True
	if not __is_gui_init:
		__is_gui_init = True
		exec(__gui_init_code, globals(), globals())

def gui_off():
	global __gui_on
	__gui_on = False

# header information
def title(name):
	global header_info
	header_info["title"] = name

def author(name):
	global header_info
	header_info["author"] = name

def version(v):
	global header_info
	header_info["version"] = v

def url(web):
	global header_info
	header_info["url"] = web

def start_test():
	global __first_use
	if not __first_use:
		return

	global __log_filename
	global __info_filename
	global __linfo_filename
	global __rel_path
	global __script_total_line
	global __color_on
	global __voice_on
	global header_info
	global __start_time

	__first_use = False
	base = base_name(sys.argv[0])
	if len(base) == 0:
		return

	if header_info["version"]:
		__log_filename = base + "_" + header_info["version"] + ".log"
		__info_filename = base + "_" + header_info["version"] + ".info"
		__linfo_filename = base + "_" + header_info["version"] + ".linfo"
	else:
		__log_filename = base + ".log"
		__info_filename = base + ".info"
		__linfo_filename = base + ".linfo"

	argv = parse_argv()
	if "--title" in argv:
		header_info["title"] = argv["--title"]
	if "--author" in argv:
		header_info["author"] = argv["--author"]
	if "--logfile" in argv:
		__log_filename = argv["--logfile"]
	if "--infofile" in argv:
		__info_filename = argv["--infofile"]
	if "--linfofile" in argv:
		__linfo_filename = argv["--linfofile"]
	if "--version" in argv:
		header_info["version"] = argv["--version"]
	if "--url" in argv:
		header_info["url"] = argv["--url"]
	if "--color" in argv:
		if argv["--color"] == "on":
			color_on()
		elif argv["--color"] == "off":
			color_off()
	if "--voice" in argv:
		if argv["--voice"] == "on":
			voice_on()
		elif argv["--voice"] == "off":
			voice_off()
	if "--gui" in argv:
		if argv["--gui"] == "on":
			gui_on()
		elif argv["--gui"] == "off":
			gui_off()

	head_str = ""
	if header_info["title"]:
		head_str += "Title: " + header_info["title"] + "\n"
	else:
		head_str += "Title: " + base + "\n"

	if header_info["url"]:
		head_str += "url: " + header_info["url"] + "\n"

	if header_info["version"]:
		head_str += "Product Version: " + header_info["version"] + "\n"

	head_str += "Author: " + header_info["author"] + "\n"
	for key in header_info:
		if key not in ("title", "url", "author", "version"):
			head_str += key + ": " + header_info[key] + "\n"
	head_str += "Start Time: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
	
	__start_time = time.time()

	if not os.path.isdir(os.path.abspath(os.path.dirname(__log_filename))):
		os.makedirs(os.path.abspath(os.path.dirname(__log_filename)))

	if not os.path.isdir(os.path.abspath(os.path.dirname(__info_filename))):
		os.makedirs(os.path.abspath(os.path.dirname(__info_filename)))

	if not os.path.isdir(os.path.abspath(os.path.dirname(__linfo_filename))):
		os.makedirs(os.path.abspath(os.path.dirname(__linfo_filename)))

	try:
		__rel_path = os.path.relpath(sys.argv[0], os.path.dirname(__linfo_filename))
		__script_total_line = sum(1 for line in open(sys.argv[0]))
	except:
		__rel_path = base
		__script_total_line = 0

	file = open(__log_filename, "w")
	file.write("")
	file.close()

	file = open(__info_filename, "w")
	file.write("")
	file.close()

	file = open(__linfo_filename, "w")
	file.write("")
	file.close()

	log(head_str, color="cyan", style="highlight", link=False)

def approx(value1, value2, tolerance = 1/3600, func = abs):
	try:
		return func(value1 - value2) <= tolerance
	except:
		return False

def __not_original_string(arg):
	return (not arg) or (arg[0] not in ("\'", "\""))

def __eff_str(value):
	if isinstance(value, str):
		return "\"" + value.replace("\"", "\\\"").replace("\'", "\\\'") + "\""
	else:
		return str(value)

@atexit.register
def end_test():
	if __start_time is None or __log_filename is None or __info_filename is None or len(sys.argv[0]) == 0:
		return

	global _current_level
	while _current_level > 0:
		end_section()

	def format_seconds_to_hhmmss(seconds):
		hours = seconds // (60*60)
		seconds %= (60*60)
		minutes = seconds // 60
		seconds %= 60
		return "%02i:%02i:%02.2f" % (hours, minutes, seconds)

	green = start_format(color="green", style="highlight")
	red = start_format(color="red", style="highlight")
	cyan = start_format(color="cyan", style="highlight")
	form1 = green
	form2 = green

	global __indent
	__indent = ""
	tail_str = ""
	for key in tailer_info:
		tail_str += cyan + key + ": " + tailer_info[key] + end_format() + "\n"
	tail_str += cyan + "End Time: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + end_format() + "\n"
	tail_str += cyan + "Time Elapse: " + format_seconds_to_hhmmss(time.time() - __start_time) + end_format()
	
	exit_code = 5
	if __current_section[0]["total"] > 0:
		exit_code = 0
		tail_str += "\n"
		tail_str += cyan + "Total: " + str(__current_section[0]["total"]) + end_format() + "\n"
		if __current_section[0]["passed"] == 0:
			form1 = red
		tail_str += form1 + "Passed: " + str(__current_section[0]["passed"]) + end_format() + "\n"
		if __current_section[0]["failed"] > 0:
			form2 = red
		tail_str += form2 + "Failed: " + str(__current_section[0]["failed"]) + end_format() + "\n"
		try:
			error_type = sys.last_type.__name__
			tail_str += red + "Result: "
			tail_str += "Error (" + error_type + ")"
			if error_type == "KeyboardInterrupt":
				exit_code = 2 
			else:
				exit_code = 3
		except:
			if __current_section[0]["failed"] == 0:
				tail_str += green + "Result: "
				tail_str += "Pass"
				exit_code = 0
			else:
				tail_str += red + "Result: "
				tail_str += "Fail"
				exit_code = 1
		tail_str += end_format()

	break_line = "\n"
	if __last_is_end_section:
		break_line = ""

	trace_str = ""
	try:
		trace_str = break_line + "".join(traceback.format_exception(sys.last_type, sys.last_value, sys.last_traceback))
	except:
		trace_str = ""

	if not break_line and not trace_str:
		log(tail_str)
	else:
		log(red + trace_str + end_format() + "\n" + tail_str)

	if __voice_on:
		try:
			say(str(sys.last_type.__name__) + ": " + str(sys.last_value))
		except:
			pass

	log_backup_dir = os.path.abspath(os.path.dirname(__log_filename)) + "/backup"
	info_backup_dir = os.path.abspath(os.path.dirname(__info_filename)) + "/backup"
	linfo_backup_dir = os.path.abspath(os.path.dirname(__linfo_filename)) + "/backup"
	if not os.path.isdir(log_backup_dir):
		os.makedirs(log_backup_dir)
	if not os.path.isdir(info_backup_dir):
		os.makedirs(info_backup_dir)
	if not os.path.isdir(linfo_backup_dir):
		os.makedirs(linfo_backup_dir)

	current_time = time.strftime("%Y%m%d%H%M%S")
	shutil.copyfile(__log_filename, log_backup_dir + "/" + base_name(__log_filename) + "_" + current_time + "." + expand_name(__log_filename))
	shutil.copyfile(__info_filename, info_backup_dir + "/" + base_name(__info_filename) + "_" + current_time + "." + expand_name(__info_filename))
	shutil.copyfile(__linfo_filename, linfo_backup_dir + "/" + base_name(__linfo_filename) + "_" + current_time + "." + expand_name(__linfo_filename))

	os._exit(exit_code)

	# exit_code = 0  # all passed
	# exit_code = 1  # some failed
	# exit_code = 2  # user killed with ctrl+c
	# exit_code = 3  # inner exception
	# exit_code = 5  # no tests

def start_format(color = "white", style = "default"):
	if not __color_on:
		return ""

	dict_style = \
	{
		"default": "0",
		"highlight": "1",
		"underline": "4",
		"shining": "5",
		"anti": "7",
		"none": "8"
	}
	dict_color = \
	{
		"black": "30",
		"red": "31",
		"green": "32",
		"yellow": "33",
		"blue": "34",
		"purple": "35",
		"cyan": "36",
		"white": "37"
	}
	return "\033[" + dict_style[style] + ";" + dict_color[color] + "m"

def end_format():
	if not __color_on:
		return ""

	return "\033[0m"

def log(*args, **kwargs):
	start_test()

	global __last_is_end_section
	__last_is_end_section = False

	if "end" not in kwargs:
		kwargs["end"] = "\n"
	if "sep" not in kwargs:
		kwargs["sep"] = " "
	if "color" not in kwargs:
		kwargs["color"] = "white"
	if "style" not in kwargs:
		kwargs["style"] = "default"
	if "link" not in kwargs:
		kwargs["link"] = True

	kwargs["end"] = str(kwargs["end"])
	kwargs["sep"] = str(kwargs["sep"])

	frame = sys._getframe()
	n_line = frame.f_back.f_lineno
	filename = frame.f_back.f_code.co_filename
	if len(sys.argv[0]) > 0:
		while os.path.abspath(filename) != os.path.abspath(sys.argv[0]):
			try:
				frame = frame.f_back
				n_line = frame.f_back.f_lineno
				filename = frame.f_back.f_code.co_filename
			except:
				n_line = __script_total_line + 1
				break

	prefix = __rel_path + ":" + str(n_line) + " " * max(0, 8-len(str(n_line))) + "|  "

	result_str = ""
	result_link_str = ""
	for i in range(len(args)):
		result_str += str(args[i])
		if i != len(args)-1:
			result_str += kwargs["sep"]
	result_str += kwargs["end"]

	result_link_str = result_str.replace("\n", "\n" + prefix + __indent)
	if result_link_str[-len("\n" + prefix + __indent):] == "\n" + prefix + __indent:
		result_link_str = result_link_str[:-len(prefix + __indent)]

	result_str = result_link_str.replace("\n" + prefix + __indent, "\n" + __indent)

	global __print_use_indent
	global __log_use_indent

	if __print_use_indent:
		if kwargs["color"] == "white" and kwargs["style"] == "default":
			print(__indent + result_str, end="", flush=True)
		else:
			print(__indent + start_format(style=kwargs["style"], color=kwargs["color"]) + result_str + end_format(), end="", flush=True)
	else:
		if kwargs["color"] == "white" and kwargs["style"] == "default":
			print(result_str, end="", flush=True)
		else:
			print(__indent + start_format(style=kwargs["style"], color=kwargs["color"]) + result_str + end_format(), end="", flush=True)

	result_str = __delete_escape(result_str)
	result_link_str = __delete_escape(result_link_str)

	if len(sys.argv[0]) > 0:
		global __log_filename
		file = open(__log_filename, "a")
		if __log_use_indent:
			file.write(__indent + result_str)
		else:
			file.write(result_str)
		file.close()

		global __info_filename
		file = open(__info_filename, "a")
		if __print_use_indent:
			file.write(__indent + result_str)
		else:
			file.write(result_str)
		file.close()

		global __linfo_filename
		file = open(__linfo_filename, "a")
		if __print_use_indent:
			file.write(prefix + __indent + result_link_str)
		else:
			file.write(result_link_str)
		file.close()

	__print_use_indent = (len(kwargs["end"]) >= 1 and kwargs["end"][-1] == '\n')
	__log_use_indent = __print_use_indent

def info(*args, **kwargs):
	start_test()

	global __last_is_end_section
	__last_is_end_section = False

	if "end" not in kwargs:
		kwargs["end"] = "\n"
	if "sep" not in kwargs:
		kwargs["sep"] = " "
	if "color" not in kwargs:
		kwargs["color"] = "white"
	if "style" not in kwargs:
		kwargs["style"] = "default"

	kwargs["end"] = str(kwargs["end"])
	kwargs["sep"] = str(kwargs["sep"])

	frame = sys._getframe()
	n_line = frame.f_back.f_lineno
	filename = frame.f_back.f_code.co_filename
	funcname = frame.f_code.co_name

	if len(sys.argv[0]) > 0:
		while os.path.abspath(filename) != os.path.abspath(sys.argv[0]):
			try:
				frame = frame.f_back
				n_line = frame.f_back.f_lineno
				filename = frame.f_back.f_code.co_filename
				funcname = frame.f_code.co_name
			except:
				n_line = __script_total_line + 1
				break

	prefix = __rel_path + ":" + str(n_line) + " " * max(0, 8-len(str(n_line))) + "|  "

	result_str = ""
	result_link_str = ""
	for i in range(len(args)):
		result_str += str(args[i])
		if i != len(args)-1:
			result_str += kwargs["sep"]
	result_str += kwargs["end"]

	result_link_str = result_str.replace("\n", "\n" + prefix + __indent)
	if result_link_str[-len("\n" + prefix + __indent):] == "\n" + prefix + __indent:
		result_link_str = result_link_str[:-len(prefix + __indent)]

	result_str = result_link_str.replace("\n" + prefix + __indent, "\n" + __indent)
	
	global __print_use_indent

	if __print_use_indent:
		if kwargs["color"] == "white" and kwargs["style"] == "default":
			print(__indent + result_str, end="", flush=True)
		else:
			print(__indent + start_format(style=kwargs["style"], color=kwargs["color"]) + result_str + end_format(), end="", flush=True)
	else:
		if kwargs["color"] == "white" and kwargs["style"] == "default":
			print(result_str, end="", flush=True)
		else:
			print(__indent + start_format(style=kwargs["style"], color=kwargs["color"]) + result_str + end_format(), end="", flush=True)

	result_str = __delete_escape(result_str)
	result_link_str = __delete_escape(result_link_str)

	if len(sys.argv[0]) > 0:
		global __info_filename
		file = open(__info_filename, "a")
		if __print_use_indent:
			file.write(__indent + result_str)
		else:
			file.write(result_str)
		file.close()

		global __linfo_filename
		file = open(__linfo_filename, "a")
		if __print_use_indent:
			file.write(prefix + __indent + result_link_str)
		else:
			file.write(result_link_str)
		file.close()

	__print_use_indent = (len(kwargs["end"]) >= 1 and kwargs["end"][-1] == '\n')

def section_number(level = None):
	if level is None:
		level = _current_level

	number = ""
	for i in range(1, level+1):
		number += str(__current_section[i]["number"]) + "."
	return number[:-1]

def section(name = "", level = 1):
	global __section_used
	global __indent
	global _current_level
	global __current_section

	__section_used = True

	green = start_format(color="green", style="highlight")
	red = start_format(color="red", style="highlight")
	cyan = start_format(color="cyan", style="highlight")
	form1 = green
	form2 = green
	
	global __last_is_end_section

	for i in range(_current_level, level-1, -1):
		if __current_section[i]["number"] != 0 and __current_section[i]["total"] != 0:
			__indent = "    " * (i-1)
			if __current_section[i]["passed"] == 0:
				form1 = red
			if __current_section[i]["failed"] > 0:
				form2 = red
			log(cyan + "[ Section " + section_number(i) + " Summary:" + \
				" Total: " + str(__current_section[i]["total"]) + ", " + end_format() + \
				form1 + "Passed: " + str(__current_section[i]["passed"]) + end_format() + cyan + ", " + end_format() + \
				form2  + "Failed: " + str(__current_section[i]["failed"]) + end_format() + cyan + " ]\n" + end_format())
			__last_is_end_section = True
			__current_section[i]["total"] = 0
			__current_section[i]["passed"] = 0
			__current_section[i]["failed"] = 0

	_current_level = level
	__current_section[level]["number"] += 1
	for i in range(level+1, len(__current_section)):
		__current_section[i]["number"] = 0

	__indent = "    " * (level-1)
	sec = section_number(level)
	if name == "":
		log("Section " + sec, color="cyan", style="highlight")
	else:
		log(sec + "  " + name, color="cyan", style="highlight")
	__indent = "    " * level

def end_section():
	global _current_level
	global __current_section
	global __indent
	global __last_is_end_section
	original_indent = __indent

	if _current_level == 0:
		return

	green = start_format(color="green", style="highlight")
	red = start_format(color="red", style="highlight")
	cyan = start_format(color="cyan", style="highlight")
	form1 = green
	form2 = green
	if __current_section[_current_level]["number"] != 0 and __current_section[_current_level]["total"] != 0:
		__indent = "    " * (_current_level-1)
		if __current_section[_current_level]["passed"] == 0:
			form1 = red
		if __current_section[_current_level]["failed"] > 0:
			form2 = red
		log(cyan + "[ Section " + section_number(_current_level) + " Summary:" + \
			" Total: " + str(__current_section[_current_level]["total"]) + ", " + end_format() + \
			form1 + "Passed: " + str(__current_section[_current_level]["passed"]) + end_format() + cyan + ", " + end_format() + \
			form2  + "Failed: " + str(__current_section[_current_level]["failed"]) + end_format() + cyan + " ]\n" + end_format())
		__last_is_end_section = True
		__current_section[_current_level]["total"] = 0
		__current_section[_current_level]["passed"] = 0
		__current_section[_current_level]["failed"] = 0

	n_back = 0
	if _current_level >= 1:
		_current_level -= 1
		n_back += 1

	while _current_level >= 1 and __current_section[_current_level] == 0:
		_current_level -= 1
		n_back += 1

	__indent = original_indent[:-4*n_back]

def subsection(name = ""):
	return section(name, level = 2)

def subsubsection(name = ""):
	return section(name, level = 3)

def subsubsubsection(name = ""):
	return section(name, level = 4)

def subsubsubsubsection(name = ""):
	return section(name, level = 5)

class Section:
	def __init__(self, section_name):
		self._name = section_name

	def __enter__(self):
		section(self._name, level=_current_level+1)

	def __exit__(self, type, value, tb):
		end_section()

def Pass(message):
	for i in range(_current_level+1):
		__current_section[i]["total"] += 1
		__current_section[i]["passed"] += 1

	log("Pass: " + message, color="green", style="highlight")

def Fail(message):
	for i in range(_current_level+1):
		__current_section[i]["total"] += 1
		__current_section[i]["failed"] += 1

	log("Fail: " + message, color="red", style="highlight")
	if __voice_on:
		say("Fail")

def Skip(message):
	log("Skip: " + message, color="green", style="highlight")

def wait(duration):
	info("Wait", duration, "seconds ... ", end="")

	if __gui_on and duration > 10:
		bar = progressbar.ProgressBar("Wait " + str(duration) + " seconds...")
		start_time = time.time()
		end_time = start_time + duration
		while time.time() - start_time < duration:
			time.sleep(min(0.1, end_time-time.time()))
			bar.update(min(time.time()-start_time, duration)/duration)
			bar.time_remain(end_time-time.time())
		bar.close()
	else:
		time.sleep(duration)

	info("Done.")

def wait_until(expression, timeout = 480, interval = 0.1, must = False):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	info("Waiting " + expression_str + " becomes True ... ", end = "")
	if flag:
		info("Successful. Waited 0 second.")
		return 0

	prev_frame = inspect.currentframe().f_back
	start_time = time.time()
	while time.time() - start_time <= timeout:
		flag = False
		if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
			flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
		else:
			flag = expression()

		if not flag:
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			info("Successful. Waited " + str(round(time_waited, 2)) + " seconds.")
			return time_waited
	info("Timeout. Waited " + str(timeout) + " seconds.")

	if must:
		raise AssertionError(expression_str + " not change to True in " + str(timeout) + " seconds.")
	
	return timeout

def wait_until_not(expression, timeout = 480, interval = 0.1, must = False):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	info("Waiting " + expression_str + " becomes False ... ", end = "")
	if not flag:
		info("Successful. Waited 0 second.")
		return 0

	prev_frame = inspect.currentframe().f_back
	start_time = time.time()
	while time.time() - start_time <= timeout:
		flag = False
		if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
			flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
		else:
			flag = expression()

		if flag:
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			info("Successful. Waited " + str(round(time_waited, 2)) + " seconds.")
			return time_waited
	info("Timeout. Waited " + str(timeout) + " seconds.")

	if must:
		raise AssertionError(expression_str + " not change to False in " + str(timeout) + " seconds.")
	
	return timeout

def please(do_something):
	message = "Please " + do_something + " manually."

	if __voice_on:
		say(message)

	info("--- Manual Operation Start ---")
	info(message)
	if __gui_on:
		tkinter.messagebox.showinfo("Manual Operation Request", message)
	else:
		input("Press Enter after you finished ...")
	info("--- Manual Operation End ---")

def please_check(something):
	message = "Please check if " + something + " manually."

	if __voice_on:
		say(message)

	result = False
	info("--- Manual Check Start ---")
	info(message)
	if __gui_on:
		result = tkinter.messagebox.askyesno("Manual Check Request", message)
	else:
		result = (input("If " + something + " ? (y/n): ") == "y")
	info("--- Manual Check End ---")

	if result:
		Pass("(" + something + ") is True.")
	else:
		Fail("(" + something + ") is False.")

	return result

def say(content):
	global __speak_engine
	if not __speak_engine:
		__speak_engine = pyttsx3.init()
		voices = __speak_engine.getProperty('voices')
		__speak_engine.setProperty('voice', voices[1].id)
		__speak_engine.setProperty('rate', 150)
		__speak_engine.setProperty('volume', 1)

	__speak_engine.say(content)
	__speak_engine.runAndWait()

def should_be_equal(value1, value2):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		if value1 == value2:
			Pass(str_args[0] + " is equal to " + str_args[1])
			if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
			   str_args[1] != str_value2 and __not_original_string(str_args[1]):
				log("     (" + str_args[0] + " = " + str_args[1] + " = " + str_value1 + ")", color="green", style="highlight")
			return True
		else:
			Fail(str_args[0] + " is not equal to " + str_args[1])
			if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
			   str_args[1] != str_value2 and __not_original_string(str_args[1]):
				log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color="red", style="highlight")
			elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
				log("     (" + str_args[0] + " = " + str_value1 + ")", color="red", style="highlight")
			elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
				log("     (" + str_args[1] + " = " + str_value2 + ")", color="red", style="highlight")
			return False
	else:
		if value1 == value2:
			Pass(str_value1 + " is equal to " + str_value2)
			return True
		else:
			Fail(str_value1 + " is not equal to " + str_value2)
			return False

def must_be_equal(value1, value2):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		if value1 == value2:
			Pass(str_args[0] + " is equal to " + str_args[1])
			if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
			   str_args[1] != str_value2 and __not_original_string(str_args[1]):
				log("     (" + str_args[0] + " = " + str_args[1] + " = " + str_value1 + ")", color="green", style="highlight")
			return True
		else:
			message = str_args[0] + " is not equal to " + str_args[1]
			Fail(message)
			if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
			   str_args[1] != str_value2 and __not_original_string(str_args[1]):
				log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color="red", style="highlight")
			elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
				log("     (" + str_args[0] + " = " + str_value1 + ")", color="red", style="highlight")
			elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
				log("     (" + str_args[1] + " = " + str_value2 + ")", color="red", style="highlight")
			raise AssertionError(message)
	else:
		if value1 == value2:
			Pass(str_value1 + " is equal to " + str_value2)
			return True;
		else:
			message = str_value1 + " is not equal to " + str_value2
			Fail(message)
			raise AssertionError(message)

def should_not_be_equal(value1, value2):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)
	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		if value1 != value2:
			Pass(str_args[0] + " is not equal to " + str_args[1])
			if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
			   str_args[1] != str_value2 and __not_original_string(str_args[1]):
				log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color="green", style="highlight")
			elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
				log("     (" + str_args[0] + " = " + str_value1 + ")", color="green", style="highlight")
			elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
				log("     (" + str_args[1] + " = " + str_value2 + ")", color="green", style="highlight")
			return True
		else:
			Fail(str_args[0] + " is equal to " + str_args[1])
			if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
			   str_args[1] != str_value2 and __not_original_string(str_args[1]):
				log("     (" + str_args[0] + " = " + str_args[1] + " = " + str_value1 + ")", color="red", style="highlight")
			return False
	else:
		if value1 != value2:
			Pass(str_value1 + " is not equal to " + str_value2)
			return True
		else:
			Fail(str_value1 + " is equal to " + str_value2)
			return False

def must_not_be_equal(value1, value2):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		if value1 != value2:
			Pass(str_args[0] + " is not equal to " + str_args[1])
			if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
			   str_args[1] != str_value2 and __not_original_string(str_args[1]):
				log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color="green", style="highlight")
			elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
				log("     (" + str_args[0] + " = " + str_value1 + ")", color="green", style="highlight")
			elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
				log("     (" + str_args[1] + " = " + str_value2 + ")", color="green", style="highlight")
			return True
		else:
			message = str_args[0] + " is equal to " + str_args[1]
			Fail(message)
			if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
			   str_args[1] != str_value2 and __not_original_string(str_args[1]):
				log("     (" + str_args[0] + " = " + str_args[1] + " = " + str_value1 + ")", color="red", style="highlight")
			raise AssertionError(message)
	else:
		if value1 != value2:
			Pass(str_value1 + " is not equal to " + str_value2)
			return True
		else:
			message = str_value1 + " is equal to " + str_value2
			Fail(message)
			raise AssertionError(message)

def should_be_greater(value1, value2):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		color = ""
		return_value = None
		if value1 > value2:
			Pass(str_args[0] + " is greater than " + str_args[1])
			color = "green"
			return_value = True
		else:
			Fail(str_args[0] + " is not greater than " + str_args[1])
			color = "red"
			return_value = False

		if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
		   str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")
		elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
			log("     (" + str_args[0] + " = " + str_value1 + ")", color=color, style="highlight")
		elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")

		return return_value
	else:
		if value1 > value2:
			Pass(str_value1 + " is greater than " + str_value2)
			return True
		else:
			Fail(str_value1 + " is not greater than " + str_value2)
			return False

def must_be_greater(value1, value2):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		message = ""
		color = ""
		return_value = None
		if value1 > value2:
			Pass(str_args[0] + " is greater than " + str_args[1])
			color = "green"
			return_value = True
		else:
			message = str_args[0] + " is not greater than " + str_args[1]
			Fail(message)
			color = "red"
			return_value = False

		if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
		   str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")
		elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
			log("     (" + str_args[0] + " = " + str_value1 + ")", color=color, style="highlight")
		elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")

		if not return_value:
			raise AssertionError(message)

		return return_value
	else:
		if value1 > value2:
			Pass(str_value1 + " is greater than " + str_value2)
			return True
		else:
			message = str_value1 + " is not greater than " + str_value2
			Fail(message)
			raise AssertionError(message)

def should_be_less(value1, value2):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)
	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		color = ""
		return_value = None
		if value1 < value2:
			Pass(str_args[0] + " is less than " + str_args[1])
			color = "green"
			return_value = True
		else:
			Fail(str_args[0] + " is not less than " + str_args[1])
			color = "red"
			return_value = False

		if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
		   str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")
		elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
			log("     (" + str_args[0] + " = " + str_value1 + ")", color=color, style="highlight")
		elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")

		return return_value
	else:
		if value1 < value2:
			Pass(str_value1 + " is less than " + str_value2)
			return True
		else:
			Fail(str_value1 + " is not less than " + str_value2)
			return False

def must_be_less(value1, value2):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		message = ""
		color = ""
		return_value = None
		if value1 < value2:
			Pass(str_args[0] + " is less than " + str_args[1])
			color = "green"
			return_value = True
		else:
			message = str_args[0] + " is not less than " + str_args[1]
			Fail(message)
			color = "red"
			return_value = False

		if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
		   str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")
		elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
			log("     (" + str_args[0] + " = " + str_value1 + ")", color=color, style="highlight")
		elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")

		if not return_value:
			raise AssertionError(message)

		return return_value
	else:
		if value1 < value2:
			Pass(str_value1 + " is less than " + str_value2)
			return True
		else:
			message = str_value1 + " is not less than " + str_value2
			Fail(message)
			raise AssertionError(message)

def should_not_be_greater(value1, value2):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		color = ""
		return_value = None
		if value1 <= value2:
			Pass(str_args[0] + " is not greater than " + str_args[1])
			color = "green"
			return_value = True
		else:
			Fail(str_args[0] + " is greater than " + str_args[1])
			color = "red"
			return_value = False

		if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
		   str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")
		elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
			log("     (" + str_args[0] + " = " + str_value1 + ")", color=color, style="highlight")
		elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")

		return return_value
	else:
		if value1 <= value2:
			Pass(str_value1 + " is not greater than " + str_value2)
			return True
		else:
			Fail(str_value1 + " is greater than " + str_value2)
			return False

def must_not_be_greater(value1, value2):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		message = ""
		color = ""
		return_value = None
		if value1 <= value2:
			Pass(str_args[0] + " is not greater than " + str_args[1])
			color = "green"
			return_value = True
		else:
			message = str_args[0] + " is greater than " + str_args[1]
			Fail(message)
			color = "red"
			return_value = False

		if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
		   str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")
		elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
			log("     (" + str_args[0] + " = " + str_value1 + ")", color=color, style="highlight")
		elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")

		if not return_value:
			raise AssertionError(message)

		return return_value
	else:
		if value1 <= value2:
			Pass(str_value1 + " is not greater than " + str_value2)
			return True
		else:
			message = str_value1 + " is greater than " + str_value2
			Fail(message)
			raise AssertionError(message)

def should_not_be_less(value1, value2):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		color = ""
		return_value = None
		if value1 >= value2:
			Pass(str_args[0] + " is not less than " + str_args[1])
			color = "green"
			return_value = True
		else:
			Fail(str_args[0] + " is less than " + str_args[1])
			color = "red"
			return_value = False

		if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
		   str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")
		elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
			log("     (" + str_args[0] + " = " + str_value1 + ")", color=color, style="highlight")
		elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")

		return return_value
	else:
		if value1 >= value2:
			Pass(str_value1 + " is not less than " + str_value2)
			return True
		else:
			Fail(str_value1 + " is less than " + str_value2)
			return False

def must_not_be_less(value1, value2):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		message = ""
		color = ""
		return_value = None
		if value1 >= value2:
			Pass(str_args[0] + " is not less than " + str_args[1])
			color = "green"
			return_value = True
		else:
			message = str_args[0] + " is less than " + str_args[1]
			Fail(message)
			color = "red"
			return_value = False

		if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
		   str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")
		elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
			log("     (" + str_args[0] + " = " + str_value1 + ")", color=color, style="highlight")
		elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")

		if not return_value:
			raise AssertionError(message)

		return return_value
	else:
		if value1 >= value2:
			Pass(str_value1 + " is not less than " + str_value2)
			return True
		else:
			message = str_value1 + " is less than " + str_value2
			Fail(message)
			raise AssertionError(message)

def should_be_true(expression):
	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	if flag == True:
		Pass(expression_str + " is True")
		return True
	else:
		Fail(expression_str + " is not True")
		return False

def must_be_true(expression):
	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	if flag == True:
		Pass(expression_str + " is True")
		return True
	else:
		message = expression_str + " is not True"
		Fail(message)
		raise AssertionError(message)

def should_be_false(expression):
	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	if flag == False:
		Pass(expression_str + " is False")
		return True
	else:
		Fail(expression_str + " is not False")
		return False

def must_be_false(expression):
	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	if flag == False:
		Pass(expression_str + " is False")
		return True
	else:
		message = expression_str + " is not False"
		Fail(message)
		raise AssertionError(message)

def should_be_approx(value1, value2, tolerance = 5, func=abs):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		color = ""
		return_value = None
		if func(value1 - value2) <= tolerance:
			Pass(str_args[0] + " is approx to " + str_args[1] + " with tolerance " + str(tolerance))
			color = "green"
			return_value = True
		else:
			Fail(str_args[0] + " is not approx to " + str_args[1] + " with tolerance " + str(tolerance))
			color = "red"
			return_value = False

		if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
		   str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")
		elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
			log("     (" + str_args[0] + " = " + str_value1 + ")", color=color, style="highlight")
		elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")

		return return_value
	else:
		if func(value1 - value2) <= tolerance:
			Pass(str_value1 + " is approx to " + str_value2 + " with tolerance " + str(tolerance))
			return True
		else:
			Fail(str_value1 + " is not approx to " + str_value2 + " with tolerance " + str(tolerance))
			return False

def must_be_approx(value1, value2, tolerance = 1/3600, func=abs):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		message = ""
		color = ""
		return_value = None
		if func(value1 - value2) <= tolerance:
			Pass(str_args[0] + " is approx to " + str_args[1] + " with tolerance " + str(tolerance))
			color = "green"
			return_value = True
		else:
			message = str_args[0] + " is not approx to " + str_args[1] + " with tolerance " + str(tolerance)
			Fail(message)
			color = "red"
			return_value = False

		if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
		   str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")
		elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
			log("     (" + str_args[0] + " = " + str_value1 + ")", color=color, style="highlight")
		elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")

		if message:
			raise AssertionError(message)

		return return_value
	else:
		if func(value1 - value2) <= tolerance:
			Pass(str_value1 + " is approx to " + str_value2 + " with tolerance " + str(tolerance))
			return_value = True
		else:
			message = str_value1 + " is not approx to " + str_value2 + " with tolerance " + str(tolerance)
			Fail(message)
			raise AssertionError(message)

def should_not_be_approx(value1, value2, tolerance = 5, func=abs):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		color = ""
		return_value = None
		if func(value1 - value2) <= tolerance:
			Fail(str_args[0] + " is approx to " + str_args[1] + " with tolerance " + str(tolerance))
			color = "red"
			return_value = False
		else:
			Pass(str_args[0] + " is not approx to " + str_args[1] + " with tolerance " + str(tolerance))
			color = "green"
			return_value = True

		if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
		   str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")
		elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
			log("     (" + str_args[0] + " = " + str_value1 + ")", color=color, style="highlight")
		elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")

		return return_value
	else:
		if func(value1 - value2) <= tolerance:
			Fail(str_value1 + " is approx to " + str_value2 + " with tolerance " + str(tolerance))
			return False
		else:
			Pass(str_value1 + " is not approx to " + str_value2 + " with tolerance " + str(tolerance))
			return True

def must_not_be_approx(value1, value2, tolerance = 1/3600, func=abs):
	str_value1 = __eff_str(value1)
	str_value2 = __eff_str(value2)

	if len(sys.argv[0]) > 0:
		str_args, _ = get_actual_args_str()
		message = ""
		color = ""
		return_value = None
		if func(value1 - value2) <= tolerance:
			message = str_args[0] + " is approx to " + str_args[1] + " with tolerance " + str(tolerance)
			Fail(message)
			color = "red"
			return_value = False
		else:
			Pass(str_args[0] + " is not approx to " + str_args[1] + " with tolerance " + str(tolerance))
			color = "green"
			return_value = True

		if str_args[0] != str_value1 and __not_original_string(str_args[0]) and \
		   str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[0] + " = " + str_value1 + ", " + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")
		elif str_args[0] != str_value1 and __not_original_string(str_args[0]):
			log("     (" + str_args[0] + " = " + str_value1 + ")", color=color, style="highlight")
		elif str_args[1] != str_value2 and __not_original_string(str_args[1]):
			log("     (" + str_args[1] + " = " + str_value2 + ")", color=color, style="highlight")

		if message:
			raise AssertionError(message)

		return return_value
	else:
		if func(value1 - value2) <= tolerance:
			message = str_value1 + " is approx to " + str_value2 + " with tolerance " + str(tolerance)
			Fail(message)
			raise AssertionError(message)
		else:
			Pass(str_value1 + " is not approx to " + str_value2 + " with tolerance " + str(tolerance))
			return True

def should_keep_true(expression, duration, interval = 0.1):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	if not flag:
		Fail(expression_str + " is False at beginning.")
		return False

	prev_frame = inspect.currentframe().f_back
	interval = min(duration, interval)
	start_time = time.time()
	if __gui_on and duration > 10:
		bar = progressbar.ProgressBar(expression_str + " should keep True for " + str(duration) + " seconds.")
		while time.time()-start_time <= duration:
			flag = False
			if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
				flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
			else:
				flag = expression()

			if not flag:
				bar.close()
				Fail(expression_str + " becomes False at " + str(round(time.time() - start_time, 2)) + " seconds.")
				return False
			else:
				elaspe = time.time() - start_time
				bar.update(elaspe/duration)
				bar.time_remain(duration - elaspe)
				time.sleep(interval)
		bar.close()
	else:
		while time.time()-start_time <= duration:
			flag = False
			if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
				flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
			else:
				flag = expression()

			if not flag:
				Fail(expression_str + " becomes False at " + str(round(time.time() - start_time, 2)) + " seconds.")
				return False
			else:
				time.sleep(interval)

	Pass(expression_str + " keeps True for " + str(duration) + " seconds.")
	return True

def must_keep_true(expression, duration, interval = 0.1):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	if not flag:
		message = expression_str + " is False at beginning."
		Fail(message)
		raise AssertionError(message)

	prev_frame = inspect.currentframe().f_back
	interval = min(duration, interval)
	start_time = time.time()
	if __gui_on and duration > 10:
		bar = progressbar.ProgressBar(expression_str + " must keep True for " + str(duration) + " seconds.")
		while time.time()-start_time <= duration:
			flag = False
			if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
				flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
			else:
				flag = expression()

			if not flag:
				bar.close()
				message = expression_str + " becomes False at " + str(round(time.time() - start_time, 2)) + " seconds."
				Fail(message)
				raise AssertionError(message)
			else:
				elaspe = time.time() - start_time
				bar.update(elaspe/duration)
				bar.time_remain(duration - elaspe)
				time.sleep(interval)
		bar.close()
	else:
		while time.time()-start_time <= duration:
			flag = False
			if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
				flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
			else:
				flag = expression()

			if not flag:
				message = expression_str + " becomes False at " + str(round(time.time() - start_time, 2)) + " seconds."
				Fail(message)
				raise AssertionError(message)
			else:
				time.sleep(interval)

	Pass(expression_str + " keeps True for " + str(duration) + " seconds.")
	return True

def should_keep_false(expression, duration, interval = 0.1):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	if flag:
		Fail(expression_str + " is True at beginning.")
		return False

	prev_frame = inspect.currentframe().f_back
	interval = min(duration, interval)
	start_time = time.time()
	if __gui_on and duration > 10:
		bar = progressbar.ProgressBar(expression_str + " should keep False for " + str(duration) + " seconds.")
		while time.time()-start_time <= duration:
			flag = False
			if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
				flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
			else:
				flag = expression()

			if flag:
				bar.close()
				Fail(expression_str + " becomes True at " + str(round(time.time() - start_time, 2)) + " seconds.")
				return False
			else:
				elaspe = time.time() - start_time
				bar.update(elaspe/duration)
				bar.time_remain(duration - elaspe)
				time.sleep(interval)
		bar.close()
	else:
		while time.time()-start_time <= duration:
			flag = False
			if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
				flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
			else:
				flag = expression()

			if flag:
				Fail(expression_str + " becomes True at " + str(round(time.time() - start_time, 2)) + " seconds.")
				return False
			else:
				time.sleep(interval)

	Pass(expression_str + " keeps False for " + str(duration) + " seconds.")
	return True

def must_keep_false(expression, duration, interval = 0.1):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	if flag:
		message = expression_str + " is True at beginning."
		Fail(message)
		raise AssertionError(message)

	prev_frame = inspect.currentframe().f_back
	interval = min(duration, interval)
	start_time = time.time()
	if __gui_on and duration > 10:
		bar = progressbar.ProgressBar(expression_str + " should keep False for " + str(duration) + " seconds.")
		while time.time()-start_time <= duration:
			flag = False
			if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
				flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
			else:
				flag = expression()

			if flag:
				bar.close()
				message = expression_str + " becomes True at " + str(round(time.time() - start_time, 2)) + " seconds."
				Fail(message)
				raise AssertionError(message)
			else:
				elaspe = time.time() - start_time
				bar.update(elaspe/duration)
				bar.time_remain(duration - elaspe)
				time.sleep(interval)
		bar.close()
	else:
		while time.time()-start_time <= duration:
			flag = False
			if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
				flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
			else:
				flag = expression()

			if flag:
				message = expression_str + " becomes True at " + str(round(time.time() - start_time, 2)) + " seconds."
				Fail(message)
				raise AssertionError(message)
			else:
				time.sleep(interval)
				
	Pass(expression_str + " keeps False for " + str(duration) + " seconds.")
	return True

def should_become_true(expression, timeout, interval = 0.1):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	if flag:
		Pass(expression_str + " is True at beginning.")
		return True

	info("Waiting " + expression_str + " becomes True ... ")

	prev_frame = inspect.currentframe().f_back
	interval = min(timeout, interval)
	start_time = time.time()
	while time.time() - start_time <= timeout:
		flag = False
		if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
			flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
		else:
			flag = expression()

		if not flag:
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			Pass(expression_str + " becomes True at " + str(time_waited) + " seconds.")
			return True

	Fail(expression_str + " doesn't become True in " + str(timeout) + " seconds.")
	return False

def must_become_true(expression, timeout, interval = 0.1):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	if flag:
		Pass(expression_str + " is True at beginning.")
		return True

	info("Waiting " + expression_str + " becomes True ... ")

	interval = min(timeout, interval)
	prev_frame = inspect.currentframe().f_back
	start_time = time.time()
	while time.time() - start_time <= timeout:
		flag = False
		if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
			flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
		else:
			flag = expression()

		if not flag:
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			Pass(expression_str + " becomes True at " + str(time_waited) + " seconds.")
			return True

	message = expression_str + " doesn't become True in " + str(timeout) + " seconds."
	Fail(message)
	raise AssertionError(message)

def should_become_false(expression, timeout, interval = 0.1):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	if not flag:
		Pass(expression_str + " is False at beginning.")
		return True

	info("Waiting " + expression_str + " becomes False ... ")

	interval = min(timeout, interval)
	prev_frame = inspect.currentframe().f_back
	start_time = time.time()
	while time.time() - start_time <= timeout:
		flag = False
		if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
			flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
		else:
			flag = expression()

		if flag:
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			Pass(expression_str + " becomes False at " + str(time_waited) + " seconds.")
			return True

	Fail(expression_str + " doesn't become False in " + str(timeout) + " seconds.")
	return False

def must_become_false(expression, timeout, interval = 0.1):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")
	
	flag = False
	if isinstance(expression, type(lambda:1)):
		flag = expression()
	else:
		flag = expression

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	if not flag:
		Pass(expression_str + " is False at beginning.")
		return True

	info("Waiting " + expression_str + " becomes False ... ")

	interval = min(timeout, interval)
	prev_frame = inspect.currentframe().f_back
	start_time = time.time()
	while time.time() - start_time <= timeout:
		flag = False
		if len(sys.argv[0]) > 0 and not isinstance(expression, type(lambda:1)):
			flag = eval(expression_str, prev_frame.f_globals, prev_frame.f_locals)
		else:
			flag = expression()

		if flag:
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			Pass(expression_str + " becomes False at " + str(time_waited) + " seconds.")
			return True
	message = expression_str + " doesn't become False in " + str(timeout) + " seconds."
	Fail(message)
	raise AssertionError(message)

def __excp_str(exception):
	if isinstance(exception, BaseException):
		return type(exception).__name__ + "(" + str(exception) + ")"
	elif isinstance(exception, type(BaseException)):
		return exception.__name__
	else:
		return ""

def __correct_excp(e, exception):
	if exception is None:
		return isinstance(e, BaseException)
	elif isinstance(exception, BaseException):
		return (__excp_str(e) == __excp_str(exception))
	elif isinstance(exception, type(BaseException)):
		return isinstance(e, exception)
	else:
		return False

def get_exception(expression, global_vars=None, local_vars=None):
	try:
		if isinstance(expression, type(lambda:1)):
			expression()
		elif isinstance(expression, str):
			exec(expression, global_vars, local_vars)
		return None
	except BaseException as e:
		return e

def wait_until_raise(expression, exception=None, timeout=480, interval=0.1, must=False):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	prev_frame = inspect.currentframe().f_back
	e = None
	if isinstance(expression, type(lambda:1)):
		e = get_exception(expression)
	else:
		e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

	info("Waiting " + expression_str + " to raise " + __excp_str(exception) + " ... ", end = "")
	if __correct_excp(e, exception):
		info("Successful. Waited 0 second.")
		return 0

	start_time = time.time()
	while time.time() - start_time <= timeout:
		flag = False
		e = None
		if isinstance(expression, type(lambda:1)):
			e = get_exception(expression)
		else:
			e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

		if not __correct_excp(e, exception):
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			info("Successful. Waited " + str(round(time_waited, 2)) + " seconds.")
			return time_waited
	info("Timeout. Waited " + str(timeout) + " seconds.")

	if must:
		raise AssertionError(expression_str + " don't raise " + __excp_str(exception) + " in " + str(timeout) + " seconds.")
	
	return timeout

def wait_until_not_raise(expression, timeout=480, interval=0.1, must=False):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	prev_frame = inspect.currentframe().f_back
	e = None
	if isinstance(expression, type(lambda:1)):
		e = get_exception(expression)
	else:
		e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

	info("Waiting " + expression_str + " don't raise any exceptions ... ", end = "")
	if e is None:
		info("Successful. Waited 0 second.")
		return 0

	start_time = time.time()
	while time.time() - start_time <= timeout:
		flag = False
		e = None
		if isinstance(expression, type(lambda:1)):
			e = get_exception(expression)
		else:
			e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

		if isinstance(e, BaseException):
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			info("Successful. Waited " + str(round(time_waited, 2)) + " seconds.")
			return time_waited
	info("Timeout. Waited " + str(timeout) + " seconds.")

	if must:
		raise AssertionError(expression_str + " doesn't become quiet in " + str(timeout) + " seconds.")
	
	return timeout

def should_raise(expression, exception=None):
	if not isinstance(expression, type(lambda:1)):
		raise RuntimeError("Please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	try:
		expression()
		Fail(expression_str + " doesn't raise any exception")
		return False
	except BaseException as e:
		if exception is None or \
		   (isinstance(exception, BaseException) and __excp_str(e) == __excp_str(exception)) or \
		   (isinstance(exception, type(BaseException)) and isinstance(e, exception)):
			Pass(expression_str + " raised " + __excp_str(e))
			return True
		else:
			Fail(expression_str + " raised " + __excp_str(e) + " but not " + __excp_str(exception))
			return False

def should_not_raise(expression):
	if not isinstance(expression, type(lambda:1)):
		raise RuntimeError("Please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	try:
		expression()
		Pass(expression_str + " doesn't raise any exception")
		return True
	except BaseException as e:
		Fail(expression_str + " raised " + __excp_str(e))
		return False

def should_keep_raising(expression, duration, interval=0.1, exception=None):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	prev_frame = inspect.currentframe().f_back
	e = None
	if isinstance(expression, type(lambda:1)):
		e = get_exception(expression)
	else:
		e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

	if not __correct_excp(e, exception):
		if __excp_str(e) == "":
			Fail(expression_str + " raises nothing at beginning.")
		else:
			Fail(expression_str + " raises " + __excp_str(e) + " at beginning.")
		return False

	interval = min(duration, interval)
	start_time = time.time()
	if __gui_on and duration > 10:
		bar = progressbar.ProgressBar(expression_str + " should keep raising " + __excp_str(exception) + " for " + str(duration) + " seconds.")
		while time.time()-start_time <= duration:
			e = None
			if isinstance(expression, type(lambda:1)):
				e = get_exception(expression)
			else:
				e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

			if not __correct_excp(e, exception):
				bar.close()
				if __excp_str(e) == "":
					Fail(expression_str + " raises nothing at " + str(round(time.time() - start_time, 2)) + " seconds.)")
				else:
					Fail(expression_str + " raises " + __excp_str(e) + " at " + str(round(time.time() - start_time, 2)) + " seconds.)")
				return False
			else:
				elaspe = time.time() - start_time
				bar.update(elaspe/duration)
				bar.time_remain(duration - elaspe)
				time.sleep(interval)
		bar.close()
	else:
		while time.time()-start_time <= duration:
			e = None
			if isinstance(expression, type(lambda:1)):
				e = get_exception(expression)
			else:
				e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

			if not __correct_excp(e, exception):
				if __excp_str(e) == "":
					Fail(expression_str + " raises nothing at " + str(round(time.time() - start_time, 2)) + " seconds.)")
				else:
					Fail(expression_str + " raises " + __excp_str(e) + " at " + str(round(time.time() - start_time, 2)) + " seconds.)")
				return False
			else:
				time.sleep(interval)

	Pass(expression_str + " keeps raising " + __excp_str(exception) + " for " + str(duration) + " seconds.")
	return True

def should_keep_not_raising(expression, duration, interval=0.1):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	prev_frame = inspect.currentframe().f_back
	e = None
	if isinstance(expression, type(lambda:1)):
		e = get_exception(expression)
	else:
		e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

	if e is not None:
		Fail(expression_str + " raises " + __excp_str(e) + " at beginning.")
		return False

	interval = min(duration, interval)
	start_time = time.time()
	if __gui_on and duration > 10:
		bar = progressbar.ProgressBar(expression_str + " should keep not raising for " + str(duration) + " seconds.")
		while time.time()-start_time <= duration:
			e = None
			if isinstance(expression, type(lambda:1)):
				e = get_exception(expression)
			else:
				e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

			if e is not None:
				bar.close()
				Fail(expression_str + " raises " + __excp_str(e) + " at " + str(round(time.time() - start_time, 2)) + " seconds.")
				return False
			else:
				elaspe = time.time() - start_time
				bar.update(elaspe/duration)
				bar.time_remain(duration - elaspe)
				time.sleep(interval)
		bar.close()
	else:
		while time.time()-start_time <= duration:
			e = None
			if isinstance(expression, type(lambda:1)):
				e = get_exception(expression)
			else:
				e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

			if e is not None:
				Fail(expression_str + " raises " + __excp_str(e) + " at " + str(round(time.time() - start_time, 2)) + " seconds.")
				return False
			else:
				time.sleep(interval)

	Pass(expression_str + " keeps not raising for " + str(duration) + " seconds.")
	return True

def should_become_raising(expression, timeout=480, interval=0.1, exception=None):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	prev_frame = inspect.currentframe().f_back
	e = None
	if isinstance(expression, type(lambda:1)):
		e = get_exception(expression)
	else:
		e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

	if __correct_excp(e, exception):
		Pass(expression_str + " raises " + __excp_str(exception) + " at beginning.")
		return True

	info("Waiting " + expression_str + " to raise " + __excp_str(exception) + " ... ")

	interval = min(timeout, interval)
	start_time = time.time()
	while time.time() - start_time <= timeout:
		e = None
		if isinstance(expression, type(lambda:1)):
			e = get_exception(expression)
		else:
			e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

		if not __correct_excp(e, exception):
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			Pass(expression_str + " raises " + __excp_str(exception) + " at " + str(time_waited) + " seconds.")
			return True

	Fail(expression_str + " doesn't raise " + __excp_str(exception) + " in " + str(timeout) + " seconds.")
	return False

def should_become_not_raising(expression, timeout=480, interval=0.1):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	prev_frame = inspect.currentframe().f_back
	e = None
	if isinstance(expression, type(lambda:1)):
		e = get_exception(expression)
	else:
		e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

	if e is None:
		Pass(expression_str + " doesn't raise anything at beginning.")
		return True

	info("Waiting " + expression_str + " to raise nothing ... ")

	interval = min(timeout, interval)
	start_time = time.time()
	while time.time() - start_time <= timeout:
		e = None
		if isinstance(expression, type(lambda:1)):
			e = get_exception(expression)
		else:
			e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

		if e is not None:
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			Pass(expression_str + " raises nothing at " + str(time_waited) + " seconds.")
			return True

	Fail(expression_str + " doesn't become not raising in " + str(timeout) + " seconds.")
	return False

def must_raise(expression, exception=None):
	if not isinstance(expression, type(lambda:1)):
		raise RuntimeError("Please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	try:
		expression()
		message = expression_str + " didn't raise any exception"
		Fail(message)
		raise AssertionError(message)
	except BaseException as e:
		if exception is None or \
		   (isinstance(exception, BaseException) and __excp_str(e) == __excp_str(exception)) or \
		   (isinstance(exception, type(BaseException)) and isinstance(e, exception)):
			Pass(expression_str + " raised " + __excp_str(e))
			return True
		else:
			message = expression_str + " raised " + __excp_str(e) + " but not " + __excp_str(exception)
			Fail(message)
			raise AssertionError(message)

def must_not_raise(expression):
	if not isinstance(expression, type(lambda:1)):
		raise RuntimeError("Please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	try:
		expression()
		Pass(expression_str + " didn't raise any exception")
		return True
	except BaseException as e:
		message = expression_str + " raised " + __excp_str(e)
		Fail(message)
		raise AssertionError(message)

def must_keep_raising(expression, duration, interval=0.1, exception=None):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	prev_frame = inspect.currentframe().f_back
	e = None
	if isinstance(expression, type(lambda:1)):
		e = get_exception(expression)
	else:
		e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

	if not __correct_excp(e, exception):
		message = ""
		if __excp_str(e) == "":
			message = expression_str + " raises nothing at beginning."
			Fail(message)
		else:
			message = expression_str + " raises " + __excp_str(e) + " at beginning."
			Fail(message)
		raise AssertionError(message)

	interval = min(duration, interval)
	start_time = time.time()
	if __gui_on and duration > 10:
		bar = progressbar.ProgressBar(expression_str + " should keep raising " + __excp_str(exception) + " for " + str(duration) + " seconds.")
		while time.time()-start_time <= duration:
			e = None
			if isinstance(expression, type(lambda:1)):
				e = get_exception(expression)
			else:
				e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

			if not __correct_excp(e, exception):
				bar.close()
				message = ""
				if __excp_str(e) == "":
					message = expression_str + " raises nothing at " + str(round(time.time() - start_time, 2)) + " seconds."
					Fail(message)
				else:
					message = expression_str + " raises " + __excp_str(e) + " at " + str(round(time.time() - start_time, 2)) + " seconds."
					Fail(message)
				raise AssertionError(message)
			else:
				elaspe = time.time() - start_time
				bar.update(elaspe/duration)
				bar.time_remain(duration - elaspe)
				time.sleep(interval)
		bar.close()
	else:
		while time.time()-start_time <= duration:
			e = None
			if isinstance(expression, type(lambda:1)):
				e = get_exception(expression)
			else:
				e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

			if not __correct_excp(e, exception):
				message = ""
				if __excp_str(e) == "":
					message = expression_str + " raises nothing at " + str(round(time.time() - start_time, 2)) + " seconds."
					Fail(message)
				else:
					message = expression_str + " raises " + __excp_str(e) + " at " + str(round(time.time() - start_time, 2)) + " seconds."
					Fail(message)
				raise AssertionError(message)
			else:
				time.sleep(interval)

	Pass(expression_str + " keeps raising " + __excp_str(exception) + " for " + str(duration) + " seconds.")
	return True

def must_keep_not_raising(expression, duration, interval=0.1):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	prev_frame = inspect.currentframe().f_back
	e = None
	if isinstance(expression, type(lambda:1)):
		e = get_exception(expression)
	else:
		e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

	if e is not None:
		message = expression_str + " raises " + __excp_str(e) + " at beginning."
		Fail(message)
		raise AssertionError(message)

	interval = min(duration, interval)
	start_time = time.time()
	if __gui_on and duration > 10:
		bar = progressbar.ProgressBar(expression_str + " should keep not raising for " + str(duration) + " seconds.")
		while time.time()-start_time <= duration:
			e = None
			if isinstance(expression, type(lambda:1)):
				e = get_exception(expression)
			else:
				e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

			if e is not None:
				bar.close()
				message = expression_str + " raises " + __excp_str(e) + " at " + str(round(time.time() - start_time, 2)) + " seconds."
				Fail(message)
				raise AssertionError(message)
			else:
				elaspe = time.time() - start_time
				bar.update(elaspe/duration)
				bar.time_remain(duration - elaspe)
				time.sleep(interval)
		bar.close()
	else:
		while time.time()-start_time <= duration:
			e = None
			if isinstance(expression, type(lambda:1)):
				e = get_exception(expression)
			else:
				e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

			if e is not None:
				message = expression_str + " raises " + __excp_str(e) + " at " + str(round(time.time() - start_time, 2)) + " seconds."
				Fail(message)
				raise AssertionError(message)
			else:
				time.sleep(interval)

	Pass(expression_str + " keeps not raising for " + str(duration) + " seconds.")
	return True

def must_become_raising(expression, timeout=480, interval=0.1, exception=None):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	prev_frame = inspect.currentframe().f_back
	e = None
	if isinstance(expression, type(lambda:1)):
		e = get_exception(expression)
	else:
		e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

	if __correct_excp(e, exception):
		Pass(expression_str + " raises " + __excp_str(exception) + " at beginning.")
		return True

	info("Waiting " + expression_str + " to raise " + __excp_str(exception) + " ... ")

	interval = min(timeout, interval)
	start_time = time.time()
	while time.time() - start_time <= timeout:
		e = None
		if isinstance(expression, type(lambda:1)):
			e = get_exception(expression)
		else:
			e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

		if not __correct_excp(e, exception):
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			Pass(expression_str + " raises " + __excp_str(exception) + " at " + str(time_waited) + " seconds.")
			return True

	message = expression_str + " doesn't raise " + __excp_str(exception) + " in " + str(timeout) + " seconds."
	Fail(message)
	raise AssertionError(message)

def must_become_not_raising(expression, timeout=480, interval=0.1):
	if len(sys.argv[0]) == 0 and not isinstance(expression, type(lambda:1)):
		current_frame = inspect.currentframe()
		func_name = current_frame.f_code.co_name
		raise RuntimeError("in Python console mode, please add 'lambda:' before expression")

	expression_str = ""
	if len(sys.argv[0]) > 0:
		str_args, str_kwargs = get_actual_args_str()
		if "expression" in str_kwargs:
			expression_str = "(" + str_kwargs["expression"] + ")"
		else:
			expression_str = "(" + str_args[0] + ")"
		expression_str = re.sub(r"^\(\s*lambda\s*:\s*", "(", expression_str)
	else:
		expression_str = str(expression)

	prev_frame = inspect.currentframe().f_back
	e = None
	if isinstance(expression, type(lambda:1)):
		e = get_exception(expression)
	else:
		e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

	if e is None:
		Pass(expression_str + " doesn't raise anything at beginning.")
		return True

	info("Waiting " + expression_str + " to raise nothing ... ")

	interval = min(timeout, interval)
	start_time = time.time()
	while time.time() - start_time <= timeout:
		e = None
		if isinstance(expression, type(lambda:1)):
			e = get_exception(expression)
		else:
			e = get_exception(expression_str, prev_frame.f_globals, prev_frame.f_locals)

		if e is not None:
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			Pass(expression_str + " raises nothing at " + str(time_waited) + " seconds.")
			return True

	message = expression_str + " doesn't become not raising in " + str(timeout) + " seconds."
	Fail(message)
	raise AssertionError(message)