import pyttsx3

global __speak_engine
__speak_engine = None

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