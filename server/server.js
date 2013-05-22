//NODE
var net = require('net');

var HOST = 'localhost';
var PORT = 8090;

var activeSocket;

/** @type {Array.<{address:string, streamAvailable:boolean, hot:boolean}> */
var MONITORS = [];

net.createServer(onSocketConnection).listen(PORT, HOST);

function onSocketConnection (socket) {
	console.log('connected');
	activeSocket = socket;

	socket.on('data', onDataReceived);
}

function onDataReceived (data){
	console.log('raw data:' + data);

	//Gets the data as an object
	var sensorData = JSON.parse(data);

	//Look for an existing record tied to the sensor's ip address
	var mInfo  = MONITORS.filter(
		function (el) {
			return (el.address == activeSocket.remoteAddress);
		}	
	)[0];

	//Creates a array object if one does not exist
	if(!mInfo){
		//Use default values of false - we'll update them later on
		mInfo = {address:activeSocket.remoteAddress, streamAvailable:false, hot:false};
		MONITORS.push(mInfo);
		console.log('New Monitor: ' + activeSocket.remoteAddress);
	}

	//Update the status
	mInfo.streamAvailable = sensorData.listening;
	mInfo.hot = sensorData.hot;

	console.log('Update From ' + activeSocket.remoteAddress);
}

//I have made a change!