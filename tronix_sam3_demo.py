"""
TRONIX SAM 3 Demo - Segmentação por texto com SAM 3 + ComfyUI
Integrado ao ecossistema TRONIX via MCP Server

Uso:
  python tronix_sam3_demo.py --frame frame.jpg --prompt "Zé, o entregador"
  python tronix_sam3_demo.py --video video.mp4 --prompt "bola de futebol"
  python tronix_sam3_demo.py --status              # verifica se SAM 3 pode rodar
"""

import sys, os, json, argparse, subprocess, tempfile, time, uuid
from pathlib import Path

sys.path.insert(0, r'C:\xampp\htdocs\agente\ComfyUI')

DESKTOP = r'C:\Users\CHCONTE RECPÇÃO\Desktop\Tronix'
FFMPEG = r'C:\Users\CHCONTE RECPÇÃO\AppData\Local\Programs\TRAE SOLO\resources\app\bin\ffmpeg.exe'
FFPROBE = r'C:\Users\CHCONTE RECPÇÃO\AppData\Local\Programs\TRAE SOLO\resources\app\bin\ffprobe.exe'

try:
    import torch
    HAS_CUDA = torch.cuda.is_available()
    TORCH_VER = torch.__version__
except:
    HAS_CUDA = False
    TORCH_VER = "0.0.0"

SAM3_AVAILABLE = False
SAM3_ERROR = ""

def check_sam3():
    global SAM3_AVAILABLE, SAM3_ERROR
    try:
        from comfy.ldm.sam3.detector import SAM3Model
        SAM3_AVAILABLE = True
        SAM3_ERROR = ""
        return True
    except Exception as e:
        SAM3_ERROR = str(e)
        return False

def extract_frames(video_path, output_dir, fps=1):
    prefix = os.path.join(output_dir, "frame_%04d.jpg")
    r = subprocess.run([
        FFMPEG, '-y', '-i', video_path,
        '-vf', f'fps={fps}',
        '-q:v', '2', prefix
    ], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"ERRO extrair frames: {r.stderr[-200:]}")
        return []
    frames = sorted(Path(output_dir).glob("frame_*.jpg"))
    return [str(f) for f in frames]

def segment_frame_sam3(frame_path, prompt):
    """
    Segmenta objetos em um frame usando SAM 3.
    Retorna lista de {mask, box, score, label}
    """
    from PIL import Image, ImageDraw
    from comfy.ldm.sam3.detector import SAM3Model
    from comfy.model_base import SAM3
    from comfy.model_management import load_model_gpu

    device = torch.device('cuda' if HAS_CUDA else 'cpu')
    print(f"  Device: {device}")

    print(f"  Carregando modelo SAM 3...")
    model = SAM3Model()
    img = Image.open(frame_path).convert('RGB')
    W, H = img.size
    img_tensor = torch.tensor(list(img.getdata())).reshape(H, W, 3).permute(2, 0, 1).float() / 255.0
    img_tensor = img_tensor.unsqueeze(0).to(device)

    print(f"  Prompt: '{prompt}'")
    results = model.forward(
        img_tensor,
        text_prompts=[prompt],
        device=device
    )

    output = []
    for r in results:
        output.append({
            "mask": r.get("mask", None),
            "box": r.get("box", None),
            "score": float(r.get("score", 0)),
            "label": prompt
        })
    return output

def draw_segmentation(frame_path, results, output_path):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.open(frame_path).convert('RGB')
    draw = ImageDraw.Draw(img, 'RGBA')

    try:
        fnt = ImageFont.truetype('arialbd.ttf', 16)
    except:
        fnt = ImageFont.load_default()

    if not results:
        draw.text((10, 10), f"Nada encontrado para o prompt", fill=(255, 0, 0), font=fnt)
        img.save(output_path)
        print(f"  Salvo: {output_path}")
        return

    colors = [(255, 0, 0, 80), (0, 255, 0, 80), (0, 0, 255, 80), (255, 255, 0, 80)]
    for i, r in enumerate(results):
        color = colors[i % len(colors)]
        box = r.get("box")
        score = r.get("score", 0)
        label = r.get("label", "?")

        if box:
            x1, y1, x2, y2 = box
            bx1, by1, bx2, by2 = max(0, int(x1)), max(0, int(y1)), min(img.width, int(x2)), min(img.height, int(y2))
            draw.rectangle([bx1, by1, bx2, by2], outline=color[:3], width=3)
            draw.rectangle([bx1, by1, bx1 + len(label) * 10 + 10, by1 + 22], fill=(0, 0, 0, 180))
            draw.text((bx1 + 4, by1 + 2), f"{label} {score:.2f}", fill=(255, 255, 255), font=fnt)

        mask_data = r.get("mask")
        if mask_data is not None and hasattr(mask_data, '__len__') and len(mask_data) > 0:
            mask_overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            mask_draw = ImageDraw.Draw(mask_overlay)
            mask_draw.bitmap((0, 0), mask_data, fill=color)
            img = Image.alpha_composite(img.convert('RGBA'), mask_overlay)

    img.save(output_path)
    print(f"  Salvo: {output_path} ({len(results)} objetos)")

def demo_image(frame_path, prompt):
    """Exemplo 1: Segmentar objeto em uma imagem"""
    print(f"\n{'='*55}")
    print(f"  SAM 3 Demo - Segmentar frame")
    print(f"  Frame: {frame_path}")
    print(f"  Prompt: {prompt}")
    print(f"{'='*55}")

    if not SAM3_AVAILABLE:
        print(f"  SAM 3 NAO DISPONIVEL: {SAM3_ERROR}")
        print(f"  Solucao: rode ComfyUI em maquina com GPU NVIDIA + CUDA 12.6+")
        print(f"  Criando placeholder para demonstracao...")
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (854, 480), (30, 30, 50))
        draw = ImageDraw.Draw(img)
        try:
            fnt = ImageFont.truetype('arialbd.ttf', 18)
            fnt2 = ImageFont.truetype('arial.ttf', 14)
        except:
            fnt = ImageFont.load_default()
            fnt2 = fnt
        draw.text((427, 80), "SAM 3 - Segment Anything 3", fill=(255, 255, 100), font=fnt, anchor='mt')
        draw.text((427, 120), f"Prompt: '{prompt}'", fill=(200, 200, 200), font=fnt2, anchor='mt')
        draw.text((427, 160), f"GPU: {'DISPONIVEL' if HAS_CUDA else 'NAO DISPONIVEL (CPU-only)'}", fill=(200, 100, 100), font=fnt2, anchor='mt')
        draw.text((427, 200), f"PyTorch: {TORCH_VER}", fill=(200, 200, 200), font=fnt2, anchor='mt')
        draw.text((427, 240), "ComfyUI + SAM 3 integrados no codigo fonte", fill=(100, 200, 100), font=fnt2, anchor='mt')
        draw.text((427, 280), "Rode em maquina com GPU para inferencia real", fill=(100, 200, 100), font=fnt2, anchor='mt')
        output = os.path.join(DESKTOP, "sam3_demo_placeholder.png")
        img.save(output)
        print(f"  Placeholder salvo: {output}")
        return

    results = segment_frame_sam3(frame_path, prompt)
    output = os.path.join(DESKTOP, f"sam3_demo_{uuid.uuid4().hex[:8]}.png")
    draw_segmentation(frame_path, results, output)
    return output

def demo_video(video_path, prompt, max_frames=5):
    """Exemplo 2: Segmentar objetos em frames de video"""
    print(f"\n{'='*55}")
    print(f"  SAM 3 Demo - Segmentar video")
    print(f"  Video: {video_path}")
    print(f"  Prompt: {prompt}")
    print(f"{'='*55}")

    temp_dir = os.path.join(tempfile.gettempdir(), f"sam3_demo_{uuid.uuid4().hex[:8]}")
    os.makedirs(temp_dir, exist_ok=True)

    frames = extract_frames(video_path, temp_dir, fps=1)
    frames = frames[:max_frames]
    print(f"  Extraidos {len(frames)} frames")

    output_frames = []
    for i, fp in enumerate(frames):
        print(f"  Frame {i+1}/{len(frames)}: {Path(fp).name}")
        if SAM3_AVAILABLE:
            results = segment_frame_sam3(fp, prompt)
        else:
            results = []
        of = os.path.join(temp_dir, f"out_{Path(fp).name}")
        if SAM3_AVAILABLE:
            draw_segmentation(fp, results, of)
        else:
            from PIL import Image
            img = Image.open(fp)
            img.save(of)
            print(f"  (placeholders - sem GPU)")
        output_frames.append(of)

    final_video = os.path.join(DESKTOP, f"sam3_demo_video_{uuid.uuid4().hex[:8]}.mp4")
    if len(output_frames) > 0:
        list_file = os.path.join(temp_dir, "frames.txt")
        with open(list_file, 'w') as f:
            for fp in output_frames:
                f.write(f"file '{fp}'\n")
        subprocess.run([
            FFMPEG, '-y', '-f', 'concat', '-safe', '0',
            '-i', list_file,
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '22',
            '-pix_fmt', 'yuv420p', final_video
        ], capture_output=True, text=True, timeout=120)
        print(f"  Video final: {final_video}")
        subprocess.run([FFPROBE, '-v', 'quiet', '-show_entries',
                       'format=duration,size:stream=width,height,codec_name,codec_type',
                       final_video], capture_output=True, text=True)

def demo_status():
    """Exemplo 3: Verificar status do SAM 3"""
    print(f"\n{'='*55}")
    print(f"  TRONIX - SAM 3 Status Check")
    print(f"{'='*55}")
    print(f"  PyTorch: {TORCH_VER}")
    print(f"  CUDA:    {'DISPONIVEL' if HAS_CUDA else 'NAO DISPONIVEL'}")
    print(f"  ComfyUI SAM3: {'OK' if SAM3_AVAILABLE else 'ERRO: ' + SAM3_ERROR}")
    print(f"  Model weights: {'OK' if os.path.isdir(r'C:\xampp\htdocs\agente\ComfyUI\models\sam3') else 'NAO BAIXADOS'}")
    print(f"  GPU recomendada: NVIDIA com CUDA 12.6+")
    print(f"  Alternativa CPU: Possivel mas extremamente lento (848M params)")
    print(f"  Arquivos SAM3: {os.path.getsize(r'C:\xampp\htdocs\agente\ComfyUI\comfy\ldm\sam3\detector.py')/1024:.0f}KB detector.py")
    print(f"                  {os.path.getsize(r'C:\xampp\htdocs\agente\ComfyUI\comfy\ldm\sam3\tracker.py')/1024:.0f}KB tracker.py")
    print(f"                  {os.path.getsize(r'C:\xampp\htdocs\agente\ComfyUI\comfy\ldm\sam3\sam.py')/1024:.0f}KB sam.py")
    print(f"  Nos SAM3 ComfyUI: SAM3_Detect, SAM3_VideoTrack, SAM3_TrackPreview, SAM3_TrackToMask", flush=True)

def create_comfyui_workflow():
    """Exemplo 4: Gerar workflow JSON para ComfyUI com SAM 3"""
    workflow = {
        "last_node_id": 10,
        "last_link_id": 10,
        "nodes": [
            {
                "id": 1,
                "type": "SAM3_Detect",
                "pos": [100, 100],
                "size": [300, 200],
                "inputs": [
                    {"name": "image", "type": "IMAGE", "link": 1},
                    {"name": "model", "type": "SAM3_MODEL", "link": 2}
                ],
                "outputs": [
                    {"name": "MASKS", "type": "MASK", "links": [3]},
                    {"name": "BOXES", "type": "BOX", "links": [4]}
                ],
                "widgets_values": ["Zé, o entregador, cabeça de círculo, corpo de linha", 0.5, "coco"]
            },
            {
                "id": 2,
                "type": "SAM3_VideoTrack",
                "pos": [500, 100],
                "size": [300, 200],
                "inputs": [
                    {"name": "video", "type": "VIDEO", "link": 5},
                    {"name": "model", "type": "SAM3_MODEL", "link": 6}
                ],
                "widgets_values": ["bola de futebol", 0.3]
            },
            {
                "id": 3,
                "type": "LoadImage",
                "pos": [-300, 100],
                "size": [300, 100],
                "widgets_values": ["frame_entregador.jpg"]
            },
            {
                "id": 4,
                "type": "SAM3_TrackPreview",
                "pos": [900, 100],
                "size": [300, 200],
                "inputs": [{"name": "track_data", "type": "TRACK_DATA", "link": 7}]
            },
            {
                "id": 5,
                "type": "PreviewImage",
                "pos": [500, 400],
                "size": [300, 100],
                "inputs": [{"name": "images", "type": "MASK", "link": 3}]
            }
        ],
        "links": [
            [1, 3, 0, 1, 0, "IMAGE"],
            [2, 1, 1, None, None, "SAM3_MODEL"],
            [3, 1, 0, 5, 0, "MASK"],
            [4, 1, 1, None, None, "BOX"],
            [5, None, None, 2, 0, "VIDEO"],
            [6, None, None, 2, 1, "SAM3_MODEL"],
            [7, 2, 0, 4, 0, "TRACK_DATA"]
        ]
    }
    path = os.path.join(DESKTOP, "sam3_comfyui_workflow.json")
    with open(path, 'w') as f:
        json.dump(workflow, f, indent=2)
    print(f"  Workflow ComfyUI salvo: {path}")
    print(f"  Abra no ComfyUI com Load → Load API Format")
    print(f"  Use imagem do video do Zé entregador para segmentar")

def demo_comfyui_workflow():
    """Exemplo 5: Mostrar como usar SAM 3 pelo ComfyUI"""
    print(f"\n{'='*55}")
    print(f"  SAM 3 - Workflow ComfyUI")
    print(f"{'='*55}")
    create_comfyui_workflow()
    print(f"\n  Fluxo:")
    print(f"  1. LoadImage(frames do video do Ze)")
    print(f"  2. SAM3_Detect(prompt='Ze, cabeca de circulo')")
    print(f"  3. SAM3_VideoTrack(prompt='bola de futebol')")
    print(f"  4. PreviewImage → ve as mascaras em tempo real")
    print(f"  5. SAM3_TrackToMask → converte tracking para mascaras")
    print(f"  6. SaveImage → exporta resultado")

def main():
    check_sam3()
    parser = argparse.ArgumentParser(description='TRONIX SAM 3 Demo')
    parser.add_argument('--frame', help='Caminho do frame para segmentar')
    parser.add_argument('--video', help='Caminho do video para segmentar')
    parser.add_argument('--prompt', default='Zé, o entregador', help='Prompt de texto para segmentacao')
    parser.add_argument('--status', action='store_true', help='Verificar status do SAM 3')
    parser.add_argument('--workflow', action='store_true', help='Gerar workflow ComfyUI')
    parser.add_argument('--max-frames', type=int, default=5, help='Max frames do video')
    args = parser.parse_args()

    if args.status:
        demo_status()
    elif args.workflow:
        demo_comfyui_workflow()
    elif args.frame:
        demo_image(args.frame, args.prompt)
    elif args.video:
        demo_video(args.video, args.prompt, args.max_frames)
    else:
        parser.print_help()
        print(f"\n  Exemplos:")
        print(f"    python tronix_sam3_demo.py --status")
        print(f"    python tronix_sam3_demo.py --workflow")
        print(f"    python tronix_sam3_demo.py --frame frame.jpg --prompt 'Ze'")
        print(f"    python tronix_sam3_demo.py --video video.mp4 --prompt 'bola'")

if __name__ == '__main__':
    main()
