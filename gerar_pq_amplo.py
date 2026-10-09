import asyncio, sys, re
from pathlib import Path

try:
    import fitz
except:
    import subprocess
    subprocess.check_call([sys.executable,'-m','pip','install','PyMuPDF','-q'])
    import fitz

try:
    import edge_tts
except:
    import subprocess
    subprocess.check_call([sys.executable,'-m','pip','install','edge-tts','-q'])
    import edge_tts

pdf = r'C:\Users\CHCONTE RECPÇÃO\Desktop\LIVRO DE ESTUDO GM CHA PRETA AL.pdf'
out = Path(r'C:\Users\CHCONTE RECPÇÃO\Desktop\estudo_audio_gm_cha_preta_al')
mp3dir = out / 'mp3'
out.mkdir(exist_ok=True)
mp3dir.mkdir(exist_ok=True)

doc = fitz.open(pdf)
texto = '\n\n'.join([p.get_text('text') for p in doc])
doc.close()

disciplinas = [
  ('direito_constitucional','Noções de Direito Constitucional'),
  ('direito_administrativo','Noções de Direito Administrativo'),
  ('direito_penal','Noções de Direito Penal'),
  ('direito_processual_penal','Noções de Direito Processual Penal'),
  ('direitos_humanos','Noções de Direitos Humanos'),
  ('legislacao_penal_extravagante','Legislação Penal Extravagante'),
  ('legislacao_geral_gm','Legislação Geral da Guarda Municipal'),
]

# extrai trechos com questoes tipo
linhas = re.split(r'\n\s*\n', texto)
candidatos = []
for l in linhas:
    l2 = l.strip()
    if len(l2) > 40 and len(l2) < 600:
        low = l2.lower()
        if 'quest' in low or '?' in low or 'assinale' in low or 'alternativa' in low or 'julgue' in low:
            candidatos.append(l2)

async def gerar():
    voz='pt-BR-AntonioNeural'
    usados = candidatos[:120] if len(candidatos)>120 else candidatos
    chunks = [usados[i:i+15] for i in range(0,len(usados),15)]
    blocos_audio = []
    for idx,chunk in enumerate(chunks[:8]):
        conteudo = 'BANCO DE QUESTÕES REAIS EXTRAÍDO DO LIVRO. PERGUNTA → RESPOSTA.\n\n'
        for j,q in enumerate(chunk,1):
            conteudo += f'PERGUNTA {j}: {q}\n'
            conteudo += 'RESPOSTA: reveja no livro os fundamentos. Treine até acertar sem olhar.\n\n'
        arq = mp3dir / f'questoes_extraidas_bloco_{idx+1}.mp3'
        comm = edge_tts.Communicate(conteudo[:9800], voz, rate='+0%')
        await comm.save(str(arq))
        blocos_audio.append(arq.name)
        print('OK', arq.name)
    print('TOTAL', len(blocos_audio))

asyncio.run(gerar())
