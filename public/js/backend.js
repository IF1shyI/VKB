require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const { OAuth2Client } = require('google-auth-library');

const app = express();
const client = new OAuth2Client(process.env.GOOGLE_CLOUD_ID);

app.use(bodyParser.json());

// Endpoint för verifiering av ID-token
app.post('/verify-token', async (req, res) => {
  const token = req.body.token;
  try {
    const ticket = await client.verifyIdToken({
      idToken: token,
      audience: process.env.GOOGLE_CLIENT_ID, // Använd miljövariabel
    });
    const payload = ticket.getPayload();
    console.log('Verifierad användare:', payload);

    res.status(200).json({
      message: 'Verifiering lyckades!',
      user: payload,
    });
  } catch (error) {
    console.error('Verifiering misslyckades:', error);
    res.status(401).json({
      message: 'Verifiering misslyckades.',
    });
  }
});


app.listen(1234, () => {
  console.log('Server körs på http://localhost:1234');
});
