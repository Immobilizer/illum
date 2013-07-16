# Lighting control listener
import socket
import json
import asyncore
import math
from smbus import SMBus
from numpy import linalg as LA
import numpy as np
import time

class EchoHandler(asyncore.dispatcher_with_send):

	def handle_read(self):
		data = self.recv(512)

		if data:
			buffer1 = data
			length = None

			print 'received data: ', data

			while True:
				print 'while True fired'
				if length is None:
					print 'if length is None fired'
					if ';' not in buffer1:
						break
					length_str = buffer1.partition(';')
					print 'buffer1.partition fired, length_str: ', length_str
					length = len(length_str[0])
					print 'length: ', length
				if length == 0:
					break
				if len(buffer1) < length:
					break
				message = buffer1[:length]
				print 'set message fired: ', message
				buffer1 = buffer1[length:]
				print 'set buffer1 fired: ', buffer1
				length = None
				
				# Process message here
				if message:
					print 'if message fired'
					controlData = json.loads(message)
					print 'json.loads fired'

					if "parameters" in controlData:
						print 'if "parameters" fired'
						ccx = controlData['parameters']['ccx']
						ccy = controlData['parameters']['ccy']
						lumens = controlData['parameters']['lumens']
						reveal = controlData['parameters']['reveal']

						#ccx = .4258
						#ccy = .3846
						#lumens = 4000
						#reveal = 10.

						ccx0 = [0.697, 0.1661, 0.1523, 0.3842]
						ccy0 = [0.3016, 0.7108, 0.0263, 0.3863]
						lumens0 = [7974, 13005, 2536, 12080]
						current0 = [400, 400, 400, 350]

						X0 = [0, 0, 0, 0]
						Y0 = [0, 0, 0, 0]
						Z0 = [0, 0, 0, 0]
						M1 = [[None for x in range(3)] for y in range(3)]
						M2 = [[None for x in range(3)] for y in range(2)]
						M3 = [[None for x in range(3)] for y in range(3)]
						M4 = [[None for x in range(3)] for y in range(2)]

						for x in range (0, 4):
							X0[x] = ccx0[x] / ccy0[x] * lumens0[x]
							Y0[x] = lumens0[x]
							Z0[x] = (1 - ccx0[x] - ccy0[x]) / ccy0[x] * lumens0[x]

						if ccy<(ccy0[3]-ccy0[0])/(ccx0[3]-ccx0[0])*(ccx-ccx0[3])+ccy0[3]:
							if ccy<(ccy0[3]-ccy0[2])/(ccx0[3]-ccx0[2])*(ccx-ccx0[3])+ccy0[3]:
								choice = 1
							else:
								choice = 0
						elif ccy<(ccy0[3]-ccy0[1])/(ccx0[3]-ccx0[1])*(ccx-ccx0[3])+ccy0[3]:
							choice = 0
						else:
							choice = 2

						a = 0

						for y in range (0, 3):
							if a == choice:
								a += 1
							M1[0][y] = X0[a]
							M1[1][y] = Y0[a]
							M1[2][y] = Z0[a]
							a += 1

						X = ccx / ccy * lumens
						Y = lumens
						Z = (1 - ccx - ccy) / ccy * lumens

						M2 = [[X, 0], [Y, 0], [Z, 0]]
						M1np = np.array(M1)
						M1inv = LA.inv(M1np)

						lf0 = np.dot(M1inv, M2)
						lfw = (lf0[2][0]) * (1 - reveal * 1.0 / 10)

						for y in range (0, 3):
							M3[0][y] = X0[y]
							M3[1][y] = Y0[y]
							M3[2][y] = Z0[y]

						M4 = [[X - X0[3] * lfw, 0], [Y - Y0[3] * lfw, 0], [Z - Z0[3] * lfw, 0]]
						M3np = np.array(M3)
						M3inv = LA.inv(M3np)

						lf = np.dot(M3inv, M4)
						lfr = lf[0, 0]
						lfg = lf[1, 0]
						lfb = lf[2, 0]

						iRed = int(current0[0] * lfr)
						iGreen = int(current0[1] * lfg)
						iBlue = int(current0[2] * lfb)
						iWhite = int(0.048498 * math.pow((lfw * lumens0[3]/4), 1.1061))

						print 'iRed: ', iRed
						print 'iGreen: ', iGreen
						print 'iBlue: ', iBlue
						print 'iWhite: ', iWhite

						cmdRed = 14
						cmdGreen = 8
						cmdBlue = 6
						cmdWhite = 4

						try:
							b.write_byte_data(addr, cmdRed, iRed)
							#time.sleep(.1)
							b.write_byte_data(addr, cmdGreen, iGreen)
							#time.sleep(.1)
							b.write_byte_data(addr, cmdBlue, iBlue)
							#time.sleep(.1)
							b.write_byte_data(addr, cmdWhite, iWhite)
							try:
								vRed = b.read_byte_data(addr, cmdRed)
								vGreen = b.read_byte_data(addr, cmdGreen)
								vBlue = b.read_byte_data(addr, cmdBlue)
								vWhite = b.read_byte_data(addr, cmdWhite)
								print 'Read byte data: ', vRed
								print 'Read byte data: ', vGreen
								print 'Read byte data: ', vBlue
								print 'Read byte data: ', vWhite
								#if value == colorTemp/2:
									#self.sendall(message)
									#print 'Color temperature set to: removed this for now'
								#else:
									#print 'Color temperature not updated'
							except IOError:
								print 'IOError: Could not read driver state'
						except IOError:
							print 'IOError: Could not deliver command to driver.'

					if "dimming" in controlData:
						dimming = controlData['dimming']
						cmdD = 10

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
							print 'IOError: Could not deliver command to driver.'

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