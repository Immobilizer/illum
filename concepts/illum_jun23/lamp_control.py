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
				if callI2C(cmdCT, colorTemp) == True:
					self.send(data)
					print 'Color temperature set to: ', colorTemp
				else:
					print 'Color temperature not updated'
			if "dimming" in controlData:
				dimming = controlData['dimming']
				cmdD = 5
				if callI2C(cmdD, dimming) == True:
					self.send(data)
					print 'Dimming level set to: ', dimming
				else:
					print 'Color temperature not updated'

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

def callI2C(cmd, val):
	b = SMBus(1) # 1 indicates /dev/i2c-1
	addr = 0x04
	while True:
		try:
			b.write_byte_data(addr, cmd, val)
			if b.read_byte_data(addr, cmd) == val:
				return True
			else:
				return False
			break
		except IOError:
			print 'IOError: Could not deliver command to driver.'

	

server = EchoServer('localhost', 50007)
asyncore.loop()