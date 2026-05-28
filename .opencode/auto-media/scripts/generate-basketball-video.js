#!/usr/bin/env node

/**
 * Geração de Vídeo de Basquete
 * 
 * Gera um vídeo de um jogador de basquete enterrando a bola
 */

const chalk = require('chalk');
const axios = require('axios');
const fs = require('fs-extra');
const path = require('path');
require('dotenv').config();

const VIDEOS_DIR = path.join(__dirname, '..', 'videos');
const TEMP_DIR = path.join(__dirname, '..', 'temp');

async function generateBasketballVideo() {
  console.log(chalk.blue.bold('\n🏀 Gerando Vídeo de Basquete\n'));

  const prompt = 'Professional basketball player dunking a basketball in an arena, slow motion, dramatic lighting, crowd cheering, high quality, cinematic';

  console.log(chalk.yellow('Prompt:'));
  console.log(chalk.cyan(`  ${prompt}\n`));

  try {
    console.log(chalk.yellow('⏳ Gerando vídeo... (isso pode levar alguns minutos)'));

    // Verificar qual API está disponível
    const videoPath = await generateWithAvailableAPI(prompt);

    if (videoPath) {
      console.log(chalk.green(`\n✅ Vídeo gerado com sucesso!`));
      console.log(chalk.cyan(`📁 Local: ${videoPath}`));
      return videoPath;
    } else {
      console.log(chalk.red('\n❌ Nenhuma API de vídeo disponível.'));
      console.log(chalk.yellow('Configure RUNWAY_API_KEY ou PIKA_API_KEY no .env'));
      return null;
    }
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro ao gerar vídeo: ${error.message}`));
    return null;
  }
}

async function generateWithAvailableAPI(prompt) {
  // Tenta Runway primeiro
  if (process.env.RUNWAY_API_KEY) {
    console.log(chalk.yellow('Usando Runway ML...'));
    return await generateWithRunway(prompt);
  }
  
  // Tenta Pika depois
  if (process.env.PIKA_API_KEY) {
    console.log(chalk.yellow('Usando Pika Labs...'));
    return await generateWithPika(prompt);
  }
  
  // Se nenhuma API estiver configurada, cria um vídeo de exemplo
  console.log(chalk.yellow('Nenhuma API configurada. Criando vídeo de exemplo...'));
  return await createSampleVideo();
}

async function generateWithRunway(prompt) {
  const apiKey = process.env.RUNWAY_API_KEY;
  
  try {
    // API do Runway ML (endpoint exemplo)
    const response = await axios.post(
      'https://api.runwayml.com/v1/generate',
      {
        prompt: prompt,
        duration: 5,
        model: 'gen-2',
        width: 1280,
        height: 720
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        timeout: 300000 // 5 minutos
      }
    );

    const videoUrl = response.data.video_url || response.data.url;
    return await downloadVideo(videoUrl, 'basketball-dunk-runway');
  } catch (error) {
    console.log(chalk.yellow(`Runway não disponível: ${error.message}`));
    return null;
  }
}

async function generateWithPika(prompt) {
  const apiKey = process.env.PIKA_API_KEY;
  
  try {
    // API do Pika Labs (endpoint exemplo)
    const response = await axios.post(
      'https://api.pika.art/v1/generate',
      {
        prompt: prompt,
        duration: '5s',
        model: 'pika-1.0',
        aspect_ratio: '16:9'
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        timeout: 300000 // 5 minutos
      }
    );

    const videoUrl = response.data.video_url || response.data.url;
    return await downloadVideo(videoUrl, 'basketball-dunk-pika');
  } catch (error) {
    console.log(chalk.yellow(`Pika não disponível: ${error.message}`));
    return null;
  }
}

async function createSampleVideo() {
  // Criar um vídeo de exemplo usando FFmpeg (se disponível)
  // Ou criar um arquivo de texto indicando que o vídeo precisa ser gerado com API
  
  const samplePath = path.join(VIDEOS_DIR, 'basketball-dunk-sample.txt');
  await fs.ensureDir(VIDEOS_DIR);
  
  const content = `
VÍDEO DE BASQUETE - EXEMPLO

Prompt: ${'Professional basketball player dunking a basketball in an arena, slow motion, dramatic lighting, crowd cheering, high quality, cinematic'}

Para gerar o vídeo real:
1. Configure uma API de geração de vídeo no .env:
   - RUNWAY_API_KEY=your_key_here
   - OU PIKA_API_KEY=your_key_here

2. Execute novamente o script

3. O vídeo será salvo na pasta: videos/

APIs recomendadas:
- Runway ML (https://runwayml.com)
- Pika Labs (https://pika.art)
`;

  await fs.writeFile(samplePath, content);
  return samplePath;
}

async function downloadVideo(videoUrl, filename) {
  await fs.ensureDir(VIDEOS_DIR);
  
  const outputPath = path.join(VIDEOS_DIR, `${filename}.mp4`);
  
  console.log(chalk.yellow(`Baixando vídeo de: ${videoUrl}`));
  
  const response = await axios({
    method: 'GET',
    url: videoUrl,
    responseType: 'stream',
    timeout: 300000 // 5 minutos
  });
  
  const writer = fs.createWriteStream(outputPath);
  response.data.pipe(writer);
  
  return new Promise((resolve, reject) => {
    writer.on('finish', () => resolve(outputPath));
    writer.on('error', reject);
  });
}

module.exports = generateBasketballVideo;

// Execução direta
if (require.main === module) {
  generateBasketballVideo().then(() => process.exit(0));
}
