/*	TCP Server for socket communication with Python clients.
	Server receives messages from python apps (lamp_control.py, sound_monitor.py).
	Server updates GOURDS array of JSON objects.
	Server does not send any commands.
 */
var HOST = 'localhost';
var PORT = 8090;

var net = require('net');
var server = net.createServer();
server.listen(PORT, HOST);

/*
 * TCP Server for socket communication with HTTP server.
 */
var net = require('net');

var tcpHOST = 'localhost';
var tcpPORT = 4040;

var tcpServer = net.createServer();
tcpServer.listen(tcpPORT, tcpHOST);

// @type {Array.<{address:string, listening:boolean, hot:boolean, colorTemp:number, dimming:number}>}
// This array is for collecting all the clients.
var GOURDS = [];
// Stores socket object
var activeSocket;

/*
 * Accepting connections from Python clients
 */
server.on('connection', function(socket) {
	console.log('got a new connection');
	activeSocket = socket;

	// Look for an existing record tied to the lamp's IP address
	var gInfo = GOURDS.filter(function (el) {
		return (el.address == activeSocket.remoteAddress);
	})[0];

	// Create an array object if one does not exist
	if (!gInfo) {

		// These are default values -- we'll update them later
		gInfo =
			{address:activeSocket.remoteAddress,
			listening:false,
			hot:false,
			colorTemp:3000,
			dimming:100}

		//Collecting all the clients
		GOURDS.push(gInfo);
		console.log('new monitor: ' + activeSocket.remoteAddress);
	}

	// Read data from a connection
	socket.on('data', function(data) {
		console.log('got data' + data);

		// Gets the data as an object
		var rawData = JSON.parse(data);

		// Update gourd status
		// What happens when the python program only sends 2 of 4 pieces of info???
		gInfo.listening = rawData.listening;
		gInfo.hot = rawData.hot;
		gInfo.colorTemp = rawData.colorTemp;
		gInfo.dimming = rawData.dimming;
	});
});

server.on('error', function(err) {
	console.log('Server closed');
});

server.on('close', function() {
	console.log('Server closed');
});

/*	
 * Accepting connections from HTTP server.
 */
tcpServer.on('connection', function(sock) {
	console.log('CONNECTED: ' + sock.remoteAddress + ':' + sock.remotePort);
	sock.write("TCP sending message : 1");
	console.log('Server listening on ' + server.address().address + ':' + server.address().port);

	sock.on('data', function(data) {
		console.log('got data' + data);
	});
});