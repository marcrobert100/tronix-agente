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
texto = ''
for p in doc:
    texto += p.get_text('text') + '\n\n'
doc.close()

# limpar lixo
linhas = re.split(r'\n\s*\n', texto)
cands = []
for l in linhas:
    l2 = re.sub(r'\s+', ' ', l.strip())
    if len(l2) < 40: continue
    low = l2.lower()
    if ('?' in l2 or 'assinale' in low or 'julgue' in low or 'marque' in low or 'alternativa' in low):
        if 'www' in low or 'qconcursos' in low: continue
        cands.append(l2)

# gerar blocos P->R
async def gerar():
    voz='pt-BR-AntonioNeural'
    blocos = [cands[i:i+10] for i in range(0,min(len(cands),70),10)]
    for idx,blk in enumerate(blocos):
        conteudo = 'MODO PERGUNTA E RESPOSTA – APRENDER OUVINDO. Ouça a PERGUNTA, pense, depois ouça a RESPOSTA. Repita até fixar.\n\n'
        for j,q in enumerate(blk,1):
            conteudo += f'PERGUNTA {j}: {q}\n'
            conteudo += f'RESPONTA {j}: Estude o fundamento legal correspondente no conteúdo. Foque em compreender, não decorar.\n\n'
        arq = mp3dir / f'pq_concursos_bloco_{idx+1}.mp3'
        comm = edge_tts.Communicate(conteudo[:9800], voz, rate='+0%')
        await comm.save(str(arq))
        print('OK', arq.name)

asyncio.run(gerar())
