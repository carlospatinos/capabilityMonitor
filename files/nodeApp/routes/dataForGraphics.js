var express = require('express');

var router = express.Router();

function getRandomArbitrary(min, max) {
  return Math.random() * (max - min) + min;
}

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function generateDate() {
  return Math.floor(new Date())
}

/* GET users listing. */
router.get('/', function(req, res, next) {
  res.send('This is a generic service for grahpics.');
});


router.get('/haDataReal', function(req, res, next) {
  res.setHeader('Content-Type', 'application/json');
  dateToQuery = req.query.dateToQuery;

  if (dateToQuery == undefined) {
    dateToQuery = generateDate() - 10000;
  } else {
    dateToQuery = parseInt(dateToQuery);
  }
  console.log("Quering regs for date greater than: " + dateToQuery);
  //dateToQuery=1437555000000
  
  var db = req.db;
  var collection = db.get('haResults');

  var options = {
    "limit": 20,
    "sort": {startTime: -1}
  }
  collection.find( {startTime : { $gt: dateToQuery } }, options , function(e,docs){
    res.send(JSON.stringify(docs, null, 3));
  });
  
});

router.post('/haDataReal', function(req, res, next) {
    // Set our internal DB variable
    var db = req.db;

    // Get our form values. These rely on the "name" attributes
    timeTaken = req.body.timeTaken;
    startTime = req.body.startTime;
    vuser = req.body.vuser;
    nodeName = req.body.nodeName;
    ipAddress = req.body.ipAddress;
    ucName = req.body.ucName;
    successfulAssertions = req.body.successfulAssertions;
    failedAssertions = req.body.failedAssertions;
    ipAddress = req.body.ipAddress;
    
    //console.log(startTime);

    dateToUse = generateDate();

    // Set our collection
    var collection = db.get('haResults');

    // Submit to the DB
    collection.insert({
        "useCases":[
          {"name": "add_node_scenario.cfg", "executionTime":"12", "successfulAssertions": "2", "failedAssertions":"2"},
          {"name": "delete_node_scenario.cfg", "executionTime":"12", "successfulAssertions": "2", "failedAssertions":"2"}
        ],
        "timeTaken" : timeTaken,
        "startTime" : dateToUse,
        "vuser":vuser,
        "nodeName":nodeName, 
        "ipAddress":ipAddress,
        "ucName":ucName,
        "successfulAssertions":successfulAssertions,
        "failedAssertions":failedAssertions
        }, function (err, doc) {
        if (err) {
            // If it failed, return error
            console.log("There was a problem adding the information to the database.");
            res.send("There was a problem adding the information to the database.");
        }
        else {
            console.log("redirection.");
            // And forward to success page
            res.redirect("haDataReal");
        }
    });
});


router.get('/simulateHaData', function(req, res, next) {
  res.setHeader('Content-Type', 'application/json');

  dateToUse = generateDate();
  value1=getRandomInt(8,10);
  value2=getRandomInt(8,10);
  value3=getRandomInt(8,12);

  var scenarios=[{
    "useCases":[
      {"name": "add_node_scenario.cfg", "executionTime":"12", "successfulAssertions": "2", "failedAssertions":"2"},
      {"name": "delete_node_scenario.cfg", "executionTime":"12", "successfulAssertions": "2", "failedAssertions":"2"}
    ],
    "timeTaken" : "17",
    "startTime" : dateToUse,
    "vuser":"VirtualUsers-3",
    "nodeName":"LTENODE06", 
    "ipAddress":"192.168.0.6",
    "ucName":"add_node+delete_node",
    "successfulAssertions":"4",
    "failedAssertions":"4"
  },{
    "useCases":[
      {"name": "add_node_scenario.cfg", "executionTime":"12", "successfulAssertions": "2", "failedAssertions":"2"},
      {"name": "delete_node_scenario.cfg", "executionTime":"12", "successfulAssertions": "2", "failedAssertions":"2"}
    ],
    "timeTaken" : "17",
    "startTime" : dateToUse,
    "vuser":"VirtualUsers-3",
    "nodeName":"LTENODE06", 
    "ipAddress":"192.168.0.6",
    "ucName":"add_node+sync+delete_node",
    "successfulAssertions":"8",
    "failedAssertions":"8"
  },{
    "useCases":[
      {"name": "add_node_scenario.cfg", "executionTime":"12", "successfulAssertions": "2", "failedAssertions":"2"},
      {"name": "delete_node_scenario.cfg", "executionTime":"12", "successfulAssertions": "2", "failedAssertions":"2"}
    ],
    "timeTaken" : "17",
    "startTime" : dateToUse,
    "vuser":"VirtualUsers-3",
    "nodeName":"LTENODE06", 
    "ipAddress":"192.168.0.6",
    "ucName":"add_mo+delete_mo",
    "successfulAssertions":"7",
    "failedAssertions":"7"
  }]
  //console.log(JSON.stringify(scenario));
  //res.send(JSON.stringify({ a: 1 }));
  //res.send(JSON.stringify({ a: 1 }, null, 3));
  //res.json()
  res.send(JSON.stringify(scenarios, null, 3));
  
});

module.exports = router;
