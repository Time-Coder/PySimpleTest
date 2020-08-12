import PySimpleGUI as sg
import gc

class ProgressBar:
	def __init__(self, title = "Please wait..."):
		self.__layout = [[sg.Text('', size=(50, 1), key="progress")],
						 [sg.ProgressBar(1000, orientation='h', size=(50, 20), key="bar")],
						 [sg.Text('', size=(50, 1), key="time_remain")]]

		self.__window = sg.Window(title, self.__layout)

	def time_remain(self, value):
		hour = int(value/60/60)
		minute = int((value - hour*60*60)/60)
		second = int(value - hour*60*60 - minute*60)

		str_hour = str(hour)
		if len(str_hour) == 1:
			str_hour = '0' + str_hour

		str_minute = str(minute)
		if len(str_minute) == 1:
			str_minute = '0' + str_minute

		str_second = str(second)
		if len(str_second) == 1:
			str_second = '0' + str_second

		self.__window["time_remain"].Update("Time Remain: " + str_hour + ":" + str_minute + ":" + str_second)

	def update(self, progress):
		event, values = self.__window.read(timeout=10)
		value = int(max(min(1000*progress, 1000), 0))
		self.__window["bar"].UpdateBar(value)
		self.__window["progress"].Update(str(round(value/10, 2)) + "% Complete")

	def close(self):
		self.__window.close()
		self.__layout = None
		self.__window = None
		gc.collect()