# Lighting control listener
import socket
import json
import asyncore
from smbus import SMBus

class EchoHandler(asyncore.dispatcher_with_send):

	def handle_read(self):
		data = self.recv(512)

		if data:
			buffer1 = data
			length = None

			print 'received data: ', data

			while True:
				#print 'while True fired'
				if length is None:
					#print 'if length is None fired'
					if ';' not in buffer1:
						break
					length_str = buffer1.partition(';')
					#print 'buffer1.partition fired, length_str: ', length_str
					length = len(length_str[0])
					#print 'length: ', length
				if length == 0:
					break
				if len(buffer1) < length:
					break
				message = buffer1[:length]
				#print 'set message fired: ', message
				buffer1 = buffer1[length:]
				#print 'set buffer1 fired: ', buffer1
				length = None
				
				# Process message here
				if message:
					#print 'if message fired'
					controlData = json.loads(message)
					#print 'json.loads fired'

					if "colorTemp" in controlData:
						#print 'if "colorTemp" fired'
						colorTemp = controlData['colorTemp']
						cmdCT = 2

						try:
							b.write_byte_data(addr, cmdCT, colorTemp)
							try:
								value = b.read_byte_data(addr, cmdCT)
								#print 'Read byte data: ', value
								if value == colorTemp/2:
									#self.sendall(message)
									print 'Color temperature set to: ', colorTemp
								else:
									print 'Color temperature not updated'
							except IOError:
								print 'IOError: Could not read driver state'
						except IOError:
							print 'IOError: Could not deliver color command to driver.'

					if "dimming" in controlData:
						dimming = controlData['dimming']
						cmdD = 11

						try:
							b.write_byte_data(addr, cmdD, dimming)
							try:
								value = b.read_byte_data(addr, cmdD)
								print 'Read byte data: ', value
								if value == dimming/2:
									#self.sendall(message)
									print 'Dimming set to: ', dimming
								else:
									print 'Dimming not updated'
							except IOError:
								print 'IOError: Could not read driver state'
						except IOError:
							print 'IOError: Could not deliver dimming command to driver.'

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
	try:
		b.write_byte_data(addr, cmd, val)
		try:
			print 'Read byte data: ', b.read_byte_data(addr, cmd)
			if b.read_byte_data(addr, cmd) == val:
				return True
			else:
				return False
		except IOError:
			print 'IOError: Could not read driver state'
	except IOError:
		print 'IOError: Could not deliver command to driver.'

b = SMBus(1) # 1 indicates /dev/i2c-1
addr = 0x04
server = EchoServer('localhost', 50007)
asyncore.loop()