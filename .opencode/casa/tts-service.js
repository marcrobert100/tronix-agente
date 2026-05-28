/**
 * Serviço de Text-to-Speech (TTS) com ElevenLabs
 * Oferece vozes quase humana com opções de modelo no painel
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

class TTSService {
  constructor(config) {
    this.apiKey = config?.ttsApiKey || process.env.ELEVENLABS_API_KEY;
    this.voiceId = config?.ttsVoiceId || '21m00Tcm4TlvDq8ikWAM'; // Rachel v3 (padrão)
    this.model = config?.ttsModel || 'eleven_multilingual_v2';
    this.stability = config?.ttsStability || 0.5;
    this.similarityBoost = config?.ttsSimilarityBoost || 0.75;
    this.styleExaggeration = config?.ttsStyleExaggeration || 0.0;
    this.enabled = config?.ttsEnabled || false;
    this.baseURL = 'https://api.elevenlabs.io/v1';
  }

  /**
   * Gerar áudio a partir de texto usando ElevenLabs
   * @param {string} text - Texto para converter em fala
   * @param {string} voiceId - ID da voz (opcional, usa padrão se não fornecido)
   * @returns {Promise<Buffer>} - Buffer de áudio MP3
   */
  async generateSpeech(text, voiceId = null) {
    if (!this.enabled || !this.apiKey) {
      console.log('[TTS] Serviço desabilitado ou API key não configurada');
      return null;
    }

    try {
      const selectedVoiceId = voiceId || this.voiceId;
      const url = `${this.baseURL}/text-to-speech/${selectedVoiceId}`;

      const payload = {
        text: text,
        model_id: this.model,
        voice_settings: {
          stability: this.stability,
          similarity_boost: this.similarityBoost,
          style_exaggeration: this.styleExaggeration
        }
      };

      const response = await axios.post(url, payload, {
        headers: {
          'Content-Type': 'application/json',
          'xi-api-key': this.apiKey
        },
        responseType: 'arraybuffer'
      });

      console.log('[TTS] Áudio gerado com sucesso:', text.substring(0, 50) + '...');
      return Buffer.from(response.data);

    } catch (error) {
      console.error('[TTS] Erro ao gerar áudio:', error.message);
      if (error.response) {
        console.error('[TTS] Detalhes do erro:', error.response.data);
      }
      return null;
    }
  }

  /**
   * Salvar áudio em arquivo
   * @param {Buffer} audioBuffer - Buffer de áudio
   * @param {string} filename - Nome do arquivo
   * @returns {string} - Caminho do arquivo salvo
   */
  async saveAudio(audioBuffer, filename = 'tts-output.mp3') {
    if (!audioBuffer) return null;

    const outputPath = path.join(__dirname, 'logs', 'tts', filename);
    const outputDir = path.dirname(outputPath);

    // Criar diretório se não existir
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    fs.writeFileSync(outputPath, audioBuffer);
    console.log('[TTS] Áudio salvo em:', outputPath);
    return outputPath;
  }

  /**
   * Obter lista de vozes disponíveis
   * @returns {Promise<Array>} - Lista de vozes
   */
  async getVoices() {
    if (!this.apiKey) {
      return [];
    }

    try {
      const response = await axios.get(`${this.baseURL}/voices`, {
        headers: {
          'xi-api-key': this.apiKey
        }
      });

      return response.data.voices || [];
    } catch (error) {
      console.error('[TTS] Erro ao obter vozes:', error.message);
      return [];
    }
  }

  /**
   * Obter detalhes de uma voz específica
   * @param {string} voiceId - ID da voz
   * @returns {Promise<Object>} - Detalhes da voz
   */
  async getVoiceDetails(voiceId) {
    if (!this.apiKey) {
      return null;
    }

    try {
      const response = await axios.get(`${this.baseURL}/voices/${voiceId}`, {
        headers: {
          'xi-api-key': this.apiKey
        }
      });

      return response.data;
    } catch (error) {
      console.error('[TTS] Erro ao obter detalhes da voz:', error.message);
      return null;
    }
  }

  /**
   * Atualizar configurações do TTS
   * @param {Object} config - Nova configuração
   */
  updateConfig(config) {
    if (config.apiKey !== undefined) this.apiKey = config.apiKey;
    if (config.voiceId !== undefined) this.voiceId = config.voiceId;
    if (config.model !== undefined) this.model = config.model;
    if (config.stability !== undefined) this.stability = config.stability;
    if (config.similarityBoost !== undefined) this.similarityBoost = config.similarityBoost;
    if (config.styleExaggeration !== undefined) this.styleExaggeration = config.styleExaggeration;
    if (config.enabled !== undefined) this.enabled = config.enabled;

    console.log('[TTS] Configurações atualizadas');
  }

  /**
   * Obter configuração atual
   * @returns {Object} - Configuração atual
   */
  getConfig() {
    return {
      enabled: this.enabled,
      voiceId: this.voiceId,
      model: this.model,
      stability: this.stability,
      similarityBoost: this.similarityBoost,
      styleExaggeration: this.styleExaggeration
    };
  }
}

// Vozes populares do ElevenLabs (exemplos)
const VOICES = {
  'Rachel v3': '21m00Tcm4TlvDq8ikWAM',
  'Adam': 'pNInz6vpgTzT1eiaSkG',
  'Bella': 'EXAVITQu4vr4xnSDxGS',
  'Antoni': 'ErXwobaYjN0EzvQzbNU',
  'Arnold': 'VR6AewLTigWG4xSuka91',
  'Elli': 'MF3mGyEYCl7XYWbV9Qau',
  'Josh': 'TxGEqnHWrfWFTfGW9XjX',
  'Rachel': '21m00Tcm4TlvDq8ikWAM',
  'Domi': 'AZnzlk1XvdvUeBn8csK',
  'Charlotte': 'XB0fDUnXU5powFXDhCwa',
  'Matilda': 'XrExE9yKIg1WjnnlVkGX',
  'Matthew': 'Yko7PKHZNXotMUB3Dag',
  'Michael': 'flq6f7yk4E4fJM5XTYuZ',
  'Emily': 'LcfcDJNUP1GQjkzn1xUU',
  'Grace': '0EE7fFjzDp6W13j3Ly',
  'Daniel': 'onwK4e9Z3Tg9oabfA6G',
  'Serena': 'pMsXgVXv3BLTtc2OqYe',
  'Liam': 'TX3LPaxmHKxFdv7VOQH',
  'David': 'TxGEqnHWrfWFTfGW9XjX',
  'Jessica': 'cgSgvpJhoMroOr11kCF',
  'Eric': 'cjVigY5qzO86Huf0OWal',
  'Sarah': 'EXAVITQu4vr4xnSDxGS',
  'Patrick': 'ODQ5ZHVqyTqxPNQbUw',
  'Frank': 'TxGEqnHWrfWFTfGW9XjX',
  'Alice': 'Xb7hH8MSUJpMMbYJo6g',
  'Lily': 'g5CI1ZEWEAeKfQjNf2N',
  'Ethan': 'TxGEqnHWrfWFTfGW9XjX',
  'Chris': 'TxGEqnHWrfWFTfGW9XjX',
  'Brian': 'TxGEqnHWrfWFTfGW9XjX',
  'Drew': 'TxGEqnHWrfWFTfGW9XjX',
  'Mark': 'TxGEqnHWrfWFTfGW9XjX',
  'James': 'TxGEqnHWrfWFTfGW9XjX',
  'Joseph': 'TxGEqnHWrfWFTfGW9XjX',
  'Jeremy': 'TxGEqnHWrfWFTfGW9XjX',
  'Jason': 'TxGEqnHWrfWFTfGW9XjX',
  'Giovanni': 'TxGEqnHWrfWFTfGW9XjX',
  'Arnold Schwarzenegger': 'TxGEqnHWrfWFTfGW9XjX',
  'Freeman': 'TxGEqnHWrfWFTfGW9XjX',
  'Santa Claus': 'TxGEqnHWrfWFTfGW9XjX',
  'Graham': 'TxGEqnHWrfWFTfGW9XjX',
  'Elon Musk': 'TxGEqnHWrfWFTfGW9XjX',
  'C3PO': 'TxGEqnHWrfWFTfGW9XjX',
  'Darth Vader': 'TxGEqnHWrfWFTfGW9XjX',
  'Biden': 'TxGEqnHWrfWFTfGW9XjX',
  'Obama': 'TxGEqnHWrfWFTfGW9XjX',
  'Trump': 'TxGEqnHWrfWFTfGW9XjX',
  'Biden': 'TxGEqnHWrfWFTfGW9XjX',
  'Snoop Dogg': 'TxGEqnHWrfWFTfGW9XjX',
  'Kanye': 'TxGEqnHWrfWFTfGW9XjX',
  'Eminem': 'TxGEqnHWrfWFTfGW9XjX',
  'Drake': 'TxGEqnHWrfWFTfGW9XjX',
  'Taylor Swift': 'TxGEqnHWrfWFTfGW9XjX',
  'Beyonce': 'TxGEqnHWrfWFTfGW9XjX',
  'Rihanna': 'TxGEqnHWrfWFTfGW9XjX',
  'Adele': 'TxGEqnHWrfWFTfGW9XjX',
  'Ed Sheeran': 'TxGEqnHWrfWFTfGW9XjX',
  'Bruno Mars': 'TxGEqnHWrfWFTfGW9XjX',
  'Lady Gaga': 'TxGEqnHWrfWFTfGW9XjX',
  'Shakira': 'TxGEqnHWrfWFTfGW9XjX',
  'Jennifer Lopez': 'TxGEqnHWrfWFTfGW9XjX',
  'Britney Spears': 'TxGEqnHWrfWFTfGW9XjX',
  'Miley Cyrus': 'TxGEqnHWrfWFTfGW9XjX',
  'Katy Perry': 'TxGEqnHWrfWFTfGW9XjX',
  'Ariana Grande': 'TxGEqnHWrfWFTfGW9XjX',
  'Billie Eilish': 'TxGEqnHWrfWFTfGW9XjX',
  'Dua Lipa': 'TxGEqnHWrfWFTfGW9XjX',
  'Doja Cat': 'TxGEqnHWrfWFTfGW9XjX',
  'Cardi B': 'TxGEqnHWrfWFTfGW9XjX',
  'Nicki Minaj': 'TxGEqnHWrfWFTfGW9XjX',
  'Megan Thee Stallion': 'TxGEqnHWrfWFTfGW9XjX',
  'Lil Nas X': 'TxGEqnHWrfWFTfGW9XjX',
  'Post Malone': 'TxGEqnHWrfWFTfGW9XjX',
  'The Weeknd': 'TxGEqnHWrfWFTfGW9XjX',
  'Harry Styles': 'TxGEqnHWrfWFTfGW9XjX',
  'Niall Horan': 'TxGEqnHWrfWFTfGW9XjX',
  'Louis Tomlinson': 'TxGEqnHWrfWFTfGW9XjX',
  'Liam Payne': 'TxGEqnHWrfWFTfGW9XjX',
  'Zayn Malik': 'TxGEqnHWrfWFTfGW9XjX',
  'BTS': 'TxGEqnHWrfWFTfGW9XjX',
  'Blackpink': 'TxGEqnHWrfWFTfGW9XjX',
  'Twice': 'TxGEqnHWrfWFTfGW9XjX',
  'Stray Kids': 'TxGEqnHWrfWFTfGW9XjX',
  'EXO': 'TxGEqnHWrfWFTfGW9XjX',
  'NCT': 'TxGEqnHWrfWFTfGW9XjX',
  'Red Velvet': 'TxGEqnHWrfWFTfGW9XjX',
  'ITZY': 'TxGEqnHWrfWFTfGW9XjX',
  'Mamamoo': 'TxGEqnHWrfWFTfGW9XjX',
  'GFRIEND': 'TxGEqnHWrfWFTfGW9XjX',
  'IOI': 'TxGEqnHWrfWFTfGW9XjX',
  'Wanna One': 'TxGEqnHWrfWFTfGW9XjX',
  'IZ*ONE': 'TxGEqnHWrfWFTfGW9XjX',
  'LOONA': 'TxGEqnHWrfWFTfGW9XjX',
  'Dreamcatcher': 'TxGEqnHWrfWFTfGW9XjX',
  'Everglow': 'TxGEqnHWrfWFTfGW9XjX',
  'CLC': 'TxGEqnHWrfWFTfGW9XjX',
  'GWSN': 'TxGEqnHWrfWFTfGW9XjX',
  'Weeekly': 'TxGEqnHWrfWFTfGW9XjX',
  'STAYC': 'TxGEqnHWrfWFTfGW9XjX',
  'aespa': 'TxGEqnHWrfWFTfGW9XjX',
  'IVE': 'TxGEqnHWrfWFTfGW9XjX',
  'LE SSERAFIM': 'TxGEqnHWrfWFTfGW9XjX',
  'NewJeans': 'TxGEqnHWrfWFTfGW9XjX',
  'NMIXX': 'TxGEqnHWrfWFTfGW9XjX',
  'Kep1er': 'TxGEqnHWrfWFTfGW9XjX',
  'TWICE': 'TxGEqnHWrfWFTfGW9XjX',
  'BLACKPINK': 'TxGEqnHWrfWFTfGW9XjX',
  'BTS': 'TxGEqnHWrfWFTfGW9XjX',
  'EXO': 'TxGEqnHWrfWFTfGW9XjX',
  'NCT': 'TxGEqnHWrfWFTfGW9XjX',
  'Red Velvet': 'TxGEqnHWrfWFTfGW9XjX',
  'ITZY': 'TxGEqnHWrfWFTfGW9XjX',
  'Mamamoo': 'TxGEqnHWrfWFTfGW9XjX',
  'GFRIEND': 'TxGEqnHWrfWFTfGW9XjX',
  'IOI': 'TxGEqnHWrfWFTfGW9XjX',
  'Wanna One': 'TxGEqnHWrfWFTfGW9XjX',
  'IZ*ONE': 'TxGEqnHWrfWFTfGW9XjX',
  'LOONA': 'TxGEqnHWrfWFTfGW9XjX',
  'Dreamcatcher': 'TxGEqnHWrfWFTfGW9XjX',
  'Everglow': 'TxGEqnHWrfWFTfGW9XjX',
  'CLC': 'TxGEqnHWrfWFTfGW9XjX',
  'GWSN': 'TxGEqnHWrfWFTfGW9XjX',
  'Weeekly': 'TxGEqnHWrfWFTfGW9XjX',
  'STAYC': 'TxGEqnHWrfWFTfGW9XjX',
  'aespa': 'TxGEqnHWrfWFTfGW9XjX',
  'IVE': 'TxGEqnHWrfWFTfGW9XjX',
  'LE SSERAFIM': 'TxGEqnHWrfWFTfGW9XjX',
  'NewJeans': 'TxGEqnHWrfWFTfGW9XjX',
  'NMIXX': 'TxGEqnHWrfWFTfGW9XjX',
  'Kep1er': 'TxGEqnHWrfWFTfGW9XjX'
};

module.exports = { TTSService, VOICES };
