var express = require('express');
var router = express.Router();

var http = require('http');
var fs = require('fs');

var maxNumOfRecords = 30;

router.get('/', function(req, res, next) {
  res.render('homeTrip', {title: 'Table of flight schedules'});
});

/* GET home page. */
router.get('/json', function(req, res, next) {
  var db = req.db;
  var collection = db.get('skyScanner');

  var options = {
    "limit": maxNumOfRecords,
    "sort": {price: 1}
  }
  collection.find( { infants : { $gt: 0 } }, options , function(e,docs){
    //res.send(JSON.stringify(docs, null, 3));
    //res.send(docs);
    res.json(docs);
  });

});

router.delete('/:id', function(req, res, next) {
  var db = req.db;
  var collection = db.get('skyScanner');

  var scheduleToDelete = req.params.id;
  console.log('Deliting: ' + scheduleToDelete);
  
  collection.remove({ '_id' : scheduleToDelete }, function(err) {
    res.send((err === null) ? { msg: '' } : { msg:'error: ' + err });
  });
  //res.send('Deleted');
});

router.delete('/batchDelete/:price', function(req, res, next) {
  var db = req.db;
  var collection = db.get('skyScanner');

  var priceToDelete = req.params.price;
  console.log('Deleting everything above: ' + priceToDelete);
  if (priceToDelete != undefined && priceToDelete >= 2800) {
    console.log('deleting price');
    res.send( { msg: '' });
    /*
    collection.remove( {price : { $gt: priceToDelete }, function(err) {
      res.send((err === null) ? { msg: '' } : { msg:'error: ' + err });
    });
*/
  } else {
    console.log('Wrong price');
  }
  
  //res.send('Deleted');
});

/*
router.get('/table', function(req, res, next) {
  var db = req.db;
  var collection = db.get('skyScanner');

  var options = {
    "limit": maxNumOfRecords,
    "sort": {price: 1}
  }
  collection.find( { infants : { $gt: 0 } }, options , function(e,docs){
    res.render('trip', {'schedules': docs, title: 'Table of flight schedules'});
  });
});
*/

module.exports = router;