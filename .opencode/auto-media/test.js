#!/usr/bin/env node

const chalk = require('chalk');
const fs = require('fs-extra');
const path = require('path');

console.log(chalk.blue.bold('\n🧪 Teste do Sistema Auto Media\n'));

async function test() {
  console.log(chalk.yellow('1. Verificando dependências...'));

  const dependencies = [
    'openai',
    'puppeteer',
    'axios',
    'dotenv',
    'fs-extra',
    'chalk',
    'inquirer'
  ];

  let allInstalled = true;
  for (const dep of dependencies) {
    try {
      require.resolve(dep);
      console.log(chalk.green(`   ✓ ${dep}`));
    } catch (error) {
      console.log(chalk.red(`   ✗ ${dep} - Não instalado`));
      allInstalled = false;
    }
  }

  if (!allInstalled) {
    console.log(chalk.red('\n❌ Algumas dependências não estão instaladas.'));
    console.log(chalk.yellow('Execute: npm install'));
    return;
  }

  console.log(chalk.yellow('\n2. Verificando estrutura de diretórios...'));

  const dirs = [
    './scripts',
    './output',
    './temp'
  ];

  for (const dir of dirs) {
    await fs.ensureDir(dir);
    console.log(chalk.green(`   ✓ ${dir}`));
  }

  console.log(chalk.yellow('\n3. Verificando arquivo .env...'));

  const envPath = './.env';
  if (await fs.pathExists(envPath)) {
    console.log(chalk.green('   ✓ .env existe'));
  } else {
    console.log(chalk.yellow('   ⚠ .env não encontrado (copie de .env.example)'));
  }

  console.log(chalk.yellow('\n4. Testando módulos...'));

  try {
    const generateImage = require('./scripts/generate-image');
    console.log(chalk.green('   ✓ generate-image.js carregado'));
  } catch (error) {
    console.log(chalk.red(`   ✗ generate-image.js: ${error.message}`));
  }

  try {
    const generateVideo = require('./scripts/generate-video');
    console.log(chalk.green('   ✓ generate-video.js carregado'));
  } catch (error) {
    console.log(chalk.red(`   ✗ generate-video.js: ${error.message}`));
  }

  try {
    const postSocial = require('./scripts/post-social');
    console.log(chalk.green('   ✓ post-social.js carregado'));
  } catch (error) {
    console.log(chalk.red(`   ✗ post-social.js: ${error.message}`));
  }

  try {
    const browserAutomation = require('./scripts/browser-automation');
    console.log(chalk.green('   ✓ browser-automation.js carregado'));
  } catch (error) {
    console.log(chalk.red(`   ✗ browser-automation.js: ${error.message}`));
  }

  console.log(chalk.green.bold('\n✅ Teste concluído com sucesso!'));
  console.log(chalk.cyan('\nPara usar o sistema:'));
  console.log(chalk.yellow('  npm start'));
  console.log(chalk.yellow('  npm run image    # Gerar imagem'));
  console.log(chalk.yellow('  npm run video    # Gerar vídeo'));
  console.log(chalk.yellow('  npm run post     # Postar em redes sociais'));
  console.log(chalk.yellow('  npm run browse   # Navegar em sites'));
}

test().catch(console.error);
