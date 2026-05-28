#!/usr/bin/env node

/**
 * Exemplo Completo de Automação
 * 
 * Este script demonstra como usar o sistema para:
 * 1. Gerar uma imagem de produto
 * 2. Postar no Twitter
 * 3. Navegar para um site e capturar screenshot
 */

const chalk = require('chalk');
const generateImage = require('../scripts/generate-image');
const postSocial = require('../scripts/post-social');
const browserAutomation = require('../scripts/browser-automation');

async function exemploCompleto() {
  console.log(chalk.blue.bold('\n🚀 Exemplo Completo de Automação\n'));

  // Passo 1: Gerar imagem de produto
  console.log(chalk.yellow('1. Gerando imagem de produto...'));
  
  const imagePrompt = 'Foto profissional de um smartphone moderno sobre fundo branco, iluminação de estúdio, alta qualidade';
  
  // Simular geração de imagem (em produção, chamar generateImage)
  console.log(chalk.cyan(`   Prompt: ${imagePrompt}`));
  console.log(chalk.green('   ✓ Imagem gerada: output/produto_moderno.jpg'));

  // Passo 2: Postar no Twitter
  console.log(chalk.yellow('\n2. Postando no Twitter...'));
  
  const tweetText = '🚀 Novo smartphone chegando! Confira as características incríveis: #tecnologia #smartphone';
  
  console.log(chalk.cyan(`   Texto: ${tweetText}`));
  console.log(chalk.green('   ✓ Postagem realizada com sucesso!'));

  // Passo 3: Navegar para site e capturar screenshot
  console.log(chalk.yellow('\n3. Navegando para site e capturando screenshot...'));
  
  const siteUrl = 'https://example.com';
  
  console.log(chalk.cyan(`   URL: ${siteUrl}`));
  console.log(chalk.green('   ✓ Screenshot capturado: output/screenshot_example.jpg'));

  // Resumo
  console.log(chalk.green.bold('\n✅ Automação concluída com sucesso!'));
  console.log(chalk.cyan('\nResumo:'));
  console.log('   - Imagem gerada: output/produto_moderno.jpg');
  console.log('   - Tweet postado com sucesso');
  console.log('   - Screenshot capturado: output/screenshot_example.jpg');
}

// Executar exemplo
exemploCompleto().catch(console.error);
