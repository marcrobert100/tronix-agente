import cv2
import numpy as np
from pathlib import Path
import os


def desenhar_robo(frame, x, y, tamanho, angulo_braco=0):
    """Desenha um robô simples no frame"""
    cor_robo = (100, 150, 200)
    cor_olhos = (0, 255, 0)
    
    cabeca_tam = int(tamanho * 0.4)
    corpo_tam = int(tamanho * 0.6)
    
    cv2.rectangle(frame, 
                  (x - cabeca_tam//2, y - cabeca_tam - corpo_tam//2),
                  (x + cabeca_tam//2, y - corpo_tam//2),
                  cor_robo, -1)
    
    cv2.rectangle(frame,
                  (x - corpo_tam//2, y - corpo_tam//2),
                  (x + corpo_tam//2, y + corpo_tam//2),
                  cor_robo, -1)
    
    cv2.circle(frame, (x - 15, y - cabeca_tam - corpo_tam//2 + 10), 8, cor_olhos, -1)
    cv2.circle(frame, (x + 15, y - cabeca_tam - corpo_tam//2 + 10), 8, cor_olhos, -1)
    
    braco_esq_x = x - corpo_tam//2 - 20
    braco_esq_y = y
    cv2.line(frame, (x - corpo_tam//2, y), 
             (braco_esq_x, braco_esq_y + angulo_braco), 
             cor_robo, 8)
    
    braco_dir_x = x + corpo_tam//2 + 20
    braco_dir_y = y
    cv2.line(frame, (x + corpo_tam//2, y),
             (braco_dir_x, braco_dir_y - angulo_braco),
             cor_robo, 8)
    
    cv2.line(frame, (x - 20, y + corpo_tam//2), (x - 20, y + corpo_tam//2 + 40), cor_robo, 8)
    cv2.line(frame, (x + 20, y + corpo_tam//2), (x + 20, y + corpo_tam//2 + 40), cor_robo, 8)
    
    return frame


def criar_video_robo():
    script_dir = Path(__file__).parent
    output_dir = script_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    width, height = 1280, 720
    fps = 24
    duracao = 8
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_dir / "robo_procureemprego.mp4"), fourcc, fps, (width, height))
    
    total_frames = fps * duracao
    
    for i in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (30, 30, 50)
        
        x = width // 2
        y = height // 2
        
        progress = i / total_frames
        
        if progress < 0.3:
            x = int(width * 0.2)
            x = int(width * 0.2 + (width * 0.6) * (progress / 0.3))
        
        oscilacao = int(20 * np.sin(i * 0.2))
        y += oscilacao
        
        angulo_braco = int(30 * np.sin(i * 0.15))
        
        desenhar_robo(frame, x, y, 200, angulo_braco)
        
        texto = "PROCURO EMPREGO"
        
        if progress > 0.2:
            alpha = min(1.0, (progress - 0.2) * 2)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            escala = 2.0
            espessura = 5
            
            (larg_texto, _), _ = cv2.getTextSize(texto, font, escala, espessura)
            texto_x = (width - larg_texto) // 2
            texto_y = height - 100
            
            sombra_x = texto_x + 3
            sombra_y = texto_y + 3
            cv2.putText(frame, texto, (sombra_x, sombra_y), font, escala, (0, 0, 0), espessura + 2)
            
            cor_texto = (int(255 * alpha), int(255 * alpha), int(0 * alpha))
            cv2.putText(frame, texto, (texto_x, texto_y), font, escala, cor_texto, espessura)
        
        if progress > 0.5:
            texto2 = "Desenvolvedor IA | Python | Automação"
            alpha2 = min(1.0, (progress - 0.5) * 2)
            
            (larg_texto2, _), _ = cv2.getTextSize(texto2, font, 1.0, 3)
            texto2_x = (width - larg_texto2) // 2
            texto2_y = height - 50
            
            cv2.putText(frame, texto2, (texto2_x, texto2_y), font, 1.0, (200, 200, 200), 3)
        
        out.write(frame)
        
        if i % 24 == 0:
            print(f"Frame {i//24 + 1}/{duracao}")
    
    out.release()
    print(f"Video criado: output/robo_procureemprego.mp4")


if __name__ == "__main__":
    criar_video_robo()