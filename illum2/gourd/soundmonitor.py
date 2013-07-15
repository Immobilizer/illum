import pyaudio
import audioop
import time
import socket
import math

SERVER = 'localhost'
SERVER_PORT = 8090
HOT = 'true'

NOISYCOUNT = 0                                         #]
AVG = 100000.0                                         #]---- Variables for noise detector...
FAST_AVG = []                                          #]
VOLUMES = []                                           #]
FAST_VOLUMES = []                                      #]

def readAudioData(in_data, frame_count, time_info, status):

	global HOT
	global NOISYCOUNT
	global AVG
	global FAST_AVG
	global VOLUMES
	global FAST_VOLUMES

	# adjust these values to fine tune sound detection
	blockThreshold = 4 # if we get this many loud blocks in a row, sound is important
	floorFactor = math.fabs((AVG - 4036.)/(-1454)) # volumes proportional to this number and under are considered the noise floor
	if 1.2 < floorFactor < 3:
		floorFactor
	elif 1.2 > floorFactor:
		floorFactor = 1.2
	else:
		floorFactor = 3

	level = audioop.rms(in_data, 2)
	report = False
	isHot = 'false'

	print("fast average: ", FAST_AVG," average: ", AVG, "floor Factor: ", floorFactor)

	FAST_VOLUMES.insert(0, level) # add level and compute a moving average for current volume
	del FAST_VOLUMES[3:]
	FAST_AVG = sum(FAST_VOLUMES) / len(FAST_VOLUMES)

	if FAST_AVG < AVG * floorFactor: # if its quiet...
		NOISYCOUNT = 0

		VOLUMES.insert(0, level) # add level and compute a moving average for noise floor
		del VOLUMES[500:]        # if current volume is loud enough, it is not part of noise floor
		AVG = sum(VOLUMES) / len(VOLUMES)

	else: # if its loud enough...
		NOISYCOUNT += 1

		if NOISYCOUNT >= blockThreshold: # write a test to determine if the mic hears legitimate sound
			isHot = 'true'
			print ("hot, NOISYCOUNT: ", NOISYCOUNT)

	if HOT != isHot: # write a test to determine if the system should call in
		HOT = isHot;
		report = True

	if report: # call node server with sockets
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((SERVER, SERVER_PORT))
		s.sendall('{"listening":true, "hot":' +  isHot + '}')
		s.close()

	return (in_data, pyaudio.paContinue)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=readAudioData)

stream.start_stream();

print("* recording")

while stream.is_active():
    time.sleep(0.1)
    #frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()
