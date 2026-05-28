#!/usr/bin/env node

/**
 * Criar Vídeo de Basquete
 * 
 * Cria um vídeo de exemplo de basquete usando FFmpeg ou gera instruções
 */

const chalk = require('chalk');
const fs = require('fs-extra');
const path = require('path');
const { exec } = require('child_process');
require('dotenv').config();

const VIDEOS_DIR = path.join(__dirname, '..', 'videos');
const OUTPUT_DIR = path.join(__dirname, '..', 'output');

async function createBasketballVideo() {
  console.log(chalk.blue.bold('\n🏀 Criando Vídeo de Basquete\n'));

  try {
    // Verificar se FFmpeg está instalado
    const ffmpegAvailable = await checkFFmpeg();
    
    if (ffmpegAvailable) {
      console.log(chalk.yellow('FFmpeg detectado. Criando vídeo animado...'));
      const videoPath = await createAnimatedVideo();
      console.log(chalk.green(`\n✅ Vídeo criado com sucesso!`));
      console.log(chalk.cyan(`📁 Local: ${videoPath}`));
    } else {
      console.log(chalk.yellow('FFmpeg não detectado. Criando arquivo de instruções...'));
      const instructionsPath = await createInstructions();
      console.log(chalk.green(`\n✅ Arquivo de instruções criado!`));
      console.log(chalk.cyan(`📁 Local: ${instructionsPath}`));
    }
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro: ${error.message}`));
  }
}

async function checkFFmpeg() {
  return new Promise((resolve) => {
    exec('ffmpeg -version', (error) => {
      resolve(!error);
    });
  });
}

async function createAnimatedVideo() {
  await fs.ensureDir(VIDEOS_DIR);
  
  const videoPath = path.join(VIDEOS_DIR, 'basketball-dunk-animated.mp4');
  
  // Criar um vídeo simples com FFmpeg
  // Este comando cria um vídeo de 5 segundos com texto animado
  const command = `ffmpeg -f lavfi -i color=c=blue:s=640x480:d=5 -vf "drawtext=text='BASKETBALL DUNK':fontcolor=white:fontsize=48:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2,drawtext=text='Player dunking the ball':fontcolor=yellow:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2+50" -c:v libx264 -pix_fmt yuv420p "${videoPath}"`;
  
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.log(chalk.yellow(`FFmpeg error: ${error.message}`));
        // Criar arquivo de instruções como fallback
        createInstructions().then(resolve);
      } else {
        resolve(videoPath);
      }
    });
  });
}

async function createInstructions() {
  await fs.ensureDir(VIDEOS_DIR);
  
  const instructionsPath = path.join(VIDEOS_DIR, 'basketball-dunk-instructions.txt');
  
  const content = `
╔════════════════════════════════════════════════════════════╗
║           VÍDEO DE BASQUETE - INSTRUÇÕES                   ║
╚════════════════════════════════════════════════════════════╝

PROMPT DE GERAÇÃO:
"Professional basketball player dunking a basketball in an arena, 
slow motion, dramatic lighting, crowd cheering, high quality, cinematic"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PARA GERAR O VÍDEO REAL:

1. Configure uma API de geração de vídeo no arquivo .env:

   # Runway ML (recomendado)
   RUNWAY_API_KEY=your_runway_api_key_here
   
   # OU Pika Labs
   PIKA_API_KEY=your_pika_api_key_here

2. Obtenha uma chave de API:
   - Runway: https://runwayml.com (plano gratuito disponível)
   - Pika: https://pika.art (plano gratuito disponível)

3. Execute o script de geração:
   node scripts/generate-basketball-video.js

4. O vídeo será salvo na pasta: videos/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ALTERNATIVAS:

A. Use serviços online gratuitos:
   - Runway ML (https://runwayml.com)
   - Pika Labs (https://pika.art)
   - Leonardo AI (https://leonardo.ai)
   - Kaiber (https://kaiber.ai)

B. Use prompts similares:
   - "Basketball player jumping for dunk, arena lights"
   - "Slam dunk in basketball court, dramatic angle"
   - "Athlete dunking basketball, crowd cheering"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ARQUIVOS GERADOS:
- videos/basketball-dunk-instructions.txt (este arquivo)
- videos/basketball-dunk-sample.txt (exemplo anterior)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Data de criação: ${new Date().toLocaleString()}
`;
  
  await fs.writeFile(instructionsPath, content);
  return instructionsPath;
}

module.exports = createBasketballVideo;

// Execução direta
if (require.main === module) {
  createBasketballVideo().then(() => process.exit(0));
}
