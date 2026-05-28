// src/middlewares/authMiddleware.js
const crypto = require("crypto");
const state = require("../config/state");

const ADMIN_USER = "cliente";
const ADMIN_PASS = "123456";

/**
 * Gera um token hexadecimal aleatório contendo 32 bytes de entropia.
 */
function gerarToken() { 
  return crypto.randomBytes(32).toString("hex"); 
}

/**
 * Checa a validade de expiração do Token de uma sessão presente no Header
 */
function authOk(req) {
  const token = req.headers["x-token"] || req.query.token;
  if (!token) return false;
  const exp = state.sessoes.get(token);
  // Se o token existir e a data de expiração não tiver violado o now()
  if (!exp || Date.now() > exp) { 
    state.sessoes.delete(token); 
    return false; 
  }
  return true;
}

/**
 * Middleware oficial do Express intercedendo requests para travar curiosos.
 */
function guard(req, res, next) {
  if (authOk(req)) return next();
  res.status(401).json({ ok: false, erro: "Não autorizado ou sessão expirada" });
}

module.exports = {
  ADMIN_USER,
  ADMIN_PASS,
  gerarToken,
  authOk,
  guard
};
