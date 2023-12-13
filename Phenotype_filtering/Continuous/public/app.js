const express = require('express');
const path = require('path');
const fs = require('fs');
const app = express();
const port = 3000;
const multer = require('multer');
const process = require('process')
const open = require('open');
const server = require('http').createServer(app);
const bodyParser = require('body-parser')

app.use(bodyParser.json({ limit: '500mb' }));


app.post('/shutdown', (req, res) => {
    console.log('Shutdown signal received');
    res.status(200).send('Shutting down');
    process.exit(); // Exit the process to shut down the server
});


const readJsonFile = (callback) => {
  const filePath = path.join(process.execPath, '..', 'Continuous_data.json');

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

app.get('/jsondata', (req, res) => {
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


function shutdownServer() {
    console.log('Shutting down server');
    server.close(() => {
        console.log('Server closed');
        process.exit(0); // Exit the process to close the server completely
    });
}



app.post('/save-json', (req, res) => {
var out = req.body;
const filePath = path.join(process.execPath, '..', 'Continuous_data.json');
    // Write the JSON data to the file
    fs.writeFile(filePath, JSON.stringify(out, null, 2), 'utf8', (err) => {
        if (err) {
            console.error(err);
            res.status(500).send('Error writing to file'); // Send an error response if writing fails
            return;
        }
        res.send({ message: 'Data successfully saved' }); // Send a success message on successful write
    });
});




app.use(express.static(__dirname)); // Serve static files

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
    open(`http://localhost:${port}`);
});

// process.on('SIGTERM', () => {
//   console.info('SIGTERM signal received.');
//   console.log('Closing http server.');
//   server.close(() => {
//       process.exit(0);
//     });
//   });