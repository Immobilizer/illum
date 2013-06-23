# Lighting control listener
import socket
import json

HOST = ''			# Symbolic name meaning all available interfaces
PORT = 50007		# All gourds will listen on this PORT
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connected by', addr
while 1:
	data = conn.recv(1024)
	print 'Received', repr(data)
	if not data: break
	controlData = dict(json.loads(data))
	print 'This is what controlData looks like: ', controlData
	colorTemp = controlData.colorTemp
	dimming = controlData.dimming
	# call an I2C control function here
	# Might want to wait for confirmation from I2C bus before updating server
	conn.sendall('{"colorTemp":' + colorTemp + ', "dimming":' + dimming + '}')
	conn.sendall(data)		# Echoes all data to gourd_server
conn.close()

#def callDriver(colorTemp, dimming):
	# Perform I2C communication here