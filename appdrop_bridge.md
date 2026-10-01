# AppDrop Bridge

Instala no iPad os IPAs que o **AppDrop** baixa mas não consegue instalar.

## Diagnóstico

O AppDrop termina o download (100%) e depois chama, via `NSTask`, um destes binários:

```
/usr/bin/appinst
/usr/bin/ipainstaller
/var/jb/usr/bin/appinst          (rootless)
/opt/procursus/bin/ipainstaller  (procursus)
```

Neste iPad (iOS 5.1.1) **nenhum existe** — o pacote `appinst` não está instalado. A
mensagem na tela do AppDrop ("Pode acontecer com apps muito grandes, ou quando
falta espaço ou memória") é genérica e engana o diagnóstico.

O erro real está em `/Library/Caches/jobs.plist`, dentro do container do AppDrop:

```
jobId: local-1790815510
state: failed
progress: 100
```

`progress: 100` + `state: failed` = o download deu certo, só a instalação quebrou.

### Não dá pra instalar o `appinst` remotamente

| Via | Resultado |
|-----|-----------|
| SSH (portas 22/44/2222/27042) | `ConnectionFailedError` |
| `com.apple.ssh_lockdown-service` | `InvalidServiceError` |
| `diagnostics_relay` | `UnknownRequest` (sem exec) |
| AFC padrão | sem root, `/usr/bin` inacessível |
| `cydia.akemi.ai` (repo do appinst) | HTTP 522 — fora do ar |
| `apt.thebigboss.org` | TLS legado, falha |

## Solução

A instalação **funciona** — só depende do `InstallationProxyService`, que o
`pymobiledevice3` usa. O AppSync está ativo no aparelho (instalamos o próprio
AppDrop sem assinatura). Este script faz a parte que o AppDrop não consegue:

1. Lê `/Library/Caches/jobs.plist` no container do AppDrop (HouseArrest)
2. Acha jobs com `state: failed` e pega a URL do IPA
3. Baixa o IPA, detecta FairPlay/DRM
4. Instala via `InstallationProxyService`
5. Registra tudo num SQLite local

## Uso

```powershell
# instala tudo que já falhou e sai
python appdrop_bridge.py --pendentes

# mostra os erros do AppDrop
python appdrop_bridge.py --listar

# busca no catálogo (43.498 apps), filtrando incompatíveis com iOS 5
python appdrop_bridge.py --buscar "angry birds"
python appdrop_bridge.py --buscar "angry birds" --todos   # mostra tudo

# busca e instala o primeiro resultado compatível
python appdrop_bridge.py --instalar-nome "temple run"

# instala uma URL específica
python appdrop_bridge.py --instalar "https://exemplo/app.ipa"

# histórico do que foi instalado
python appdrop_bridge.py --historico

# fica em background instalando automaticamente (Ctrl+C para sair)
python appdrop_bridge.py --monitorar

# baixa/atualiza o catálogo direto do iPad
python appdrop_bridge.py --puxar-catalogo
```

Atalho duplo-clique: `appdrop_bridge.bat` (menu).

### Aparelho

O script detecta o iPad/iPhone automaticamente pelo USB. Se houver mais de um
aparelho conectado, aponte o UDID:

```powershell
$env:IPAD_UDID = 'a1b2c3d4...'
python appdrop_bridge.py --pendentes
```

## Recursos

- **Histórico SQLite** — data, origem, bundle, tamanho, FairPlay, resultado
- **Busca por nome** — no catálogo do AppDrop (43.498 apps em `entries_unique`)
- **Correção de URL 404** — o catálogo tem URLs velhas do archive.org; o script
  consulta `archive.org/metadata/<item>` e casa o arquivo pelo nome
- **Ranking** — título exato > começa com termo > contém > só bundle id
- **Filtro iOS 5** — esconde o que exige iOS 6+ (`min_minos > 50000`)
- **Pula o que já está instalado** — consulta `get_apps()` antes
- **Detecta FairPlay** — avisa em vez de falhar calado
- **Notificação Windows** — toast ao terminar
- **Cache local** — não re-baixa o mesmo IPA

## Estrutura do catálogo

O AppDrop guarda as URLs em duas partes:

| Tabela | Campo | Exemplo |
|--------|-------|---------|
| `urls` | `url` | `https://archive.org/download/ipacollection/ipacollection.zip/Downloads` |
| `entries_unique` | `filename` | `Temple_Run_v1.5_os30.ipa` |

A URL real é a junção dos dois. Usar só `urls.url` dá 404 — foi o primeiro bug.

Tabelas: `entries` (157k), `entries_unique` (43k, a útil), `urls` (27k),
`descriptions`, `downloads`, `cat_icon_pool`.
`sqlite_stat4` está corrompida no catálogo — ignorar.

## Workflow prático

1. No iPad, use o AppDrop normalmente para escolher e baixar
2. No PC, rode `appdrop_bridge.py --pendentes`
3. Ou instale direto: `appdrop_bridge.py --instalar-nome "nome do app"`

## Limitações

- **FairPlay/DRM**: IPA da App Store vem criptografado. O script detecta e avisa
- Precisa do iPad conectado por USB e pareado
- O AppDrop limpa o IPA do container após a falha, então o bridge re-baixa pela URL

## AppDrop não instala tweaks

Confirmado por análise do binário:

| Termo | Ocorrências no AppDrop |
|-------|------------------------|
| `substrate` | 0 |
| `dpkg` | 0 |
| `MobileSubstrate` | 0 |
| `WinterBoard` | 0 |
| `CydiaSubstrate` | 0 |

O AppDrop instala **apps** (IPA). Tweaks vão pelo Cydia. Ele só usa
`cydia://package/ca.adrien.appdrop` para atualizar o próprio AppDrop.

Quem instala tweak é o Cydia, ou ferramentas como **gadget** e **OpenSSH** (que
usam SSH e não precisam do `appinst`).

## Validado nesta máquina

| App | Bundle | Tamanho |
|-----|--------|---------|
| 2010 Map | `com.appventions.worldmap` | 9.2 MB |
| 3D Tunnel | `com.pierotoffanin.3dtunnel` | 3.1 MB |
| Angry Birds | `com.rovio.AngryBirdsSpaceEP` | 54.4 MB |

## Arquivos

| Item | Descrição |
|------|-----------|
| `appdrop_bridge.py` | script principal |
| `appdrop_bridge.bat` | menu interativo |
| `%LOCALAPPDATA%\appdrop_bridge\catalog.db` | catálogo 104 MB |
| `%LOCALAPPDATA%\appdrop_bridge\historico.db` | histórico SQLite |
| `%LOCALAPPDATA%\appdrop_bridge\cache\` | IPAs baixados |

## Dependência

```
pymobiledevice3 >= 11.20.2
```