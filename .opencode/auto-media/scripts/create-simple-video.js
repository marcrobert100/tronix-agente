#!/usr/bin/env node

/**
 * Criar Vídeo Simples de Basquete
 * 
 * Cria um vídeo simples com animação de basquete usando FFmpeg
 */

const chalk = require('chalk');
const fs = require('fs-extra');
const path = require('path');
const { exec } = require('child_process');
require('dotenv').config();

const VIDEOS_DIR = path.join(__dirname, '..', 'videos');

async function createSimpleVideo() {
  console.log(chalk.blue.bold('\n🏀 Criando Vídeo Simples de Basquete\n'));

  try {
    await fs.ensureDir(VIDEOS_DIR);
    
    const videoPath = path.join(VIDEOS_DIR, 'basketball-dunk.mp4');
    
    console.log(chalk.yellow('Criando vídeo com animação de basquete...'));
    
    // Criar um vídeo simples com círculos (bola) e animação
    const command = `ffmpeg -f lavfi -i color=c=darkblue:s=640x480:d=5 -f lavfi -i color=c=orange:s=50x50:d=5 -filter_complex "[0:v][1:v] overlay=295:100:enable='between(t,0,5)'[out]" -map "[out]" -c:v libx264 -pix_fmt yuv420p "${videoPath}" -y`;
    
    return new Promise((resolve, reject) => {
      exec(command, (error, stdout, stderr) => {
        if (error) {
          console.log(chalk.red(`Erro: ${error.message}`));
          reject(error);
        } else {
          console.log(chalk.green(`\n✅ Vídeo criado com sucesso!`));
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

module.exports = createSimpleVideo;

// Execução direta
if (require.main === module) {
  createSimpleVideo().then(() => process.exit(0));
}
