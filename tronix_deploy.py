import zipfile
import os

ARQUIVOS = ['tronix_core.json', '.env', 'tronix_seguro.py', 'tronix_log_seguro.py']
OUTPUT = 'tronix_deploy.zip'

def criar_deploy():
    with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arquivo in ARQUIVOS:
            if os.path.exists(arquivo):
                zipf.write(arquivo)
                print(f"Adicionado: {arquivo}")
            else:
                print(f"ERRO: {arquivo} não encontrado")
    
    info = os.path.getsize(OUTPUT)
    print(f"\nDeploy gerado: {OUTPUT} ({info} bytes)")
    return OUTPUT

if __name__ == "__main__":
    criar_deploy()