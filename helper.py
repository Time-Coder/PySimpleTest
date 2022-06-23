import inspect

def delete_python_comments(content):
	is_in_str = False
	str_start_char = None
	last_is_slash = False
	i = 0
	while i < len(content):
		if content[i] == '\\':
			last_is_slash = True
		elif content[i] == "'" and not last_is_slash:
			if not is_in_str:
				is_in_str = True
				str_start_char = "'"
			elif str_start_char == "'":
				is_in_str = False
				str_start_char = None

			last_is_slash = False
		elif content[i] == '"' and not last_is_slash:
			if not is_in_str:
				is_in_str = True
				str_start_char = '"'
			elif str_start_char == '"':
				is_in_str = False
				str_start_char = None

			last_is_slash = False
		elif content[i] == "#" and not is_in_str:
			pos_endl = content.find("\n", i)
			if pos_endl == -1:
				pos_endl = len(content)
			content = content[:i] + content[pos_endl:]

			last_is_slash = False

		else:
			last_is_slash = False

		i += 1

	return content

__code_dict = {}
def get_actual_args_str():
	current_frame = inspect.currentframe()
	n_line = current_frame.f_back.f_back.f_lineno
	filename = current_frame.f_back.f_back.f_code.co_filename
	funcname = current_frame.f_back.f_code.co_name

	code = ""
	global __code_dict
	if filename in __code_dict:
		code = __code_dict[filename]
	else:
		code = open(filename).read()
		__code_dict[filename] = code

	i_break = -1
	for i in range(n_line):
		i_break = code.find('\n', i_break+1)

	func_begin = code.rfind(funcname, 0, i_break) + len(funcname)
	pos_left_brace = code.find('(', func_begin)
	i = pos_left_brace + 1
	n_left_brace = 1


	is_in_comment = False
	is_in_str = False
	str_start_char = None
	last_is_slash = False
	while i < len(code):
		if code[i] == '\\':
			last_is_slash = True
		elif code[i] == "'" and not last_is_slash:
			if not is_in_str:
				is_in_str = True
				str_start_char = "'"
			elif str_start_char == "'":
				is_in_str = False
				str_start_char = None

			last_is_slash = False
		elif code[i] == '"' and not last_is_slash:
			if not is_in_str:
				is_in_str = True
				str_start_char = '"'
			elif str_start_char == '"':
				is_in_str = False
				str_start_char = None

			last_is_slash = False
		elif code[i] == "#" and not is_in_str:
			is_in_comment = True
			last_is_slash = False
		elif code[i] == "\n" and is_in_comment:
			is_in_comment = False
			last_is_slash = False
		elif code[i] == ")" and not is_in_str and not is_in_comment:
			n_left_brace -= 1
			last_is_slash = False
		elif code[i] == "(" and not is_in_str and not is_in_comment:
			n_left_brace += 1
			last_is_slash = False
		else:
			last_is_slash = False

		if n_left_brace == 0:
			break

		i += 1


	str_args = delete_python_comments(code[pos_left_brace+1:i]) + "#"

	args = []
	kwargs = {}
	is_key_value = False
	key = ""
	pos_start = 0

	n_left_small_brace = 0
	n_left_middle_brace = 0
	n_left_big_brace = 0

	is_in_str = False
	str_start_char = None
	last_is_slash = False
	i = 0
	while i < len(str_args):
		if str_args[i] == "'" and not last_is_slash:
			if not is_in_str:
				is_in_str = True
				str_start_char = "'"
			elif str_start_char == "'":
				is_in_str = False
				str_start_char = None
		elif str_args[i] == '"' and not last_is_slash:
			if not is_in_str:
				is_in_str = True
				str_start_char = '"'
			elif str_start_char == '"':
				is_in_str = False
				str_start_char = None

		elif str_args[i] == "(" and not is_in_str:
			n_left_small_brace += 1
		elif str_args[i] == ")" and not is_in_str:
			n_left_small_brace -= 1

		elif str_args[i] == "[" and not is_in_str:
			n_left_middle_brace += 1
		elif str_args[i] == "]" and not is_in_str:
			n_left_middle_brace -= 1

		elif str_args[i] == "{" and not is_in_str:
			n_left_big_brace += 1
		elif str_args[i] == "}" and not is_in_str:
			n_left_big_brace -= 1

		if str_args[i] == '\\':
			last_is_slash = True
		else:
			last_is_slash = False

		if not is_in_str and n_left_small_brace == 0 and n_left_middle_brace == 0 and n_left_big_brace == 0:
			if str_args[i] in [',', '#']:
				if is_key_value:
					kwargs[key] = str_args[pos_start:i].strip(" \\\t\n")
					is_key_value = False
				else:
					args.append(str_args[pos_start:i].strip(" \\\t\n"))
				pos_start = i + 1
			elif str_args[i] == '=':
				key = str_args[pos_start:i].strip(" \\\t\n")
				is_key_value = True
				pos_start = i + 1

		i += 1

	return args, kwargs