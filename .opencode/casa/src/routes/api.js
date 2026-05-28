// src/routes/api.js
const express = require("express");
const { guard } = require("../middlewares/authMiddleware");
const settingsController = require("../controllers/settingsController");

const router = express.Router();

/**
 * Endpoint Públicos (Open)
 */
router.post("/login", settingsController.login);

/**
 * Endpoints Privados (Guardados)
 */
router.post("/logout", guard, settingsController.logout);
router.get("/status", guard, settingsController.getStatus);
router.post("/groq-key", guard, settingsController.saveGroqKey);

// Outros controladores de menu, cupons, e afins serão expostos aqui no futuro...

module.exports = router;
