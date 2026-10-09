# Como usar — Bancada Celular

Clique no atalho **Bancada Celular** na area de trabalho. Abre o menu numerado.

---

## Antes do primeiro uso (faz uma vez so)

| Para | Situacao |
|---|---|
| Samsung FRP (menu 1) | Precisa driver USB Samsung no PC |
| mtkclient (menu 6) | **JA INSTALADO** — UsbDk 1.0.22. Verificado, driver rodando |
| DumprX (menu 7) | Precisa Git Bash ou WSL |

**Driver do mtkclient:** o mtkclient atual usa `libusb1` (pyusb), nao precisa mais do
Zadig/libusb-win32. O driver correto e o **UsbDk**, que ja esta instalado neste kit:

```
bin\UsbDk\UsbDk_1.0.22_x64.msi   (assinado pela Red Hat, instalacao silenciosa)
```

Se precisar reinstalar: `msiexec /i bin\UsbDk\UsbDk_1.0.22_x64.msi /qn`

O `bin\Zadig\zadig-2.9.exe` tambem esta no kit como plano B (libusb-win32), mas so
instale se o UsbDk falhar — ele **substitui** o driver do aparelho e derruba o ADB ate
desinstalar.

Para conferir se tudo esta certo: menu 10.

---

## Menu 0 - Diagnostico (comece sempre aqui)

Le **nao altera nada** no aparelho. Confirma:
- se o cabo USB funciona (maior causa de "nao conecta" e cabo de carga)
- modelo, IMEI, estado do ADB
- se a depuracao USB esta ligada

Deixa o aparelho na tela de bloqueio e roda. Se aparecer na lista, ta comunicando.

---

## Menu 1 - Samsung FRP pelo navegador

**Quando:** Samsung travado pedindo conta Google, USB debugging nao liberado.

**Limite:** patch de seguranca **antes de Ago/2022**. Samsung novo nao entra.

**Passo a passo:**
1. No aparelho: abrir o discador → **Emergency Dialer** → digitar `#0#`
2. Entra no Test Mode → **conectar o cabo USB no PC**
3. No PC: o menu 1 ja abriu o `index.html` no navegador
4. Chrome ou Edge (precisa ser Chromium)
5. Secao **WebSerial** → *Connect* → escolher o dispositivo (CDC ACM, tipo `COM16`)
6. Clicar os botoes **na ordem** que aparecem
7. Secao **WebUSB** → *Connect* → botoes na ordem
8. Clicar *Reboot*

**Se der erro "device has been lost":** normal. O comando `AT+DEBUGLVC` reconfigura o USB e
o aparelho solta a conexao. Nao entra em panico, so reconecte.

**Em alguns aparelhos** ainda vai pedir pra continuar o setup. Isso e normal.

---

## Menu 2 - FRP universal (Android 5 ate 15)

GUI em Python. **Precisa de USB debugging ligado no aparelho** — diferente do menu 1.

Se o aparelho nao tem USB debugging ligado e nao tem como ligar (travado no setup),
use o menu 1 ou 3.

---

## Menu 3 - Samsung FRP via ADB

Complicado **adb_utils.py**. Faz upload de binario e roda. Alternativa ao menu 1.
O metodo manual faz `settings put secure user_setup_complete 1`.

---

## Menu 4 - dlock (tela de bloqueio)

**Mais confiavel da lista pra PIN/pattern/senha.** Sem root.

Roda, detecta os aparelhos conectados, tenta varios metodos, valida se removeu, faz reboot.
Multi-aparelho: se deixar 3 celulares plugged, ele processa os 3.

O aparelho precisa estar com depuracao USB ativa. Ele **desabilita** a tela de bloqueio —
depois voce redefine o PIN nas Configuracoes.

---

## Menu 5 - LockKnife (forensics)

Suite completa. Comandos de bancada:

```
lockknife device list     lista aparelhos ADB
lockknife device info     info detalhada (modelo, Android, serial)
lockknife crack --help    recuperacao de credencial
lockknife health          diagnostico da propria ferramenta
```

Pelo menu voce so consegue passar argumentos. Para comandos completos, abra o Prompt de
Comando e digite direto.

---

## Menu 6 - mtkclient (MediaTek)

O motor mais forte do kit. Dump de firmware, leitura/escrita de eMMC, FRP via BROM,
PRELOADER. Usado pra recuperar aparelho com brick.

**Driver ja instalado** (UsbDk 1.0.22, driver rodando). Antes de abrir o mtkclient,
rode o **menu 10** — ele diz se o aparelho ja entrou em modo BROM.

**Colocar em BROM:** desligue o aparelho → segure **vol+ e vol- juntos** → conecte o cabo
USB sem soltar. No menu 10 tem que aparecer `VID=0x0E8D`. Aí o mtkclient conecta.

```
python mtk.py        linha de comando
python mtk_gui.py    interface grafica
```

Comandos comuns:
```
python mtk.py r     *r*e*ade*    leitura de particao
python mtk.py w     *r*e*ade*    escrita (DESTRUTIVO)
python mtk.py --help
```

So com autorizacao. Escrita em particao errada deixa o aparelho morto de vez.

---

## Menu 10 - Diagnostico USB / MTK

Confere a pilha inteira de acesso USB em 4 passos:

1. **Servico UsbDk** — precisa estar `RUNNING`
2. **UsbDkController -n** — dispositivos que o driver enxerga
3. **libusb via mtkclient** — o que o mtkclient vai realmente enxergar
4. **ADB** — dispositivos com depuracao autorizada

**Como ler:**

| Resultado | Significado | O que fazer |
|---|---|---|
| `VID=0x0E8D` | MediaTek em BROM | pode abrir o menu 6 |
| `VID=0x2717` | aparelho em modo normal | precisa entrar em BROM |
| sem `0x0E8D` | ainda nao esta em BROM | desligar, segurar vol+ e vol-, conectar |

**Se o UsbDk nao estiver rodando:**
```
msiexec /i bin\UsbDk\UsbDk_1.0.22_x64.msi /qn
sc start UsbDk
```

Este menu e so leitura — nao altera nada no aparelho.

---

## Menu 11 - Monitorar modo BROM

Fica olhando a porta USB e **bipe** quando o MediaTek aparece como `0x0E8D`. Se a
janela ficar te esperando, é o jeito mais fácil de acertar o timing.

**Ordem certa:**

1. **PC:** abre o menu 11 e deixa rodando
2. **Celular:** desliga completamente
3. Retira a tampa traseira
4. **Desconecta a bateria** — puxa o conector plástico pequeno, **não** levanta a célula
5. Segura **`Vol+` e `Vol−`** juntos
6. Conecta o cabo USB sem soltar
7. Espera o bipe → solta os botões
8. Menu 6

**Por que tirar a bateria:** com a célula conectada, o gerenciamento de energia do
aparelho segura o boot e ele volta pro Android normal. Sem a bateria, o processador
entra direto no BROM quando recebe o USB.

**Segurança da bateria:** a célula é de lítio. Puxe pelo **conector**, nunca pela
placa. Não use metal, não fure, não force o conector.

**Alternativa sem desmontar:** desligue, segure `Vol−` + `Botão Liga` e conecte o
cabo. Funciona em parte dos aparelhos MediaTek. Se não engatar em 5 minutos, use o
método da bateria.

Nada é escrito no aparelho em nenhum desses passos. BROM só abre comunicação.



---

## Menu 7 - DumprX (firmware)

Extrai `.ozip .ofp .kdz .pac .img payload.bin` e separa boot/system/vendor.
Bom pra aparelho que so volta na tela de boot e precisa do firmware original.

Roda em Git Bash ou WSL:
```bash
bash setup.sh                          # uma vez
./dumper.sh 'caminho/para/firmware.zip'
```

O menu so abre a pasta — o comando precisa ser digitado no terminal Linux.

---

## Menu 8 - Databases

- `open-device-db` — specs, firmware, info de reparo por modelo
- `PhonePCB` — mapas de RF e pontos de teste de board

Consulta na OS antes de comecar o reparo. Evita perder 2 horas caçando problema que ja tem
resposta documentada.

---

## Menu 9 - BoardRipper (boardview + schematic)

Viewer de hardware. Abre o arquivo de boardview e o PDF do schematic **lado a lado**,
com o nets clicaveis. É o programa que resolve "qual e o pino deste sinal?".

Arquivo unico de 8MB em `dados\BoardRipper-lite.html`. Roda **offline**, no proprio
navegador, sem servidor e sem Docker. Nada e enviado pra internet.

**Abrir um aparelho:**
1. Menu 9 (ou duplo clique no `9-boardview.bat`)
2. **Ctrl+O** → escolher o `.brd` / `.fz` / `.tvw` / `.cad` / `.pcb`
3. **Ctrl+P** → escolher o PDF do schematic
4. As duas janelas ficam lado a lado, ja sincronizadas

**Atalhos:**

| Tecla | O que faz |
|---|---|
| `Ctrl+O` | abrir boardview |
| `Ctrl+P` | abrir schematic em PDF |
| `Space` | vira a board (frente / verso) |
| `F` | focar a net selecionada |
| `Esc` | limpar selecao |

**Truques de bancada:**
- **Clicar num pino** acende a net inteira naquele ponto
- **Botao direito na net** → *Find in schematic* leva o PDF direto no ponto
- Clique no **numero do pino** (nao no via) pra ver a net do lado contrario
- Modo escuro: icone do sol, no canto
- Da pra **arrastar o arquivo direto** pra janela

**Formatos suportados:** `.brd` (Allegro/Extracta/BCD) · `.fz` · `.tvw` · `.bdv` ·
`.bv` · `.cad` · `.pcb` · `.kicad_pcb` · `.PcbDoc` (Altium)

**Onde conseguir os arquivos:**
- Android: escolha do aparelho → *Repair* → *Board Diagram* (o proprio fabricante)
- iPhone: sites como `phoneboard.repair`, `iar.inc`, `eefix`
- iFixit teardown vem com PDF linkado

O kit **nao baixa boardview** — arquivo tem licenca do fabricante e nao entra em git.
Tu precisa baixar separado e abrir pelo menu 9.

---

## Menu 14 - Doctor (rode sempre antes de reclamar que algo quebrou)

```
14. Doctor
```

Verifica o kit inteiro e grava `logs\doctor_report.json`.

O que ele faz que nenhum outro item faz:

- **Deriva o driver USB do codigo-fonte do mtkclient**, nao do manual. Le
  `usblib.py` e ve se ele importa `libusb1` ou `libusb0`. Se o mtkclient
  mudar de driver numa atualizacao, o doctor acusa antes de voce perder tempo.
- **Prova viva da USB**: importa `UsbClass` de verdade e conta os dispositivos.
  Se aparecer 6, entao pyusb + libusb1 + UsbDk estao todos funcionando juntos.
- **Confere o manual contra a realidade**: todo `.bat` citado no COMO_USAR.md
  precisa existir de fato.
- **Descobre os repos sozinho**: varre a pasta, acha todo `.git` e registra
  commit + remote de cada um. Nao depende de caminho chumbado.
- **Checa entrypoint de cada clone** procurando `.py`, `.sh`, `.ps1`, `.js`,
  `.ts`, `.rs`, `.go`, `.html` -- porque nem todo repo e Python.
- **`pip check`** para achar conflito de versao entre as dependencias.
- Sai com codigo 1 se algo que impede o uso estiver quebrado. Bom pra script.

Deps opcionais (nao bloqueiam): `mfusepy` so e necessario para montar
particao em arquivo, e exige WinFsp instalado.

---

## Receituario rapido

| Sintoma | Comece por |
|---|---|
| Nao sei nem por onde comecar | **menu 14 (doctor)** |
| Suspeita que o kit quebrou | **menu 14 (doctor)** |
| Samsung pedindo conta Google, ADB ativo | menu 2 |
| Samsung pedindo conta Google, ADB inativo | menu 1 |
| Esqueceram PIN/pattern/senha | menu 4 |
| MediaTek travado, precisa de FRP ou dump | menu 6 |
| Xiaomi travado, destravar bootloader | menu 12 (72h-168h de espera da Xiaomi) |
| Aparelho so volta na tela de boot | menu 7 |
| Botoes nao funcionam, suspeita de agua | menu 0 + menu 9 (boardview) + analisador de board |
| Cliente nao lembra a conta Google | pedir a senha. Sem ela, so reprogramando eMMC (UFI Box) |
| Precisa achar o pino de um sinal | menu 9 |

---

## O que este kit NAO faz

- **Nao desbloqueia bootloader** — depende de modelo e regiao
- **Nao resolve FRP em aparelho novo** — precisa UFI Box (R$400–800)
- **Nao vem com arquivos de boardview** — o viewer (menu 9) ta aqui, os arquivos voce baixa
- **Nao tem gravador de eMMC** — so o mtkclient, se o aparelho permitir

