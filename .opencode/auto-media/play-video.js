#!/usr/bin/env node

/**
 * Reproduzir Vídeo de Basquete
 */

const chalk = require('chalk');
const { exec } = require('child_process');
const path = require('path');

const videoPath = path.join(__dirname, 'videos', 'basketball-3d-simple-advanced.mp4');

console.log(chalk.blue.bold('\n🏀 Reproduzindo Vídeo de Basquete\n'));

console.log(chalk.yellow(`Arquivo: ${videoPath}`));

// Tentar abrir o vídeo com o player padrão do sistema
let command;
if (process.platform === 'win32') {
  command = `start "" "${videoPath}"`;
} else if (process.platform === 'darwin') {
  command = `open "${videoPath}"`;
} else {
  command = `xdg-open "${videoPath}"`;
}

exec(command, (error) => {
  if (error) {
    console.log(chalk.red(`\n❌ Erro ao abrir o vídeo: ${error.message}`));
    console.log(chalk.yellow(`\n📁 O vídeo está localizado em:`));
    console.log(chalk.cyan(`   ${videoPath}`));
    console.log(chalk.yellow(`\n🎯 Abra manualmente com seu player de vídeo favorito.`));
  } else {
    console.log(chalk.green(`\n✅ Vídeo aberto com sucesso!`));
  }
});
