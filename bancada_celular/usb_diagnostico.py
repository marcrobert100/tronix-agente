import logging
import sys

sys.path.insert(0, r"C:\xampp\htdocs\agente\bancada_celular\mtk\mtkclient")

from mtkclient.Library.Connection.usblib import UsbClass

NAMES = {
    (0x0E8D, None): "MediaTek (BROM/preloader)",
    (0x2717, 0xFF48): "Xiaomi Redmi 6A",
    (0x0BDA, 0x8178): "Realtek RTL8192CU wifi",
    (0x0461, 0x0010): "Logitech/teclado",
    (0x10C4, 0x0005): "Silicon Labs CP210x",
    (0x8087, 0x0024): "Intel Bluetooth",
}


def usb_name(vid, pid):
    if vid is None:
        return "?"
    for (v, p), n in NAMES.items():
        if v == vid and (p is None or p == pid):
            return n
    return "desconhecido"


logging.getLogger().handlers = []
u = UsbClass(logging.INFO, devclass=-1)

print("--- detectdevices: VID/PID visiveis via pyusb+libusb ---")
try:
    devs = u.detectdevices()
    print("TOTAL:", len(devs) if devs else 0)
    for d in (devs or []):
        vid = getattr(d, "vid", None)
        pid = getattr(d, "pid", None)
        print(f"    VID={vid} PID={pid}  {usb_name(vid, pid)}")
        if vid == 0x0E8D:
            print("       ^^^ MEDIA TEK detectado")
except Exception as e:
    print("ERRO:", type(e).__name__, e)

print()
print("--- backend em uso ---")
print("libusb1 :", u.backend)
