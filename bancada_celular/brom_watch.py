import re
import subprocess
import sys
import time
import winsound

CTL = r"C:\Program Files\UsbDk Runtime Library\UsbDkController.exe"
TARGET = re.compile(r"0e8d", re.I)

print("=" * 60)
print("  MODO BROM - monitor de conexao")
print("=" * 60)
print()
print("  Deixando o celular DESLIGADO e sem bateria,")
print("  segure vol+ e vol- e conecte o cabo.")
print()
print("  Procurando MediaTek 0E8D... (Ctrl+C para sair)")
print()

deadline = time.time() + 300
seen = set()

while time.time() < deadline:
    try:
        out = subprocess.run(
            [CTL, "-n"], capture_output=True, text=True, timeout=15
        ).stdout
    except Exception:
        time.sleep(0.4)
        continue

    ids = re.findall(r"ID:\s*([0-9a-f]{4}):([0-9a-f]{4})", out, re.I)
    for vid, pid in ids:
        key = (vid, pid)
        if key not in seen:
            seen.add(key)
            tag = "  <== MEDIA TEK / BROM!" if vid.lower() == "0e8d" else ""
            print(f"  {time.strftime('%H:%M:%S')}  {vid}:{pid}{tag}")

    if TARGET.search(out):
        print()
        print("=" * 60)
        print("  BROM DETECTADO - 0x0E8D")
        print("=" * 60)
        print()
        print("  Pode soltar os botoes de volume.")
        print("  Deixe o cabo conectado e abra o menu 6 do kit.")
        print()
        for _ in range(3):
            winsound.Beep(1400, 250)
            time.sleep(0.35)
        sys.exit(0)

    time.sleep(0.4)

print()
print("  Tempo esgotado (5 min) sem 0x0E8D.")
print("  Dicas: bateria totalmente desconectada, cabo de dados,")
print("  segure vol+ E vol- juntos, so depois conecte.")
sys.exit(1)
