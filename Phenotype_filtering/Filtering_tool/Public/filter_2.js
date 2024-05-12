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

function searchAutocomplete() {
  var input = document.getElementById('search-bar').value;
  var regex = new RegExp(input, "i"); // "i" for case-insensitive
  var autocompleteList = document.getElementById('autocomplete-list');
  autocompleteList.innerHTML = ''; // Clear existing suggestions

  if (!input) return false;

  jsonData.forEach(function(obj) {
    var descriptionVariable = obj["[Description] Variable"].replace(/ /g, '_') || "";
    var descriptionLabel = obj["[Description] Label"] || "";

    // Use regex test to check for match instead of includes
    if (regex.test(descriptionVariable) || regex.test(descriptionLabel)) {
      var suggestionDiv = document.createElement("DIV");
      suggestionDiv.innerHTML = descriptionVariable + " (" + descriptionLabel + ")";
      suggestionDiv.addEventListener("click", function() {
        document.getElementById('search-bar').value = this.innerText;
        autocompleteList.innerHTML = '';

        document.getElementById(descriptionVariable).scrollIntoView()
            jsonData.forEach(function(obj,index) {
            if (obj["[Description] Variable"].replace(/ /g, '_') ==descriptionVariable) {currentIndex=index}
            })
            update();
      });

      autocompleteList.appendChild(suggestionDiv);
    }
  });
}

document.addEventListener("click", function () {
  document.getElementById('autocomplete-list').innerHTML = '';

});

function update(){
    let flagged = 0;
    let problematic = 0;
    let problematic_addressed = 0;
    let SexSpecific = 0;
    let included = 0;
    jsonData.forEach(function(obj,index) {
        if (obj['[Hidden] problem'].length !==0) {problematic++
            if (obj['[Hidden] problem'].includes('Sex-Specific ?')){SexSpecific++}
            exclude = document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+'To_exclude_box').checked ;
            SS = document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+'Sex-Specific_box').checked ;
            if (exclude || SS) {problematic_addressed++}
        } 
        if (!obj['To_exclude']){
            included++
        }
    });
document.getElementById('Problematic_total').textContent= 'Adressed : ' + problematic_addressed+ '/'+problematic ;
const current = currentIndex+1
document.getElementById('viewing').textContent='Viewing : ' + current + '/'+jsonData.length ;
document.getElementById('Included').textContent='Included : ' + included + '/'+jsonData.length ;
}


function validate(){
    if (problematic_addressed === problematic){
        alert("All flagged phenotypes were adressed.")
    } else {
        alert("All flagged phenotypes have been adressed")
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
    if (file_type === 'continuous'){
      ['Not_normalize','To_exclude'].forEach(function (textName) {
          textbox = document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+textName+'_text');
          checkbox = document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+textName+'_box');
          if (checkbox.checked) {
              obj["justification_" + textName] = textbox.value ;
          }
      });
      ['Sex-Specific'].forEach(function (ChoiceName) {
          listOptions = document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+ChoiceName+'_options');
          checkbox = document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+ChoiceName+'_box');
          if (checkbox.checked !== false) {
              obj["Choice_" + ChoiceName] = listOptions.value ;
          }
      });
      ["To_exclude", "Not_normalize","Sex-Specific"].forEach(function (checkboxName) {
          obj[checkboxName] = obj[checkboxName] || false;
      });
      ["Threshold_Left", "Threshold_Right"].forEach(function (thresholdName) {
          obj[thresholdName] = obj[thresholdName] !== null && obj[thresholdName] !== undefined ? obj[thresholdName] : null;
           textbox = document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+thresholdName+'_text');
          if (obj[thresholdName] !== null && obj[thresholdName] !== undefined) {
              obj["justification_" + thresholdName] = textbox.value ;
          }
      });
    }
    else if (file_type === 'binary'){
        ['To_exclude'].forEach(function (textName) {
        textbox = document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+textName+'_text');
        checkbox = document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+textName+'_box');
        if (checkbox.checked !== false) {
            obj["justification_" + textName] = textbox.value ;
        }
    });
    ['Sex-Specific'].forEach(function (ChoiceName) {
        listOptions = document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+ChoiceName+'_options');
        checkbox = document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+ChoiceName+'_box');
        if (checkbox.checked !== false) {
            obj["Choice_" + ChoiceName] = listOptions.value ;
        }
    });
    ["To_exclude","Sex-Specific"].forEach(function (checkboxName) {
        obj[checkboxName] = obj[checkboxName] || false;
    });
    }
  });
  var updatedJsonData = JSON.stringify(jsonData);
    fetch('/save-json?type='+file_type, {
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
            if (['[Statistics] PERC_95', '[Statistics] PERC_5','[Statistics] median'].every(element => head.includes(element)) && [' PERC_95', ' PERC_5',' median'].includes(Statistics)){
                if ([' PERC_95', ' PERC_5'].includes(Statistics)){return;}
                else if (Statistics ===' median') {
                    cell = '[' + Rounder(object['[Statistics] PERC_5']) +' , ' + Rounder(object['[Statistics] median']) + ' , '+ Rounder(object['[Statistics] PERC_95']) + ']' ;
                    rowID ='Percentile [5,50,95]'
                }
            }
            else if (['[Statistics] SD', '[Statistics] Mean'].every(element => head.includes(element)) && [' Mean', ' SD'].includes(Statistics)){
                if (' SD' === Statistics){return;}
                else if (Statistics===' Mean') {
                    rowID = 'μ\u0305 [SD]'
                    cell= Rounder(object['[Statistics] Mean']) + ' [' +  Rounder(object['[Statistics] SD']) +' ]'
                }
            }
            else if (['[Statistics] Minimum', '[Statistics] Maximum'].every(element => head.includes(element)) && [' Minimum', ' Maximum'].includes(Statistics)){
                if (' Minimum' === Statistics){return;}
                else if (Statistics===' Maximum') {
                    cell = '[' + Rounder(object['[Statistics] Minimum']) +' , ' + Rounder(object['[Statistics] Maximum']) + ']' 
                    rowID = 'Range'
                }
            }
            else {
                    cell = Rounder(object[key])
                    rowID = Statistics.replace('Mean','μ\u0305 ').replace('mean','μ\u0305 ')
            }
                row = tbody.insertRow();
                var th = document.createElement("th");
                row.appendChild(th);
                var td = row.insertCell();
                th.textContent = rowID;
                td.textContent = cell;
            };

    });
        Container_table.appendChild(table)
        return Container_table
}



function loader(){
console.log('test')
jsonData.forEach(function(obj,index) {
    var objectDix = document.createElement('nav-item');
    objectDix.id=obj["[Description] Variable"].replace(/ /g, '_')
                if (file_type === 'continuous'){
                    var headerKeys =['To_exclude','Not_normalize',"Threshold_Right",'Threshold_Left',"Sex-Specific"]
                    }
                else {var headerKeys =['To_exclude',"Sex-Specific"]}
                //Create a header explaining phenotype
                var title= document.createElement("h1");
                title.textContent=obj["[Description] Label"] ;
                title.className="text-center"
                var title2= document.createElement("h3");
                title2.className="text-center"
                title2.textContent= obj["[Description] Variable"].replace(/ /g, '_') ;
                objectDix.appendChild(title);
                objectDix.appendChild(title2);
                //Create Container of all tables with bootstrap grid so in-line
                var Container_table = document.createElement('div');
                Container_table.className = "row"  ;
                // 1) Options table
                var Container_table1 = document.createElement('div');
                Container_table1.className = "col" ;
                Container_table1.id = obj["[Description] Variable"].replace(/ /g, '_')+'Container_table1';
                var table1 = document.createElement("table");
                var thead1 = table1.createTHead();
                var tbody1 = table1.createTBody();
                thead1.textContent = 'Filters';
                [headerKeys].forEach(function(key) {
                    if (key === "To_exclude"){
                        row = tbody1.insertRow();
                        var th = document.createElement("th");
                        th.textContent = key.replace(/_/g, ' ');
                        row.appendChild(th);
                        var td = row.insertCell()
                        var checkbox = document.createElement("input");
                        checkbox.type = "checkbox";
                        checkbox.checked = obj[key] || false;
                        checkbox.id=obj["[Description] Variable"].replace(/ /g, '_')+key+'_box';
                        td.appendChild(checkbox);
                        checkbox.addEventListener('change', function() {
                            jsonData[index][key] = checkbox.checked;
                        });
                        var textbox = document.createElement("input"); 
                        const attributes = {
                        id: obj["[Description] Variable"].replace(/ /g, '_')+key+'_text',
                        class: "topic-picker ui-autocomplete-input",
                        type: "text",
                        maxlength: "100",
                        placeholder: 'Justification to not exclude',
                        role: "textbox",
                        'aria-autocomplete': "list",
                        'aria-haspopup': "true"
                        };
                        Object.entries(attributes).forEach(([hey, value]) => textbox.setAttribute(hey, value));
                        textbox.style.display=checkbox.checked !== false ? "block" : "none";
                        textbox.value = checkbox.checked !== false ? jsonData[index]["justification_" + key].toString() : "";
                        if (checkbox.checked === false){
                            jsonData[index]["justification_" + key]==""
                        }
                        td.appendChild(textbox);
                        checkbox.addEventListener("click", function() {
                            toggleTextbox(obj["[Description] Variable"].replace(/ /g, '_') + key) })

                        textbox.addEventListener("click", function() {
                            var inputId = obj["[Description] Variable"].replace(/ /g, '_')+key+'_text';
                        $(`#${inputId}`).autocomplete({
                            source: getUniqueFeatureValues(jsonData, key)
                        });
                        });
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
                            checkbox.id = obj["[Description] Variable"].replace(/ /g, '_') + key + '_box';
                            td.appendChild(checkbox);
                            checkbox.addEventListener('change', function() {
                                jsonData[index][key] = checkbox.checked;
                            });
                            var SexInput = document.createElement("select");; 
                            SexInput.id = obj["[Description] Variable"].replace(/ /g, '_') + key +'_options';
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
                            togglelistOptions(obj["[Description] Variable"].replace(/ /g, '_') + key)
                        });
                    } 
                    else if (key === "Threshold_Left" || key === "Threshold_Right") { //creates drop down menu
                        row = tbody1.insertRow();
                        var th = document.createElement("th");
                        th.textContent = key.replace(/_/g, ' ');
                        row.appendChild(th);
                        var td = row.insertCell()
                        var thresholdInput = document.createElement("select");
                        thresholdInput.id=obj["[Description] Variable"].replace(/ /g, '_')+key+'_input';
                        var noneOption = document.createElement("option");
                        noneOption.value = "None";
                        noneOption.text = "None";
                        thresholdInput.add(noneOption);
                        for (var i = 1; i <= 5; i++) {
                            var option = document.createElement("option");
                            option.value = i.toString() + 'SD';
                            option.text = i.toString() + 'SD';
                            thresholdInput.add(option);
                        }

                        thresholdInput.value = obj[key] !== null && obj[key] !== undefined ? obj[key].toString()+ 'SD' : "None";
                        thresholdInput.addEventListener('change', function() {
                        jsonData[index][key] = thresholdInput.value !== "None" ? parseInt(thresholdInput.value) : null;
                    })
                        var textbox = document.createElement("input"); 
                        const attributes = {
                        id: obj["[Description] Variable"].replace(/ /g, '_')+key+'_text',
                        class: "topic-picker ui-autocomplete-input",
                        type: "text",
                        maxlength: "100",
                        name: "q",
                        acceskey: "b",
                        autocomplete: "off",
                        placeholder: 'Justification to not normalize',
                        role: "textbox",
                        'aria-autocomplete': "list",
                        'aria-haspopup': "true"
                        };
                        Object.entries(attributes).forEach(([key, value]) => textbox.setAttribute(key, value));
                        textbox.style.display= thresholdInput.value !== 'None' ? "block" : "none";
                        textbox.value = typeof obj["justification_" + key] !== 'undefined' ? obj["justification_" + key].toString() : "";
                        thresholdInput.addEventListener("click", function() {
                            toggleTextboxOptions(obj["[Description] Variable"].replace(/ /g, '_')+key)
                        });
                        textbox.addEventListener("click", function() {
                        var inputId = obj["[Description] Variable"].replace(/ /g, '_')+key+'_text';
                        $(`#${inputId}`).autocomplete({
                            source: getUniqueFeatureValues(jsonData, key)
                        });
                        });
                        td.appendChild(thresholdInput)
                        td.appendChild(textbox);
                    } 
                    else if (key === "Not_normalize"){
                        row = tbody1.insertRow();
                        var th = document.createElement("th");
                        th.textContent = key.replace(/_/g, ' ');
                        row.appendChild(th);
                        var td = row.insertCell()
                        var checkbox = document.createElement("input");
                        checkbox.type = "checkbox";
                        checkbox.checked = obj[key] || false;
                        checkbox.id=obj["[Description] Variable"].replace(/ /g, '_')+key+'_box';
                        td.appendChild(checkbox);
                        checkbox.addEventListener('change', function() {
                            jsonData[index][key] = checkbox.checked;
                        });
                        var textbox = document.createElement("input"); 
                        const attributes = {
                        id: obj["[Description] Variable"].replace(/ /g, '_')+key+'_text',
                        class: "topic-picker ui-autocomplete-input",
                        type: "text",
                        maxlength: "100",
                        name: "q",
                        acceskey: "b",
                        autocomplete: "off",
                        placeholder: 'Justification to not normalize',
                        role: "textbox",
                        'aria-autocomplete': "list",
                        'aria-haspopup': "true"
                        };
                        Object.entries(attributes).forEach(([key, value]) => textbox.setAttribute(key, value));
                        textbox.style.display=checkbox.checked !== false ? "block" : "none";
                        textbox.value = checkbox.checked !== false ? obj["justification_" + key].toString() : "";
                        td.appendChild(textbox);
                        checkbox.addEventListener("click", function() {
                            toggleTextbox(obj["[Description] Variable"].replace(/ /g, '_') + key)
                        });
                        textbox.addEventListener("click", function() {
                        textbox.autocomplete({
                            source: getUniqueFeatureValues(jsonData, key)
                        });
                        });
                        textbox.addEventListener("click", function() {
                        var inputId = obj["[Description] Variable"].replace(/ /g, '_')+key+'_text';
                        $(`#${inputId}`).autocomplete({
                            source: getUniqueFeatureValues(jsonData, key)
                        });
                        });
                }
                });
               Container_table1.appendChild(table1); // table 1 added to Container of table 1
               Container_table.appendChild(Container_table1)

               var Container_image1 = document.createElement('div');
               Container_image1.className = "col" ;
               Container_image1.style.display = 'flex';
               Container_image1.style.justifyContent = 'center';
   if (typeof obj['[Statistics] N unique values'] === "undefined" || obj['[Statistics] N unique values'] > 1) {
               var separatorImage = document.createElement("img");
               separatorImage.id = obj["[Description] Variable"].replace(/ /g, '_') + "_image";
               fetch_image(obj["[Description] Variable"].replace(/ /g, '_'));
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
                
    if (obj['[Hidden] problem'].length !== 0 ){
   var problem=obj['[Hidden] problem']
    problem.forEach(function(key) { 
            objectDix.appendChild(createWarning(key));

} )}
    Container_table.style.display = 'flex';
Container_table.style.justifyContent = 'center';

               // Adding Container tables to Json container
               objectDix.appendChild(Container_table) ;
               objectDix.appendChild(Container_image1)
jsonContainer.appendChild(objectDix)
               });
}

const elementIsVisibleInViewport = (el, partiallyVisible = true) => {
  const { top, left, bottom, right } = el.getBoundingClientRect();
  const { innerHeight, innerWidth } = window;
  return partiallyVisible
    ? ((top > 0 && top < innerHeight) ||
        (bottom > 0 && bottom < innerHeight))
    : top >= 0 && bottom <= innerHeight;
};

//document.onscroll = event => {UpdatedCurrentIndex(); update();}

var mousewheelevt=(/Firefox/i.test(navigator.userAgent))? "DOMMouseScroll" : "mousewheel" //FF doesn't recognize mousewheel as of FF3.x

if (document.attachEvent){ //if IE (and Opera depending on user setting)
    document.attachEvent("on"+mousewheelevt, function(e){ UpdatedCurrentIndex();
     update() ;
 })
} else if (document.addEventListener) {//WC3 browsers
    document.addEventListener(mousewheelevt, function(e){ UpdatedCurrentIndex(); 
        update() }, 
    false)
}

function verify_integrity (){ 
        jsonData.forEach(function(obj,index) {
            let variables = [];
            if (variables.includes(obj["[Description] Variable"].replace(/ /g, '_'))) {
                console.error('Error, multiple object in JSON file have the same "[Description] Variable" value');
                alert('Error, multiple object in JSON file have the same "[Description] Variable" value');
            }
            else {variables.push(obj["[Description] Variable"].replace(/ /g, '_'));}
})
}

function Next (){
    let found = false
    for (i = (currentIndex+1); i < jsonData.length; i++) {
        if(jsonData[i]['[Hidden] problem'].length !==0){currentIndex=i ; found = true ; break; }
        console.error(i)
}
    if (found){
    document.getElementById(jsonData[currentIndex]["[Description] Variable"]).scrollIntoView();
    update();
} else {
    alert("There is no further flagged phenotypes.")
}
}


function UpdatedCurrentIndex(){
for (let i = 0; i < jsonData.length; i++) {
        if( elementIsVisibleInViewport(document.getElementById(jsonData[i]["[Description] Variable"])) ) {currentIndex=i ; 
    break;
    }
}
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
document.getElementById('Default').addEventListener('change', function() {
    document.getElementById('Default_table').style.display = document.getElementById('Default').checked ? 'block' : 'none'
})
document.getElementById('Next-btn').addEventListener('click', Next);


const touched = new Set();
let currentIndex = 0;
let flagged = 0;
let problematic = 0;
let problematic_addressed = 0;
let SexSpecific = 0;
let included = 0;

document.getElementById('submitButtonDefaults').addEventListener('click', function() {
    if (document.getElementById('Default').checked !== false) {
    jsonData.forEach(function(obj,index) {
        ['To_exclude','Not_normalize'].forEach(function(key){
            if (typeof document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+key+'_box') !== "undefined") {
                if(document.getElementById('Default_'+key).value !== "0") {
                document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+key+'_box').checked = document.getElementById('Default_'+key).value == 'Yes'
                obj[key]=document.getElementById('Default_'+key).value == 'Yes'
                document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+key+'_text').value = " Default/Baseline "
                toggleTextbox(obj["[Description] Variable"].replace(/ /g, '_') + key)
                }
            }
        });
        ["Threshold_Right",'Threshold_Left'].forEach(function(key){
            if (typeof document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+key+'_box') !== "undefined") {
                if(document.getElementById('Default_'+key).value !== "0") {
                    document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+key+'_input').value = document.getElementById('Default_'+key).value
                    document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+key+'_text').value = " Default/Baseline "
                    obj[key]=document.getElementById('Default_'+key).value
                    toggleTextboxOptions(obj["[Description] Variable"].replace(/ /g, '_')+key)
                }
            }
        });
    }) ;
}
});

let file_type =''


function getUniqueFeatureValues(jsonData, featureName) {
    const uniqueValues = new Set(); // Use a Set to store unique values

    // Iterate over each object in the jsonData array
    jsonData.forEach(obj => {
        if (obj[featureName] !== undefined) { // Check if the feature exists in the object
            uniqueValues.add(document.getElementById(obj["[Description] Variable"].replace(/ /g, '_')+featureName+'_text').value); // Add the feature value to the Set
        }
    });

    return Array.from(uniqueValues); // Convert the Set to an Array to return
}

document.getElementById('binary_choice').addEventListener('click', function() {
            file_type ='binary'
            fetch('/jsondata?type='+file_type)
           .then(response => response.json())
               .then(Data => {
               jsonData = Data
               verify_integrity()
               loader();
           })
          .catch(error => {
             console.error('Error fetching the JSON file:', error);
              alert('Error loading the JSON file. Check the console for more information. Make sure the expected file exist : binary_data.json');
          });
        })
        

document.getElementById('continuous_choice').addEventListener('click', function() {
            file_type = 'continuous'
            fetch('/jsondata?type=continuous')
           .then(response => response.json())
               .then(Data => {
               jsonData = Data
               verify_integrity()
               loader();
           })
          .catch(error => {
             console.error('Error fetching the JSON file:', error);
              alert('Error loading the JSON file. Check the console for more information. Make sure the expected file exist : continuous_data.json');
          });
        })
        
window.addEventListener('beforeunload', function (e) {
            navigator.sendBeacon('/shutdown');
});
