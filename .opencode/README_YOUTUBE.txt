=== README - UPLOAD DE VÍDEO PARA O YOUTUBE ===

OBJETIVO:
Fazer upload do vídeo "frutas.mp4" para o YouTube usando a API do YouTube.

SITUAÇÃO ATUAL:
✓ Vídeo encontrado: C:\Users\CHCONTE RECPÇÃO\Desktop\frutas.mp4
✓ Tamanho: 9.85 MB (16.07 segundos)
✓ Formato: MP4 (compatível com YouTube)
✓ Scripts Python criados

PROBLEMA:
✗ API key fornecida não funciona para a YouTube Data API v3
✗ Upload de vídeos requer OAuth 2.0, não API key

SOLUÇÃO - 2 OPÇÕES:

OPÇÃO 1: USAR API KEY (apenas para consultas)
1. Crie uma nova API key no Google Cloud Console
2. Ative a API "YouTube Data API v3"
3. Atualize os scripts com a nova API key
4. Use para consultas (não upload)

OPÇÃO 2: CONFIGURAR OAuth 2.0 (para upload)
1. Acesse: https://console.cloud.google.com/
2. Crie um projeto e ative "YouTube Data API v3"
3. Crie credenciais OAuth 2.0 para "Desktop app"
4. Baixe o arquivo client_secret.json
5. Execute: python youtube_upload.py

ARQUIVOS CRIADOS:
Scripts Python:
- youtube_upload.py (upload com OAuth)
- youtube_check.py (verifica API key)
- youtube_channel_info.py (info do canal)
- configurar_oauth.py (ajuda OAuth)
- verificar_oauth.py (verifica OAuth)
- criar_api_key.py (cria API key)
- usar_nova_api_key.py (instruções)
- verify_video_file.py (verifica vídeo)

Arquivos de texto:
- README_YOUTUBE.txt (este arquivo)
- RESUMO_FINAL.txt (resumo completo)
- OAUTH_CONFIG_PASSOS.txt (instruções OAuth)
- detalhes_api_key.txt (detalhes da API key)

PRÓXIMOS PASSOS:
1. Ler este arquivo
2. Escolher Opção 1 ou 2 acima
3. Seguir as instruções
4. Executar o script correspondente

NOTA:
- API key: apenas para consultas (leitura)
- OAuth 2.0: necessário para upload de vídeos
- O vídeo está pronto para upload!
