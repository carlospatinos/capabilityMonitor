var fs = require('fs');
var jsonDataSrc = fs.readFileSync('flight.json', 'utf8');
/*
var obj;
fs.readFile('flight.json', 'utf8', function (err, data) {
  if (err) console.error(err);
  obj = JSON.parse(data);
  console.log(obj);
});
*/

var jsonData = JSON.parse(jsonDataSrc);
for (var i = 0; i < jsonData.flights.length; i++) {
    var flight = jsonData.flights[i];
    console.log(flight.departureDate);
}

