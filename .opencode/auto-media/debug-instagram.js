#!/usr/bin/env node

const chalk = require('chalk');
const puppeteer = require('puppeteer');
const fs = require('fs-extra');
const path = require('path');
require('dotenv').config();

console.log(chalk.blue.bold('\n🔍 Debug Instagram - Verificando estrutura da página\n'));

async function debugInstagram() {
  const username = process.env.INSTAGRAM_USERNAME;
  const password = process.env.INSTAGRAM_PASSWORD;
  
  console.log(chalk.green(`✓ Usuário: ${username}`));
  console.log(chalk.green('✓ Senha: configurada'));
  
  let browser;
  try {
    console.log(chalk.yellow('\n1. Iniciando Google Chrome...'));
    
    const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
    
    browser = await puppeteer.launch({
      headless: false,
      slowMo: 200,
      executablePath: chromePath,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--window-size=1280,800'
      ]
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    
    console.log(chalk.yellow('\n2. Acessando Instagram...'));
    await page.goto('https://www.instagram.com/', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    // Aguardar carregamento
    await page.waitForTimeout(3000);
    
    console.log(chalk.yellow('\n3. Capturando screenshot da página inicial...'));
    await page.screenshot({ path: 'debug-instagram-home.png', fullPage: true });
    console.log(chalk.green('✅ Screenshot salvo: debug-instagram-home.png'));
    
    console.log(chalk.yellow('\n4. Verificando elementos na página...'));
    
    // Listar todos os inputs
    const inputs = await page.evaluate(() => {
      const inputs = document.querySelectorAll('input');
      return Array.from(inputs).map(input => ({
        name: input.name,
        type: input.type,
        id: input.id,
        placeholder: input.placeholder,
        className: input.className
      }));
    });
    
    console.log(chalk.cyan('\n📝 Inputs encontrados:'));
    inputs.forEach((input, i) => {
      console.log(chalk.cyan(`  ${i + 1}. name="${input.name}" type="${input.type}" placeholder="${input.placeholder}"`));
    });
    
    // Listar botões
    const buttons = await page.evaluate(() => {
      const buttons = document.querySelectorAll('button');
      return Array.from(buttons).map(button => ({
        type: button.type,
        text: button.textContent.trim().substring(0, 50),
        className: button.className
      }));
    });
    
    console.log(chalk.cyan('\n🔘 Botões encontrados:'));
    buttons.forEach((button, i) => {
      console.log(chalk.cyan(`  ${i + 1}. type="${button.type}" text="${button.text}"`));
    });
    
    // Verificar se há link de cadastro
    const hasSignUpLink = await page.evaluate(() => {
      return document.body.innerHTML.includes('Cadastrar') || 
             document.body.innerHTML.includes('Sign up') ||
             document.body.innerHTML.includes('Não tem uma conta?');
    });
    
    if (hasSignUpLink) {
      console.log(chalk.yellow('\n⚠️  Parece que há link de cadastro na página'));
    }
    
    // Verificar URL atual
    const currentUrl = page.url();
    console.log(chalk.cyan(`\n🌐 URL atual: ${currentUrl}`));
    
    // Verificar título da página
    const title = await page.title();
    console.log(chalk.cyan(`📄 Título: ${title}`));
    
    console.log(chalk.yellow('\n5. Mantendo navegador aberto para inspeção...'));
    console.log(chalk.yellow('   (Feche manualmente quando terminar)'));
    
    // Manter navegador aberto por 30 segundos para inspeção
    await new Promise(resolve => setTimeout(resolve, 30000));
    
    await browser.close();
    console.log(chalk.green('\n🔍 Debug concluído!'));
    
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro: ${error.message}`));
    
    if (browser) {
      try {
        await page.screenshot({ path: 'debug-error.png' });
        console.log(chalk.yellow('📸 Screenshot de erro salvo: debug-error.png'));
      } catch (screenshotError) {
        console.log(chalk.red(`Erro ao capturar screenshot: ${screenshotError.message}`));
      }
      
      await browser.close();
    }
  }
}

debugInstagram().then(() => {
  process.exit(0);
}).catch(error => {
  console.log(chalk.red(`💥 Erro inesperado: ${error.message}`));
  process.exit(1);
});