# Lighting control listener
import socket
import json
import asyncore
from smbus import SMBus

class EchoHandler(asyncore.dispatcher_with_send):

	def handle_read(self):
		data = self.recv(512)
		print 'received data: ', data
		if data:
			controlData = json.loads(data)
			if "colorTemp" in controlData:
				colorTemp = controlData['colorTemp']
				cmdCT = 3
				self.sendall(data)
				if callI2C(cmdCT, colorTemp) == True:
					self.sendall(data)
					print 'Color temperature set to: ', colorTemp
				else:
					print 'Color temperature not updated'
			if "dimming" in controlData:
				dimming = controlData['dimming']
				cmdD = 5
				self.sendall(data)
				if callI2C(cmdD, dimming) == True:
					self.sendall(data)
					print 'Dimming level set to: ', dimming
				else:
					print 'Dimming level not updated'

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
	try:
		b.write_byte_data(addr, cmd, val)
		try:
			if b.read_byte_data(addr, cmd) == val:
				return True
			else:
				return False
		except IOError:
			print 'IOError: Could not read driver state'
	except IOError:
		print 'IOError: Could not deliver command to driver.'

server = EchoServer('localhost', 50007)
asyncore.loop()