import inspect
import sys
import re

def reg_rfind(content, pattern, pos_start, pos_end):
	str_index, comment_index = get_invalid_index(content)

	its = list(re.finditer(pattern, content[pos_start:pos_end]))
	if len(its) == 0:
		return -1

	for it in reversed(its):
		if it.start() not in str_index and it.start() not in comment_index:
			return it.start()

	return it.start()

def find_pair(content, i):
	if i < 0 or i >= len(content) or content[i] not in "([{":
		return -1

	start_pair = content[i]
	end_pair = None
	if content[i] == '(':
		end_pair = ')'
	elif content[i] == '[':
		end_pair = ']'
	elif content[i] == '{':
		end_pair = '}'

	n_start_pair = 0
	str_index, comment_index = get_invalid_index(content)
	while i < len(content):
		if i not in str_index and i not in comment_index:
			if content[i] == start_pair:
				n_start_pair += 1
			elif content[i] == end_pair:
				n_start_pair -= 1

			if n_start_pair == 0:
				break

		i += 1

	return i

def rfind_pair(content, i):
	if i < 0 or i >= len(content) or content[i] not in ")]}":
		return -1

	start_pair = content[i]
	end_pair = None
	if content[i] == ')':
		end_pair = '('
	elif content[i] == ']':
		end_pair = '['
	elif content[i] == '}':
		end_pair = '{'

	n_start_pair = 0
	str_index, comment_index = get_invalid_index(content)
	while i < len(content):
		if i not in str_index and i not in comment_index:
			if content[i] == start_pair:
				n_start_pair += 1
			elif content[i] == end_pair:
				n_start_pair -= 1

			if n_start_pair == 0:
				break

		i -= 1

	return i

def get_var_before_pos(code, pos):
	if pos < 0:
		return None

	if pos > len(code):
		pos = len(code)-1

	pos = rskip_space(code, pos)
	if pos == -1:
		return None

	token, _ = rget_token(code, pos)
	used_frame = inspect.currentframe().f_back.f_back.f_back

	return eval(token["word"], used_frame.f_globals, used_frame.f_locals)

__str_index_dict = {}
__comment_index_dict = {}
def get_invalid_index(content):
	global __str_index_dict
	if content in __str_index_dict:
		return __str_index_dict[content], __comment_index_dict[content]

	str_index = set()
	comment_index = set()
	in_comment = False
	in_str = False
	str_start_char = None
	last_is_slash = False
	i = 0
	while i < len(content):
		should_add = True
		if content[i] == "'" and not last_is_slash:
			if not in_str:
				should_add = False
				in_str = True
				str_start_char = "'"
			elif str_start_char == "'":
				in_str = False
				str_start_char = None
		elif content[i] == '"' and not last_is_slash:
			if not in_str:
				should_add = False
				in_str = True
				str_start_char = '"'
			elif str_start_char == '"':
				in_str = False
				str_start_char = None
		elif content[i] in "#\\" and not in_str:
			in_comment = True
		elif content[i] == "\n" and in_comment:
			in_comment = False
		
		if content[i] == '\\' and in_str:
			last_is_slash = (not last_is_slash)
		else:
			last_is_slash = False

		if should_add:
			if in_str:
				str_index.add(i)
			if in_comment:
				comment_index.add(i)

		i += 1

	__str_index_dict[content] = str_index
	__comment_index_dict[content] = comment_index

	return str_index, comment_index


def delete_python_comments(content):
	str_start_char = None
	i = 0

	str_index, comment_index = get_invalid_index(content)
	while i < len(content):
		if i not in str_index:
			if content[i] == "#":
				pos_endl = content.find("\n", i)
				if pos_endl == -1:
					pos_endl = len(content)
				content = content[:i] + content[pos_endl:]
			elif content[i] == '\\':
				pos_endl = content.find("\n", i)
				if pos_endl == -1:
					pos_endl = len(content)
				else:
					pos_endl += 1

				content = content[:i] + content[pos_endl:]

		i += 1

	return content

__code_dict = {}
def get_actual_args_str():
	current_frame = inspect.currentframe()
	n_line = current_frame.f_back.f_back.f_lineno
	filename = current_frame.f_back.f_back.f_code.co_filename
	funcname = current_frame.f_back.f_code.co_name
	is_method = ("self" in current_frame.f_back.f_locals)

	if (funcname == "__init__" or funcname == "__new__") and is_method:
		funcname = current_frame.f_back.f_locals["self"].__class__.__name__
		is_method = False

	code = ""
	global __code_dict
	if filename in __code_dict:
		code = __code_dict[filename]
	else:
		code = open(filename, "r", encoding=sys.getdefaultencoding(), errors="ignore").read()
		__code_dict[filename] = code

	i_break = -1
	for i in range(n_line):
		i_break = code.find('\n', i_break+1)

	pos_func_start = i_break
	func_begin_bak = None
	func_begin = None

	if is_method:
		while True:
			pos_func_start = reg_rfind(code, funcname + r"\s*\(", 0, pos_func_start-1)
			if pos_func_start == -1:
				func_begin = func_begin_bak
				break

			if func_begin_bak is None:
				func_begin_bak = func_begin

			var = get_var_before_pos(code, pos_func_start-1)
			if var is None or (is_method and current_frame.f_back.f_locals["self"] is var):
				func_begin = pos_func_start + len(funcname)
				break
	else:
		pos_func_start = reg_rfind(code, funcname + r"\s*\(", 0, pos_func_start-1)
		func_begin = pos_func_start + len(funcname)

	pos_left_brace = code.find('(', func_begin)
	i = find_pair(code, pos_left_brace)
	str_args = delete_python_comments(code[pos_left_brace+1:i]) + "#"

	args = []
	kwargs = {}
	is_key_value = False
	key = ""
	pos_start = 0

	n_left_small_brace = 0
	n_left_middle_brace = 0
	n_left_big_brace = 0

	str_index, comment_index = get_invalid_index(str_args)
	i = 0
	while i < len(str_args):
		if i not in str_index:
			if str_args[i] == "(":
				n_left_small_brace += 1
			elif str_args[i] == ")":
				n_left_small_brace -= 1

			elif str_args[i] == "[":
				n_left_middle_brace += 1
			elif str_args[i] == "]":
				n_left_middle_brace -= 1

			elif str_args[i] == "{":
				n_left_big_brace += 1
			elif str_args[i] == "}":
				n_left_big_brace -= 1

			if n_left_small_brace == 0 and n_left_middle_brace == 0 and n_left_big_brace == 0:
				if str_args[i] in ",#":
					if is_key_value:
						kwargs[key] = str_args[pos_start:i].strip(" \\\t\n")
						is_key_value = False
					else:
						args.append(str_args[pos_start:i].strip(" \\\t\n"))
					pos_start = i + 1
				elif str_args[i] == '=' and (i-1 > 0 and str_args[i-1] not in "><!=") and (i+1 < len(str_args) and str_args[i+1] != "="):
					key = str_args[pos_start:i].strip(" \\\t\n")
					is_key_value = True
					pos_start = i + 1

		i += 1

	return args, kwargs