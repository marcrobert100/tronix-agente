import re
import fitz

pdf = r'C:\Users\CHCONTE RECPÇÃO\Desktop\LIVRO DE ESTUDO GM CHA PRETA AL.pdf'
doc = fitz.open(pdf)
texto = ''
for p in doc:
    texto += p.get_text('text') + '\n\n'
doc.close()
linhas = re.split(r'\n\s*\n', texto)
c = 0
for l in linhas:
    l2 = l.strip()
    if len(l2) > 60 and ('?' in l2 or 'assinale' in l2.lower() or 'alternativa' in l2.lower()):
        c += 1
        if c <= 3:
            print(l2[:140])
print('TOTAL', c)
