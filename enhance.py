def wait_until(expression, timeout = 480, interval = 0.1, must = False):
	str_args = get_actual_args_string()
	info("Waiting (" + str_args[0] + ") becomes True ... ", end = "")
	if expression:
		info("Successful. Waited 0 second.")
		return 0

	start_time = time.time()
	while time.time() - start_time <= timeout:
		if not eval(str_args[0]):
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			info("Successful. Waited " + str(round(time_waited, 2)) + " seconds.")
			return time_waited
	info("Timeout. Waited " + str(timeout) + " seconds.")

	if must:
		raise AssertionError("(" + str_args[0] + ") not change to True in " + str(timeout) + " seconds.")
	
	return timeout

def wait_until_not(expression, timeout = 480, interval = 0.1, must = False):
	str_args = get_actual_args_string()
	info("Waiting (" + str_args[0] + ") becomes False ... ", end = "")
	if not expression:
		info("Successful. Waited 0 second.")
		return 0

	start_time = time.time()
	while time.time() - start_time <= timeout:
		if eval(str_args[0]):
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			info("Successful. Waited " + str(round(time_waited, 2)) + " seconds.")
			return time_waited
	info("Timeout. Waited " + str(timeout) + " seconds.")

	if must:
		raise AssertionError("(" + str_args[0] + ") not change to False in " + str(timeout) + " seconds.")
	
	return timeout

def should_keep_true(expression, time_delta, interval = 0.1):
	str_args = get_actual_args_string()
	interval = min(time_delta, interval)

	if not expression:
		Fail("(" + str_args[0] + ") doesn't keep True for " + str(time_delta) + " seconds.")
		log("     (It is False at beginning.)", color="red", style="highlight")
		return False

	start_time = time.time()
	if time_delta > 10:
		bar = progressbar.ProgressBar("(" + str_args[0] + ") should keep True for " + str(time_delta) + " seconds.")
		while time.time()-start_time <= time_delta:
			if not eval(str_args[0]):
				bar.close()
				Fail("(" + str_args[0] + ") doesn't keep True for " + str(time_delta) + " seconds.")
				log("     (It becomes False at " + str(round(time.time() - start_time, 2)) + " seconds.)", color="red", style="highlight")
				return False
			else:
				elaspe = time.time() - start_time
				bar.update(elaspe/time_delta)
				bar.time_remain(time_delta - elaspe)
				time.sleep(interval)
		bar.close()
	else:
		while time.time()-start_time <= time_delta:
			if not eval(str_args[0]):
				Fail("(" + str_args[0] + ") doesn't keep True for " + str(time_delta) + " seconds.")
				log("     (It becomes False at " + str(round(time.time() - start_time, 2)) + " seconds.)", color="red", style="highlight")
				return False
			else:
				time.sleep(interval)

	Pass("(" + str_args[0] + ") keeps True for " + str(time_delta) + " seconds.")
	return True

def must_keep_true(expression, time_delta, interval = 0.1):
	str_args = get_actual_args_string()
	interval = min(time_delta, interval)

	if not expression:
		message = "(" + str_args[0] + ") doesn't keep True for " + str(time_delta) + " seconds."
		Fail(message)
		log("     (It is False at beginning.)", color="red", style="highlight")
		raise AssertionError(message)
		return False

	start_time = time.time()
	if time_delta > 10:
		bar = progressbar.ProgressBar("(" + str_args[0] + ") must keep True for " + str(time_delta) + " seconds.")
		while time.time()-start_time <= time_delta:
			if not eval(str_args[0]):
				bar.close()
				message = "(" + str_args[0] + ") doesn't keep True for " + str(time_delta) + " seconds."
				Fail(message)
				log("     (It becomes False at " + str(round(time.time() - start_time, 2)) + " seconds.)", color="red", style="highlight")
				raise AssertionError(message)
				return False
			else:
				elaspe = time.time() - start_time
				bar.update(elaspe/time_delta)
				bar.time_remain(time_delta - elaspe)
				time.sleep(interval)
		bar.close()
	else:
		while time.time()-start_time <= time_delta:
			if not eval(str_args[0]):
				message = "(" + str_args[0] + ") doesn't keep True for " + str(time_delta) + " seconds."
				Fail(message)
				log("     (It becomes False at " + str(round(time.time() - start_time, 2)) + " seconds.)", color="red", style="highlight")
				raise AssertionError(message)
				return False
			else:
				time.sleep(interval)

	Pass("(" + str_args[0] + ") keeps True for " + str(time_delta) + " seconds.")
	return True

def should_keep_false(expression, time_delta, interval = 0.1):
	str_args = get_actual_args_string()
	interval = min(time_delta, interval)

	if expression:
		Fail("(" + str_args[0] + ") doesn't keep False for " + str(time_delta) + " seconds.")
		log("     (It's True at beginning.)")
		return False

	start_time = time.time()
	if time_delta > 10:
		bar = progressbar.ProgressBar("(" + str_args[0] + ") should keep False for " + str(time_delta) + " seconds.")
		while time.time()-start_time <= time_delta:
			if eval(str_args[0]):
				bar.close()
				Fail("(" + str_args[0] + ") doesn't keep False for " + str(time_delta) + " seconds.")
				log("     (It becomes True at " + str(round(time.time() - start_time, 2)) + " seconds.)", color="red", style="highlight")
				return False
			else:
				elaspe = time.time() - start_time
				bar.update(elaspe/time_delta)
				bar.time_remain(time_delta - elaspe)
				time.sleep(interval)
		bar.close()
	else:
		while time.time()-start_time <= time_delta:
			if eval(str_args[0]):
				Fail("(" + str_args[0] + ") doesn't keep False for " + str(time_delta) + " seconds.")
				log("     (It becomes True at " + str(round(time.time() - start_time, 2)) + " seconds.)", color="red", style="highlight")
				return False
			else:
				time.sleep(interval)

	Pass("(" + str_args[0] + ") keeps False for " + str(time_delta) + " seconds.")
	return True

def must_keep_false(expression, time_delta, interval = 0.1):
	str_args = get_actual_args_string()
	interval = min(time_delta, interval)

	if expression:
		message = "(" + str_args[0] + ") doesn't keep False for " + str(time_delta) + " seconds."
		Fail(message)
		log("     (It's True at beginning.)", color="red", style="highlight")
		raise AssertionError(message)
		return False

	start_time = time.time()
	if time_delta > 10:
		bar = progressbar.ProgressBar("(" + str_args[0] + ") should keep False for " + str(time_delta) + " seconds.")
		while time.time()-start_time <= time_delta:
			if eval(str_args[0]):
				bar.close()
				message = "(" + str_args[0] + ") doesn't keep False for " + str(time_delta) + " seconds."
				Fail(message)
				log("     (It becomes True at " + str(round(time.time() - start_time, 2)) + " seconds.)", color="red", style="highlight")
				raise AssertionError(message)
				return False
			else:
				elaspe = time.time() - start_time
				bar.update(elaspe/time_delta)
				bar.time_remain(time_delta - elaspe)
				time.sleep(interval)
		bar.close()
	else:
		while time.time()-start_time <= time_delta:
			if eval(str_args[0]):
				message = "(" + str_args[0] + ") doesn't keep False for " + str(time_delta) + " seconds."
				Fail(message)
				log("     (It becomes True at " + str(round(time.time() - start_time, 2)) + " seconds.)", color="red", style="highlight")
				raise AssertionError(message)
				return False
			else:
				time.sleep(interval)
				
	Pass("(" + str_args[0] + ") keeps False for " + str(time_delta) + " seconds.")
	return True

def should_become_true(expression, timeout, interval = 0.1):
	str_args = get_actual_args_string()
	if expression:
		Pass("(" + str_args[0] + ") becomes True in " + str(timeout) + " seconds.")
		log("     (It is True at beginning.)", color="green", style="highlight")
		return True

	info("Waiting (" + str_args[0] + ") becomes True ... ")

	start_time = time.time()
	while time.time() - start_time <= timeout:
		if not eval(str_args[0]):
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			Pass("(" + str_args[0] + ") becomes True in " + str(timeout) + " seconds.")
			log("     (It becomes True at " + str(time_waited) + " seconds.)", color="green", style="highlight")
			return True

	Fail("(" + str_args[0] + ") doesn't become True in " + str(timeout) + " seconds.")
	return False

def must_become_true(expression, timeout, interval = 0.1):
	str_args = get_actual_args_string()
	if expression:
		Pass("(" + str_args[0] + ") becomes True in " + str(timeout) + " seconds.")
		log("     (It is True at beginning.)", color="green", style="highlight")
		return True

	info("Waiting (" + str_args[0] + ") becomes True ... ")

	start_time = time.time()
	while time.time() - start_time <= timeout:
		if not eval(str_args[0]):
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			Pass("(" + str_args[0] + ") becomes True in " + str(timeout) + " seconds.")
			log("     (It becomes True at " + str(time_waited) + " seconds.)", color="green", style="highlight")
			return True

	message = "(" + str_args[0] + ") doesn't become True in " + str(timeout) + " seconds."
	Fail(message)
	raise AssertionError(message)
	return False

def should_become_false(expression, timeout, interval = 0.1):
	str_args = get_actual_args_string()
	if not expression:
		Pass("(" + str_args[0] + ") becomes False in " + str(timeout) + " seconds.")
		log("     (It's False at beginning.)", color="green", style="highlight")
		return True

	info("Waiting (" + str_args[0] + ") becomes False ... ")

	start_time = time.time()
	while time.time() - start_time <= timeout:
		if eval(str_args[0]):
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			Pass("(" + str_args[0] + ") becomes False in " + str(timeout) + " seconds.")
			log("     (It becomes False at " + str(time_waited) + " seconds.)", color="green", style="highlight")
			return True

	Fail("(" + str_args[0] + ") doesn't become False in " + str(timeout) + " seconds.")
	return False

def must_become_false(expression, timeout, interval = 0.1):
	str_args = get_actual_args_string()
	if not expression:
		Pass("(" + str_args[0] + ") becomes False in " + str(timeout) + " seconds.")
		log("     (It's False at beginning.)", color="green", style="highlight")
		return True

	info("Waiting \"" + str_args[0] + "\" becomes False ... ")

	start_time = time.time()
	while time.time() - start_time <= timeout:
		if eval(str_args[0]):
			time.sleep(interval)
		else:
			time_waited = time.time() - start_time
			Pass("(" + str_args[0] + ") becomes False in " + str(timeout) + " seconds.")
			log("     (It becomes False at " + str(time_waited) + " seconds.)", color="green", style="highlight")
			return True
	message = "(" + str_args[0] + ") doesn't become False in " + str(timeout) + " seconds."
	Fail(message)
	raise AssertionError(message)
	return False