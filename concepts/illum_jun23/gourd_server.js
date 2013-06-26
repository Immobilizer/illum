/*	@type {Array.<{address:string, listening:boolean, hot:boolean, colorTemp:number, dimming:number}>}
 *	Stores all information about every networked lamp. */
var GOURDS = [];

/*	For accessing socket outised socket.on('connection') closure.
 *	After somebody is connected, foo.write(); can be called. */
 var foo;

/*	mServer = TCP server for socket communication with sound analysis program.
 *	mServer populates GOURDS. */
var mPort = 8090;
var mHost = 'localhost';

var net = require('net');
var mServer = net.createServer();
mServer.listen(mPort, mHost);

mServer.on('connection', function(socket) {
	console.log('mServer CONNECTED: ' + socket.remoteAddress + ':' + socket.remotePort);

	//Look for existing record tied to lamp's IP address.
	var gInfo = GOURDS.filter(function (el) {
		return (el.address == socket.remoteAddress);
	})[0];

	//Create an array object if one does not exist.
	if (!gInfo) {
		//Default values -- they are updated later
		gInfo =
			{address:socket.remoteAddress,listening:false,hot:false,
			colorTemp:3000,dimming:100}
		GOURDS.push(gInfo);
		console.log('New Monitor: ' + socket.remoteAddress);
	}

	//Listen for sound monitor data
	socket.on('data', function(data) {
		console.log('Got data: ' + data);
		var mData = JSON.parse(data);

		//Update sound status
		if (mData.hasOwnProperty("listening")) {
			gInfo.listening = mData.listening;
		}
		if (mData.hasOwnProperty("hot")) {
			gInfo.hot = mData.hot;
		}

		//Call HTTP server and give it up-to-date "hot" status.
		if (foo != undefined) {
			foo.write(JSON.stringify(GOURDS));
		}
	});
});

mServer.on('error', function(err) {
	console.log('mServer closed -- error: ' + err);
});

mServer.on('close', function() {
	console.log('mServer closed');
});

/*	cServer = TCP server for socket communication with HTTP server.
 *	Receives commands from browser and determines what to do.
 *	lSocket = Sends/receives commands to lighting control program. */
var cPort = 4040;
var cHost = 'localhost';
var lPort = 50007;

var cServer = net.createServer();
cServer.listen(cPort, cHost);

//Listening for connection by HTTP server
cServer.on('connection', function(sock) {
	console.log('cServer CONNECTED: ' + sock.remoteAddress + ':' + sock.remotePort);
	//For testing purposes. Not necessary in production:
	sock.write("cServer sending message: Thanks for the connection, browser");
	//Pass the socket to a function for outside use.
	foo = new Foo(sock);

	//Routes data from HTTP server to gourd lighting control
	sock.on('data', function(data) {
		console.log('Got data: ' + data);
		//bData = data sent by browser
		var bData = JSON.parse(data);

		//New socket to communicate with lighting control program.
		var lSocket = new net.Socket();

		if (bData.command == "get_status") {
			var status = JSON.stringify(GOURDS);
			sock.write(status);
		} else if (bData.command == "open_stream") {
			var status = JSON.stringify(GOURDS);
		} else if (bData.command == "set_colorTemp") {
			lSocket.connect(lPort, bData.parameters.address);
			lSocket.write('{"colorTemp":' + bData.parameters.colorTemp + '}');
			var bar = new Bar(lSocket, "colorTemp", bData.parameters.colorTemp);
		} else if (bData.command == "set_dimming") {
			lSocket.connect(lPort, bData.parameters.address);
			lSocket.write('{"dimming":' + bData.parameters.dimming + '}');
			var bar = new Bar(lSocket, "dimming", bData.parameters.dimming);
		}

	});

});

// Writes a message to the HTTP server socket outside the ('connection') closure.
function Foo (socket) {
	this.write = function (update) {
		if(socket) {
			socket.write(update);
		}
	}
}

/*	Reads a message from a lSocket outside the ('connection') closure.
 *	Sends this message to HTTP server socket. */
function Bar (socket, cmd, val) {
	socket.on('data', function(data) {
		console.log('Got data from lighting control: ' + data);
		var gInfo = GOURDS.filter(function (el) {
			return (el.address == socket.remoteAddress);
		})[0];
		gInfo.cmd = val;
		foo.write(JSON.stringify(GOURDS));
	});
}