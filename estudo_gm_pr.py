import asyncio, sys
from pathlib import Path

try:
    import edge_tts
except:
    import subprocess
    subprocess.check_call([sys.executable,'-m','pip','install','edge-tts','-q'])
    import edge_tts

out = Path(r'C:\Users\CHCONTE RECPÇÃO\Desktop\estudo_audio_gm_cha_preta_al')
mp3dir = out / 'mp3'
out.mkdir(exist_ok=True)
mp3dir.mkdir(exist_ok=True)

disciplinas = [
  ('direito_constitucional','Direito Constitucional'),
  ('direito_administrativo','Direito Administrativo'),
  ('direito_penal','Direito Penal'),
  ('direito_processual_penal','Direito Processual Penal'),
  ('direitos_humanos','Direitos Humanos'),
  ('legislacao_penal_extravagante','Legislação Penal Extravagante'),
  ('legislacao_geral_gm','Legislação Geral da Guarda Municipal'),
]

async def gerar():
    voz='pt-BR-AntonioNeural'
    for slug,nome in disciplinas:
        linhas = ['MODO: PERGUNTA E RESPOSTA. Ou�a pergunta... pause... ou�a resposta. Repita.', '']
        for i in range(1,11):
            linhas.append(f'PERGUNTA {i} - {nome}: Quais os temas mais cobrados em {nome} para GM Chã Preta AL?')
            linhas.append(f'RESPONTA {i} - Foque em conceitos, artigos-chave, legislação e aplicação prática.')
            linhas.append('')
        conteudo = '\n'.join(linhas)
        arq = mp3dir / f'{slug}_pq_resposta.mp3'
        comm = edge_tts.Communicate(conteudo, voz, rate='+0%')
        await comm.save(str(arq))
        print('OK', arq.name)

asyncio.run(gerar())
