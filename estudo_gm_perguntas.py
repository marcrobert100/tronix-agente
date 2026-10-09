import asyncio, sys, re
from pathlib import Path
from random import shuffle

try:
    import fitz
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable,'-m','pip','install','PyMuPDF','-q'])
    import fitz

try:
    import edge_tts
except ImportError:
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
  ('direito_constitucional','Direito Constitucional'),
  ('direito_administrativo','Direito Administrativo'),
  ('direito_penal','Direito Penal'),
  ('direito_processual_penal','Direito Processual Penal'),
  ('direitos_humanos','Direitos Humanos'),
  ('legislacao_penal_extravagante','Legislação Penal Extravagante'),
  ('legislacao_geral_gm','Legislação Geral da Guarda Municipal'),
]

# gerar 10 perguntas base por disciplina
async def gerar():
    voz='pt-BR-AntonioNeural'
    for slug,nome in disciplinas:
        blocos = []
        for i in range(1,11):
            blocos.append(f\"PERGUNTA {i}: (Concurso GM Chã Preta/AL – {nome})\n\nDefina/responda: temas mais cobrados – foco peso 3,0.\n\nRESPOSTA: revise conceito, fundamento legal, aplicabilidade prática.\")
        conteudo = 'MODO APRENDIZADO: PERGUNTA → RESPOSTA. Repita ouvindo até fixar.\n\n' + '\n\n---\n\n'.join(blocos)
        arq = mp3dir / f'{slug}_perguntas_respostas.mp3'
        comm = edge_tts.Communicate(conteudo[:9500], voz, rate='+0%')
        await comm.save(str(arq))
        print(arq.name,'OK')

asyncio.run(gerar())
