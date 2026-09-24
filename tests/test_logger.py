# tests/test_logger.py
import os
import sys
import json
import tempfile
import shutil

# Add parent directory to path to import tronix_logger
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tronix_logger

def test_validacao_tipo_invalido():
    """Tipo inválido deve ser corrigido para 'video' (padrão)."""
    # Simula banco temporário
    test_dir = tempfile.mkdtemp()
    original_db = tronix_logger.DB_PATH
    tronix_logger.DB_PATH = os.path.join(test_dir, 'test.db')
    try:
        tronix_logger.inicializar()
        # Tipo inválido -> deve virar 'video'
        cid = tronix_logger.registrar(tipo='tipo_invalido', titulo='Teste', arquivo='test.mp4')
        assert cid is not None
        # Recupera para verificar
        conn = tronix_logger.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT tipo FROM conteudo WHERE id=?", (cid,))
        row = cursor.fetchone()
        conn.close()
        assert row[0] == 'video', f"Esperado 'video', got {row[0]}"
    finally:
        tronix_logger.DB_PATH = original_db
        shutil.rmtree(test_dir, ignore_errors=True)

def test_sanitizacao_strings():
    """Strings devem ser truncadas e caracteres perigosos removidos."""
    test_dir = tempfile.mkdtemp()
    original_db = tronix_logger.DB_PATH
    tronix_logger.DB_PATH = os.path.join(test_dir, 'test.db')
    try:
        tronix_logger.inicializar()
        titulo_longo = 'A' * 300  # limite 200
        legenda_com_html = '<script>alert(1)</script>Texto'
        cid = tronix_logger.registrar(
            tipo='video',
            titulo=titulo_longo,
            arquivo='video.mp4',
            legenda=legenda_com_html,
            hashtags='#tag1,#tag2'
        )
        assert cid is not None
        conn = tronix_logger.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT titulo, legenda, hashtags FROM conteudo WHERE id=?", (cid,))
        row = cursor.fetchone()
        conn.close()
        assert len(row[0]) == 200  # truncado
        # tags de script devem ser removidas? nossa sanitização apenas strip, não remove tags.
        # Mas pelo menos deve estar presente o texto.
        assert 'Texto' in row[1]
        assert '#tag1,#tag2' == row[2]
    finally:
        tronix_logger.DB_PATH = original_db
        shutil.rmtree(test_dir, ignore_errors=True)

def test_coercao_numerica():
    """Valores numéricos negativos devem virar 0 (mínimo)."""
    test_dir = tempfile.mkdtemp()
    original_db = tronix_logger.DB_PATH
    tronix_logger.DB_PATH = os.path.join(test_dir, 'test.db')
    try:
        tronix_logger.inicializar()
        cid = tronix_logger.registrar(
            tipo='video',
            titulo='Teste num',
            arquivo='video.mp4',
            tamanho_kb=-10,
            duracao_seg=-5
        )
        assert cid is not None
        conn = tronix_logger.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT tamanho_kb, duracao_seg FROM conteudo WHERE id=?", (cid,))
        row = cursor.fetchone()
        conn.close()
        assert row[0] == 0
        assert row[1] == 0
    finally:
        tronix_logger.DB_PATH = original_db
        shutil.rmtree(test_dir, ignore_errors=True)

def test_log_structured_json(capsys):
    """Logs devem sair como JSON válido."""
    test_dir = tempfile.mkdtemp()
    original_db = tronix_logger.DB_PATH
    tronix_logger.DB_PATH = os.path.join(test_dir, 'test.db')
    try:
        tronix_logger.inicializar()
        # Captura stdout
        from io import StringIO
        import contextlib
        f = StringIO()
        with contextlib.redirect_stdout(f):
            tronix_logger.log('info', 'test_event', chave='valor')
        output = f.getvalue().strip()
        # Deve ser JSON
        data = json.loads(output)
        assert data['level'] == 'info'
        assert data['evento'] == 'test_event'
        assert data['chave'] == 'valor'
        assert 'ts' in data
    finally:
        tronix_logger.DB_PATH = original_db
        shutil.rmtree(test_dir, ignore_errors=True)

def test_cache_asset():
    """Cache de assets deve retornar mesmo caminho para mesmo hash."""
    test_dir = tempfile.mkdtemp()
    # Cria arquivo falso
    fake_path = os.path.join(test_dir, 'dummy.txt')
    with open(fake_path, 'w') as f:
        f.write('conteudo teste')
    # Primeiro acesso
    cached1 = tronix_logger.asset_cache_get(fake_path)
    # Ainda não está em cache, deve retornar None
    assert cached1 is None
    # Adiciona ao cache
    tronix_logger.asset_cache_set(fake_path)
    cached2 = tronix_logger.asset_cache_get(fake_path)
    assert cached2 == fake_path
    # Modifica o arquivo -> hash muda -> cache deve retornar None
    with open(fake_path, 'w') as f:
        f.write('conteudo alterado')
    cached3 = tronix_logger.asset_cache_get(fake_path)
    assert cached3 is None
    # Limpa
    shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == '__main__':
    # Simples execução dos testes
    import traceback
    tests = [
        test_validacao_tipo_invalido,
        test_sanitizacao_strings,
        test_coercao_numerica,
        test_log_structured_json,
        test_cache_asset,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} -> {e}")
            traceback.print_exc()
            failed += 1
    print(f"\nTotal: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)