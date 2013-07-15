
/**
 * Module dependencies.
 */

var express = require('express')
  , routes = require('./routes')
  , user = require('./routes/user')
  , http = require('http')
  , path = require('path')
  , tcpsock = require('net');

var app = express();
var server = app.listen(8888);
var io = require('socket.io').listen(server);

var tcp_HOST = 'localhost';
var tcp_PORT = 4040;

// all environments
//app.set('port', process.env.PORT || 8888);
app.set('views', __dirname + '/views');
app.set('view engine', 'jade');
app.use(express.favicon());
app.use(express.logger('dev'));
app.use(express.bodyParser());
app.use(express.methodOverride());
app.use(app.router);
app.use(express.static(path.join(__dirname, 'public')));

// development only
if ('development' == app.get('env')) {
  app.use(express.errorHandler());
}

app.get('/', routes.index);
app.get('/users', user.list);


// Listens for browser connection
io.sockets.on('connection', function (socket) { 

	var tcpClient = new tcpsock.Socket();
	tcpClient.setEncoding("ascii");
	tcpClient.setKeepAlive(true);

	// Connects to gourd server
	tcpClient.connect(tcp_PORT, tcp_HOST, function() {
		console.info('CONNECTED TO : ' + tcp_HOST + ':' + tcp_PORT);

		// Receives data from gourd server and sends to browser
		tcpClient.on('data', function(data) {
			console.log('Got update from gourd server: ' + data);
			socket.emit("httpServer", data);
		});

		tcpClient.on('end', function(data) {
			console.log('END DATA : ' + data);
		});
	});

	// Receives data from the browser
	socket.on('tcp', function(message) {
		console.log('Got update from browser: ' + message);
		tcpClient.write(message);
		return;
	});

	// Gets initial data for new browser
	socket.on('hello', function(message) {
		console.log('A new broswer connected: ' + message);
		tcpClient.write(message);
		return;
	});
});
