const express = require('express')
const app = express()
const port = 3000


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
  res.send(JSON.stringify(req.oidc.user));
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})