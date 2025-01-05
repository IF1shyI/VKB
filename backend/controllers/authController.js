const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const User = require('../models/user');
const Admin = require('../models/admin');
const { SECRET_KEY } = process.env;

// Inloggning
exports.login = async (req, res) => {
  const { username, password } = req.body;

  try {
    const user = await User.findOne({ username });
    if (!user) {
      return res.status(401).json({ message: 'Fel användarnamn eller lösenord' });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).json({ message: 'Fel användarnamn eller lösenord' });
    }

    const token = jwt.sign({ username: user.username }, SECRET_KEY, { expiresIn: '1h' });
    return res.status(200).json({ message: 'Inloggning lyckades!', token });
  } catch (error) {
    return res.status(500).json({ message: 'Något gick fel' });
  }
};

// Utloggning
exports.logout = (req, res) => {
  res.status(200).json({ message: 'Utloggning lyckades' });
};

// Kontrollera session
exports.checkSession = (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ message: 'Ingen token tillhandahållen' });
  }

  try {
    const decodedToken = jwt.verify(token, SECRET_KEY);
    res.status(200).json({ message: 'Session giltig', username: decodedToken.username });
  } catch (err) {
    res.status(401).json({ message: 'Ogiltig token' });
  }
};

// Kontrollera om användaren är admin
exports.checkAdmin = async (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ message: 'Ingen token tillhandahållen' });
  }

  try {
    const decodedToken = jwt.verify(token, SECRET_KEY);
    const user = await User.findOne({ username: decodedToken.username });
    const admin = await Admin.findOne({ username: user.username });

    if (admin) {
      return res.status(200).json({ message: 'Autentiserad som admin' });
    }
    return res.status(401).json({ message: 'Oautentiserad' });
  } catch (err) {
    return res.status(401).json({ message: 'Ogiltig token' });
  }
};
