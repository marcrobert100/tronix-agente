#!/usr/bin/env node

/**
 * Criar Vídeo 3D de Basquete Simples
 */

const chalk = require('chalk');
const fs = require('fs-extra');
const path = require('path');
const { exec } = require('child_process');

const VIDEOS_DIR = path.join(__dirname, '..', 'videos');

async function create3DBasketball() {
  console.log(chalk.blue.bold('\n🏀 Criando Vídeo 3D de Basquete\n'));

  try {
    await fs.ensureDir(VIDEOS_DIR);
    
    const videoPath = path.join(VIDEOS_DIR, 'basketball-3d-simple.mp4');
    
    console.log(chalk.yellow('Criando vídeo 3D com efeitos...'));
    
    // Comando FFmpeg simplificado e corrigido
    const command = `ffmpeg -f lavfi -i color=c=darkblue:s=1920x1080:d=5 -f lavfi -i color=c=orange:s=100x100:d=5 -filter_complex "[0:v]drawbox=x=0:y=800:w=1920:h=280:color=brown:t=fill[ground];[ground]drawbox=x=860:y=600:w=200:h=200:color=gray:t=fill[hoop];[1:v]scale=100:100[ball];[hoop][ball]overlay=910:500:enable='between(t,0,5)'[final]" -map "[final]" -c:v libx264 -pix_fmt yuv420p -r 25 "${videoPath}" -y`;
    
    return new Promise((resolve, reject) => {
      exec(command, (error, stdout, stderr) => {
        if (error) {
          console.log(chalk.red(`Erro: ${error.message}`));
          reject(error);
        } else {
          console.log(chalk.green(`\n✅ Vídeo 3D criado com sucesso!`));
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

module.exports = create3DBasketball;

// Execução direta
if (require.main === module) {
  create3DBasketball().then(() => process.exit(0));
}
