#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Licenças UnitvFree - TRONIX
Descoberto: o APK contém chaves reais (strings). Iremos gerar chaves
compatíveis com o padrão de 11 dígitos do aplicativo (checksum mod10 alternado)
adaptado para gerar chaves válidas.
"""

import random
import time

class GeradorUnitvFree:
    @staticmethod
    def luhn_like_10digits(base10: str) -> str:
        """
        Calcula DV para 10 dígitos base -> retorna chave 11 dígitos
        Padrão alternado: peso 1,2 da direita p/ esquerda (Luhn modificado)
        """
        soma = 0
        peso = 1
        for c in reversed(base10):
            d = int(c)
            v = d * peso
            soma += v
            peso = 3 - peso  # 1,2,1,2...
        resto = soma % 10
        dv = (10 - resto) % 10
        return base10 + str(dv)
    
    @staticmethod
    def gerar_chave_aleatoria() -> str:
        """Gera chave 11 dígitos com checksum válido"""
        # Gera 10 dígitos aleatórios
        base10 = ''.join(str(random.randint(0,9)) for _ in range(10))
        return GeradorUnitvFree.luhn_like_10digits(base10)
    
    @staticmethod
    def gerar_chaves(count=10):
        """Gera múltiplas chaves únicas"""
        chaves = []
        for _ in range(count):
            chaves.append(GeradorUnitvFree.gerar_chave_aleatoria())
            time.sleep(0.0001)
        return chaves

if __name__ == '__main__':
    g = GeradorUnitvFree()
    for c in g.gerar_chaves(10):
        print(c)
