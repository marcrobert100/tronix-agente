#!/usr/bin/env node

/**
 * Geração de Imagens Realistas
 * 
 * APIs suportadas:
 * - OpenAI DALL-E 3
 * - Stability AI (Stable Diffusion)
 */

const chalk = require('chalk');
const inquirer = require('inquirer');
const axios = require('axios');
const fs = require('fs-extra');
const path = require('path');
require('dotenv').config();

const OUTPUT_DIR = process.env.OUTPUT_DIR || './output';
const TEMP_DIR = process.env.TEMP_DIR || './temp';

async function generateImage() {
  console.log(chalk.blue('\n🎨 Gerador de Imagens Realistas\n'));

  const answers = await inquirer.prompt([
    {
      type: 'list',
      name: 'api',
      message: 'Qual API deseja usar?',
      choices: [
        { name: 'OpenAI DALL-E 3', value: 'dalle' },
        { name: 'Stability AI (Stable Diffusion)', value: 'stability' }
      ]
    },
    {
      type: 'input',
      name: 'prompt',
      message: 'Descreva a imagem que deseja gerar:',
      validate: (input) => input.length > 0 ? true : 'Por favor, descreva a imagem.'
    },
    {
      type: 'list',
      name: 'size',
      message: 'Tamanho da imagem:',
      choices: ['1024x1024', '1024x1792', '1792x1024'],
      when: (answers) => answers.api === 'dalle'
    },
    {
      type: 'list',
      name: 'quality',
      message: 'Qualidade:',
      choices: ['standard', 'hd'],
      when: (answers) => answers.api === 'dalle'
    },
    {
      type: 'input',
      name: 'filename',
      message: 'Nome do arquivo (sem extensão):',
      default: 'image'
    }
  ]);

  try {
    console.log(chalk.yellow('\n⏳ Gerando imagem...'));

    let imageUrl;
    if (answers.api === 'dalle') {
      imageUrl = await generateWithDalle(answers.prompt, answers.size, answers.quality);
    } else {
      imageUrl = await generateWithStability(answers.prompt);
    }

    // Baixar a imagem
    const outputPath = await downloadImage(imageUrl, answers.filename);
    
    console.log(chalk.green(`\n✅ Imagem gerada com sucesso!`));
    console.log(chalk.cyan(`📁 Local: ${outputPath}`));
    
    return outputPath;
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro ao gerar imagem: ${error.message}`));
    return null;
  }
}

async function generateWithDalle(prompt, size = '1024x1024', quality = 'standard') {
  const apiKey = process.env.OPENAI_API_KEY;
  
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY não configurada no .env');
  }

  const response = await axios.post(
    'https://api.openai.com/v1/images/generations',
    {
      model: 'dall-e-3',
      prompt: prompt,
      size: size,
      quality: quality,
      n: 1
    },
    {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    }
  );

  return response.data.data[0].url;
}

async function generateWithStability(prompt) {
  const apiKey = process.env.STABILITY_API_KEY;
  
  if (!apiKey) {
    throw new Error('STABILITY_API_KEY não configurada no .env');
  }

  const response = await axios.post(
    'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
    {
      text_prompts: [
        {
          text: prompt,
          weight: 1
        }
      ],
      cfg_scale: 7,
      height: 1024,
      width: 1024,
      samples: 1,
      steps: 30
    },
    {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    }
  );

  // Stability AI retorna base64, precisamos converter
  const base64Image = response.data.artifacts[0].base64;
  const buffer = Buffer.from(base64Image, 'base64');
  
  // Salvar temporariamente
  const tempPath = path.join(TEMP_DIR, 'stability_temp.png');
  await fs.ensureDir(TEMP_DIR);
  await fs.writeFile(tempPath, buffer);
  
  return tempPath;
}

async function downloadImage(url, filename) {
  await fs.ensureDir(OUTPUT_DIR);
  
  const extension = url.endsWith('.png') ? 'png' : 'jpg';
  const outputPath = path.join(OUTPUT_DIR, `${filename}.${extension}`);
  
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

module.exports = generateImage;

// Execução direta
if (require.main === module) {
  generateImage().then(() => process.exit(0));
}
