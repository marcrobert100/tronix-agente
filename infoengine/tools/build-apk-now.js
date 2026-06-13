#!/usr/bin/env node
/**
 * Gera APK usando Bubblewrap programaticamente com o mínimo de interação.
 * Força resposta "No" para JDK apenas manipulando o stream.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const BUILD_DIR = path.join(os.tmpdir(), 'stitch-apk-' + Date.now());

async function run() {
  console.log('=== Build APK: Stitch Contos Mágicos ===\n');

  // Cria diretório
  fs.mkdirSync(BUILD_DIR, { recursive: true });

  // Cria arquivo de config do Bubblewrap manualmente
  const twaManifest = {
    packageName: 'com.stitch.contosmagicos',
    display: 'standalone',
    hostName: 'localhost',
    launcherName: 'Stitch Contos',
    name: 'Stitch Contos Mágicos',
    versionCode: 1,
    versionName: '1.0.0',
    webManifestUrl: 'http://localhost/infoengine/manifest.json',
    startUrl: 'http://localhost/infoengine/index.html',
    appVersionName: '1.0.0',
    appVersionCode: 1,
    signing: {
      auto: true,
      keyAlias: 'stitch-key',
      keyPassword: 'stitch123',
      keyPath: path.join(BUILD_DIR, 'stitch.keystore'),
      storePassword: 'stitch123',
    },
    iconUrl: 'http://localhost/infoengine/assets/icons/icon-512.svg',
    icons: {
      foreground: { src: 'http://localhost/infoengine/assets/icons/icon-512.svg', type: 'image/svg+xml', sizes: '512x512' },
      background: { src: 'http://localhost/infoengine/assets/icons/icon-512.svg', type: 'image/svg+xml', sizes: '512x512' },
    },
    url: 'http://localhost/infoengine/index.html',
    themeColor: '#ffd700',
    backgroundColor: '#0b081a',
    orientation: 'any',
    fallbackType: 'customtabs',
    features: [],
    extraShortcutItems: [],
    locale: 'pt-BR',
  };

  fs.writeFileSync(path.join(BUILD_DIR, 'twa-manifest.json'), JSON.stringify(twaManifest, null, 2));
  console.log('  Config TWA salva em', BUILD_DIR);

  // Gera keystore
  console.log('  Gerando keystore...');
  try {
    require('child_process').execSync(
      `"${process.env.JAVA_HOME || ''}\\bin\\keytool" -genkey -v -keystore "${path.join(BUILD_DIR, 'stitch.keystore')}" -alias stitch-key -keyalg RSA -keysize 2048 -validity 10000 -storepass stitch123 -keypass stitch123 -dname "CN=Stitch, OU=Dev, O=Stitch, L=City, ST=ST, C=BR"`,
      { stdio: 'pipe', timeout: 30000 }
    );
    console.log('  Keystore criado');
  } catch (e) {
    console.log('  Keystore ja existe ou keytool nao encontrado:', e.message.substring(0, 100));
  }

  // Tenta usar Bubblewrap com --no-jdk
  console.log('\n  Executando Bubblewrap build...\n');
  
  const proc = spawn('npx', [
    '@bubblewrap/cli', 'build',
    '--directory', BUILD_DIR,
  ], {
    stdio: ['pipe', 'inherit', 'inherit'],
    shell: true,
    env: { ...process.env, BUBBLEWRAP_NONINTERACTIVE: '1' },
  });

  // Fecha stdin imediatamente para evitar prompts
  proc.stdin.end();

  const timeout = setTimeout(() => {
    console.log('\n  ⏱ Timeout. Matando processo...');
    proc.kill('SIGTERM');
    setTimeout(() => proc.kill('SIGKILL'), 2000);
  }, 240000);

  proc.on('close', (code) => {
    clearTimeout(timeout);
    console.log(`\n  Bubblewrap exit code: ${code}`);

    // Procurar APK
    const apks = findApk(BUILD_DIR);
    if (apks.length > 0) {
      const dest = path.join('C:\\xampp\\htdocs\\agente\\infoengine\\assets', 'stitch-contos.apk');
      fs.copyFileSync(apks[0], dest);
      console.log(`\n✅ APK GERADO: ${dest}`);
      console.log(`   Tamanho: ${(fs.statSync(dest).size / 1024 / 1024).toFixed(1)} MB`);
    } else {
      console.log('\n❌ APK nao encontrado no output.');
      console.log('Alternativa: acesse https://pwabuilder.com e use:');
      console.log('  URL: http://localhost/infoengine/');
    }
  });
}

function findApk(dir) {
  const results = [];
  try {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) results.push(...findApk(full));
      else if (entry.name.endsWith('.apk')) results.push(full);
    }
  } catch {}
  return results;
}

run().catch(console.error);
