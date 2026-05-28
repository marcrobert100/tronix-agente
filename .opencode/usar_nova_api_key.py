#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para usar uma nova API key do YouTube Data API v3.
"""

def main():
    print("=" * 60)
    print("USAR NOVA API KEY DO YOUTUBE DATA API v3")
    print("=" * 60)
    
    print("\nPara usar uma nova API key:")
    print("1. Crie uma nova API key no Google Cloud Console")
    print("2. Abra o arquivo 'youtube_check.py'")
    print("3. Substitua a linha 'API_KEY = ...' pela nova API key")
    print("4. Salve o arquivo")
    print("5. Execute: python youtube_check.py")
    
    print("\n" + "=" * 60)
    print("ARQUIVOS QUE PRECISAM SER ATUALIZADOS:")
    print("=" * 60)
    
    files = [
        'youtube_check.py',
        'youtube_channel_info.py'
    ]
    
    for f in files:
        print(f"- {f}")
    
    print("\n" + "=" * 60)
    print("INSTRUÇÕES RÁPIDAS:")
    print("=" * 60)
    print("1. Abra o arquivo em um editor de texto")
    print("2. Encontre a linha: API_KEY = 'AIzaSyDMnQjY94YAKcOkJS9fG9q1TQMcj3sU9Hw'")
    print("3. Substitua pela nova API key")
    print("4. Salve e execute o script")

if __name__ == '__main__':
    main()
