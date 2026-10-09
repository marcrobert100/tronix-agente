import os, asyncio, sys
from pathlib import Path

try:
    import fitz
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyMuPDF', '-q'])
    import fitz

try:
    import edge_tts
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'edge-tts', '-q'])
    import edge_tts

pdf = r'C:\Users\CHCONTE RECPÇÃO\Desktop\LIVRO DE ESTUDO GM CHA PRETA AL.pdf'
out = Path(r'C:\Users\CHCONTE RECPÇÃO\Desktop\estudo_audio_gm_cha_preta_al')
mp3dir = out / 'mp3'
html_file = out / 'index.html'
out.mkdir(exist_ok=True)
mp3dir.mkdir(exist_ok=True)

doc = fitz.open(pdf)
partes = []
for i,p in enumerate(doc,1):
    t = p.get_text('text')
    partes.append(t)
doc.close()

texto_total = '\n\n'.join(partes)

disciplinas = [
  ('direito_constitucional','Noções de Direito Constitucional'),
  ('direito_administrativo','Noções de Direito Administrativo'),
  ('direito_penal','Noções de Direito Penal'),
  ('direito_processual_penal','Noções de Direito Processual Penal'),
  ('direitos_humanos','Noções de Direitos Humanos'),
  ('legislacao_penal_extravagante','Legislação Penal Extravagante'),
  ('legislacao_geral_gm','Legislação Geral da Guarda Municipal'),
]

blocos = []
for slug,nome in disciplinas:
    txt = f'''ESTUDO FOCADO – {nome.upper()}

FOCO ESTRATÉGICO
Peso 3,0 – 12 pontos. Prioritário para GM Chã Preta – AL.

1. PESQUISA DE QUESTÕES ANTERIORES
- Provas anteriores GM/Segurança Pública
- Fontes: QConcursos, PCI Concursos, Gran Cursos, Passei Direto, Aprova Concursos
- Separar por disciplina, mapear recorrência, frequência por banca

2. ANÁLISE DAS QUESTÕES
- Classificar por tema/subtema
- Identificar nível (FUNVAPI)
- Tópicos com maior incidência

3. TREINAMENTO SOB TEMPO CRONOMETRADO
- Simular prova real
- Revisar erros (edital + fichas)
- Lista de reforço

4. BANCO TEMÁTICO + REVISÕES ESPAÇADAS
- Organizar por temas
- 3 revisões: início, meio, véspera
- Focar no mais cobrado

5. SIMULADOS ESPECÍFICOS
- Por disciplina (peso 3,0)
- Ajustar plano conforme frequência

BENEFÍCIOS: estilo da banca, foco no que cai, economia de tempo, confiança.
'''
    blocos.append({'id':slug,'titulo':nome,'texto':txt})

async def gerar_mp3():
    voz = 'pt-BR-AntonioNeural'
    for b in blocos:
        arq = mp3dir / f'{b["id"]}_estrategia.mp3'
        comm = edge_tts.Communicate(b['texto'], voz, rate='+0%')
        await comm.save(str(arq))
        b['mp3'] = f'mp3/{b["id"]}_estrategia.mp3'

asyncio.run(gerar_mp3())
