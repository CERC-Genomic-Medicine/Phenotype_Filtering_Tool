function toggleTextbox(vary) {
  const checkbox = document.getElementById(vary+'_box');
  const textbox = document.getElementById(vary+'_text');
  textbox.style.display = checkbox.checked ? 'block' : 'none';
}

function toggleTextboxOposite(vary) {
  const checkbox = document.getElementById(vary+'_box');
  const textbox = document.getElementById(vary+'_text');
  textbox.style.display = checkbox.checked ? 'none' : 'block';
}
function toggleTextboxOptions(vary) {
  const Options = document.getElementById(vary+'_input');
  const textbox = document.getElementById(vary+'_text');
  textbox.style.display = Options.value !== 'None' ? 'block' : 'none';
}
function togglelistOptions(vary) {
  const checkbox = document.getElementById(vary+'_box');
  const options = document.getElementById(vary+'_options');
  options.style.display = checkbox.checked ? 'block' : 'none';
}

const touched = new Set();
let flagged = 0;
let problematic = 0;
let problematic_addressed = 0;
let SexSpecific = 0

function update(){
let flagged = 0;
let problematic = 0;
let problematic_addressed = 0;
let SexSpecific = 0
let included = 0


jsonData.forEach(function(obj,index) {
if (obj['[Hidden] problem'].length !==0) {problematic++
    if (obj['[Hidden] problem'].includes('Females') || obj['[Hidden] problem'].includes('Males')){SexSpecific++}
    exclude = document.getElementById(obj["[Description] Variable"]+'To exclude_box').checked ;
    SS = document.getElementById(obj["[Description] Variable"]+'Sex-Specific_box').checked ;
    if (exclude || SS) {problematic_addressed++}
} 
if (!obj['To exclude']){
    included++
}
});
document.getElementById('Problematic_total').textContent= 'Adressed : ' + problematic_addressed+ '/'+problematic ;
const current = currentIndex+1
document.getElementById('viewing').textContent='Viewed : ' + current + '/'+jsonData.length ;
document.getElementById('Included').textContent='Included : ' + included + '/'+jsonData.length ;

}


function validate(){
    if (problematic_addressed === problematic && touched.size===jsonData.length){
        alert("All phenotypes were adressed and viewed.")
    } else {
        alert("not all phenotypes were adressed and/or viewed.")
}

}


//Function to adress max number of decimal
function Rounder(number) {
        if (isNaN(number)){ returned = number;}
        else if (String((number- Math. floor(number))).length > 2 ) {returned = number.toFixed(3);}
        else {returned = number;}
    return returned
    }
    // Update jsonData with default values for Included, Normalize and Threshold properties
function saveChanges() {
  jsonData.forEach(function(obj) {
      ['Not normalize','To exclude'].forEach(function (textName) {
          textbox = document.getElementById(obj["[Description] Variable"]+textName+'_text');
          checkbox = document.getElementById(obj["[Description] Variable"]+textName+'_box');
          if (checkbox.checked !== false) {
              obj["justification_" + textName] = textbox.value ;
          }
      });
      ['Sex-Specific'].forEach(function (ChoiceName) {
          listOptions = document.getElementById(obj["[Description] Variable"]+ChoiceName+'_options');
          checkbox = document.getElementById(obj["[Description] Variable"]+ChoiceName+'_box');
          if (checkbox.checked !== false) {
              obj["Choice_" + ChoiceName] = listOptions.value ;
          }
      });
      ["To exclude", "Not normalize","Sex-Specific"].forEach(function (checkboxName) {
          obj[checkboxName] = obj[checkboxName] || false;
      });
      ["Threshold Left", "Threshold Right"].forEach(function (thresholdName) {
          obj[thresholdName] = obj[thresholdName] !== null && obj[thresholdName] !== undefined ? obj[thresholdName] : null;
           textbox = document.getElementById(obj["[Description] Variable"]+thresholdName+'_text');
          if (obj[thresholdName] !== null && obj[thresholdName] !== undefined) {
              obj["justification_" + thresholdName] = textbox.value ;
          }
      });
  });
  var updatedJsonData = JSON.stringify(jsonData);
    fetch('/save-json', {
        method: 'POST', // Specify the method as POST
        headers: {
            'Content-Type': 'application/json', // Specify the content type as JSON
        },
        body: updatedJsonData // Convert the JavaScript object to a JSON string
    })
    .then(response => {
        if (!response.ok) {
            // Handle response if it's not OK (e.g., server error)
            throw new Error('Network response was not oknb ' + response.statusText);
        }
        return response.json(); // Parse the JSON response
    })
    .then(data => {
        // Handle the successful response here
        console.log('Success:', data);
        alert('Data successfully saved');
    })
    .catch((error) => {
        // Handle any errors that occurred during the fetch
        console.error('Error:', error);
        alert('Error saving data: ' + error.message);
    });
}

function createWarning(text){
    const alertDiv = document.createElement('div');
    alertDiv.classList.add('alert', 'alert-warning', 'd-flex', 'align-items-center');
    alertDiv.setAttribute('role', 'alert');
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '16');
    svg.setAttribute('height', '16');
    svg.setAttribute('fill', 'currentColor');
    svg.setAttribute('class', 'bi bi-exclamation-triangle-fill');
    svg.setAttribute('viewBox', '0 0 16 16');

    // Create the path element
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5m.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2');

    // Append the path to the SVG
    svg.appendChild(path);

    // Create the SVG element

    // Create the use element for SVG

    // Create the div for text content
    const textDiv = document.createElement('div');
    textDiv.textContent = '  ' + text;

    // Append SVG and text div to main container
    alertDiv.appendChild(svg);
    alertDiv.appendChild(textDiv);

    // Append the main container to the body or a specific element in the document
    return(alertDiv);
}

function loader(){
jsonData.forEach(function(obj,index) {
    var objectDix = document.createElement('div');
    objectDix.id=obj["[Description] Variable"]
    var headerKeys = Object.keys(obj);
    headerKeys.splice(1, 0, "Threshold Right");
    headerKeys.splice(1, 0, "Threshold Left");
    headerKeys.splice(1, 0, "Sex-Specific");
    headerKeys.splice(1, 0, "To normalize");
    headerKeys.splice(1, 0, "To exclude");
    //Create a header explaining phenotype
    var title= document.createElement("h1");
    title.textContent=obj["[Description] Label"] ;
    title.className="text-center"
    var title2= document.createElement("h3");
    title2.className="text-center"
    title2.textContent= obj["[Description] Variable"] ;
    objectDix.appendChild(title);
    objectDix.appendChild(title2);
    //Create Container of all tables with bootstrap grid so in-line
    var Container_table = document.createElement('div');
    Container_table.className = "row"  ;
    // 1) Options table
    var Container_table1 = document.createElement('div');
    Container_table1.className = "col" ;
    Container_table1.id = obj["[Description] Variable"]+'Container_table1';
    const table1_index = ['To exclude', 'Not normalize',"Sex-Specific",'Threshold Left', 'Threshold Right'] ;
    var table1 = document.createElement("table");
    table1.className="table table-striped"
    var thead1 = table1.createTHead();
    var tbody1 = table1.createTBody();
    thead1.textContent = 'Filters';
    table1_index.forEach(function(key) {
        row = tbody1.insertRow();
        var th = document.createElement("th");
        th.textContent = key;
        row.appendChild(th);
        var td = row.insertCell()
        if (key === "To exclude"){
            var checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.checked = obj[key] || false;
            checkbox.id=obj["[Description] Variable"]+key+'_box';
            td.appendChild(checkbox);
            checkbox.addEventListener('change', function() {
                jsonData[index][key] = checkbox.checked;
            });
            var textbox = document.createElement("input"); 
            textbox.type="text";
            textbox.id=obj["[Description] Variable"]+key+'_text';
            textbox.style.display=checkbox.checked !== false ? "block" : "none";
            textbox.placeholder='Justification to exclude';
            textbox.value = checkbox.checked !== false ? obj["justification_" + key].toString() : "";
            td.appendChild(textbox);
            checkbox.addEventListener("click", function() {
                toggleTextbox(obj["[Description] Variable"] + key) })
            }
        else if (key === "Sex-Specific"){
                var checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.checked = obj[key] || false;
                checkbox.id=obj["[Description] Variable"]+key+'_box';
                td.appendChild(checkbox);
                checkbox.addEventListener('change', function() {
                    jsonData[index][key] = checkbox.checked;
                });
                var SexInput = document.createElement("select");; 
                SexInput.id=obj["[Description] Variable"] + key+'_options';
                var noneOption = document.createElement("option");
                noneOption.value = "None";
                noneOption.text = "None";
                SexInput.add(noneOption);
                var option = document.createElement("option");
                option.value = 'Males';
                option.text = 'Males';
                SexInput.add(option);
                var option = document.createElement("option");
                option.value = 'Females';
                option.text = 'Females';
                SexInput.add(option);
                SexInput.style.display=checkbox.checked !== false ? "block" : "none";
                SexInput.value = checkbox.checked !== false ? obj["Choice_" + key].toString() : "";
                td.appendChild(SexInput);
            checkbox.addEventListener("click", function() {
                togglelistOptions(obj["[Description] Variable"] + key)
            });
        }
        else if (key === "Not normalize"){
                var checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.checked = obj[key] || false;
                checkbox.id=obj["[Description] Variable"]+key+'_box';
                td.appendChild(checkbox);
                checkbox.addEventListener('change', function() {
                    jsonData[index][key] = checkbox.checked;
                });
                var textbox = document.createElement("input"); 
                textbox.type="text";
                textbox.id=obj["[Description] Variable"]+key+'_text';
                textbox.style.display=checkbox.checked !== false ? "block" : "none";
                textbox.placeholder='Justification to not normalize';
                textbox.value = checkbox.checked !== false ? obj["justification_" + key].toString() : "";
                td.appendChild(textbox);
            checkbox.addEventListener("click", function() {
                toggleTextbox(obj["[Description] Variable"] + key)
            });
        } else if (key === "Threshold Left" || key === "Threshold Right") { //creates drop down menu
            var thresholdInput = document.createElement("select");
            thresholdInput.id=obj["[Description] Variable"]+key+'_input';
            var noneOption = document.createElement("option");
            noneOption.value = "None";
            noneOption.text = "None";
            thresholdInput.add(noneOption);
            for (var i = 1; i <= 5; i++) {
                var option = document.createElement("option");
                option.value = i.toString();
                option.text = i.toString() + 'SD';
                thresholdInput.add(option);
            }
            thresholdInput.value = obj[key] !== null && obj[key] !== undefined ? obj[key].toString() : "None";
            thresholdInput.addEventListener('change', function() {
            jsonData[index][key] = thresholdInput.value !== "None" ? parseInt(thresholdInput.value) : null;
        })
            var textbox = document.createElement("input"); 
            textbox.type="text";
            textbox.id=obj["[Description] Variable"]+key+'_text';
            textbox.style.display= thresholdInput.value !== 'None' ? "block" : "none";
            textbox.placeholder='Justification';
            textbox.value = typeof obj["justification_" + key] !== 'undefined' ? obj["justification_" + key].toString() : "";
            thresholdInput.addEventListener("click", function() {
                toggleTextboxOptions(obj["[Description] Variable"]+key)
            });
            td.appendChild(thresholdInput)
            td.appendChild(textbox);
        }
    });
        Container_table1.appendChild(table1); // table 1 added to Container of table 1

         // 2) Statistics table

        var table2 = document.createElement("table");
        table2.className="table table-striped"
        var thead2 = table2.createTHead();
        var tbody2 = table2.createTBody();
        thead2.textContent = 'Statistics';
        var Container_table2 = document.createElement('div');
        Container_table2.className = "col"
        Container_table2.id = obj["[Description] Variable"]+'_Container_table2';
        headerKeys.forEach(function(key) {
            Statistics=key.replace('[Statistics] ','')
            if (key.split(' ')[0] === '[Statistics]'){
                if (['PERC_95', 'PERC_5', 'SD','median','Maximum'].includes(Statistics)){}
                else{
                row = tbody2.insertRow();
                var th = document.createElement("th");
                row.appendChild(th);
                var td = row.insertCell();
                if (Statistics == 'Mean'){
                    rowID = 'μ\u0305 [SD]'
                    cell= Rounder(obj['[Statistics] Mean']) + ' [' +  Rounder(obj['[Statistics] SD']) +' ]'
                    }
                else if (Statistics === 'median') {
                    cell = '[' + Rounder(obj['[Statistics] PERC_5']) +' , ' + Rounder(obj['[Statistics] median']) + ' , '+ Rounder(obj['[Statistics] PERC_95']) + ']' ;
                    rowID ='Percentile [5,50,95]'
                    }
                else if (Statistics === 'Minimum'){
                    cell = '[' + Rounder(obj['[Statistics] Minimum']) +' , ' + Rounder(obj['[Statistics] Maximum']) + ']' 
                    rowID = 'Range'
                }
                else {
                    cell = Rounder(obj[key])
                    rowID = Statistics
                }
                th.textContent = rowID;
                td.textContent = cell;
                if (obj['[Hidden] problem'].includes(key)){
                    th.style.backgroundColor = "#f75b00";
                    td.style.backgroundColor = "#f75b00";
            }
            }
        }
        });
       Container_table2.appendChild(table2);

       // 3) Outlier information table
        var table3 = document.createElement("table");
        table3.className="table table-striped"
        var thead3 = table3.createTHead();
        var tbody3 = table3.createTBody();
        thead3.textContent = 'Outliers';
        var Container_table3 = document.createElement('div');
        Container_table3.className = "col" ;
        Container_table3.id = obj["[Description] Variable"]+'_Container_table3';
        headerKeys.forEach(function(key) {
            outliers=key.replace('[Outliers]','') // all outlier information have this tag
            if (key.split(' ')[0] === '[Outliers]'){
                row = tbody3.insertRow();
                var th = document.createElement("th");
                th.textContent = outliers.replace('mean','μ\u0305');
                row.appendChild(th);
                var td = row.insertCell();
                td.textContent = Rounder(obj[key]);
            }
        });
       Container_table3.appendChild(table3);

       // 3) Outlier information table
       //4) Samples table

        var table4 = document.createElement("table");
        table4.className="table table-striped"
        var thead4 = table4.createTHead();
        var tbody4 = table4.createTBody();
        thead4.textContent = 'Samples';
        var Container_table4 = document.createElement('div');
        Container_table4.className = "col" ;
        Container_table4.id = obj["[Description] Variable"]+'_Container_table4';
        headerKeys.forEach(function(key) { 
            if (key.split(' ')[0] === '[Samples]'){
                Samples=key.replace('[Samples]','')
                row = tbody4.insertRow();
                var th = document.createElement("th");
                th.textContent = Samples;
                row.appendChild(th);
                var td = row.insertCell();
                td.textContent = Rounder(obj[key]);
                if (obj['[Hidden] problem'].includes(Samples)){
                    th.style.backgroundColor = "#f75b00";
                    td.style.backgroundColor = "#f75b00";
            }
            }
        });
   Container_table4.appendChild(table4);

    
   // Adding Container tables to Json container
   Container_table.appendChild(Container_table1) ;
   Container_table1.parentNode.insertBefore(Container_table2, Container_table1.nextSibling) ;
   Container_table1.parentNode.insertBefore(Container_table3, Container_table1.nextSibling) ;
   Container_table1.parentNode.insertBefore(Container_table4, Container_table1.nextSibling) ;
   var problem=obj['[Hidden] problem'].split('|')
    problem.forEach(function(key) { 
            objectDix.appendChild(createWarning(key));
} )


   objectDix.appendChild(Container_table) ;


   //add image after tables
   if (obj['[Statistics] N uniques values'] > 1) {

   var separatorImage = document.createElement("img");
   separatorImage.id = obj["[Description] Variable"] + "_image";
   fetch_image(obj[Object.keys(obj)[0]].split(" ")[0]);
   separatorImage.classList.add("separator-image");
   objectDix.appendChild(separatorImage);
}
jsonContainer.appendChild(objectDix)
objectDix.style.display = "none";
               });
}
let currentIndex = 0;

function displayNext(){
            if (currentIndex+1 == jsonData.length){ alert("No more objects to display.");
    } else {
    currentIndex++;
    touched.add(currentIndex)
    update();
        document.getElementById(jsonData[currentIndex-1]["[Description] Variable"]).style.display = "none";
        document.getElementById(jsonData[currentIndex]["[Description] Variable"]).style.display = 'block';
}
}

function displayPrev(){
            if (currentIndex == 0){ alert("No more objects to display.");
    } else {
    currentIndex--;
    update();
        touched.add(currentIndex)
        document.getElementById(jsonData[currentIndex+1]["[Description] Variable"]).style.display = "none";
        document.getElementById(jsonData[currentIndex]["[Description] Variable"]).style.display = 'block';
}
}

function displayCurrentObject(){        
    document.getElementById(jsonData[currentIndex]["[Description] Variable"]).style.display = 'block';
        update();    
        touched.add(currentIndex) ;
    }

document.getElementById('save-btn').addEventListener('click', saveChanges);
document.getElementById('val-btn').addEventListener('click', validate);
document.getElementById('next-btn').addEventListener('click', displayNext);
document.getElementById('prev-btn').addEventListener('click', displayPrev);


fetch('/jsondata')
   .then(response => response.json())
       .then(Data => {
       jsonData = Data
       loader();
       displayCurrentObject(); // Display the first object after loading
   })
  .catch(error => {
     console.error('Error fetching the JSON file:', error);
      alert('Error loading the JSON file. Check the console for more information.');
  });

window.addEventListener('beforeunload', function (e) {
            navigator.sendBeacon('/shutdown');
});

function fetch_image(filename){
fetch('/images/'+filename+'_distribution.png')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok' + filename);
        }
        return response.blob();
   })
    .then(blob => {
        const imageObjectURL = URL.createObjectURL(blob);
        document.getElementById(filename+ "_image").src=imageObjectURL;
    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:' + filename, error);
    });
}
