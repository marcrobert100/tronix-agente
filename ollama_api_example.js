const axios = require('axios');

// Configuração da API Ollama
const OLLAMA_URL = 'http://localhost:11434/api/generate';
const MODEL = 'qwen2:0.5b';

async function generateText(prompt, model = MODEL) {
    const payload = {
        model: model,
        prompt: prompt,
        stream: false
    };

    try {
        const response = await axios.post(OLLAMA_URL, payload, { timeout: 60000 });
        return response.data.response || '';
    } catch (error) {
        return `Erro: ${error.message}`;
    }
}

// Exemplos de uso
async function main() {
    // Exemplo 1: Conversa simples
    console.log('=== Exemplo 1: Conversa simples ===');
    const resposta1 = await generateText('Olá, como você está?');
    console.log(`Resposta: ${resposta1}\n`);

    // Exemplo 2: Tradução
    console.log('=== Exemplo 2: Tradução ===');
    const resposta2 = await generateText('Traduza para inglês: "Bom dia, mundo!"');
    console.log(`Resposta: ${resposta2}\n`);

    // Exemplo 3: Resumo
    console.log('=== Exemplo 3: Resumo ===');
    const texto = 'A inteligência artificial está transformando indústrias ao automatizar tarefas e analisar grandes volumes de dados.';
    const resposta3 = await generateText(`Resuma este texto em uma frase: ${texto}`);
    console.log(`Resposta: ${resposta3}\n`);

    // Exemplo 4: Código
    console.log('=== Exemplo 4: Geração de código ===');
    const resposta4 = await generateText('Escreva uma função Python que calcula o fatorial de um número.');
    console.log(`Resposta: ${resposta4}\n`);
}

main();