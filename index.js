const express = require('express')
const bodyParser = require('body-parser')
const app = express()
const port = 3000
const {PythonShell} =require('python-shell'); 
const path = require('path');


const { auth } = require('express-openid-connect');
app.set('view engine', 'pug')
app.set('views', __dirname + '/views');

app.use(express.static(__dirname + '/views'));


const config = {
  authRequired: false,
  auth0Logout: true,
  secret: 'a long, randomly-generated string stored in env',
  baseURL: 'http://localhost:3000',
  clientID: 'jF8byytgDKOGvSia7LKjEwUGtLEXs3kj',
  issuerBaseURL: 'https://vrtsguelph.us.auth0.com'
};

// auth router attaches /login, /logout, and /callback routes to the baseURL
app.use(auth(config));

// req.isAuthenticated is provided from the auth router
app.get('/', (req, res) => {
});

const { requiresAuth } = require('express-openid-connect');

app.get('/mdg', requiresAuth(), (req, res) => {
  res.render('mdg')
});

app.get('/MASTER.csv', requiresAuth(), (req, res) => {
  res.sendFile(path.join(__dirname, 'MASTER.csv'));
  //res.sendFile("./MASTER.csv")
});

app.get('/data', requiresAuth(), (req, res) => {
  const fs = require('fs')

  const path = './MASTER.csv'

  try {
    if (fs.existsSync(path)) {
      res.render("data")
    }
  } catch(err) {
    console.error(err)
  }
});

app.post('/mdg', function(req, res) {
  
  var spawn = require("child_process").spawn; 
      
    // Parameters passed in spawn - 
    // 1. type_of_script 
    // 2. list containing Path of the script 
    //    and arguments for the script  
      
    // E.g : http://localhost:3000/name?firstname=Mike&lastname=Will 
    // so, first name = Mike and last name = Will 
    //var process = spawn('cd',["vrtsAWS"] ); 
    console.log("juhjfd")
    var process = spawn('python',["vrtsAWS/MasterDataGenerator.py"]); 
    
  
    // Takes stdout data from script which executed 
    // with arguments and send this data to res object 
    process.stdout.on('data', function(data) { 
        console.log(data.toString()); 
    } ) 

    //res.render("mdg")
  
  res.render('mdg')
  //res.send(200);
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})

