import socket
#create an INET Socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 8090));
s.sendall('{"listening":true, "hot":true}')
s.close();