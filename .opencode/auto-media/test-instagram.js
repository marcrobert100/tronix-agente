#!/usr/bin/env node

const chalk = require('chalk');
require('dotenv').config();

console.log(chalk.blue.bold('\n📸 Teste de Conexão Instagram\n'));

async function testInstagramConnection() {
  try {
    console.log(chalk.yellow('1. Verificando credenciais...'));
    
    const username = process.env.INSTAGRAM_USERNAME;
    const password = process.env.INSTAGRAM_PASSWORD;
    
    if (!username || !password) {
      console.log(chalk.red('❌ Credenciais não encontradas no .env'));
      console.log(chalk.yellow('Configure INSTAGRAM_USERNAME e INSTAGRAM_PASSWORD'));
      return;
    }
    
    console.log(chalk.green(`✓ Usuário: ${username}`));
    console.log(chalk.green('✓ Senha: configurada'));
    
    console.log(chalk.yellow('\n2. Tentando conectar ao Instagram...'));
    
    const { IgApiClient } = require('instagram-private-api');
    const ig = new IgApiClient();
    
    // Gerar dispositivo
    ig.state.generateDevice(username);
    
    // Tentar login
    const auth = await ig.account.login(username, password);
    
    console.log(chalk.green('\n✅ Conexão bem-sucedida!'));
    console.log(chalk.cyan(`👤 Nome: ${auth.full_name}`));
    console.log(chalk.cyan(`👥 Seguidores: ${auth.follower_count}`));
    console.log(chalk.cyan(`👤 Seguindo: ${auth.following_count}`));
    console.log(chalk.cyan(`📝 Posts: ${auth.media_count}`));
    
    // Salvar estado da sessão
    const state = await ig.state.serialize();
    console.log(chalk.green('\n✅ Sessão autenticada e pronta para uso!'));
    
    return auth;
    
  } catch (error) {
    console.log(chalk.red(`\n❌ Erro na conexão: ${error.message}`));
    
    if (error.message.includes('login')) {
      console.log(chalk.yellow('\n💡 Dicas:'));
      console.log(chalk.yellow('1. Verifique se o nome de usuário está correto'));
      console.log(chalk.yellow('2. Verifique se a senha está correta'));
      console.log(chalk.yellow('3. O Instagram pode bloquear logins de apps de terceiros'));
      console.log(chalk.yellow('4. Tente autenticação de dois fatores'));
    }
    
    return null;
  }
}

testInstagramConnection().then(() => {
  console.log(chalk.blue('\n🔌 Teste finalizado'));
  process.exit(0);
}).catch(error => {
  console.log(chalk.red(`\n💥 Erro inesperado: ${error.message}`));
  process.exit(1);
});