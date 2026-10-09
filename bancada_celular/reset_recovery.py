"""
Bancada Celular - Reset de fabrica guiado via recovery
=====================================================
Rota de maior rendimento e menor risco do kit: nao exige BROM, nao
exige EDL, nao exige cracker, nao exige conta de programacao.

  >>> AVISO CRITICO <<<
Reset de fabrica SEMPRE dispara o FRP (Factory Reset Protection).
O Google exige no primeiro boot a conta que estava no aparelho.
Se o cliente nao tem a senha dessa conta NA MAO, o reset nao
resolve o problema dele: transforma "esqueci a senha" em "perdi
a senha E os dados". Nao faca reset sem confirmar antes.
"""

import re
import subprocess
import sys
import time

BASE = r"C:\xampp\htdocs\agente\bancada_celular"
ADB = r"C:\Users\CHCONTE RECPÇÃO\AppData\Local\Android\Sdk\platform-tools\adb.exe"

# como entrar no recovery de cada marca (o 原 differ e muito)
COMBOS = {
    "Xiaomi": ("segure VOL+ e POWER juntos ate vibrar, solte no logo Mi",
               "no logo, aperte VOL+ de novo, nao POWER"),
    "Redmi": ("segure VOL+ e POWER juntos ate vibrar, solte no logo Mi",
              "no logo, aperte VOL+ de novo, nao POWER"),
    "Samsung": ("segure VOL+ e BIXBY e POWER juntos (ou HOME se tiver botao home)",
                "no logo Samsung, aperte VOL+ + BIXBY por 1 segundo e solte"),
    "Motorola": ("segure VOL- e POWER. Vai entrar no FASTBOOT, nao recovery",
                 "no fastboot, aperte VOL- duas vezes e depois POWER"),
    "LG": ("segure VOL+ e VOL- e POWER. Solte so o POWER",
           "solte os dois volumes quando aparecer o logo"),
    "Asus": ("segure VOL- e POWER ate o logo, ou POWER + VOL+ + HOME",
             "no logo, segure VOL+ e aperte POWER"),
    "Realme": ("segure VOL- e POWER ate o logo",
               "no logo, aperte VOL- de novo, nao POWER"),
    "Oppo": ("segure VOL- e POWER ate o logo",
             "no logo, aperte VOL- de novo, nao POWER"),
    "OnePlus": ("segure VOL- e POWER ate o logo",
                "no fastboot, aperte VOL+ por 1 segundo e solte (nao POWER)"),
    "Huawei": ("segure VOL- e POWER ate o logo",
               "no logo, aperte VOL+ de novo, nao POWER"),
}

GENERICO = ("segue o manual da marca: Usually 'ligar + volume'",
            "procure 'seu modelo + recovery mode' no YouTube antes de forcar")


def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return ((r.stdout or "") + (r.stderr or "")).strip()
    except Exception as e:
        return ""


def adb(*args, timeout=30):
    return run([ADB] + list(args), timeout)


def t(titulo):
    print()
    print("=" * 62)
    print(f"  {titulo}")
    print("=" * 62)


def p(msg=""):
    print(msg)


def sim(txt):
    if not txt:
        return False
    return "yes" in txt.lower() or "true" in txt.lower()


def ask(pergunta):
    try:
        return input(pergunta).strip()
    except EOFError:
        return ""


# ------------------------------------------------------------------ detectar
t("1. DETECTANDO O APARELHO")

d = adb("devices", "-l")
ser = ""
for linha in d.splitlines()[1:]:
    p = linha.split()
    if len(p) >= 2 and p[1] == "device":
        ser = p[0]
        break

if not ser:
    p("  Nenhum aparelho autorizado no ADB.")
    p("  Ligue a depuracao USB na tela de bloqueio e conecte o cabo.")
    p("  (Sem ADB a gente ainda faz o reset, so que na mao. Segue as instrucoes")
    p("   do passo 3 e volta depois para conferir.)")
    p("")
    p("  Sem ADB, pule para o passo 3: as instrucoes por marca estao no manual.")
    sys.exit(1)

p(f"  aparelho: {ser}")

marca = adb("shell", "getprop", "ro.product.brand")
modelo = adb("shell", "getprop", "ro.product.model")
android = adb("shell", "getprop", "ro.build.version.release")
p(f"  marca   : {marca}")
p(f"  modelo  : {modelo}")
p(f"  android : {android}")

# --------------------------------------------------------- preflight FRP
t("2. PRE-FLIGHT  (a parte que evitaoday o preco de voce errar")

conta_google = ""
for m in re.finditer(r"([\w.+-]+@[\w-]+\.[\w.]+)", adb("shell", "dumpsys", "account", "|", "head", "-40")):
    conta_google = m.group(1)
    if "google" in conta_google.lower() or "gmail" in conta_google.lower():
        break

p(f"  conta Google no aparelho: {conta_google or '(nao encontrada / sem permissao)'}")

frp_ativo = sim(adb("shell", "settings", "get", "secure", "frp_management_permission")
                if False else adb("shell", "getprop", "ro.frp.pbt.dm"))

adb_ligado = adb("shell", "settings", "get", "global", "adb_enabled")
p(f"  depuracao USB: {adb_ligado}")

p("")
p("  >>> ESTE E O PONTO QUE MAIS CUSTA CARO NA BANCADA <<<")
p("")
p("  Reset de fabrica -> aparelho pede conta Google no primeiro boot.")
p("  Se o cliente NAO tem a senha dessa conta, voce:")
p("     1. apagou o aparelho inteiro")
p("     2. deixou ele sem como usar")
p("     3. tem que fazer FRP service, que e mais caro e nem sempre funciona")
p("")
p("  CONFIRME COM O CLIENTE, AGORA, ANTES DE APAGAR:")
p("     'O senhor tem a senha do e-mail do Google com acesso a esse celular? SIM ou NAO'")
p("")

tem_senha = ask("  Cliente tem a senha do Google na mao? (digite SIM ou NAO): ").upper()

if not tem_senha.startswith("S"):
    p("")
    p("  >>> PARA. NAO RESETA. <<<")
    p("")
    p("  Sem a senha do Google nao tem reset que salve esse caso. Voce")
    p("  apaga os dados E cria o problema de FRP. O caminho agora:")
    p("     a) recuperar a senha do Google com o proprio cliente (google.com/find,")
    p("        support.google.com/accounts) - isso e gratuito, so demora")
    p("     b) ou o servico de FRP, que e outro preco, outra conversa")
    p("")
    p("  Vou gerar as orientacoes de FRP e encerrar sem apagar nada.")
    with open(BASE + r"\logs\reset_aviso_frp.txt", "w", encoding="utf-8") as f:
        f.write(f"RESET BLOQUEADO - cliente sem senha do Google\n")
        f.write(f"aparelho: {ser} {marca} {modelo}\n")
        f.write(f"conta no aparelho: {conta_google}\n")
    p("  Registro salvo em logs\\reset_aviso_frp.txt")
    sys.exit(2)

# --------------------------------------------------------------- backup
p("")
fazer_backup = ask("  Fazer backup do /sdcard antes de apagar? (digite SIM): ").upper()
pasta = None
if fazer_backup.startswith("S"):
    import datetime
    pasta = f"C:\\Users\\CHCONTE RECPÇÃO\\Desktop\\backup_{modelo.strip().replace(' ','')}_{datetime.datetime.now():%Y%m%d_%H%M}"
    p(f"  baixando para: {pasta}")
    r = adb("pull", "/sdcard", pasta, timeout=1800)
    ok = "files pulled" in r
    p(f"  resultado: {'OK' if ok else 'FALHOU - confira: ' + r[:120]}")
    if not ok:
        p("  O backup falhou. Nao continue sem ele: reset apaga e nao volta.")
        sys.exit(3)
else:
    p("  Sem backup. Sem volta. (cliente avisado)")

# --------------------------------------------------------------- confirmacao
t("3. CONFIRMACAO FINAL")

p("  Vai apagar TUDO do aparelho:")
p("     - fotos, videos, contatos, conversas, apps, senhas salvas")
p("     - o aparelho volta como se acabou de sair da caixa")
p("")
p("  Confirmando que o cliente esta ciente e autorizou:")
p("")
digite = ask("  Digite APAGAR TUDO para confirmar: ")
if digite.strip().upper() != "APAGAR TUDO":
    p("  Cancelado. Nada foi apagado.")
    sys.exit(0)

# --------------------------------------------------------------- recovery
t("4. ENTRANDO NO RECOVERY")

chave = COMBOS.get(marca.strip(), GENERICO)
p(f"  Para {marca} {modelo}:")
p("")
p(f"  1) Desligue o aparelho por 15 segundos")
p(f"  2) {chave[0]}")
p(f"  3) {chave[1]}")
p("  4) Vai aparecer MENU (Recovery). Se vier 'ERRO' ou 'SDCARD', PARE")
p("")
p("  No menu do recovery, navegue com os VOLUMES e confirme com o POWER:")
p("")
p("     'Wipe Data' / 'Apagar Dados'  ->  'Wipe All Data' / 'Factory Reset'")
p("     ->  'Yes' / 'Confirm'")
p("")
p("  >> vai demorar 5 a 20 minutos e parecer travado. NAO tire o cabo. <<")
p("")
input("  Aperte ENTER aqui depois que a tela mostrar 'Wipe data done'... ")

t("5. APARECENDO O DEPOIS")

p("  1) O aparelho vai reiniciar sozinho no '_factory_ ou em 'Hello'")
p("  2) Vai aparecer a tela de boas-vindas (config inicial)")
p("  3) Se aparecer 'Verificacao' / 'Find My Mi account' / conta Google:")
p("     NAO É FRP ainda, é a verificacao de fabrica. Repita a conta do cliente.")
p("  4) Se pedir conta Google E o cliente nao tem: é FRP de verdade. Volte aqui.")
p("  5) Configure normally. Depois teste: ligou, rede, camera, som.")
p("")
p("  Cliente|DEVE| ter anotado a conta Google no verso da OS antes de sair da loja.")
p("")

p("  Quer que eu reconecte e verifique o aparelho agora? (S/N)")
if ask("  ").upper().startswith("S"):
    p("  aguardando o aparelho subir...")
    for _ in range(60):
        time.sleep(3)
        if "device" in adb("devices"):
            p("  aparelho de volta no sistema.")
            p("  build: " + adb("shell", "getprop", "ro.build.version.incremental"))
            p("  conta agora: " + (adb("shell", "dumpsys", "account", "|", "grep", "name=")[:100] or "(nenhuma)"))
            break
    else:
        p("  ainda nao subiu. Verifique se eleAsk para a tela de boas-vindas (normal).")

p("")
p("  Fim.")
input("  ENTER para sair. ")
