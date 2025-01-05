const express = require('express');
const router = express.Router();
const { login, logout, checkSession, checkAdmin } = require('../controllers/authController');

router.post('/login', login);
router.post('/logout', logout);
router.get('/checksession', checkSession);
router.post('/checkadmin', checkAdmin);

module.exports = router;
