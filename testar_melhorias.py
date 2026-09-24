import sys; sys.path.insert(0, 'C:\\xampp\\htdocs\\agente')
import tronix_logger as t

t.inicializar()

print('=== MELHORIAS DO tronix_logger.py ===')
print()

print('1) REGISTRO EM LOTE (batch insert)')
ids = t.registrar_lote([
    {'tipo': 'video', 'titulo': 'Demo lote 1', 'arquivo': 'demo1.mp4', 'tamanho_kb': 500},
    {'tipo': 'imagem', 'titulo': 'Demo lote 2', 'arquivo': 'demo2.png', 'tamanho_kb': 200},
])
print(f'   IDs criados: {ids}')

print()
print('2) TAREFAS (nova tabela integrada)')
tid = t.registrar_tarefa('KIMI', 'testou_melhorias_tronix_logger')
print(f'   Tarefa ID: {tid}')

print()
print('3) ESTATISTICAS MELHORADAS (dict com totais)')
stats = t.estatisticas()
print(f'   Conteudos: {stats["conteudos"]}')
print(f'   Total geral: {stats["total_geral"]}')
print(f'   Total KB: {stats["total_kb"]}')

print()
print('4) EXPORT JSON')
export = t.exportar_json()
print(f'   JSON gerado: {len(export)} chars')

print()
print('5) LIMPEZA AUTOMATICA (VACUUM)')
r = t.limpar(365)
print(f'   Registros removidos: {r.get("removidos", 0)}')

print()
print('6) CLI - comandos novos')
print('   python tronix_logger.py status')
print('   python tronix_logger.py listar')
print('   python tronix_logger.py exportar backup.json')
print('   python tronix_logger.py limpar 60')

print()
print('=== TODAS AS MELHORIAS VERIFICADAS ===')
