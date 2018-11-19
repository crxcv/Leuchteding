from machine import Pin, PWM
from rtttl import RTTTL
import _thread

piezo_pin = 21
piezo = PWM(piezo_pin)
piezo.deinit()
abort_playback = False

SONGS = [
	'OneMoreT:d=16,o=5,b=125:4e,4e,4e,4e,4e,4e,8p,4d#.,4e,4e,4e,4e,4e,4e,8p,4d#.,4e,4e,4e,4e,4e,4e,8p,4d#.,4f#,4f#,4f#,4f#,4f#,4f#,8f#,4d#.,4e,4e,4e,4e,4e,4e,8p,4d#.,4e,4e,4e,4e,4e,4e,8p,4d#.,1f#,2f#',
	'MarioTitle:d=4,o=5,b=125:8d7,8d7,8d7,8d6,8d7,8d7,8d7,8d6,2d#7,8d7,p,32p,8d6,8b6,8b6,8b6,8d6,8b6,8b6,8b6,8d6,8b6,8b6,8b6,16b6,16c7,b6,8a6,8d6,8a6,8a6,8a6,8d6,8a6,8a6,8a6,8d6,8a6,8a6,8a6,16a6,16b6,a6,8g6,8d6,8b6,8b6,8b6,8d6,8b6,8b6,8b6,8d6,8b6,8b6,8b6,16a6,16b6,c7,e7,8d7,8d7,8d7,8d6,8c7,8c7,8c7,8f#6,2g6',
	'Tetris:d=4,o=5,b=160:e6,8b,8c6,8d6,16e6,16d6,8c6,8b,a,8a,8c6,e6,8d6,8c6,b,8b,8c6,d6,e6,c6,a,2a,8p,d6,8f6,a6,8g6,8f6,e6,8e6,8c6,e6,8d6,8c6,b,8b,8c6,d6,e6,c6,a,a'
]

def waitForExitNotification(timeout):
	""" waitForExitNotification(timeout)
	uses _thread.wait(timeout) to sleep for amount of ms saved in timeout and
	checks notfication for _thread.EXIT notification. Returns True if
	_thread.EXIT notification is recieved, else returns False

	timeout: (ms) time in ms used for _thread.wait()
	return: (boolean) True if _thread.EXIT is recieved, else False.
	"""
	ntf = _thread.wait(timeout)
	if ntf == _thread.EXIT:
		return True
	return False

def play_tone(freq, msec):
	"""play_tone(freq, msec)
	plays a single tone on piezo buzzer
	freq: frequency of the tone
	msec: duration in millis
	"""
	global piezo
	global abort_playback
	print('freq = {:6.1f} msec = {:6.1f}'.format(freq, msec))
	if freq >0:
		piezo.freq(int(freq))
		piezo.duty(50)

	ntf0 =waitForExitNotification(int(msec *0.9))
	piezo.duty(0)
	ntf1 = waitForExitNotification(int(msec * 0.1))
	if (ntf0 or ntf1):
		piezo.deinit()
		abort_playback = True

def find_song(name):
	""" find_song(name)
	searches in SONGS list for song name and plays
	its tones with the play_tone function
	name: name of the song to search for
	"""
	global abort_playback
	abort_playback = False
	piezo.init()

	for song in SONGS:
		song_name = song.split(":")[0]
		if song_name == name:
			tune = RTTTL(song)

			for freq, msec in tune.notes():
				play_tone(freq, msec)
				if abort_playback:
					return
			piezo.deinit()
