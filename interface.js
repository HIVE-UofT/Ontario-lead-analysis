const fs = require('fs');

// Path to the JSON file
const filePath = './final.json';

// Read the JSON file
fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
        console.error('Error reading the file:', err);
        return;
    }

    try {
        const jsonData = JSON.parse(data);
        
        // get all possible school names
        Object.keys(jsonData)
        
        // get statistics for all schools
        data = jsonData["ALL"]
        // Total exceedance info
        console.log(data["section1"])
        // exceedance info per year 
        console.log(data["section2"])        

        // get data for a specific school:
        data = jsonData["LAMBTON KENT COMP S"]
        // General info
        console.log(data["section0"])
        // Total exceedance info about this school
        console.log(data["section1"])
        // exceedance info per year for this school
        console.log(data["section2"])
        // exceedance records for this school, sorted by Sample Date from oldest to newest
        console.log(data["section3"].slice(0,5))

    } catch (error) {
        console.error('Error parsing JSON:', error);
    }
});