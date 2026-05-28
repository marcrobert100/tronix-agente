#!/usr/bin/env node

const chalk = require('chalk');
const puppeteer = require('puppeteer');
const fs = require('fs-extra');
const path = require('path');
require('dotenv').config();

console.log(chalk.blue.bold('\n🌐 Login Instagram v2 - Usando elementos DIV\n'));

async function loginInstagramV2() {
  const username = process.env.INSTAGRAM_USERNAME;
  const password = process.env.INSTAGRAM_PASSWORD;
  
  if (!username || !password) {
    console.log(chalk.red('❌ Credenciais não encontradas no .env'));
    return null;
  }
  
  console.log(chalk.green(`✓ Usuário: ${username}`));
  console.log(chalk.green('✓ Senha: configurada'));
  
  let browser;
  try {
    console.log(chalk.yellow('\n1. Iniciando Google Chrome...'));
    
    const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
    
    browser = await puppeteer.launch({
      headless: false,
      slowMo: 100,
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
    
    console.log(chalk.yellow('\n3. Preenchendo formulário de login...'));
    
    // Esperar campo de email
    await page.waitForSelector('input[name="email"]', { timeout: 10000 });
    
    // Preencher email e senha
    await page.type('input[name="email"]', username, { delay: 50 });
    await page.type('input[name="pass"]', password, { delay: 50 });
    
    console.log(chalk.yellow('\n4. Clicando em "Entrar"...'));
    
    // Tentar clicar no botão usando texto
    try {
      // Método 1: Clicar em elemento com texto "Entrar"
      await page.evaluate(() => {
        const elements = document.querySelectorAll('*');
        for (const el of elements) {
          if (el.textContent.trim().toLowerCase() === 'entrar') {
            el.click();
            return true;
          }
        }
        return false;
      });
      
      console.log(chalk.green('✓ Clique executado via JavaScript'));
      
    } catch (error) {
      console.log(chalk.yellow(`⚠️  Método 1 falhou: ${error.message}`));
      
      // Método 2: Clicar no formulário
      try {
        await page.click('form');
        console.log(chalk.green('✓ Clique no formulário'));
      } catch (error2) {
        console.log(chalk.yellow(`⚠️  Método 2 falhou: ${error2.message}`));
      }
    }
    
    console.log(chalk.yellow('\n5. Aguardando redirecionamento...'));
    
    // Esperar navegação
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 30000 });
    
    console.log(chalk.yellow('\n6. Verificando login...'));
    
    const currentUrl = page.url();
    console.log(chalk.cyan(`🌐 URL atual: ${currentUrl}`));
    
    if (currentUrl.includes('instagram.com') && !currentUrl.includes('accounts/login')) {
      console.log(chalk.green('\n✅ Login realizado com sucesso!'));
      
      // Capturar informações do perfil
      console.log(chalk.yellow('\n7. Capturando informações do perfil...'));
      
      // Ir para perfil
      await page.goto(`https://www.instagram.com/${username}/`, { 
        waitUntil: 'networkidle2',
        timeout: 15000 
      });
      
      await page.waitForTimeout(3000);
      
      // Capturar informações
      const profileInfo = await page.evaluate(() => {
        const info = {};
        
        // Nome
        const nameElement = document.querySelector('h1');
        if (nameElement) info.name = nameElement.textContent;
        
        // Bio
        const bioElement = document.querySelector('h1 + div');
        if (bioElement) info.bio = bioElement.textContent;
        
        // Estatísticas
        const stats = document.querySelectorAll('header section ul li');
        if (stats.length >= 3) {
          info.posts = stats[0].textContent;
          info.followers = stats[1].textContent;
          info.following = stats[2].textContent;
        }
        
        return info;
      });
      
      console.log(chalk.cyan(`👤 Nome: ${profileInfo.name || 'N/A'}`));
      console.log(chalk.cyan(`👥 Seguidores: ${profileInfo.followers || 'N/A'}`));
      console.log(chalk.cyan(`👤 Seguindo: ${profileInfo.following || 'N/A'}`));
      console.log(chalk.cyan(`📝 Posts: ${profileInfo.posts || 'N/A'}`));
      
      // Salvar cookies
      const cookies = await page.cookies();
      const cookiesPath = path.join(__dirname, 'instagram_cookies.json');
      await fs.writeJson(cookiesPath, cookies, { spaces: 2 });
      console.log(chalk.green(`\n✅ Cookies salvos em: ${cookiesPath}`));
      
      // Capturar screenshot do perfil
      await page.screenshot({ path: 'profile-screenshot.png', fullPage: true });
      console.log(chalk.green('✅ Screenshot do perfil salvo: profile-screenshot.png'));
      
      console.log(chalk.yellow('\n⏳ Mantendo navegador aberto por 15 segundos...'));
      await new Promise(resolve => setTimeout(resolve, 15000));
      
      await browser.close();
      console.log(chalk.green('\n🎉 Login via browser concluído com sucesso!'));
      
      return { success: true, profileInfo };
      
    } else {
      console.log(chalk.red('❌ Login falhou - URL não mudou'));
      console.log(chalk.cyan(`URL atual: ${currentUrl}`));
      
      // Capturar screenshot para debug
      await page.screenshot({ path: 'login-error-v2.png' });
      console.log(chalk.yellow('📸 Screenshot de erro salvo: login-error-v2.png'));
      
      await browser.close();
      return null;
    }
    
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro: ${error.message}`));
    
    if (browser) {
      try {
        await page.screenshot({ path: 'login-error-exception-v2.png' });
        console.log(chalk.yellow('📸 Screenshot de exceção salvo: login-error-exception-v2.png'));
      } catch (screenshotError) {
        console.log(chalk.red(`Erro ao capturar screenshot: ${screenshotError.message}`));
      }
      
      await browser.close();
    }
    
    return null;
  }
}

// Executar se chamado diretamente
if (require.main === module) {
  loginInstagramV2().then(() => {
    process.exit(0);
  }).catch(error => {
    console.log(chalk.red(`💥 Erro inesperado: ${error.message}`));
    process.exit(1);
  });
}

module.exports = loginInstagramV2;