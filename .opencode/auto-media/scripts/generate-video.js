#!/usr/bin/env node

/**
 * Geração de Vídeos
 * 
 * APIs suportadas:
 * - Runway ML
 * - Pika Labs
 */

const chalk = require('chalk');
const inquirer = require('inquirer');
const axios = require('axios');
const fs = require('fs-extra');
const path = require('path');
require('dotenv').config();

const OUTPUT_DIR = process.env.OUTPUT_DIR || './output';
const TEMP_DIR = process.env.TEMP_DIR || './temp';

async function generateVideo() {
  console.log(chalk.blue('\n🎬 Gerador de Vídeos\n'));

  const answers = await inquirer.prompt([
    {
      type: 'list',
      name: 'api',
      message: 'Qual API deseja usar?',
      choices: [
        { name: 'Runway ML', value: 'runway' },
        { name: 'Pika Labs', value: 'pika' }
      ]
    },
    {
      type: 'input',
      name: 'prompt',
      message: 'Descreva o vídeo que deseja gerar:',
      validate: (input) => input.length > 0 ? true : 'Por favor, descreva o vídeo.'
    },
    {
      type: 'list',
      name: 'duration',
      message: 'Duração:',
      choices: ['3s', '4s', '5s', '10s'],
      default: '4s'
    },
    {
      type: 'input',
      name: 'filename',
      message: 'Nome do arquivo (sem extensão):',
      default: 'video'
    }
  ]);

  try {
    console.log(chalk.yellow('\n⏳ Gerando vídeo...'));

    let videoPath;
    if (answers.api === 'runway') {
      videoPath = await generateWithRunway(answers.prompt, answers.duration);
    } else {
      videoPath = await generateWithPika(answers.prompt, answers.duration);
    }

    console.log(chalk.green(`\n✅ Vídeo gerado com sucesso!`));
    console.log(chalk.cyan(`📁 Local: ${videoPath}`));
    
    return videoPath;
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro ao gerar vídeo: ${error.message}`));
    return null;
  }
}

async function generateWithRunway(prompt, duration) {
  const apiKey = process.env.RUNWAY_API_KEY;
  
  if (!apiKey) {
    throw new Error('RUNWAY_API_KEY não configurada no .env');
  }

  // Runway ML API (exemplo - a API real pode variar)
  const response = await axios.post(
    'https://api.runwayml.com/v1/generate',
    {
      prompt: prompt,
      duration: parseInt(duration),
      model: 'gen-2'
    },
    {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    }
  );

  // Download do vídeo
  return await downloadVideo(response.data.video_url, 'runway-video');
}

async function generateWithPika(prompt, duration) {
  const apiKey = process.env.PIKA_API_KEY;
  
  if (!apiKey) {
    throw new Error('PIKA_API_KEY não configurada no .env');
  }

  // Pika Labs API (exemplo)
  const response = await axios.post(
    'https://api.pika.art/v1/generate',
    {
      prompt: prompt,
      duration: duration,
      model: 'pika-1.0'
    },
    {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    }
  );

  // Download do vídeo
  return await downloadVideo(response.data.video_url, 'pika-video');
}

async function downloadVideo(url, filename) {
  await fs.ensureDir(OUTPUT_DIR);
  
  const outputPath = path.join(OUTPUT_DIR, `${filename}.mp4`);
  
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

module.exports = generateVideo;

// Execução direta
if (require.main === module) {
  generateVideo().then(() => process.exit(0));
}
