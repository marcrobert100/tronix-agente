#!/usr/bin/env node

/**
 * Navegação Automatizada em Sites
 * 
 * Funcionalidades:
 * - Acessar sites
 * - Preencher formulários
 * - Clicar em elementos
 * - Capturar screenshots
 * - Extrair dados
 */

const chalk = require('chalk');
const inquirer = require('inquirer');
const puppeteer = require('puppeteer');
const fs = require('fs-extra');
const path = require('path');
require('dotenv').config();

const OUTPUT_DIR = process.env.OUTPUT_DIR || './output';
const HEADLESS = process.env.BROWSER_HEADLESS === 'true';
const SLOW_MO = parseInt(process.env.BROWSER_SLOW_MO) || 0;

async function browserAutomation() {
  console.log(chalk.blue('\n🌐 Automação de Navegação Web\n'));

  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'url',
      message: 'URL do site para acessar:',
      validate: (input) => input.startsWith('http') ? true : 'URL inválida.'
    },
    {
      type: 'list',
      name: 'action',
      message: 'O que deseja fazer?',
      choices: [
        { name: 'Apenas acessar e capturar screenshot', value: 'screenshot' },
        { name: 'Preencher formulário', value: 'form' },
        { name: 'Clicar em elemento', value: 'click' },
        { name: 'Extrair dados', value: 'extract' },
        { name: 'Executar tarefa personalizada', value: 'custom' }
      ]
    }
  ]);

  let browser;
  try {
    console.log(chalk.yellow('\n⏳ Iniciando navegador...'));

    browser = await puppeteer.launch({
      headless: HEADLESS,
      slowMo: SLOW_MO,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });

    console.log(chalk.yellow(`\n⏳ Acessando ${answers.url}...`));
    await page.goto(answers.url, { waitUntil: 'networkidle2' });

    let result;
    switch (answers.action) {
      case 'screenshot':
        result = await captureScreenshot(page);
        break;
      case 'form':
        result = await fillForm(page);
        break;
      case 'click':
        result = await clickElement(page);
        break;
      case 'extract':
        result = await extractData(page);
        break;
      case 'custom':
        result = await executeCustomTask(page);
        break;
    }

    console.log(chalk.green(`\n✅ Tarefa concluída!`));
    if (result) {
      console.log(chalk.cyan(`📁 Resultado: ${result}`));
    }

    await browser.close();
    return result;
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro: ${error.message}`));
    if (browser) await browser.close();
    return null;
  }
}

async function captureScreenshot(page) {
  const filename = `screenshot_${Date.now()}.png`;
  const outputPath = path.join(OUTPUT_DIR, filename);
  
  await fs.ensureDir(OUTPUT_DIR);
  await page.screenshot({ path: outputPath, fullPage: true });
  
  return outputPath;
}

async function fillForm(page) {
  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'selector',
      message: 'Seletor do campo de texto:'
    },
    {
      type: 'input',
      name: 'text',
      message: 'Texto para preencher:'
    }
  ]);

  await page.type(answers.selector, answers.text);
  await page.keyboard.press('Enter');
  
  return 'Formulário preenchido';
}

async function clickElement(page) {
  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'selector',
      message: 'Seletor do elemento para clicar:'
    }
  ]);

  await page.click(answers.selector);
  await page.waitForNavigation({ waitUntil: 'networkidle2' });
  
  return 'Elemento clicado';
}

async function extractData(page) {
  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'selector',
      message: 'Seletor dos dados para extrair:'
    }
  ]);

  const data = await page.evaluate((selector) => {
    const elements = document.querySelectorAll(selector);
    return Array.from(elements).map(el => el.textContent.trim());
  }, answers.selector);

  const filename = `extracted_data_${Date.now()}.json`;
  const outputPath = path.join(OUTPUT_DIR, filename);
  
  await fs.ensureDir(OUTPUT_DIR);
  await fs.writeJson(outputPath, data, { spaces: 2 });
  
  return outputPath;
}

async function executeCustomTask(page) {
  console.log(chalk.yellow('\n📝 Tarefa personalizada:'));
  console.log(chalk.cyan('Exemplo de script:'));
  console.log(`
  // Navegar para uma página
  await page.goto('https://example.com');
  
  // Preencher formulário
  await page.type('#email', 'exemplo@email.com');
  
  // Clicar em botão
  await page.click('#submit');
  
  // Esperar navegação
  await page.waitForNavigation();
  
  // Capturar screenshot
  await page.screenshot({ path: 'output.png' });
  `);

  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'script',
      message: 'Cole o script JavaScript para executar:'
    }
  ]);

  try {
    // Executar script personalizado (cuidado com segurança!)
    const result = await eval(`(async () => { ${answers.script} })()`);
    return result || 'Script executado';
  } catch (error) {
    throw new Error(`Erro no script: ${error.message}`);
  }
}

module.exports = browserAutomation;

// Execução direta
if (require.main === module) {
  browserAutomation().then(() => process.exit(0));
}
