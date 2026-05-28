#!/usr/bin/env python3
"""
Tronix Database Connector
=========================
Conecta o sistema Tronix ao banco de dados MySQL do XAMPP.
Sincroniza skills, projetos e logs de evolução.
"""

import mysql.connector
import json
import os
from datetime import datetime

class TronixDBConnector:
    def __init__(self):
        self.connection = None
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  # XAMPP default
            'database': 'tronix_system'
        }
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            print("✅ Conectado ao banco de dados Tronix System")
            return True
        except mysql.connector.Error as err:
            print(f"❌ Erro de conexão: {err}")
            return False
    
    def sync_skills(self, skills_list):
        """Sync active skills to database"""
        if not self.connection:
            print("❌ Não conectado ao banco de dados")
            return False
        
        cursor = self.connection.cursor()
        
        # Clear existing skills
        cursor.execute("DELETE FROM skills")
        
        # Insert new skills
        for skill in skills_list:
            cursor.execute(
                "INSERT INTO skills (nome, ativo) VALUES (%s, %s)",
                (skill, True)
            )
        
        self.connection.commit()
        cursor.close()
        print(f"✅ {len(skills_list)} skills sincronizadas")
        return True
    
    def sync_projects(self, projects_data):
        """Sync projects to database"""
        if not self.connection:
            print("❌ Não conectado ao banco de dados")
            return False
        
        cursor = self.connection.cursor()
        
        # Clear existing projects
        cursor.execute("DELETE FROM projetos")
        
        # Insert projects
        for project in projects_data:
            cursor.execute(
                "INSERT INTO projetos (nome, descricao, status, data_criacao) VALUES (%s, %s, %s, %s)",
                (project.get('nome'), project.get('descricao'), project.get('status', 'ativo'), datetime.now())
            )
        
        self.connection.commit()
        cursor.close()
        print(f"✅ {len(projects_data)} projetos sincronizados")
        return True
    
    def log_evolution(self, operation, status, message, skills_count=None):
        """Log evolution to database"""
        if not self.connection:
            print("❌ Não conectado ao banco de dados")
            return False
        
        cursor = self.connection.cursor()
        
        cursor.execute(
            """INSERT INTO logs_evolucao 
               (timestamp, operacao, status, skills_count, localizacao, criador, mensagem) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (datetime.now(), operation, status, skills_count, 
             "Viçosa, Alagoas, Brasil", "Marcos Roberto", message)
        )
        
        self.connection.commit()
        cursor.close()
        print(f"✅ Log de evolução registrado: {operation}")
        return True
    
    def get_skills(self):
        """Get all skills from database"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM skills WHERE ativo = 1")
        skills = cursor.fetchall()
        cursor.close()
        return skills
    
    def get_projects(self):
        """Get all projects from database"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM projetos WHERE status = 'ativo'")
        projects = cursor.fetchall()
        cursor.close()
        return projects
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Conexão fechada")

def main():
    """Main function to test connection"""
    connector = TronixDBConnector()
    
    if connector.connect():
        # Load skills from tronix_core.json
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
        print(f"\n📊 Skills no banco de dados: {len(db_skills)}")
        for skill in db_skills[:5]:  # Show first 5
            print(f"  - {skill['nome']}")
        
        connector.close()

if __name__ == "__main__":
    main()
