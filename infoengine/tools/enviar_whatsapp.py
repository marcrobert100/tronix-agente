"""
Envio via WhatsApp — InfoEngine
Envia templates, PDFs e mensagens pelo WhatsApp.

Modos:
  --link   : Gera link wa.me (padrão, não requer dependências)
  --auto   : Envio automático via pywhatkit (requer Chrome + pywhatkit)

Uso:
  python enviar_whatsapp.py --numero 5582991856656 --mensagem "Olá!"
  python enviar_whatsapp.py --numero 5582991856656 --arquivo ../templates/infantil/o-dragao-que-aprendeu-a-abracar.html
  python enviar_whatsapp.py --numero 5582991856656 --mensagem "Veja isto!" --link
  python enviar_whatsapp.py --numero 5582991856656 --auto
"""

import argparse
import os
import subprocess
import sys
import webbrowser

NUMERO_PADRAO = "5582991856656"


def gerar_link_wa(numero, mensagem=None):
    """Gera link wa.me para compartilhamento manual."""
    url = f"https://wa.me/{numero}"
    if mensagem:
        from urllib.parse import quote
        url += f"?text={quote(mensagem)}"
    return url


def enviar_link(numero, mensagem=None):
    """Abre wa.me no navegador padrão."""
    url = gerar_link_wa(numero, mensagem)
    print(f"Abrindo WhatsApp...")
    print(f"Link: {url}")
    webbrowser.open(url)
    return True


def enviar_auto(numero, mensagem, arquivo=None):
    """Envio automático via pywhatkit."""
    try:
        import pywhatkit
    except ImportError:
        print("ERRO: pywhatkit não instalado.")
        print("Instale com: pip install pywhatkit")
        print("Requer Chrome instalado e WhatsApp Web logado.")
        return False

    try:
        if arquivo and os.path.exists(arquivo):
            ext = os.path.splitext(arquivo)[1].lower()
            if ext in (".jpg", ".jpeg", ".png", ".gif"):
                pywhatkit.sendwhats_image(numero, arquivo, mensagem, 15)
                print(f"Imagem enviada: {arquivo}")
            else:
                print("Envio automático de arquivos não-imagem suporta apenas link wa.me.")
                print(f"Use --link para compartilhar o arquivo via link.")
                url = gerar_link_wa(numero, f"{mensagem}\n\n{arquivo}")
                webbrowser.open(url)
        else:
            hora = int(__import__('datetime').datetime.now().strftime("%H"))
            minuto = int(__import__('datetime').datetime.now().strftime("%M")) + 2
            pywhatkit.sendwhatmsg(numero, mensagem, hora, minuto)
            print(f"Mensagem agendada para {hora}:{minuto}")
        return True
    except Exception as e:
        print(f"ERRO no envio automático: {e}")
        print("Fallback: abrindo link wa.me...")
        return enviar_link(numero, mensagem)


def listar_templates(diretorio="..\\templates"):
    """Lista templates disponíveis para envio."""
    base = os.path.join(os.path.dirname(__file__), diretorio)
    if not os.path.exists(base):
        print(f"Diretório não encontrado: {base}")
        return []
    templates = []
    for root, dirs, files in os.walk(base):
        for f in files:
            if f.endswith(".html"):
                templates.append(os.path.join(root, f))
    return templates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Envio via WhatsApp — InfoEngine")
    parser.add_argument("--numero", default=NUMERO_PADRAO, help="Número com código do país (ex: 5582991856656)")
    parser.add_argument("--mensagem", default="", help="Texto da mensagem")
    parser.add_argument("--arquivo", help="Caminho do arquivo para compartilhar")
    parser.add_argument("--link", action="store_true", default=True, help="Modo link wa.me (padrão)")
    parser.add_argument("--auto", action="store_true", help="Modo automático via pywhatkit")
    parser.add_argument("--listar", action="store_true", help="Listar templates disponíveis")

    args = parser.parse_args()

    if args.listar:
        print("=== Templates Disponíveis ===")
        for t in listar_templates():
            print(f"  {t}")
        sys.exit(0)

    if not args.mensagem and not args.arquivo:
        args.mensagem = "Olá! Vi isto no InfoEngine e achei que você gostaria de ver. 🚀"

    if args.arquivo:
        if not os.path.exists(args.arquivo):
            print(f"Arquivo não encontrado: {args.arquivo}")
            sys.exit(1)
        args.mensagem += f"\n\n{os.path.basename(args.arquivo)}"
        url = gerar_link_wa(args.numero, args.mensagem)
        print(f"Link gerado: {url}")
        print("Copie o link acima e cole no navegador ou no WhatsApp.")
        webbrowser.open(url)
    elif args.auto:
        enviar_auto(args.numero, args.mensagem, args.arquivo)
    else:
        enviar_link(args.numero, args.mensagem)

    print("\nDica: Após abrir o WhatsApp, selecione o contato e envie.")
