var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var http = require('http');

// New Code
var mongo = require('mongodb');
var monk = require('monk');
var db = monk('localhost:27017/enmCapabilitiesResults');

var routes = require('./routes/index');
var dataForGraphics = require('./routes/dataForGraphics');
var plot = require('./routes/plot');
var trip = require('./routes/trip');

var app = express();



// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

// uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// Make our db accessible to our router
app.use(function(req,res,next){
    req.db = db;
    next();
});

app.use('/', routes);
app.use('/dataForGraphics', dataForGraphics);
app.use('/plot', plot);
app.use('/trip', trip);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handlers

// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
  app.use(function(err, req, res, next) {
    res.status(err.status || 500);
    res.render('error', {
      message: err.message,
      error: err
    });
  });
}

// production error handler
// no stacktraces leaked to user
app.use(function(err, req, res, next) {
  res.status(err.status || 500);
  res.render('error', {
    message: err.message,
    error: {}
  });
});


app.set('port', process.env.OPENSHIFT_NODEJS_PORT || 8081 );
app.set('ipAddress', process.env.OPENSHIFT_NODEJS_IP || '127.0.0.1' );

var server = app.listen(app.get('port'), app.get('ipAddress'), function() {
  console.log('%s: Node server started on %s:%d ...',
                        Date(Date.now() ), app.get('ipAddress'), server.address().port);
});

/*
var server = http.createServer(app);
server.listen(app.get('port'), function(){
  console.log('Express server listening on port ' + app.get('port'));
});
*/

module.exports = app;