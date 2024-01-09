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


function update(){
jsonData.forEach(function(obj,index) {
if (obj['[Hidden] problem'].length !==0) {problematic++
    if (obj['[Hidden] problem'].includes('Sex-Specific ?')){SexSpecific++}
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
        if (problematic_addressed === problematic) {  alert("not all phenotypes were view in this session. But all flagged phenotypes have been adressed")}
        else if (touched.size===jsonData.length) {alert("not all phenotypes were adressed. But all phenotypes have been viewed in this session") }
        else { alert("not all phenotypes were viewed and not all problematic phenotypes were adressed.")}  
}
}


//Function to adress max number of decimal
function Rounder(number) {
        if (isNaN(number)){ returned = number;}
        else if (String((number- Math. floor(number))).length > 2 ) {returned = number.toFixed(3);}
        else {returned = number;}
    return returned
    }

//removal 
// Update jsonData with default values for Included, Normalize and Threshold properties
function saveChanges() {
  jsonData.forEach(function(obj) {
    if (window.form === 'Continuous'){
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
    }
    else if (window.form === 'Binary'){
        ['To exclude'].forEach(function (textName) {
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
    ["To exclude","Sex-Specific"].forEach(function (checkboxName) {
        obj[checkboxName] = obj[checkboxName] || false;
    });
    }
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


function display(text, object){
    var table = document.createElement("table");
    var thead = table.createTHead();
    var tbody = table.createTBody();
    thead.textContent = text.replace(']','').replace('[','');
    var Container_table = document.createElement('div');
    var head = Object.keys(object);
    Container_table.className = "col"
    head.forEach(function(key) {
        Statistics=key.replace(text,'')
        if (key.split(' ')[0] === text){
            row = tbody.insertRow();
            var th = document.createElement("th");
            row.appendChild(th);
            var td = row.insertCell();
                cell = Rounder(object[key])
                rowID = Statistics
            th.textContent = rowID;
            td.textContent = cell;
        }
    });
        Container_table.appendChild(table)
        return Container_table
}



function loader(){
jsonData.forEach(function(obj,index) {
    var objectDix = document.createElement('div');
    objectDix.id=obj["[Description] Variable"]
                var headerKeys = Object.keys(obj);
                ["Sex-Specific",'To exclude'].forEach(function(key){
                    if (!headerKeys.includes(key)){headerKeys.splice(1, 0, key)}
                    });
                if (window.form === 'Continuous'){
                    ["Threshold Right",'Threshold Left','Not normalize'].forEach(function(key){
                        if (!headerKeys.includes(key)){headerKeys.splice(1, 0, key)}
                        });
                    }
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
                var table1 = document.createElement("table");
                var thead1 = table1.createTHead();
                var tbody1 = table1.createTBody();
                thead1.textContent = 'Filters';
                headerKeys.forEach(function(key) {
                    if (key === "To exclude"){
                        row = tbody1.insertRow();
                        var th = document.createElement("th");
                        th.textContent = key;
                        row.appendChild(th);
                        var td = row.insertCell()
                        var checkbox = document.createElement("input");
                        checkbox.type = "checkbox";
                        checkbox.checked = obj[key] || false;
                        checkbox.id=obj["[Description] Variable"]+key+'_box';
                        td.appendChild(checkbox);
                        checkbox.addEventListener('change', function() {
                            jsonData[index][key] = checkbox.checked;
                        });
                        var textbox = document.createElement("input"); 
                        textbox.type = "text";
                        textbox.className='form-control';
                        textbox.id = obj["[Description] Variable"]+key+'_text';
                        textbox.style.display=checkbox.checked !== false ? "block" : "none";
                        textbox.placeholder='Justification to exclude';
                        textbox.value = checkbox.checked !== false ? obj["justification_" + key].toString() : "";
                        td.appendChild(textbox);
                        checkbox.addEventListener("click", function() {
                            toggleTextbox(obj["[Description] Variable"] + key) })
                    }
                    else if (key === "Sex-Specific"){
                            row = tbody1.insertRow();
                            var th = document.createElement("th");
                            th.textContent = key;
                            row.appendChild(th);
                            var td = row.insertCell()
                            var checkbox = document.createElement("input");
                            checkbox.type = "checkbox";
                            checkbox.checked = obj[key] || false;
                            checkbox.id = obj["[Description] Variable"] + key + '_box';
                            td.appendChild(checkbox);
                            checkbox.addEventListener('change', function() {
                                jsonData[index][key] = checkbox.checked;
                            });
                            var SexInput = document.createElement("select");; 
                            SexInput.id = obj["[Description] Variable"] + key +'_options';
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
                            SexInput.style.display = checkbox.checked !== false ? "block" : "none";
                            SexInput.value = checkbox.checked !== false ? obj["Choice_" + key].toString() : "";
                            td.appendChild(SexInput);
                        checkbox.addEventListener("click", function() {
                            togglelistOptions(obj["[Description] Variable"] + key)
                        });
                    } 
                    else if (key === "Threshold Left" || key === "Threshold Right") { //creates drop down menu
                        row = tbody1.insertRow();
                        var th = document.createElement("th");
                        th.textContent = key;
                        row.appendChild(th);
                        var td = row.insertCell()
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
                    else if (key === "Not normalize"){
                        row = tbody1.insertRow();
                        var th = document.createElement("th");
                        th.textContent = key;
                        row.appendChild(th);
                        var td = row.insertCell()
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
                }
                });
               Container_table1.appendChild(table1); // table 1 added to Container of table 1
               Container_table.appendChild(Container_table1)

               var Container_image1 = document.createElement('div');
               Container_image1.className = "col" ;
   if (window.form === 'Binary' || typeof obj['[Statistics] N uniques values'] != "undefined" || obj['[Statistics] N uniques values'] > 1) {
               var separatorImage = document.createElement("img");
               separatorImage.id = obj["[Description] Variable"] + "_image";
               fetch_image(obj["[Description] Variable"]);
               separatorImage.classList.add("separator-image");
               Container_image1.appendChild(separatorImage);
            }

                let tables_head = Object.keys(obj).map(item => {
                    let splitItems = item.split(' '); // Split the string into an array of words
                    return splitItems[0]; // Return only the second word (index 1)
                });
                let tables_title = [...new Set(tables_head)].filter(item => item.startsWith('['));

                let hidden = tables_title.indexOf('[Hidden]');
                // Check if the element is in the array
                if(hidden !== -1) {
                    // Remove the element using splice
                    tables_title.splice(hidden, 1);
                }

                let Desc = tables_title.indexOf('[Description]');
                // Check if the element is in the array
                if(Desc !== -1) {
                    // Remove the element using splice
                    tables_title.splice(Desc, 1);
                }

                tables_title.forEach(function(text) {
                    Container_table1.parentNode.insertBefore(display(text, obj), Container_table1.nextSibling) ;
                })

               // Adding skewness and kurtosis warning
   var problem=obj['[Hidden] problem'].split('|')
    problem.forEach(function(key) { 
            objectDix.appendChild(createWarning(key));
} )

               // Adding Container tables to Json container
               objectDix.appendChild(Container_table) ;
               objectDix.appendChild(Container_image1)
jsonContainer.appendChild(objectDix)
objectDix.style.display = "none";
               });
}

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

function fetch_image(filename){
fetch('/images/'+filename+'.png')
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

// EXECUTE

document.getElementById('save-btn').addEventListener('click', saveChanges);
document.getElementById('val-btn').addEventListener('click', validate);
document.getElementById('next-btn').addEventListener('click', displayNext);
document.getElementById('prev-btn').addEventListener('click', displayPrev);

const touched = new Set();
let currentIndex = 0;
let flagged = 0;
let problematic = 0;
let problematic_addressed = 0;
let SexSpecific = 0
let included = 0


document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('jsonForm');
    form.addEventListener('change', function(event) {
        event.preventDefault();
        window.form=form.value
        fetch('/submit-json-path', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ value: window.form }) // Send the string as part of a JSON object
        })
        .then(data => {
            fetch('/jsondata')
           .then(response => response.json())
               .then(Data => {
               jsonData = Data
               loader();
               form.style.display = "none";
               displayCurrentObject(); // Display the first object after loading
           })
          .catch(error => {
             console.error('Error fetching the JSON file:', error);
              alert('Error loading the JSON file. Check the console for more information.' + error);
          });
        })
        .catch((error) => {
            console.error('Error:', error);
        });
        
        window.addEventListener('beforeunload', function (e) {
                    navigator.sendBeacon('/shutdown');
        });
    });
});
