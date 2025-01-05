const express = require('express');
const router = express.Router();
const { createPaymentIntent } = require('../controllers/stripeController');

router.post('/secret_key', createPaymentIntent);

module.exports = router;
