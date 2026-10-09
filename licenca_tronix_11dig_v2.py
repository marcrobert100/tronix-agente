#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Licenciamento TRONIX - Formato 11 Dígitos
Gera chaves numéricas de 11 dígitos com checksum de validação
Compatível com o formato utilizado pelo Ativador UnitvFree
"""

import hmac
import hashlib
import os
import time
from datetime import datetime

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
        # Seed com alta entropia para garantir chaves únicas
        seed = f"{cliente}:{time.time_ns()}:{os.urandom(16).hex()}:{dias_validade}:{datetime.now().isoformat()}"
        
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
            chave = self.gerar_chave(f"{cliente}_{i}_{time.time_ns()}", 365)
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
