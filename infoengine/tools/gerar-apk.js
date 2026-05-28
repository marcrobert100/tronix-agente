#!/usr/bin/env node
/**
 * Stitch Contos Mágicos — Gerador de APK
 *
 * Converte o InfoEngine em um aplicativo Android nativo.
 *
 * Opções:
 *   node gerar-apk.js          — modo interativo
 *   node gerar-apk.js --apk    — tenta build local com Capacitor
 *   node gerar-apk.js --pwa    — só prepara arquivos PWA + instruções
 *   node gerar-apk.js --url <url>  — usa URL personalizada
 *
 * Pré-requisitos para build local:
 *   - Node.js 18+
 *   - Android Studio + SDK 31+
 *   - Java 17+
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const APP_NAME = 'Stitch Contos Mágicos';
const APP_ID = 'com.stitch.contosmagicos';
const INFOENGINE_DIR = path.resolve(__dirname, '..');
const ROOT_DIR = path.resolve(__dirname, '..', '..');

function run(cmd, cwd = INFOENGINE_DIR) {
  console.log(`  > ${cmd}`);
  try {
    return execSync(cmd, { cwd, stdio: 'pipe', encoding: 'utf-8' });
  } catch (e) {
    return { error: e.stderr || e.message };
  }
}

function checkDeps() {
  const deps = [];
  try { execSync('node --version', { stdio: 'pipe' }); deps.push('node'); } catch { }
  try { execSync('npx --version', { stdio: 'pipe' }); deps.push('npx'); } catch { }
  try { execSync('java -version 2>&1 | findstr version', { stdio: 'pipe' }); deps.push('java'); } catch { }
  try { execSync('adb --version 2>&1 | findstr Android', { stdio: 'pipe' }); deps.push('adb'); } catch { }
  return deps;
}

async function setupCapacitor(url) {
  const appDir = path.join(ROOT_DIR, 'stitch-app');
  if (fs.existsSync(appDir)) {
    console.log('  Pasta stitch-app já existe.');
    return appDir;
  }

  console.log('\n  Criando projeto Capacitor...');
  fs.mkdirSync(appDir, { recursive: true });

  // Cria package.json
  const pkg = {
    name: 'stitch-contos-magicos',
    version: '1.0.0',
    private: true,
    scripts: {
      'build:android': 'npx cap copy && npx cap sync android && npx cap open android',
      'build:apk': 'cd android && gradlew assembleDebug',
    },
    dependencies: {
      '@capacitor/core': '^6.0.0',
      '@capacitor/android': '^6.0.0',
    },
    devDependencies: {
      '@capacitor/cli': '^6.0.0',
    },
  };
  fs.writeFileSync(path.join(appDir, 'package.json'), JSON.stringify(pkg, null, 2));

  // Cria index.html (redirect para servidor ou local)
  const html = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
  <meta http-equiv="refresh" content="0;url=${url}">
  <title>${APP_NAME}</title>
  <link rel="manifest" href="${url}/manifest.json">
  <style>
    body { background: #0b081a; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; }
    .loader { width:48px; height:48px; border:4px solid rgba(255,215,0,0.3); border-top-color:#ffd700; border-radius:50%; animation:spin 0.8s linear infinite; }
    @keyframes spin { to { transform:rotate(360deg); } }
  </style>
</head>
<body>
  <div class="loader"></div>
  <script>
    window.location.replace('${url}');
  </script>
</body>
</html>`;
  fs.writeFileSync(path.join(appDir, 'index.html'), html);

  // Cria capacitor.config.json
  const capConfig = {
    appId: APP_ID,
    appName: APP_NAME,
    webDir: '.',
    bundledWebRuntime: false,
    server: url ? { url, cleartext: true } : undefined,
    android: { allowMixedContent: true },
  };
  fs.writeFileSync(path.join(appDir, 'capacitor.config.json'), JSON.stringify(capConfig, null, 2));

  console.log('  Projeto criado em:', appDir);
  return appDir;
}

function buildAndroid(appDir) {
  console.log('\n  1. Instalando dependências...');
  run('npm install', appDir);
  if (typeof run('npm install', appDir) === 'object') {
    console.log('  Erro ao instalar. Execute manualmente:');
    console.log(`    cd ${appDir} && npm install`);
    return false;
  }

  console.log('\n  2. Instalando Capacitor...');
  run('npx cap init', appDir);
  run('npx cap add android', appDir);

  console.log('\n  3. Copiando assets...');
  run('npx cap copy', appDir);
  run('npx cap sync', appDir);

  console.log('\n  4. Build APK...');
  const result = run('cd android && gradlew assembleDebug', appDir);
  if (typeof result === 'object') {
    console.log('  Build falhou. Verifique Android Studio.');
    return false;
  }

  const apkPath = path.join(appDir, 'android', 'app', 'build', 'outputs', 'apk', 'debug', 'app-debug.apk');
  if (fs.existsSync(apkPath)) {
    const dest = path.join(INFOENGINE_DIR, 'assets', 'stitch-contos.apk');
    fs.copyFileSync(apkPath, dest);
    console.log(`\n  ✅ APK gerado: ${dest}`);
    return true;
  }
  return false;
}

function printManualInstructions(url) {
  console.log(`
╔══════════════════════════════════════════════════════════╗
║         STITCH CONTOS MÁGICOS — GERAR APK              ║
╠══════════════════════════════════════════════════════════╣
║                                                        ║
║   MÉTODO 1 — PWABuilder (recomendado, sem instalação)  ║
║   ─────────────────────────────────────────────         ║
║   1. Acesse: https://pwabuilder.com                     ║
║   2. Digite a URL: ${url.padEnd(45)}║
║   3. Clique "Start"                                     ║
║   4. Escolha "Package for stores" → "Android"           ║
║   5. Baixe o APK assinado                              ║
║                                                        ║
║   MÉTODO 2 — Local (Capacitor + Android SDK)            ║
║   ──────────────────────────────────────────            ║
║   Requer: Android Studio, SDK 31+, Java 17              ║
║                                                         ║
║   Comandos:                                             ║
║     cd ${(path.join(ROOT_DIR, 'stitch-app')).padEnd(45)}║
║     npm install                                         ║
║     npx cap add android                                 ║
║     npx cap copy                                        ║
║     npx cap sync                                        ║
║     cd android && gradlew assembleDebug                 ║
║                                                         ║
║   APK gerado em: android/app/build/outputs/apk/debug/   ║
║                                                         ║
║   MÉTODO 3 — Online (Androidjs)                         ║
║   ──────────────────────────────                        ║
║   1. Acesse: https://androidjs.com                      ║
║   2. Faça upload dos arquivos (infoengine/)             ║
║   3. Configure manifest e gere APK                      ║
║                                                         ║
╚══════════════════════════════════════════════════════════╝
`);
}

async function main() {
  const args = process.argv.slice(2);
  const mode = args.includes('--apk') ? 'apk' : args.includes('--pwa') ? 'pwa' : 'interactive';
  const urlIndex = args.indexOf('--url');
  const url = urlIndex !== -1 ? args[urlIndex + 1] : 'https://marcrobert100.github.io/tronix-agente/infoengine/';

  console.log(`
╔══════════════════════════════════════╗
║   ${APP_NAME}                         
║   Gerador de APK                     
╚══════════════════════════════════════╝
  `);
  console.log(`  URL base: ${url}`);
  console.log(`  Modo: ${mode}`);

  if (mode === 'apk') {
    const deps = checkDeps();
    console.log(`  Dependências encontradas: ${deps.join(', ') || 'nenhuma'}`);

    if (!deps.includes('java') || !deps.includes('adb')) {
      console.log('\n  ⚠️  Android SDK não detectado.');
      console.log('  Instale Android Studio e configure JAVA_HOME + ANDROID_HOME.');
      console.log('  Usando modo PWA como fallback.\n');
      printManualInstructions(url);
      return;
    }

    const appDir = await setupCapacitor(url);
    buildAndroid(appDir);
  } else {
    await setupCapacitor(url);
    printManualInstructions(url);
  }

  console.log('\n  ✅ Pronto! Para gerar APK manualmente, siga as instruções acima.');
  console.log('  Ou use: node gerar-apk.js --apk (se tiver Android SDK)\n');
}

main().catch(err => {
  console.error('Erro:', err.message);
  process.exit(1);
});
