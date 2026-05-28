#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar o arquivo de vídeo antes do upload.
"""

import os
import subprocess
import json

def get_video_info(file_path):
    """Obtém informações do arquivo de vídeo usando ffprobe (se disponível)."""
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo não encontrado: {file_path}")
        return None
    
    # Tenta usar ffprobe para obter informações do vídeo
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data
    except FileNotFoundError:
        print("ffprobe não encontrado. Instale o FFmpeg para mais informações.")
    
    # Informações básicas sem ffprobe
    size = os.path.getsize(file_path)
    return {
        'format': {
            'size': str(size),
            'format_name': 'unknown'
        }
    }

def main():
    """Função principal."""
    video_path = r'C:\Users\CHCONTE RECPÇÃO\Desktop\frutas.mp4'
    
    print("=== VERIFICAÇÃO DO ARQUIVO DE VÍDEO ===")
    print(f"Arquivo: {video_path}")
    
    if not os.path.exists(video_path):
        print("ERRO: O arquivo de vídeo não foi encontrado!")
        return
    
    # Informações básicas
    size = os.path.getsize(video_path)
    print(f"Tamanho: {size:,} bytes ({size/1024/1024:.2f} MB)")
    print(f"Existe: Sim")
    
    # Tenta obter mais informações
    info = get_video_info(video_path)
    if info and 'format' in info:
        print(f"Formato: {info['format'].get('format_name', 'unknown')}")
        if 'duration' in info['format']:
            duration = float(info['format']['duration'])
            print(f"Duração: {duration:.2f} segundos")
    
    print("\n=== STATUS ===")
    if size > 0:
        print("[OK] O arquivo esta pronto para upload")
        print("[OK] Proximo passo: Configurar OAuth 2.0 (veja INSTRUCOES_UPLOAD_YOUTUBE.txt)")
    else:
        print("[X] O arquivo esta vazio")

if __name__ == '__main__':
    main()
