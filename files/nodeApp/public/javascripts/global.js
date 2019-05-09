// Userlist data array for filling in info box
var schedules = [];
var unwantedPrice = 2700;

// DOM Ready =============================================================
$(document).ready(function() {

    // Populate the user table on initial page load
    populateTable();

    $('#schedules table tbody').on('click', 'td a.deleteme', deleteSchedule);
});

// Functions =============================================================

// Fill table with data
function populateTable() {

    // Empty content string
    var tableContent = '';

    // jQuery AJAX call for JSON
    $.getJSON( '/trip/json', function( data ) {
        schedules = data;
        // For each item in our JSON, add a table row and cells to the content string
        $.each(data, function(){
            tableContent += '<tr>';
            tableContent += '<td>' + this.priceCurrency + ' ' + this.price + ' </td>';
            tableContent += '<td>' + this.numberOfDays + '</td>';
            tableContent += '<td>' + this.departureDate + '</td>';
            tableContent += '<td>' + this.returnDate + '</td>';
            tableContent += '<td>' + this.origin + '</td>';
            tableContent += '<td>' + this.destiny + '</td>';
            tableContent += '<td>' + this.executionDate + '</td>';
            tableContent += '<td>' + this.adults + '</td>';
            tableContent += '<td>' + this.children + '</td>';
            tableContent += '<td>' + this.infants + '</td>';
            tableContent += '<td><a href="' + this.url + '" class="btn btn-info mini" target="_blank">Info</a></td>';
            tableContent += '<td><a href="#" role="button" data-toggle="modal" class="btn btn-warning mini deleteme" rel="' + this._id + '">Delete</a></td>';
            tableContent += '</tr>';
        });

        // Inject the whole content string into our existing HTML table
        $('#schedules table tbody').html(tableContent);
    });
};


function deleteSchedule(event) {
    // Prevent Link from Firing
    event.preventDefault();
    var confirmation = confirm('Is the real price over ' + unwantedPrice + '? If so go ahead and delete it.');
     if (confirmation === true) {
        var scheduleId = $(this).attr('rel');
        // If they did, do our delete
        $.ajax({
            type: 'DELETE',
            url: '/trip/' + scheduleId
        }).done(function( response ) {
            // Check for a successful (blank) response
            if (response.msg === '') {

            } else {
                alert('Error: ' + response.msg);
            }

            // Update the table
            populateTable();

        });

    }
    else {
        // If they said no to the confirm, do nothing
        console.log('User changing his/her mind.');
        return false;

    }
};


function batchDelete(price) {
    // Prevent Link from Firing
    
    if (price != undefined) {
        // If they did, do our delete
        $.ajax({
            type: 'DELETE',
            url: '/trip/batchDelete/' + price
        }).done(function( response ) {
            // Check for a successful (blank) response
            if (response.msg === '') {

            } else {
                alert('Error: ' + response.msg);
            }
            // Update the table
            populateTable();
        });
    }
    else {
        // If they said no to the confirm, do nothing
        console.log('Price is undefined.');
        return false;
    }
};