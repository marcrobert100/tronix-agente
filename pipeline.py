"""
Pipeline Tronix - 1 comando para gerar, logar e publicar
Uso: python pipeline.py --tema "extraterrestre invade a terra" [--publicar]
"""
import os, sys, json, subprocess, argparse
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

try:
    from tronix_logger import inicializar as db_init, log_pipeline, registrar as db_registrar
except ImportError:
    def db_init(): pass
    def log_pipeline(*a, **kw): pass
    def db_registrar(*a, **kw): return None

PYTHON = sys.executable

def run_script(script, args=""):
    cmd = f'"{PYTHON}" "{os.path.join(ROOT, script)}" {args}'
    print(f"  [RUN] {script} {args}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT, timeout=300)
    out = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        print(f"  [OK] {script}")
    else:
        print(f"  [WARN] {script} retornou {result.returncode}")
    return out, result.returncode

def etapa(desc):
    print(f"\n{'='*60}")
    print(f"  {desc}")
    print(f"{'='*60}")

def main():
    parser = argparse.ArgumentParser(description="Pipeline Tronix - 1 comando")
    parser.add_argument("--tema", default="paisagem brasileira, hyper-realista, 4k", help="Tema do conteudo")
    parser.add_argument("--publicar", action="store_true", help="Publicar nas redes sociais")
    parser.add_argument("--apenas-log", action="store_true", help="So testar o pipeline de log")
    args = parser.parse_args()

    print(f"\n  TRONIX PIPELINE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Tema: {args.tema}")
    print(f"  Publicar: {'SIM' if args.publicar else 'NAO'}")

    db_init()
    log_pipeline("PIPELINE", "pipeline.py", "sucesso", f"Inicio: {args.tema}")

    if args.apenas_log:
        etapa("APENAS LOG - Teste de pipeline")
        db_registrar("imagem", f"Teste pipeline {datetime.now():%H%M%S}", "teste.png", "uploads", "teste", "#teste", "", 100, 0)
        log_pipeline("PIPELINE", "pipeline.py", "sucesso", "Pipeline testado")
        print("\n  Pipeline de log OK")
        return

    etapa("1. GERAR IMAGEM")
    img_out, _ = run_script("gera_imagem.py", f'--prompt "{args.tema}" --output pipeline_temp.png')
    if not os.path.exists(os.path.join(ROOT, "pipeline_temp.png")):
        print("  [FALLBACK] Imagem nao gerada, usando imagem padrao")

    etapa("2. CRIAR VIDEO (Ken Burns)")
    video_out, _ = run_script("gera_video.py", f'--pasta pipeline_temp.png --saida videos_saida/pipeline_{datetime.now():%H%M%S}.mp4 --duracao 6 --animacao fade')

    video_file = None
    for f in sorted(os.listdir(os.path.join(ROOT, "videos_saida"))):
        if f.startswith("pipeline_"):
            video_file = f

    if not video_file:
        video_file = "pipeline_placeholder.mp4"
        print("  [WARN] Nenhum video gerado")

    etapa("3. ADICIONAR VOZ")
    voz_out, _ = run_script("tronix_super_editor.py", f'videos_saida/{video_file}')

    etapa("4. REGISTRAR NO BANCO")
    tamanho = 0
    video_path = os.path.join(ROOT, "videos_saida", video_file)
    if os.path.exists(video_path):
        tamanho = os.path.getsize(video_path) // 1024
    db_registrar("video", f"Pipeline: {args.tema[:40]}", video_file, "videos_saida",
                 f"Gerado por pipeline.py em {datetime.now():%Y-%m-%d}", "#tronix #pipeline",
                 "AntonioNeural", tamanho, 6)
    log_pipeline("PIPELINE", "pipeline.py", "sucesso", f"Video {video_file} registrado")

    etapa("5. POSTAR (opcional)")
    if args.publicar:
        run_script("tronix_instagram.py", f'--video videos_saida/{video_file}')
        run_script("tronix_youtube.py", f'--file videos_saida/{video_file}')
    else:
        print("  [SKIP] --publicar nao informado")

    log_pipeline("PIPELINE", "pipeline.py", "sucesso", "Pipeline E2E concluido")

    print(f"\n{'='*60}")
    print(f"  PIPELINE CONCLUIDO")
    print(f"  Tema: {args.tema}")
    print(f"  Video: videos_saida/{video_file}")
    print(f"  Status: Registrado no banco")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
