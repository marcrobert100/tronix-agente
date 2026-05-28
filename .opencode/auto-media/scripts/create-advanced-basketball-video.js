#!/usr/bin/env node

/**
 * Criar Vídeo Avançado de Basquete
 * 
 * Cria um vídeo com animação de basquete mais elaborada usando FFmpeg
 */

const chalk = require('chalk');
const fs = require('fs-extra');
const path = require('path');
const { exec } = require('child_process');
require('dotenv').config();

const VIDEOS_DIR = path.join(__dirname, '..', 'videos');

async function createAdvancedVideo() {
  console.log(chalk.blue.bold('\n🏀 Criando Vídeo Avançado de Basquete\n'));

  try {
    await fs.ensureDir(VIDEOS_DIR);
    
    const videoPath = path.join(VIDEOS_DIR, 'basketball-dunk-advanced.mp4');
    
    console.log(chalk.yellow('Criando vídeo com animação avançada...'));
    
    // Criar um vídeo com animação de bola caindo (simulando enterrada)
    // Cenário: quadra de basquete com bola e cesta
    const command = `ffmpeg -f lavfi -i color=c=darkblue:s=640x480:d=5 -f lavfi -i color=c=orange:s=60x60:d=5 -filter_complex "[0:v]drawbox=x=0:y=380:w=640:h=100:color=brown:t=fill[base];[base]drawbox=x=280:y=380:w=80:h=100:color=gray:t=fill[hoop];[1:v]scale=60:60[ball];[hoop][ball]overlay=290:100:enable='between(t,0,1)'[step1];[step1][ball]overlay=290:150:enable='between(t,1,2)'[step2];[step2][ball]overlay=290:200:enable='between(t,2,3)'[step3];[step3][ball]overlay=290:250:enable='between(t,3,4)'[step4];[step4][ball]overlay=290:300:enable='between(t,4,5)'[final]" -map "[final]" -c:v libx264 -pix_fmt yuv420p "${videoPath}" -y`;
    
    return new Promise((resolve, reject) => {
      exec(command, (error, stdout, stderr) => {
        if (error) {
          console.log(chalk.red(`Erro: ${error.message}`));
          // Criar vídeo simples como fallback
          createFallbackVideo().then(resolve);
        } else {
          console.log(chalk.green(`\n✅ Vídeo avançado criado com sucesso!`));
          console.log(chalk.cyan(`📁 Local: ${videoPath}`));
          resolve(videoPath);
        }
      });
    });
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro: ${error.message}`));
    return null;
  }
}

async function createFallbackVideo() {
  console.log(chalk.yellow('Criando vídeo simples como fallback...'));
  
  const videoPath = path.join(VIDEOS_DIR, 'basketball-dunk-simple.mp4');
  
  const command = `ffmpeg -f lavfi -i color=c=darkblue:s=640x480:d=5 -f lavfi -i color=c=orange:s=60x60:d=5 -filter_complex "[0:v]drawbox=x=0:y=380:w=640:h=100:color=brown:t=fill[base];[base]drawbox=x=280:y=380:w=80:h=100:color=gray:t=fill[hoop];[1:v]scale=60:60[ball];[hoop][ball]overlay=290:100:enable='between(t,0,5)'[final]" -map "[final]" -c:v libx264 -pix_fmt yuv420p "${videoPath}" -y`;
  
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.log(chalk.red(`Erro no fallback: ${error.message}`));
        reject(error);
      } else {
        console.log(chalk.green(`\n✅ Vídeo simples criado com sucesso!`));
        console.log(chalk.cyan(`📁 Local: ${videoPath}`));
        resolve(videoPath);
      }
    });
  });
}

module.exports = createAdvancedVideo;

// Execução direta
if (require.main === module) {
  createAdvancedVideo().then(() => process.exit(0));
}
