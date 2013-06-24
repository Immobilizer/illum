# Lighting control listener
import socket
import json
import asyncore
from smbus import SMBus

class EchoHandler(asyncore.dispatcher_with_send):

	def handle_read(self):
		data = self.recv(8192)
		if data:
			#self.send(data)
			controlData = json.loads(data)
			print 'This is what controlData looks like: ', controlData
			if "colorTemp" in controlData:
				colorTemp = controlData['colorTemp']
				cmdCT = 3
				callI2C(cmdCT, colorTemp)
				print 'Color temperature: ', colorTemp
			if "dimming" in controlData:
				dimming = controlData['dimming']
				cmdD = 5
				callI2C(cmdD, dimming)
				print 'Dimming level: ', dimming

class EchoServer(asyncore.dispatcher):

	def __init__(self, host, port):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind((host, port))
		self.listen(5)

	def handle_accept(self):
		pair = self.accept()
		if pair is not None:
			sock, addr = pair
			print 'Incoming connection from %s' % repr(addr)
			handler = EchoHandler(sock)

def callI2C(cmd, value):
	b = SMBus(1) # 1 indicates /dev/i2c-1
	addr = 0x04
	b.write_byte_data(addr, cmd, val)

server = EchoServer('localhost', 50007)
asyncore.loop()