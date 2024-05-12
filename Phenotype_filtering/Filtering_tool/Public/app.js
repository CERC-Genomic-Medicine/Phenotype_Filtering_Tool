const express = require('express');
const session = require('express-session');
const path = require('path');
const fs = require('fs');
const app = express();
const port = 3000;
const multer = require('multer');
const process = require('process')
const open = require('open');
const bodyParser = require('body-parser')

app.use(bodyParser.json({ limit: '500mb' }));


let globalJsonPath = null;


app.post('/shutdown', (req, res) => {
    console.log('Shutdown signal received');
    res.status(200).send('Shutting down');
    process.exit(); // Exit the process to shut down the server
});



function shutdownServer() {
    console.log('Shutting down server');
    server.close(() => {
        console.log('Server closed');
        process.exit(0); // Exit the process to close the server completely
    });
}


app.post('/save-json', (req, res) => {
var out = req.body;
  const fileType = req.query.type; // This would be "binary" or any other type you pass
  globalJsonPath = path.join(process.execPath, '../', fileType + '_data.json');
  console.error(globalJsonPath)
    // Write the JSON data to the file
    fs.writeFile(globalJsonPath, JSON.stringify(out, null, 2), 'utf8', (err) => {
        if (err) {
            console.error(err);
            res.status(500).send('Error writing to file'); // Send an error response if writing fails
            return;
        }
        res.send({ message: 'Data successfully saved' }); // Send a success message on successful write
    });
});


app.get('/jsondata', (req, res) => {
  const fileType = req.query.type; // This would be "binary" or any other type you pass
  globalJsonPath = path.join(process.execPath, '../', fileType + '_data.json');
    console.error(globalJsonPath)
  readJsonFile((err, jsonData) => {
    if (err) {
      res.status(500).send('Error reading JSON data');
    } else {
      res.json(jsonData);
    }
  });
});


app.get('/images/:filename', (req, res) => {
    const filename = req.params.filename;
    const imagePath = path.join(process.execPath, '../images', filename);
    fs.access(imagePath, fs.constants.F_OK, (err) => {
        if (err) {
            console.error(err);
            res.status(404).send('Image not found');
            return;
        }
        
        res.sendFile(imagePath);
    });
});



const readJsonFile = (callback) => {
  const filePath = globalJsonPath;
  console.log(globalJsonPath)
  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      console.error(`Error reading file from disk: ${err}`);
      callback(err);
    } else {
      try {
        const jsonData = JSON.parse(data);
        callback(null, jsonData);
      } catch (err) {
        console.error(`Error parsing JSON string: ${err}`);
        callback(err);
      }
    }
  });
};

app.use(express.static(__dirname)); // Serve static files

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
    open(`http://localhost:${port}`);
});
