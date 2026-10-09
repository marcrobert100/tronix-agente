# Bancada Celular — canivete suíço

Kit de software para manutenção de celular. Roda 100% local, sem servidor, sem nuvem.
Instalado em `C:\xampp\htdocs\agente\bancada_celular\`

**Iniciar tudo:** `INICIAR.bat`

---

## Regra de ouro

Só opere em aparelho com **autorização por escrito do dono**. Na recepção, anote a conta
Google/Samsung no verso da OS. Sem isso você consome seu nome. FRP existe para bloquear
aparelho roubado — burpá-lo em aparelho de terceiro é crime (Lei 9.279/96, receptação).

---

## O que está instalado

### Diagnóstico (leitura, não altera nada)
| Ferramenta | Função |
|---|---|
| `diagnostico-aparelho.bat` | adb + fastboot + info do aparelho conectado |
| `0` no menu | lista modelo, IMEI, estado ADB |

### FRP — Factory Reset Protection
| # | Ferramenta | Quando usar | Limite real |
|---|---|---|---|
| 1 | **Samsung FRP (web)** `NDXCode/Samsung-FRP-Bypass-WEB` | Samsung travado. Melhor ponto de entrada: zero instalação, roda no Chrome/Edge | patch de segurança **antes de Ago/2022** |
| 2 | **FRP Freedom** `youngrichu/frp-freedom` | Qualquer Android 5→15. GUI tkinter, log de auditoria | precisa de ADB autorizado |
| 3 | **Samsung FRP GUI** `MaKraMc/Samsung-FRP-Bypass-GUI` | Samsung com USB debugging ligado | via ADB |

**Método do #1:** discador → Emergency Dialer → `#0#` → conectar USB → WebSerial → botões em ordem → WebUSB → botões em ordem → Reboot.

### Tela de bloqueio (PIN / pattern / senha)
| # | Ferramenta | Observação |
|---|---|---|
| 4 | **dlock** (Go, binário Windows) | Sem root. Tenta múltiplos métodos, multi-aparelho, valida. Mais confiável da lista |
| 5 | **LockKnife** v1.2.0 (Rust) | Suite forensics. Comandos de bancada: `device list`, `device info`, `crack` |
| — | `androidpatternlock` | Quebra pattern antigo via SHA1 do `gesture.key` (sem salt). Só Android velho, aparelho rooteado |
| — | `PassReset` | Módulo TWRP/OrangeFox. Apaga qualquer lock. Exige recovery custom |

### MediaTek — o motor mais forte
`6-mtkclient.bat` → `mtkclient` (B.Kerler). Dump de firmware, leitura/escrita de eMMC, FRP via BROM, PRELOADER.

**Driver já instalado e verificado:** UsbDk 1.0.22 (`bin\UsbDk\UsbDk_1.0.22_x64.msi`, assinado pela Red Hat).
`usbdk.sys` v1.0.22.0 em `System32\drivers`, serviço `UsbDk` em estado **RUNNING**, `libusb1` do pyusb
enxerga os 6 dispositivos USB da máquina. Confirmado na prática.

> **Nota:** o mtkclient atual usa `libusb1` (pyusb) e **não usa mais Zadig/libusb-win32**.
> Manuais antigos mandam instalar Zadig — está obsoleto. O `bin\Zadig\zadig-2.9.exe` ficou no
> kit só como plano B; ele *substitui* o driver do aparelho e derruba o ADB até desinstalar.

**Para entrar em modo BROM:** desligar → segurar **vol+ e vol-** → conectar o cabo. No menu 10
precisa aparecer `VID=0x0E8D`.

### Firmware e databases
| Pasta | Conteúdo |
|---|---|
| `firmware/DumprX` | Extrator de firmware (`.ozip .ofp .kdz .pac .img payload.bin` → boot/system/vendor). Precisa WSL ou Git Bash: `bash setup.sh` |
| `dados/open-device-db` | Specs, firmware, info de reparo por modelo |
| `dados/PhonePCB` | Mapas de RF e pontos de teste de board |

### Boardview / schematic
| # | Ferramenta | Função |
|---|---|---|
| 9 | **BoardRipper** `dados/BoardRipper-lite.html` | Abre boardview (`.brd .fz .tvw .cad .pcb`) + PDF do schematic lado a lado, nets clicáveis. Arquivo único de 8MB, offline, sem Docker |

`Ctrl+O` abre a board, `Ctrl+P` abre o schematic, `Space` vira a board, botão direito na net → *Find in schematic*.
Formatos: `.brd` (Allegro/BCD) · `.fz` · `.tvw` · `.bdv` · `.bv` · `.cad` · `.pcb` · `.kicad_pcb` · `.PcbDoc`.

O **viewer** está instalado; os **arquivos de boardview** não. Licença do fabricante, não entram em
git. Baixe separado (Android: *Repair* → *Board Diagram* no site do fabricante; iPhone: `phoneboard.repair`, `iar.inc`)
e abra pelo menu 9.


---

## O que NÃO está aqui (e por quê)

| Ferramenta | Motivo |
|---|---|
| `ghostking2802/CiLocks` | Traz criação de payload (msfvenom) e IP logger. É kit de malware — infecta o PC da loja. Não instalar |
| Softwares cracks (GSM Aladdin, Octoplus, UnlockTool) | Fonte quase sempre trojanizada. Se for usar, compre do fornecedor oficial |
| Ferramentas de bootloader unlock | Depende de modelo e região. Nokia/Huawei travam no bootloader |

## Equipamento de hardware que estas ferramentas exigem

- Cabo USB de dados (não só carga) — a maior causa de "não conecta"
- Driver USB Samsung instalado (para o #1)
- ~~Zadig + libusb-win32~~ → **UsbDk 1.0.22, já instalado** (ver #6)
- Case ou suporte com trava para segurar o aparelho durante o processo

---

## Realidade 2026

**FRP em aparelho novo não tem software que resolva.** Samsung com patch depois de Ago/2022
e iPhone 2018+ usam segurança presa em hardware. Saídas reais:

1. Cliente entra com a conta dele → tu formata e pronto
2. **Reprogramar eMMC/UFS** com UFI Box → storage novo = FRP zerado, **mas perde todos os dados**

Para o caminho 2 é preciso o UFI Box (R$400–800 + dongle). Nenhum software substitui isso.

---

## Fluxo de trabalho sugerido

1. **Recepção** — termo de autorização + anotar conta Google no verso da OS
2. `diagnostico-aparelho.bat` — confirmar modelo, se ADB ativa, se tem Google Find
3. Sem senha do Google → oferecer "formato e apaga tudo"
4. Samsung travado → #1 (1 minuto, zero instalação)
5. MediaTek → #6 com Zadig instalado
6. Antes de soldar → #9, abrir boardview do modelo e achar o pino do sinal
7. Nada funcionou → avaliar UFI Box, com termo de perda de dados assinado
8. Envolver o aparelho com lacre/adesivo numerado, registrar IMEI na OS

---

## Logs

`logs/` — saída de instalação (`install_mtk.log`, `install_frp.log`, `dlock.log`).

## Ambiente verificado

Python 3.12.10 · adb/fastboot (winget Google.PlatformTools) · git 2.53 · PySide6 6.11 · Node 24.14.1
Testes do frp-freedom: 8/8 passando.

### Pilha USB (verificada nesta máquina)

| Camada | Estado |
|---|---|
| `usbdk.sys` 1.0.22.0 (Red Hat) | instalado em `System32\drivers` |
| Serviço `UsbDk` | **RUNNING** (kernel driver) |
| `UsbDkController -n` | 6 dispositivos USB enumerados |
| pyusb `libusb1` | 6 dispositivos, incluindo `0x2717:0xFF48` (Redmi 6A) |
| Zadig 2.9 | baixado e assinado (plano B, **não instalado**) |

Dispositivo de teste: **Xiaomi Redmi 6A** (MediaTek Helio A22), `VID_2717 PID_FF48`, ADB autorizado.
Para validar o mtkclient de ponta a ponta, precisa entrar em BROM e aparecer `0x0E8D`.

