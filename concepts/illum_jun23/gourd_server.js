/*	@type {Array.<{address:string, listening:boolean, hot:boolean, colorTemp:number, dimming:number}>}
 *	Stores all information about every networked lamp. */
var GOURDS = [];

/*	For accessing socket outised socket.on('connection') closure.
 *	After browser is connected, these can be called. */
var foo;
var bar;

/*	mServer = TCP server for socket communication with sound monitor program.
 *	mServer populates GOURDS. */
var mPort = 8090;
var mHost = 'localhost';

var net = require('net');
var mServer = net.createServer();
mServer.listen(mPort, mHost);

mServer.on('connection', function(socket) {
	console.log('mServer CONNECTED: ' + socket.remoteAddress + ':' + socket.remotePort);

	// Look for existing record tied to lamp's IP address.
	var gInfo = GOURDS.filter(function (el) {
		return (el.address == socket.remoteAddress);
	})[0];

	// Create an array object if one does not exist.
	if (!gInfo) {
		console.log('New sound monitor: ' + socket.remoteAddress);
		// Default values -- they are updated later
		gInfo =
			{address:socket.remoteAddress,listening:false,hot:false,
			colorTemp:3000,dimming:100}
		GOURDS.push(gInfo);
	}

	// Listen for sound monitor data
	socket.on('data', function(data) {
		console.log('Got data from sound monitor: ' + data);
		var mData = JSON.parse(data);

		// Update sound status
		if (mData.hasOwnProperty("listening")) {
			gInfo.listening = mData.listening;
		}
		if (mData.hasOwnProperty("hot")) {
			gInfo.hot = mData.hot;
		}

		// Call HTTP server and give it up-to-date "hot" status.
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

// Listening for connection by HTTP server
cServer.on('connection', function(sock) {
	console.log('cServer CONNECTED: ' + sock.remoteAddress + ':' + sock.remotePort);
	// Pass the socket to a function for outside use.
	foo = new Foo(sock);
	var chunk = "";

	// Command routing
	sock.on('data', function(data) {
		console.log('Got data from express server: ' + data);

		/*try {
			var bData = JSON.parse(data); // bData is data sent by the browser
		} catch (err) {
			console.log("JSON parse error:" + err);
		}*/

		//var lSocket = new net.Socket(); // lighting control python communication

		// Look for ";" delimeter which indicates end of command
		chunk += data.toString(); // Add string on the end of 'chunk'
		d_index = chunk.indexOf(';'); // Find the delimeter
		console.log('chunk is: ' + chunk + ', d_index is: ' + d_index);

		// Keep going until no delimeter is found
		while (d_index > -1) {
			try {
				var lSocket = new net.Socket(); // lighting control python communication
				string = chunk.substring(0, d_index); // Create string up until delimeter
				console.log(string);
				bData = JSON.parse(string); // Parse the current string
				
				if(bData.command == "get_status") {
					foo.write(JSON.stringify(GOURDS));
				} else if (bData.command == "set_colorTemp") {
					lSocket.connect(lPort, bData.parameters.address);
					bar = new Bar(lSocket);
					bar.write('{"colorTemp":' + bData.parameters.colorTemp + '}');
				} else if (bData.command == "set_dimming") {
					lSocket.connect(lPort, bData.parameters.address);
					bar = new Bar(lSocket);
					bar.write('{"dimming":' + bData.parameters.dimming + '}');
				}
			} finally {
				chunk = chunk.substring(d_index + 1); // Cuts off the processed chunk
				d_index = chunk.indexOf(';'); // Find the new delimiter
				console.log('old chunk cut off: ' + chunk + ', d_index: ' + d_index);
			}
		}
	});
});

// Routes commands to be sent to lighting control
function routeCmd (foo, lSocket, bData) {
	console.log('routeCmd fired');
}

// Writes HTTP message outside the cServer ('connection') closure.
function Foo (socket) {
	this.write = function (update) {
		if(socket) {
			socket.write(update);
		}
	}
}

// Writes/Reads lighting control messages outside the cServer ('connection') closure.
function Bar (socket) {
	this.write = function (update) {
		if(socket) {
			socket.write(update);
		}
	}

	socket.on('data', function(data) {
		console.log('Got data from lighting control: ' + data);
		var lData = JSON.parse(data);

		var gInfo = GOURDS.filter(function (el) {
			return (el.address == socket.remoteAddress);
		})[0];

		if (lData.hasOwnProperty("colorTemp")) {
			gInfo.colorTemp = lData.colorTemp;
		}
		if (lData.hasOwnProperty("dimming")) {
			gInfo.dimming = lData.dimming;
		}

		if (foo != undefined) {
			foo.write(JSON.stringify(GOURDS));
		}
		
	});
}