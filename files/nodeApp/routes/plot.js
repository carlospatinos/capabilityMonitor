var express = require('express');
var router = express.Router();

var http = require('http');
var fs = require('fs');

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Express' });
});

router.get('/ha', function(req, res, next) {
  res.render('haPlot', { title: 'Express' });
});

router.get('/performance', function(req, res, next) {
  res.render('perfPlot', { title: 'Express' });
});

router.get('/live', function(req, res, next) {
  res.render('live', { title: 'Express' });
});

module.exports = router;
