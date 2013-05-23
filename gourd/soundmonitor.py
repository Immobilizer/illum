import pyaudio
import audioop
import time
import socket

SERVER = 'localhost'
SERVER_PORT = 8090
HOT = 'false'

 
def readAudioData(in_data, frame_count, time_info, status):
	global HOT
	level = audioop.rms(in_data, 2)
	report = False
	isHot = 'false'

	print(level)

	#write a test to determine if the mic hears sound
	if level >= 1500:
		isHot = 'true'

	#write a test to determine if the system should call in
	if HOT != isHot:
		HOT = isHot;
		report = True

	if report:
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
