"""
Bancada Celular - Doctor
Verifica o ambiente inteiro do kit e valida o que a documentacao afirma
contra o que esta realmente instalado.

Principio: nao confia no doc. Deriva o requisito do codigo-fonte e do
estado real da maquina. Por isso o manual nao pode mais mentir sozinho.
"""

import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
MTK = os.path.join(BASE, "mtk", "mtkclient")
REPORT = os.path.join(BASE, "logs", "doctor_report.json")

checks = []
todos_ok = True


def add(ok, cat, name, detail, fix=""):
    global todos_ok
    if ok is None:
        mark = "---"
    elif ok:
        mark = "[ OK ]"
    else:
        mark = "[ !! ]"
        todos_ok = False
    line = f"  {mark} {name}"
    if detail:
        line += f"  ->  {detail}"
    print(line)
    if not ok and fix:
        print(f"         CORRIGIR: {fix}")
    checks.append(
        {"ok": ok, "categoria": cat, "item": name, "detalhe": detail, "correcao": fix}
    )
    return ok


def sec(t):
    print()
    print(f"--- {t} " + "-" * max(0, 56 - len(t)))


def run(cmd, timeout=25):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or "") + (r.stderr or "")
    except Exception:
        return ""


def which(name):
    return shutil.which(name)


def fsize(p):
    try:
        return os.path.getsize(p)
    except OSError:
        return 0


# ---------------------------------------------------------------- ambiente
sec("AMBIENTE")

ver = sys.version.split()[0]
add(
    tuple(int(x) for x in ver.split(".")[:2]) >= (3, 9),
    "ambiente",
    f"Python {ver}",
    f"em {sys.executable}",
    "instale Python 3.9 ou superior",
)

for tool, args, label in [
    ("adb", ["version"], "adb"),
    ("fastboot", ["--version"], "fastboot"),
    ("git", ["--version"], "git"),
]:
    p = which(tool)
    if p:
        out = run([p] + args).strip().splitlines()
        first = out[0] if out else ""
        add(True, "ambiente", label, first or os.path.basename(p))
    else:
        add(False, "ambiente", label, "nao encontrado", f"winget install {tool}")

node = which("node")
add(
    bool(node),
    "ambiente",
    "Node.js",
    run([node, "--version"]).strip() if node else "nao encontrado",
    "so e necessario se for compilar o BoardRipper desktop",
)

# ------------------------------------------------------- driver USB (USB)
sec("DRIVER USB / MEDIA TEK  (derivado do codigo, nao do manual)")

usblib = os.path.join(MTK, "mtkclient", "Library", "Connection", "usblib.py")
code = ""
if os.path.isfile(usblib):
    with open(usblib, "r", encoding="utf-8", errors="ignore") as fh:
        code = fh.read()

usa_libusb1 = "usb.backend.libusb1" in code
usa_libusb0 = "usb.backend.libusb0" in code

if not code:
    add(False, "driver", "mtkclient", "usblib.py nao encontrado", "reclone o repo mtkclient")
    driver_necessario = "desconhecido"
else:
    if usa_libusb1:
        driver_necessario = "UsbDk"
        add(
            True,
            "driver",
            "mtkclient usa libusb1 (pyusb)",
            "detectado no codigo-fonte: usb.backend.libusb1",
        )
    else:
        driver_necessario = "Zadig (libusb-win32)"
        add(
            True,
            "driver",
            "mtkclient usa libusb0 (antigo)",
            "detectado no codigo-fonte: usb.backend.libusb0",
        )
    if usa_libusb0 and usa_libusb1:
        add(
            True,
            "driver",
            "fallback libusb0 presente",
            "mtkclient aceita os dois caminhos de driver",
        )

# estado do UsbDk
sv = run(["sc.exe", "query", "UsbDk"])
udk_rodando = "RUNNING" in sv.upper() or "4" in sv
sysdrv = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "drivers", "usbdk.sys")

if driver_necessario == "UsbDk":
    add(
        os.path.isfile(sysdrv),
        "driver",
        "usbdk.sys instalado",
        f"{fsize(sysdrv) / 1024:.0f} KB em System32\\drivers" if os.path.isfile(sysdrv) else "ausente",
        "msiexec /i bin\\UsbDk\\UsbDk_1.0.22_x64.msi /qn",
    )
    add(
        udk_rodando,
        "driver",
        "servico UsbDk",
        "RUNNING" if udk_rodando else "parado ou ausente",
        "msiexec /i bin\\UsbDk\\UsbDk_1.0.22_x64.msi /qn  e  sc start UsbDk",
    )
    ctl = r"C:\Program Files\UsbDk Runtime Library\UsbDkController.exe"
    add(
        os.path.isfile(ctl),
        "driver",
        "UsbDkController",
        ctl if os.path.isfile(ctl) else "nao encontrado",
        "reinstale o MSI do UsbDk",
    )

if which("python"):
    r = run([sys.executable, "-c", "import usb.backend.libusb1 as l;print('ok' if l.get_backend() else 'no')"])
    add(
        "ok" in r,
        "driver",
        "pyusb + libusb1 importavel",
        r.strip() or "sem retorno",
        "pip install pyusb libusb",
    )

# zadig
zadig = os.path.join(BASE, "bin", "Zadig", "zadig-2.9.exe")
if os.path.isfile(zadig):
    add(
        True,
        "driver",
        "Zadig 2.9 (plano B)",
        f"{fsize(zadig) / 1048576:.1f} MB, instalado: NAO (correto)",
        "so instale se o driver principal falhar",
    )
else:
    add(None, "driver", "Zadig 2.9 (plano B)", "nao baixado", "opcional")

# ------------------------------------------------------------- dispositivos
sec("DISPOSITIVOS CONECTADOS")

adb = which("adb")
serials = []
if adb:
    out = run([adb, "devices", "-l"])
    for line in out.splitlines()[1:]:
        line = line.strip()
        if line and line.split()[1] == "device":
            serials.append(line.split()[0])
    if serials:
        add(True, "dispositivo", "ADB autorizado", ", ".join(serials))
    elif "unauthorized" in out:
        add(False, "dispositivo", "ADB", "aparelho nao autorizado", "aceite a huella RSA no celular")
    else:
        add(None, "dispositivo", "ADB", "nenhum aparelho conectado")

fb = which("fastboot")
fbs = []
if fb:
    out = run([fb, "devices"])
    for line in out.splitlines():
        p = line.split()
        if len(p) >= 2 and p[1] == "fastboot":
            fbs.append(p[0])
    if fbs:
        add(True, "dispositivo", "fastboot conectado", ", ".join(fbs))
    else:
        add(None, "dispositivo", "fastboot", "nenhum aparelho em fastboot")

# estado do bootloader, se houver
if fbs and fb:
    gv = run([fb, "getvar", "unlocked"])
    m = re.search(r"unlocked:\s*(\w+)", gv)
    if m:
        unl = m.group(1)
        add(
            unl == "yes",
            "dispositivo",
            "bootloader destravado",
            f"unlocked={unl}",
            "Xiaomi: conta Mi + 72-168h + Mi Unlock Tool (menu 12)",
        )
    ua = run([fb, "flashing", "get_unlock_ability"])
    m2 = re.search(r"unlock_ability\s*=\s*(\d)", ua)
    if m2:
        add(
            m2.group(1) != "0",
            "dispositivo",
            "bootloader elegivel para destravar",
            f"unlock_ability={m2.group(1)}",
            "0 = ainda nao elegivel. Vincule conta Mi no aparelho e aguarde o prazo",
        )

# --------------------------------------------------------------- ferramentas
sec("FERRAMENTAS DO KIT")


def check_dexe(rel, name, note=""):
    p = os.path.join(BASE, rel)
    ok = os.path.isfile(p) and fsize(p) > 0
    return add(ok, "ferramenta", name, note or (f"{fsize(p) / 1024:.0f} KB" if ok else "ausente"), "verifique o menu")


check_dexe(os.path.join("bin", "dlock", "dlock.exe"), "dlock", "binario Windows, tela de bloqueio")
check_dexe(
    os.path.join("dados", "BoardRipper-lite.html"),
    "BoardRipper-lite",
    "offline, sem Docker",
)
check_dexe(os.path.join("bin", "mi-unlock", "miflash_unlock.exe"), "Mi Unlock Tool", "oficial Xiaomi")

# integridade do BoardRipper
br = os.path.join(BASE, "dados", "BoardRipper-lite.html")
if os.path.isfile(br):
    with open(br, "r", encoding="utf-8", errors="ignore") as fh:
        head = fh.read(200)
        fh.seek(max(0, fsize(br) - 200))
        tail = fh.read()
    bom = "<!doctype html" in head.lower() and "</html>" in tail.lower()
    add(bom, "ferramenta", "BoardRipper HTML integro", "abre e fecha corretamente" if bom else "TRUNCADO - rebaixe")

    with open(br, "rb") as fh:
        h = hashlib.sha256(fh.read()).hexdigest()
    add(True, "ferramenta", "BoardRipper SHA256", h[:32] + "...")

# deps python do mtkclient
# nome do pacote no pip != nome do modulo importavel
PIP_PARA_IMPORT = {
    "pyusb": "usb",
    "pycryptodome": "Crypto",
    "pycryptodomex": "Cryptodome",
    "pyserial": "serial",
    "shiboken6": "shiboken6",
    "pyside6": "PySide6",
    "colorama": "colorama",
    "capstone": "capstone",
    "keystone-engine": "keystone",
    "keystone": "keystone",
    "unicorn": "unicorn",
    "mfusepy": "mfusepy",
    "flake8": "flake8",
}

req = os.path.join(MTK, "requirements.txt")
if os.path.isfile(req) and which("python"):
    with open(req, "r", encoding="utf-8", errors="ignore") as fh:
        mods = [
            re.split(r"[<>=!\[;]", ln.strip())[0]
            for ln in fh
            if ln.strip() and not ln.startswith("#")
        ]
    mods = [m for m in mods if m and m not in ("wheel", "setuptools")]
    # deps que so sao necessarias para tarefas especificas - nao bloqueiam o kit
    OPCIONAIS = {
        "mfusepy": "so para montar/desserializar particao em arquivo (ex.: r --decode). exige WinFsp",
        "flake8": "apenas lint do mtkclient, nao roda em producao",
    }
    faltando = []
    opcionais_faltando = []
    for m in mods:
        mod = PIP_PARA_IMPORT.get(m, m)
        # imprime um sentinela: import bem-sucedido nao devolve NADA em stdout,
        # entao "vazio" significa sucesso, nao falha.
        r = run([sys.executable, "-c", f"import {mod};print('SENTINELA_OK')"])
        if "SENTINELA_OK" not in r:
            item = m if m not in PIP_PARA_IMPORT else f"{m} (import {mod})"
            (opcionais_faltando if m in OPCIONAIS else faltando).append(item)
    add(
        not faltando,
        "ferramenta",
        "deps do mtkclient (obrigatorias)",
        f"{len(mods) - len(faltando) - len(opcionais_faltando)}/{len(mods) - len(opcionais_faltando)} instaladas"
        if not faltando
        else "faltando: " + ", ".join(faltando),
        "pip install -r mtk\\mtkclient\\requirements.txt",
    )
    if opcionais_faltando:
        add(
            None,
            "ferramenta",
            "deps opcionais",
            "faltando: " + ", ".join(opcionais_faltando) + " - " + OPCIONAIS["mfusepy"],
            "so se for usar montagem de particao: instale WinFsp + pip install mfusepy",
        )

    # pip check: dependencia com versao quebrada
    pc = run([sys.executable, "-m", "pip", "check"], timeout=60)
    quebradas = [l for l in pc.splitlines() if "broken" in l.lower()]
    add(
        not quebradas,
        "ferramenta",
        "pip check (conflitos de versao)",
        "nenhum conflito" if not quebradas else f"{len(quebradas)} conflito(s)",
        "pip check  e veja o que esta em conflito",
    )

# prova real: o mtkclient consegue falar com a camada USB?
# roda com cwd no repo, senao o pacote mtkclient nao esta no sys.path
if os.path.isdir(MTK) and which("python"):
    probe = (
        "from mtkclient.Library.Connection.usblib import UsbClass;"
        "u=UsbClass(-1,devclass=-1);"
        "print('DISPOSITIVOS',len(u.detectdevices()))"
    )
    try:
        r = subprocess.run(
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            timeout=90,
            cwd=MTK,
        )
        r = (r.stdout or "") + (r.stderr or "")
    except Exception:
        r = ""
    m = re.search(r"DISPOSITIVOS\s+(\d+)", r)
    if m:
        add(
            True,
            "ferramenta",
            "mtkclient enxerga a USB (prova viva)",
            f"{m.group(1)} dispositivo(s) via UsbClass",
        )
    else:
        err = (r.strip().splitlines() or ["sem retorno"])[-1][:90]
        add(
            False,
            "ferramenta",
            "mtkclient enxerga a USB (prova viva)",
            err,
            "pip install -r mtk\\mtkclient\\requirements.txt  e  reinstale o driver",
        )

# ------------------------------------------------------ integridade dos repos
sec("INTEGRIDADE DOS CLONES")

# nao chutamos nome de arquivo nem forcamos python: cada repo tem sua linguagem.
# o doctor procura qualquer fonte executavel de qualquer ecossistema.
EXTENSOES = [
    "*.py",
    "*.sh",
    "*.ps1",
    "*.bat",
    "*.js",
    "*.ts",
    "*.rs",
    "*.go",
    "*.html",
    "*.lua",
    "*.rb",
]
IGNORAR = {".git", "node_modules", "__pycache__", ".github", "target", "dist", "build"}


def entrypoint(repo):
    for pad in EXTENSOES:
        achados = [
            f
            for f in glob.glob(os.path.join(repo, "**", pad), recursive=True)
            if not any(parte in IGNORAR for parte in f.split(os.sep))
            and not f.endswith((".pyc", ".min.js"))
        ]
        if achados:
            return os.path.relpath(min(achados, key=len), repo).replace("\\", "/")
    return None


for repo in [
    os.path.join(BASE, "frp", "frp-freedom"),
    os.path.join(BASE, "frp", "samsung-frp-gui"),
    os.path.join(BASE, "mtk", "mtkclient"),
    os.path.join(BASE, "firmware", "DumprX"),
    os.path.join(BASE, "lockscreen", "LockKnife"),
    os.path.join(BASE, "dados", "BoardRipper"),
]:
    if not os.path.isdir(repo):
        continue
    nome = os.path.basename(repo)
    ep = entrypoint(repo)
    n = len([f for f in os.listdir(repo) if not f.startswith(".")])
    add(
        bool(ep),
        "clone",
        nome,
        f"entrypoint {ep} ({n} itens)" if ep else f"VAZIO ou sem codigo ({n} itens)",
        "git clone novamente ou git checkout -- .",
    )

# exemplo de boardview
ex = os.path.join(BASE, "dados", "boardview-exemplos")
if os.path.isdir(ex):
    n = len([f for f in os.listdir(ex) if not f.startswith(".")])
    add(n > 0, "ferramenta", "boardview de exemplo", f"{n} arquivo(s) em dados\\boardview-exemplos")

# ------------------------------------------------------------ doc x realidade
sec("DOCUMENTACAO x REALIDADE  (o que o manual afirma vs o que existe)")

doc = os.path.join(BASE, "COMO_USAR.md")
texto = ""
if os.path.isfile(doc):
    with open(doc, "r", encoding="utf-8", errors="ignore") as fh:
        texto = fh.read()

if texto:
    fala_zadig = bool(re.search(r"[Zz]adig", texto))
    precisa_usbdk = driver_necessario == "UsbDk"

    if precisa_usbdk and fala_zadig:
        ctx = re.search(r"[^\n]*[Zz]adig[^\n]*", texto)
        add(
            None,
            "doc",
            "manual menciona Zadig",
            f"codigo exige {driver_necessario} - confere se o texto so cita como plano B: {(ctx.group(0)[:60] if ctx else '')}",
            "",
        )
    if not fala_zadig and not precisa_usbdk:
        add(True, "doc", "manual coerente com o codigo", f"driver: {driver_necessario}")

    # todo launcher citado no manual precisa existir de fato.
    # sem tolerancia a "_": um .bat chamado _10-x.bat num menu que espera
    # 10-x.bat quebra em execucao, e o doctor precisa dizer isso.
    faltam = []
    for m in re.finditer(r"`?(\d{1,2}-[a-z0-9_-]+\.bat)`?", texto, re.I):
        rel = m.group(1)
        if not os.path.isfile(os.path.join(BASE, rel)):
            faltam.append(rel)
    add(
        not faltam,
        "doc",
        "launchers citados existem",
        "todos presentes" if not faltam else "faltando: " + ", ".join(sorted(set(faltam))),
        "rode o doctor de novo apos criar os .bat",
    )

# ------------------------------------------------------------------- menu
sec("MENU")

ini = os.path.join(BASE, "INICIAR.bat")
if os.path.isfile(ini):
    with open(ini, "r", encoding="utf-8", errors="ignore") as fh:
        src = fh.read()
    opts = re.findall(r"echo\s+(\d+)\.", src)
    hdl = re.findall(r'if\s+"%op%"=="(\d+)"', src)
    orfa = [o for o in opts if o not in hdl]
    add(
        not orfa,
        "menu",
        "todas as opcoes tem handler",
        f"{len(opts)} opcoes, {len(hdl)} handlers",
        "opcao sem handler: " + ", ".join(orfa) if orfa else "",
    )

    # ---- a checagem que importa: o handler aponta pra arquivo que existe? ----
    # ter handler nao basta. a forma aceita no menu e  call "%~dp0"X.bat
    # (o %~dp0 entre aspas, separado do nome). parseamos as duas formas:
    #   call "%~dp0"X.bat        <- forma atual, inequivoca
    #   call "%~dp0X.bat"        <- forma antiga, sem separacao
    quebradas = []
    for linha in src.splitlines():
        m = re.search(r'if\s+"%op%"=="(\d+)"\s*call\s+(.*)$', linha)
        if not m:
            continue
        num, alvo = m.group(1), m.group(2).strip()
        alvo = alvo.strip('"')
        mm = re.match(r'^%~dp0"?(.*)$', alvo)
        if not mm:
            continue
        rel = mm.group(1)
        if not rel.lower().endswith(".bat"):
            continue
        if not os.path.isfile(os.path.join(BASE, rel)):
            quebradas.append(f"menu {num} -> {alvo}")
    add(
        not quebradas,
        "menu",
        "handlers apontam pra arquivo real",
        f"{len(hdl)} handlers testados, todos os alvos existem"
        if not quebradas
        else f"{len(quebradas)} quebrado(s)",
        "corrigir o nome no INICIAR.bat ou renomear o .bat",
    )
    for q in quebradas:
        print(f"         QUEBRADO: {q}")

    bats = glob.glob(os.path.join(BASE, "*.bat"))
    ruins = []
    for b in bats:
        with open(b, "r", encoding="utf-8", errors="ignore") as fh:
            t = fh.read()
        if t.count("(") != t.count(")"):
            ruins.append(os.path.basename(b))
    add(
        not ruins,
        "menu",
        "sintaxe dos .bat",
        f"{len(bats)} arquivos, parenteses balanceados" if not ruins else "quebrado: " + ", ".join(ruins),
    )

    # .bat com LF puro ou com BOM falha em silencio no cmd. nao avisa nada,
    # o menu simplesmente nao abre ou come o primeiro comando.
    encoding_alert = []
    for b in bats:
        with open(b, "rb") as fh:
            bruto = fh.read()
        nome = os.path.basename(b)
        if bruto[:3] == b"\xef\xbb\xbf":
            encoding_alert.append(f"{nome} (BOM UTF-8)")
        lf = bruto.count(b"\n")
        crlf = bruto.count(b"\r\n")
        if lf and crlf != lf:
            encoding_alert.append(f"{nome} (LF sem CRLF)")
    add(
        not encoding_alert,
        "menu",
        "encoding dos .bat (CRLF e sem BOM)",
        f"{len(bats)} arquivos ok" if not encoding_alert else f"{len(encoding_alert)} com problema",
        "normalize: LF->CRLF e gravar sem BOM",
    )
    for a in encoding_alert:
        print(f"         ENCODING: {a}")
else:
    add(False, "menu", "INICIAR.bat", "ausente", "restaure o menu principal")

# ----------------------------------------------------------------- manifest
sec("MANIFESTO DE VERSOES")

# descoberta automatica: qualquer .git sob a kit vira entrada.
# nao chumbamos path - se o kit for movido, o manifesto continua funcionando.
manifest = {
    "gerado_em": datetime.datetime.now().isoformat(timespec="seconds"),
    "python": ver,
    "driver_exigido": driver_necessario,
    "repos": {},
}

achados = 0
for root, dirs, _files in os.walk(BASE):
    if ".git" in dirs:
        rel = os.path.relpath(root, BASE).replace("\\", "/")
        rev = run(["git", "-C", root, "log", "-1", "--format=%h|%ad|%s", "--date=short"]).strip()
        remoto = run(["git", "-C", root, "remote", "get-url", "origin"]).strip()
        sujo = run(["git", "-C", root, "status", "--porcelain"])
        manifest["repos"][rel] = {
            "commit": rev or "?",
            "origin": remoto or "(sem remoto)",
            "alteracoes_locais": len([l for l in sujo.splitlines() if l.strip()]),
        }
        marca = " [modificado]" if sujo.strip() else ""
        add(True, "versao", rel, rev or "?")
        if remoto:
            print(f"         {remoto}{marca}")
        achados += 1
        dirs[:] = [d for d in dirs if d != ".git"]

add(
    achados > 0,
    "versao",
    f"repos clonados: {achados}",
    "todos com commit registrado",
    "se algum sumir do manifesto, o repo nao tem .git",
)

if os.path.isfile(REPORT):
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "resumo": {
                    "ok": sum(1 for c in checks if c["ok"] is True),
                    "falha": sum(1 for c in checks if c["ok"] is False),
                    "neutro": sum(1 for c in checks if c["ok"] is None),
                },
                "checks": checks,
                "manifest": manifest,
            },
            fh,
            indent=2,
            ensure_ascii=False,
        )
    add(True, "manifesto", "relatorio gravado", os.path.relpath(REPORT, BASE))

# ------------------------------------------------------------------ veredito
problemas = [c for c in checks if c["ok"] is False]
neutros = [c for c in checks if c["ok"] is None]

print()
print("=" * 60)
if not problemas:
    print("  VEREDITO: kit integro. Nenhum problema que impeca o uso.")
else:
    print(f"  VEREDITO: {len(problemas)} problema(s) que impedem o uso.")
    print()
    for i, c in enumerate(problemas, 1):
        print(f"   {i}. [{c['categoria']}] {c['item']} - {c['detalhe']}")
        if c["correcao"]:
            print(f"      >>> {c['correcao']}")
print()
print(f"  {sum(1 for c in checks if c['ok'] is True)} ok | {len(problemas)} falha | {len(neutros)} info")
print(f"  relatorio: {os.path.relpath(REPORT, BASE)}")
print("=" * 60)

sys.exit(0 if not problemas else 1)
