#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Licenciamento TRONIX
Gera e valida chaves de licença com criptografia HMAC-SHA256
"""

import base64
import hmac
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional

# Chave secreta para assinatura (ALTERE EM PRODUÇÃO)
SECRET_KEY = "TRONIX_LICENCA_SECRETA_2026_MARCOS_ROBERTO"

class LicencaTronix:
    def __init__(self, secret_key: str = SECRET_KEY):
        self.secret_key = secret_key.encode('utf-8')
    
    def gerar_chave(self, cliente: str, dias_validade: int = 365) -> str:
        """
        Gera uma nova chave de licença
        
        Args:
            cliente: Nome do cliente
            dias_validade: Quantidade de dias de validade
            
        Returns:
            Chave de licença codificada em base64url
        """
        data_hoje = datetime.now().date()
        data_expira = (data_hoje + timedelta(days=dias_validade)).isoformat()
        
        # Dados da licença
        payload = {
            'cliente': cliente,
            'emitida': data_hoje.isoformat(),
            'expira': data_expira,
            'versao': '1.0.0'
        }
        
        # Serializa payload
        payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        payload_bytes = payload_str.encode('utf-8')
        
        # Gera assinatura HMAC-SHA256
        assinatura = hmac.new(self.secret_key, payload_bytes, hashlib.sha256).digest()
        assinatura_trunc = assinatura[:16]  # 128 bits
        
        # Combina payload + assinatura
        dados = payload_bytes + assinatura_trunc
        chave = base64.urlsafe_b64encode(dados).decode('utf-8').rstrip('=')
        
        return chave
    
    def validar_chave(self, chave: str) -> Tuple[bool, Optional[Dict]]:
        """
        Valida uma chave de licença
        
        Args:
            chave: Chave de licença a ser validada
            
        Returns:
            (valida, dados_licenca) ou (False, motivo_erro)
        """
        try:
            # Adiciona padding se necessário
            padding = 4 - len(chave) % 4
            if padding != 4:
                chave_padded = chave + '=' * padding
            else:
                chave_padded = chave
            
            dados_decodificados = base64.urlsafe_b64decode(chave_padded)
            
            # Separa payload e assinatura (últimos 16 bytes)
            if len(dados_decodificados) < 16:
                return False, {'erro': 'Chave inválida - formato incorreto'}
            
            payload_bytes = dados_decodificados[:-16]
            assinatura_recebida = dados_decodificados[-16:]
            
            # Verifica assinatura
            assinatura_calculada = hmac.new(
                self.secret_key, 
                payload_bytes, 
                hashlib.sha256
            ).digest()[:16]
            
            if not hmac.compare_digest(assinatura_recebida, assinatura_calculada):
                return False, {'erro': 'Chave inválida - assinatura não confere'}
            
            # Decodifica payload
            payload_str = payload_bytes.decode('utf-8')
            payload = json.loads(payload_str)
            
            # Verifica validade
            data_expira = datetime.fromisoformat(payload['expira']).date()
            data_hoje = datetime.now().date()
            
            if data_hoje > data_expira:
                dias_expirados = (data_hoje - data_expira).days
                return False, {
                    'erro': f'Licença expirada há {dias_expirados} dias',
                    'expirou_em': payload['expira']
                }
            
            # Calcula dias restantes
            dias_restantes = (data_expira - data_hoje).days
            payload['dias_restantes'] = dias_restantes
            
            return True, payload
            
        except Exception as e:
            return False, {'erro': f'Erro ao validar chave: {str(e)}'}
    
    def listar_info(self, chave: str) -> Dict:
        """Lista informações detalhadas da licença"""
        valida, dados = self.validar_chave(chave)
        return {
            'valida': valida,
            'dados': dados
        }

def menu():
    print("=" * 60)
    print("SISTEMA DE LICENCIAMENTO TRONIX")
    print("=" * 60)
    print("1. Gerar nova licença")
    print("2. Validar licença")
    print("3. Gerar licença para cliente específico")
    print("4. Sair")
    print("=" * 60)
    
    opcao = input("Escolha uma opção: ").strip()
    return opcao

def main():
    lic = LicencaTronix()
    
    while True:
        opcao = menu()
        
        if opcao == '1':
            cliente = input("Nome do cliente: ").strip() or "Cliente Padrão"
            try:
                dias = int(input("Dias de validade (padrão 365): ").strip() or "365")
            except ValueError:
                dias = 365
            
            chave = lic.gerar_chave(cliente, dias)
            print("\n" + "=" * 60)
            print("CHAVE GERADA COM SUCESSO!")
            print("=" * 60)
            print(f"Cliente: {cliente}")
            print(f"Dias: {dias}")
            print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print("=" * 60)
            print(chave)
            print("=" * 60)
            print("\n")
        
        elif opcao == '2':
            chave = input("Digite a chave de licença: ").strip()
            valida, dados = lic.validar_chave(chave)
            
            print("\n" + "=" * 60)
            if valida:
                print("✓ LICENÇA VÁLIDA")
                print("=" * 60)
                print(f"Cliente: {dados.get('cliente')}")
                print(f"Emitida: {dados.get('emitida')}")
                print(f"Expira: {dados.get('expira')}")
                print(f"Dias restantes: {dados.get('dias_restantes')}")
                print(f"Versão: {dados.get('versao')}")
            else:
                print("✗ LICENÇA INVÁLIDA")
                print("=" * 60)
                print(dados.get('erro'))
            print("=" * 60)
            print("\n")
        
        elif opcao == '3':
            cliente = input("Nome do cliente: ").strip()
            if not cliente:
                print("Cliente não pode ser vazio!")
                continue
            try:
                dias = int(input("Dias de validade: ").strip())
            except ValueError:
                print("Dias inválidos!")
                continue
            
            chave = lic.gerar_chave(cliente, dias)
            nome_arquivo = f"licenca_{cliente.lower().replace(' ', '_')}.txt"
            
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("SISTEMA DE LICENCIAMENTO TRONIX\n")
                f.write("=" * 60 + "\n")
                f.write(f"CLIENTE: {cliente}\n")
                f.write(f"CHAVE: {chave}\n")
                f.write(f"EMITIDA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"VALIDADE: {dias} dias\n")
                f.write("=" * 60 + "\n")
            
            print("\n" + "=" * 60)
            print("LICENÇA SALVA COM SUCESSO!")
            print("=" * 60)
            print(f"Arquivo: {nome_arquivo}")
            print(f"Chave: {chave}")
            print("=" * 60)
            print("\n")
        
        elif opcao == '4':
            print("Encerrando...")
            break
        
        else:
            print("Opção inválida!\n")

if __name__ == '__main__':
    main()
