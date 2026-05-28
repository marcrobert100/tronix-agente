#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar uma nova API key do YouTube Data API v3.
"""

import webbrowser

def main():
    print("=" * 60)
    print("CRIAR NOVA API KEY DO YOUTUBE DATA API v3")
    print("=" * 60)
    
    print("\nPara criar uma nova API key:")
    print("1. Acesse: https://console.cloud.google.com/")
    print("2. Selecione ou crie um projeto")
    print("3. Vá para 'APIs & Services' > 'Library'")
    print("4. Ative 'YouTube Data API v3'")
    print("5. Vá para 'APIs & Services' > 'Credentials'")
    print("6. Clique em 'Create Credentials' > 'API key'")
    print("7. Copie a nova API key")
    
    print("\n" + "=" * 60)
    print("ABRINDO GOOGLE CLOUD CONSOLE...")
    print("=" * 60)
    
    try:
        webbrowser.open('https://console.cloud.google.com/')
    except:
        print("Não foi possível abrir o navegador automaticamente.")
        print("Abra manualmente: https://console.cloud.google.com/")

if __name__ == '__main__':
    main()
