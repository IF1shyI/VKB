const express = require('express');
const router = express.Router();
const { updateTier } = require('../controllers/userController');

router.post('/update_tier', updateTier);

module.exports = router;
