const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  tier: { type: String, enum: ['BA', 'PA', 'FA', 'privat'], required: true },
  email: { type: String, required: true },
});

module.exports = mongoose.model('User', userSchema);
