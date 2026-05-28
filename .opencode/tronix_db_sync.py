#!/usr/bin/env python3
"""
Tronix Database Synchronizer
============================
Sincroniza o sistema Tronix com o banco de dados MySQL do XAMPP.
"""

import pymysql
import json
import os
from datetime import datetime

class TronixDBSync:
    def __init__(self):
        self.connection = None
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'tronix_system',
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = pymysql.connect(**self.config)
            print("[OK] Conectado ao banco de dados Tronix System")
            return True
        except Exception as e:
            print(f"[ERRO] Falha na conexão: {e}")
            return False
    
    def sync_skills(self, skills_list):
        """Sync active skills to database"""
        if not self.connection:
            print("[ERRO] Não conectado ao banco de dados")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # Clear existing skills
                cursor.execute("DELETE FROM skills")
                
                # Insert new skills
                for skill in skills_list:
                    cursor.execute(
                        "INSERT INTO skills (nome, descricao, categoria) VALUES (%s, %s, %s)",
                        (skill, f"Skill {skill} do Tronix", "AI")
                    )
                
                self.connection.commit()
                print(f"[OK] {len(skills_list)} skills sincronizadas")
                return True
        except Exception as e:
            print(f"[ERRO] Falha ao sincronizar skills: {e}")
            return False
    
    def sync_projects(self, projects_data):
        """Sync projects to database"""
        if not self.connection:
            print("[ERRO] Não conectado ao banco de dados")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # Clear existing projects
                cursor.execute("DELETE FROM projetos")
                
                # Insert projects
                for project in projects_data:
                    cursor.execute(
                        "INSERT INTO projetos (nome, descricao, status, data_criacao) VALUES (%s, %s, %s, %s)",
                        (project.get('nome'), project.get('descricao'), 
                         project.get('status', 'ativo'), datetime.now())
                    )
                
                self.connection.commit()
                print(f"[OK] {len(projects_data)} projetos sincronizados")
                return True
        except Exception as e:
            print(f"[ERRO] Falha ao sincronizar projetos: {e}")
            return False
    
    def log_evolution(self, operation, status, message, skills_count=None):
        """Log evolution to database"""
        if not self.connection:
            print("[ERRO] Não conectado ao banco de dados")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # Ajustado para a estrutura real da tabela logs_evolucao
                cursor.execute(
                    """INSERT INTO logs_evolucao 
                       (agente, acao, timestamp) 
                       VALUES (%s, %s, %s)""",
                    ("Tronix", f"{operation}: {message}", datetime.now())
                )
                
                self.connection.commit()
                print(f"[OK] Log de evolução registrado: {operation}")
                return True
        except Exception as e:
            print(f"[ERRO] Falha ao registrar log: {e}")
            return False
    
    def get_skills(self):
        """Get all skills from database"""
        if not self.connection:
            return []
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM skills WHERE categoria = 'AI'")
                return cursor.fetchall()
        except Exception as e:
            print(f"[ERRO] Falha ao obter skills: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("[OK] Conexão fechada")

def main():
    """Main function to sync Tronix with database"""
    connector = TronixDBSync()
    
    if connector.connect():
        # Load skills from tronix_core.json
        try:
            with open('tronix_core.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                skills = data.get('skills_ativas', [])
            
            # Sync skills
            connector.sync_skills(skills)
            
            # Log evolution
            connector.log_evolution(
                "SINCRONIZACAO_SKILLS",
                "ATIVO",
                f"Tronix sincronizado com {len(skills)} skills",
                len(skills)
            )
            
            # Get skills from DB
            db_skills = connector.get_skills()
            print(f"\n[INFO] Skills no banco de dados: {len(db_skills)}")
            for skill in db_skills[:10]:  # Show first 10
                print(f"  - {skill['nome']}")
            
        except Exception as e:
            print(f"[ERRO] Falha ao carregar tronix_core.json: {e}")
        
        connector.close()

if __name__ == "__main__":
    main()
