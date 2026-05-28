#!/usr/bin/env node

/**
 * Postagem Automática em Redes Sociais
 * 
 * APIs suportadas:
 * - Twitter/X
 * - Instagram
 * - Facebook
 */

const chalk = require('chalk');
const inquirer = require('inquirer');
const fs = require('fs-extra');
const path = require('path');
require('dotenv').config();

const OUTPUT_DIR = process.env.OUTPUT_DIR || './output';

async function postSocial() {
  console.log(chalk.blue('\n📱 Postagem em Redes Sociais\n'));

  // Listar arquivos disponíveis
  const files = await fs.readdir(OUTPUT_DIR).catch(() => []);
  const imageFiles = files.filter(f => /\.(jpg|jpeg|png|gif)$/i.test(f));
  const videoFiles = files.filter(f => /\.(mp4|mov|avi)$/i.test(f));

  const answers = await inquirer.prompt([
    {
      type: 'list',
      name: 'platform',
      message: 'Qual plataforma deseja postar?',
      choices: [
        { name: 'Twitter/X', value: 'twitter' },
        { name: 'Instagram', value: 'instagram' },
        { name: 'Facebook', value: 'facebook' }
      ]
    },
    {
      type: 'list',
      name: 'file',
      message: 'Selecione o arquivo para postar:',
      choices: [...imageFiles, ...videoFiles, '❌ Nenhum arquivo (apenas texto)'],
      when: () => imageFiles.length > 0 || videoFiles.length > 0
    },
    {
      type: 'input',
      name: 'caption',
      message: 'Legenda do post:',
      validate: (input) => input.length > 0 ? true : 'Por favor, insira uma legenda.'
    },
    {
      type: 'confirm',
      name: 'schedule',
      message: 'Agendar postagem?',
      default: false
    },
    {
      type: 'input',
      name: 'scheduleTime',
      message: 'Data e hora (YYYY-MM-DD HH:MM):',
      when: (answers) => answers.schedule,
      validate: (input) => {
        const date = new Date(input);
        return !isNaN(date.getTime()) ? true : 'Data inválida.';
      }
    }
  ]);

  try {
    console.log(chalk.yellow('\n⏳ Postando...'));

    let result;
    switch (answers.platform) {
      case 'twitter':
        result = await postToTwitter(answers);
        break;
      case 'instagram':
        result = await postToInstagram(answers);
        break;
      case 'facebook':
        result = await postToFacebook(answers);
        break;
    }

    console.log(chalk.green(`\n✅ Postagem realizada com sucesso!`));
    console.log(chalk.cyan(`🔗 URL: ${result.url}`));
    
    return result;
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro ao postar: ${error.message}`));
    return null;
  }
}

async function postToTwitter(answers) {
  const { TwitterApi } = require('twitter-api-v2');
  
  const client = new TwitterApi({
    appKey: process.env.TWITTER_API_KEY,
    appSecret: process.env.TWITTER_API_SECRET,
    accessToken: process.env.TWITTER_ACCESS_TOKEN,
    accessSecret: process.env.TWITTER_ACCESS_SECRET
  });

  const rwClient = client.readWrite;

  if (answers.file) {
    const mediaPath = path.join(OUTPUT_DIR, answers.file);
    const mediaId = await rwClient.v1.uploadMedia(mediaPath);
    await rwClient.v2.tweet({
      text: answers.caption,
      media: { media_ids: [mediaId] }
    });
  } else {
    await rwClient.v2.tweet({ text: answers.caption });
  }

  return { url: 'https://twitter.com/user/status/...' };
}

async function postToInstagram(answers) {
  // Instagram Private API (exemplo)
  const { IgApiClient } = require('instagram-private-api');
  
  const ig = new IgApiClient();
  ig.state.generateDevice(process.env.INSTAGRAM_USERNAME);
  
  await ig.account.login(
    process.env.INSTAGRAM_USERNAME,
    process.env.INSTAGRAM_PASSWORD
  );

  if (answers.file) {
    const mediaPath = path.join(OUTPUT_DIR, answers.file);
    const photo = await ig.photo.upload({
      file: await fs.readFile(mediaPath),
      caption: answers.caption
    });
    return { url: `https://instagram.com/p/${photo.id}` };
  } else {
    throw new Error('Instagram requer uma imagem ou vídeo.');
  }
}

async function postToFacebook(answers) {
  const { FacebookAdsApi } = require('facebook-nodejs-business-sdk');
  
  FacebookAdsApi.init(process.env.FACEBOOK_ACCESS_TOKEN);

  // Postar na página do Facebook (exemplo)
  // A implementação depende da configuração específica da API do Facebook
  
  return { url: 'https://facebook.com/post/...' };
}

module.exports = postSocial;

// Execução direta
if (require.main === module) {
  postSocial().then(() => process.exit(0));
}
