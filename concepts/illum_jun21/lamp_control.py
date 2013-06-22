import socket

SERVER = 'localhost'
SERVER_PORT = 8090

while True:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((SERVER, SERVER_PORT))
	data = s.recv(1024)
	print 'Received', repr(data)
	colorTemp = data.colorTemp
	dimming = data.dimming
	# call an I2C control function here
	# Might want to wait here for confirmation from I2C bus before updating server
	s.sendall('{"colorTemp":' + colorTemp + ', "dimming":' +  dimming + '}')
	s.close()

def callDriver(colorTemp, dimming):
	# Perform I2C communication here