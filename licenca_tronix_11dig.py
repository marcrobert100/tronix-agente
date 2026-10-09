#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Licenciamento TRONIX - Formato 11 Dígitos
Gera chaves numéricas de 11 dígitos com checksum de validação
Compatível com o formato utilizado pelo Ativador UnitvFree
"""

import hmac
import hashlib
from datetime import datetime, timedelta

SECRET_KEY = "TRONIX_LICENCA_11DIG_2026_MARCOS_ROBERTO"

class Licenca11Digitos:
    def __init__(self, secret_key: str = SECRET_KEY):
        self.secret_key = secret_key.encode('utf-8')
    
    @staticmethod
    def _calcular_dv(numero_base: str) -> str:
        """Calcula dígito verificador (mod 10 alternado)"""
        soma = 0
        peso = 1
        # Percorre da direita para esquerda alternando peso 1 e 2
        for c in reversed(numero_base):
            d = int(c)
            v = d * peso
            soma += v
            peso = 3 - peso  # alterna 1 e 2
        
        resto = soma % 10
        dv = (10 - resto) % 10
        return str(dv)
    
    def gerar_chave(self, cliente: str = "Cliente", dias_validade: int = 365) -> str:
        """Gera uma chave numérica de 11 dígitos"""
        data_base = datetime.now().strftime('%Y%m%d%H%M%S')
        seed = f"{cliente}:{data_base}:{dias_validade}"
        
        # Gera hash HMAC-SHA256
        h = hmac.new(self.secret_key, seed.encode('utf-8'), hashlib.sha256).digest()
        
        # Converte para número inteiro
        num = int.from_bytes(h, 'big')
        
        # Pega 10 dígitos base
        base_10 = str(num % 10**10).zfill(10)
        
        # Calcula dígito verificador (11º dígito)
        dv = self._calcular_dv(base_10)
        
        chave = base_10 + dv
        return chave
    
    def gerar_multiplas(self, quantidade: int = 5, cliente: str = "Lote") -> list:
        """Gera múltiplas chaves de 11 dígitos"""
        chaves = []
        for i in range(quantidade):
            chave = self.gerar_chave(f"{cliente}_{i}", 365)
            chaves.append(chave)
        return chaves
    
    def validar_chave(self, chave: str):
        """Valida chave de 11 dígitos"""
        if isinstance(chave, str):
            chave = chave.strip().replace('-', '').replace(' ', '')
        
        # Verifica formato
        if len(chave) != 11 or not chave.isdigit():
            return False, {'erro': 'Formato inválido. Deve conter exatamente 11 dígitos numéricos.'}
        
        base_10 = chave[:-1]
        dv_recebido = chave[-1]
        dv_calculado = self._calcular_dv(base_10)
        
        if dv_recebido != dv_calculado:
            return False, {'erro': 'Chave inválida (checksum não confere).'}
        
        return True, {
            'valida': True,
            'formato': '11-digitos',
            'chave': chave
        }

if __name__ == '__main__':
    lic = Licenca11Digitos()
    print("TESTE - Sistema 11 Dígitos TRONIX")
    print("=" * 40)
    for i in range(3):
        c = lic.gerar_chave(f"Teste{i}")
        ok, _ = lic.validar_chave(c)
        print(f"{i+1}. {c} -> {'OK' if ok else 'ERRO'}")
