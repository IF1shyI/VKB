const User = require('../models/user');
const jwt = require('jsonwebtoken');
const { SECRET_KEY } = process.env;

// Uppdatera användartier
exports.updateTier = async (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ message: 'Ingen autentisering tillhandahölls.' });
  }

  try {
    const decodedToken = jwt.verify(token, SECRET_KEY);
    const { new_tier } = req.body;

    if (!new_tier || !['BA', 'PA'].includes(new_tier)) {
      return res.status(400).json({ message: 'Ogiltigt tier' });
    }

    const user = await User.findOneAndUpdate(
      { username: decodedToken.username },
      { tier: new_tier },
      { new: true }
    );

    if (!user) {
      return res.status(404).json({ message: 'Användare ej hittad' });
    }

    res.status(200).json({ message: `Tier uppdaterad till ${new_tier}` });
  } catch (err) {
    return res.status(500).json({ message: 'Något gick fel' });
  }
};
