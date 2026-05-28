#!/usr/bin/env node

const chalk = require('chalk');
const puppeteer = require('puppeteer');
require('dotenv').config();

console.log(chalk.blue.bold('\n🔍 Inspecionando Botão de Login Instagram\n'));

async function inspectLoginButton() {
  let browser;
  try {
    console.log(chalk.yellow('\n1. Iniciando Google Chrome...'));
    
    const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
    
    browser = await puppeteer.launch({
      headless: false,
      slowMo: 200,
      executablePath: chromePath,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    
    console.log(chalk.yellow('\n2. Acessando Instagram...'));
    await page.goto('https://www.instagram.com/', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    await page.waitForTimeout(3000);
    
    console.log(chalk.yellow('\n3. Preenchendo formulário...'));
    
    // Preencher email e senha
    await page.type('input[name="email"]', 'test@example.com', { delay: 50 });
    await page.type('input[name="pass"]', 'testpassword', { delay: 50 });
    
    console.log(chalk.yellow('\n4. Inspecionando botões...'));
    
    // Inspecionar todos os botões
    const buttonsInfo = await page.evaluate(() => {
      const buttons = document.querySelectorAll('button');
      const info = [];
      
      buttons.forEach((btn, i) => {
        info.push({
          index: i,
          type: btn.type,
          text: btn.textContent.trim().substring(0, 100),
          className: btn.className,
          id: btn.id,
          disabled: btn.disabled,
          innerHTML: btn.innerHTML.substring(0, 200)
        });
      });
      
      return info;
    });
    
    console.log(chalk.cyan('\n🔘 Botões encontrados:'));
    buttonsInfo.forEach(btn => {
      console.log(chalk.cyan(`\n  Botão ${btn.index}:`));
      console.log(chalk.cyan(`    Type: ${btn.type}`));
      console.log(chalk.cyan(`    Text: "${btn.text}"`));
      console.log(chalk.cyan(`    Class: ${btn.className}`));
      console.log(chalk.cyan(`    ID: ${btn.id}`));
      console.log(chalk.cyan(`    Disabled: ${btn.disabled}`));
    });
    
    // Inspecionar elementos com texto "Log in" ou "Entrar"
    const loginElements = await page.evaluate(() => {
      const elements = document.querySelectorAll('*');
      const loginElements = [];
      
      elements.forEach((el, i) => {
        const text = el.textContent.trim().toLowerCase();
        if (text.includes('log in') || text.includes('entrar') || text.includes('login')) {
          loginElements.push({
            tag: el.tagName,
            text: text.substring(0, 100),
            className: el.className,
            id: el.id
          });
        }
      });
      
      return loginElements;
    });
    
    console.log(chalk.cyan('\n📝 Elementos com texto de login:'));
    loginElements.forEach(el => {
      console.log(chalk.cyan(`  <${el.tag}> "${el.text}"`));
    });
    
    // Capturar screenshot
    await page.screenshot({ path: 'inspect-login.png', fullPage: true });
    console.log(chalk.green('\n✅ Screenshot salvo: inspect-login.png'));
    
    console.log(chalk.yellow('\n5. Mantendo navegador aberto para inspeção...'));
    console.log(chalk.yellow('   (Feche manualmente quando terminar)'));
    
    await new Promise(resolve => setTimeout(resolve, 30000));
    
    await browser.close();
    console.log(chalk.green('\n🔍 Inspeção concluída!'));
    
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro: ${error.message}`));
    if (browser) await browser.close();
  }
}

inspectLoginButton().then(() => {
  process.exit(0);
}).catch(error => {
  console.log(chalk.red(`💥 Erro inesperado: ${error.message}`));
  process.exit(1);
});