#!/usr/bin/env node

/**
 * Geração de Imagem de Basquete
 * 
 * Gera uma imagem de um jogador de basquete enterrando a bola
 */

const chalk = require('chalk');
const axios = require('axios');
const fs = require('fs-extra');
const path = require('path');
require('dotenv').config();

const OUTPUT_DIR = path.join(__dirname, '..', 'output');
const VIDEOS_DIR = path.join(__dirname, '..', 'videos');

async function generateBasketballImage() {
  console.log(chalk.blue.bold('\n🏀 Gerando Imagem de Basquete\n'));

  const prompt = 'Professional basketball player dunking a basketball in an arena, dramatic lighting, crowd in background, high quality, cinematic';

  console.log(chalk.yellow('Prompt:'));
  console.log(chalk.cyan(`  ${prompt}\n`));

  try {
    console.log(chalk.yellow('⏳ Gerando imagem...'));

    // Usar API da Clod (que já testamos e funciona)
    const imagePath = await generateWithClod(prompt);

    if (imagePath) {
      console.log(chalk.green(`\n✅ Imagem gerada com sucesso!`));
      console.log(chalk.cyan(`📁 Local: ${imagePath}`));
      return imagePath;
    } else {
      console.log(chalk.red('\n❌ Não foi possível gerar a imagem.'));
      return null;
    }
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro ao gerar imagem: ${error.message}`));
    return null;
  }
}

async function generateWithClod(prompt) {
  const apiKey = process.env.OPENAI_API_KEY;
  
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY não configurada no .env');
  }

  try {
    // Usar a API da Clod (que é compatível com OpenAI)
    const response = await axios.post(
      'https://api.clod.io/v1/images/generations',
      {
        model: 'dall-e-3',
        prompt: prompt,
        size: '1024x1024',
        quality: 'standard',
        n: 1
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const imageUrl = response.data.data[0].url;
    return await downloadImage(imageUrl, 'basketball-dunk');
  } catch (error) {
    console.log(chalk.yellow(`Clod não disponível: ${error.message}`));
    
    // Tentar OpenAI direto
    return await generateWithOpenAI(prompt);
  }
}

async function generateWithOpenAI(prompt) {
  const apiKey = process.env.OPENAI_API_KEY;
  
  try {
    const response = await axios.post(
      'https://api.openai.com/v1/images/generations',
      {
        model: 'dall-e-3',
        prompt: prompt,
        size: '1024x1024',
        quality: 'standard',
        n: 1
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const imageUrl = response.data.data[0].url;
    return await downloadImage(imageUrl, 'basketball-dunk');
  } catch (error) {
    console.log(chalk.yellow(`OpenAI não disponível: ${error.message}`));
    return null;
  }
}

async function downloadImage(url, filename) {
  await fs.ensureDir(OUTPUT_DIR);
  
  const outputPath = path.join(OUTPUT_DIR, `${filename}.png`);
  
  console.log(chalk.yellow(`Baixando imagem de: ${url}`));
  
  const response = await axios({
    method: 'GET',
    url: url,
    responseType: 'stream'
  });
  
  const writer = fs.createWriteStream(outputPath);
  response.data.pipe(writer);
  
  return new Promise((resolve, reject) => {
    writer.on('finish', () => resolve(outputPath));
    writer.on('error', reject);
  });
}

module.exports = generateBasketballImage;

// Execução direta
if (require.main === module) {
  generateBasketballImage().then(() => process.exit(0));
}
