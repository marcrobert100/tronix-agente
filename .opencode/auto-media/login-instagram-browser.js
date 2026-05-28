#!/usr/bin/env node

const chalk = require('chalk');
const puppeteer = require('puppeteer');
require('dotenv').config();

console.log(chalk.blue.bold('\n🌐 Login Instagram via Browser Automation\n'));

async function loginInstagramViaBrowser() {
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
    
    // Usar Google Chrome instalado no sistema
    const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
    
    browser = await puppeteer.launch({
      headless: false, // Modo visível para debug
      slowMo: 100, // Desacelerar para ver ações
      executablePath: chromePath, // Usar Chrome instalado
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process'
      ]
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    
    console.log(chalk.yellow('\n2. Acessando Instagram...'));
    await page.goto('https://www.instagram.com/accounts/login/', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    console.log(chalk.yellow('\n3. Preenchendo formulário de login...'));
    
    // Esperar campo de email aparecer (Instagram mudou para email em vez de username)
    await page.waitForSelector('input[name="email"]', { timeout: 10000 });
    
    // Preencher email (usando username como email)
    await page.type('input[name="email"]', username, { delay: 50 });
    
    // Preencher senha
    await page.type('input[name="pass"]', password, { delay: 50 });
    
    console.log(chalk.yellow('\n4. Clicando em login...'));
    
    // Clicar botão de login
    await page.click('button[type="submit"]');
    
    // Esperar navegação
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 30000 });
    
    console.log(chalk.yellow('\n5. Verificando login...'));
    
    // Verificar se login foi bem-sucedido
    const currentUrl = page.url();
    
    if (currentUrl.includes('/accounts/login/')) {
      // Login pode ter falhado, verificar se há erro
      const errorElement = await page.$('#slfErrorAlert');
      if (errorElement) {
        const errorText = await page.evaluate(el => el.textContent, errorElement);
        console.log(chalk.red(`❌ Erro no login: ${errorText}`));
        return null;
      }
    }
    
    // Verificar se redirecionou para feed
    if (currentUrl.includes('instagram.com') && !currentUrl.includes('login')) {
      console.log(chalk.green('\n✅ Login realizado com sucesso!'));
      
      // Capturar informações do perfil
      console.log(chalk.yellow('\n6. Capturando informações do perfil...'));
      
      // Ir para perfil
      await page.goto(`https://www.instagram.com/${username}/`, { 
        waitUntil: 'networkidle2',
        timeout: 15000 
      });
      
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
      
      // Salvar cookies para uso futuro
      const cookies = await page.cookies();
      const fs = require('fs-extra');
      const path = require('path');
      
      const cookiesPath = path.join(__dirname, 'instagram_cookies.json');
      await fs.writeJson(cookiesPath, cookies, { spaces: 2 });
      console.log(chalk.green(`\n✅ Cookies salvos em: ${cookiesPath}`));
      
      // Manter navegador aberto por 10 segundos para visualizar
      console.log(chalk.yellow('\n⏳ Navegador fechará em 10 segundos...'));
      await new Promise(resolve => setTimeout(resolve, 10000));
      
      await browser.close();
      console.log(chalk.green('\n🎉 Login via browser concluído com sucesso!'));
      
      return { success: true, profileInfo };
      
    } else {
      console.log(chalk.red('❌ Login falhou - URL não mudou'));
      console.log(chalk.cyan(`URL atual: ${currentUrl}`));
      
      // Capturar screenshot para debug
      await page.screenshot({ path: 'login-error.png' });
      console.log(chalk.yellow('📸 Screenshot de erro salvo: login-error.png'));
      
      await browser.close();
      return null;
    }
    
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro: ${error.message}`));
    
    if (browser) {
      // Capturar screenshot em caso de erro
      try {
        await page.screenshot({ path: 'login-error-exception.png' });
        console.log(chalk.yellow('📸 Screenshot de exceção salvo: login-error-exception.png'));
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
  loginInstagramViaBrowser().then(() => {
    process.exit(0);
  }).catch(error => {
    console.log(chalk.red(`💥 Erro inesperado: ${error.message}`));
    process.exit(1);
  });
}

module.exports = loginInstagramViaBrowser;