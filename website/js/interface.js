const fs = require('fs');

// Path to the JSON file
const filePath = './final.json';

function timeConverter(UNIX_timestamp){
    var a = new Date(UNIX_timestamp);
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var year = a.getFullYear();
    var month = months[a.getMonth()];
    var date = a.getDate();
    var time = month + ' ' + date + ', ' + year // + ' ' + hour + ':' + min + ':' + sec ;
    return time;
  }
  console.log(timeConverter(1560687480000))

// Read the JSON file
fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
        console.error('Error reading the file:', err);
        return;
    }

    try {
        const jsonData = JSON.parse(data);
        
        // get all possible school names
        //console.log(Object.entries(jsonData))
        
        // get statistics for all schools
        // data = jsonData["ALL"]
        // Total exceedance info
        // console.log(data["section1"])
        // exceedance info per year 
        // console.log(data["section2"])        

        // get data for a specific school:
        //data = jsonData["LAMBTON KENT COMP S"]
        // General info
        //console.log(data["section0"]["School Name"])
        // Total exceedance info about this school
        //console.log(data["section1"])
        // exceedance info per year for this school
        //console.log(data["section2"])
        // exceedance records for this school, sorted by Sample Date from oldest to newest
        //console.log(data["section3"].slice(0,5))

    } catch (error) {
        console.error('Error parsing JSON:', error);
    }
});