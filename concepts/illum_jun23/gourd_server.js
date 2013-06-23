/*	
 *	TCP server for socket communication w/ HTTP server.
 *	HTTP server sends data, TCP server routes data to gourd.
 *	TCP server receives data from gourd and routes to HTTP server.
 */
var tcp_PORT = 4040;			// Port for HTTP server communication
var tcp_HOST = 'localhost';
var lc_PORT = 50007;			// Port for gourd lighting control

var net = require('net');
var tcpServer = net.createServer();
tcpServer.listen(tcp_PORT, tcp_HOST);

// Listening for connection by HTTP server
tcpServer.on('connection', function(sock) {
	console.log('CONNECTED: ' + sock.remoteAddress + ':' + sock.remotePort);
	sock.write("TCP sending message: Thanks for the connection, browser.");
	console.log('Server listening on ' + tcpServer.address().address + ':' + tcpServer.address().port);

	// Routes data from HTTP server to gourd lighting control.
	sock.on('data', function(data) {
		console.log('got data ' + data);
		var browserData = JSON.parse(data);
		console.log(browserData);
		var socket = new net.Socket();
		// Perform the correct action depending on the command.
		if (browserData.command == "get_status") {
			var status = JSON.stringify(GOURDS);
			// Sends GOURDS right back to HTTP server
			sock.write(status);
		} else if (browserData.command == "open_stream") {
			// Server doesn't have to do anything here -- gourd broadcasts on port 8000
		} else if (browserData.command == "set_colorTemp") {
			socket.connect(lc_PORT, browserData.parameters.address);
			socket.write('{"colorTemp":' + browserData.parameters.colorTemp + '}');
		} else if (browserData.command == "set_dimming") {
			socket.connect(lc_PORT, browserData.parameters.address);
			socket.write('{"dimming":' + browserData.parameters.dimming + '}');
		}
	});
});

/*
 *	TCP server for socket communication with gourd sound analysis.
 *	Creates an array GOURDS to store all gourd clients.
 */
var sm_PORT = 8090;				// Port for gourd sound analysis
var sm_HOST = 'localhost';

var server = net.createServer();
server.listen(sm_PORT, sm_HOST);

// @type {Array.<{address:string, listening:boolean, hot:boolean, colorTemp:number, dimming:number}>}
var GOURDS = [];

server.on('connection', function(socket) {
	console.log('CONNECTED: ' + socket.remoteAddress + ':' + socket.remotePort);

	// Look for an existing record tied to the lamp's IP address
	var gInfo = GOURDS.filter(function (el) {
		return (el.address == socket.remoteAddress);
	})[0];

	// Create an array object if one does not exist
	if (!gInfo) {
		// These are default values -- we'll update them later
		gInfo =
			{address:socket.remoteAddress,
			listening:false,
			hot:false,
			colorTemp:3000,
			dimming:100}
		//Collecting all the clients
		GOURDS.push(gInfo);
		console.log('new monitor: ' + socket.remoteAddress);
	}

	// Read data from a connection
	socket.on('data', function(data) {
		console.log('got data' + data);
		// Gets the data as an object
		var smData = JSON.parse(data);
		// Update gourd status
		if (smData.listening != null) {
			gInfo.listening = smData.listening;}
		if (smData.hot != null) {
			gInfo.hot = smData.hot;}
		if (smData.colorTemp != null) {
			gInfo.colorTemp = smData.colorTemp;}
		if (smData.dimming != null) {
		gInfo.dimming = smData.dimming;}
		// Send sound control status to HTTP server
		sock.write(JSON.stringify(GOURDS));
	});
});

server.on('error', function(err) {
	console.log('Server closed');
});

server.on('close', function() {
	console.log('Server closed');
});