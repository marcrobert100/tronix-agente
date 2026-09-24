# Portaria Facial - Sistema de Reconhecimento para Condomínio/Portaria

Sistema **offline** de controle de acesso por reconhecimento facial, rodando 100% no celular Android.

## Funcionalidades
- **Cadastro de moradores**: Nome, CPF, tipo (Morador/Visitante/Funcionário), unidade, rosto
- **Reconhecimento em tempo real**: Câmera frontal, FaceNet embedding, similaridade cosseno
- **TTS (voz)**: Fala nome e info ao reconhecer ("Acesso liberado, João")
- **SQLite local**: Banco criptografado no celular, sem nuvem
- **Logs de acesso**: Histórico com timestamp, similaridade, status
- **Configurável**: Limiar de similaridade, frases de liberado/negado

## Arquitetura
```
main.py           # App Kivy (UI + navegação)
database.py       # SQLite (pessoas, embeddings, config, logs)
face_recognition.py # FaceNet (MTCNN + InceptionResnetV1) ou fallback OpenCV
tts_engine.py     # pyttsx3 (voz offline PT-BR)
buildozer.spec    # Build Android APK
```

## Requisitos
- Python 3.10+
- Android 7.0+ (API 24) com câmera frontal
- 2GB RAM mínimo (4GB recomendado para FaceNet)

## Instalação Desktop (Teste)
```bash
cd portaria_facial
pip install -r requirements.txt
python main.py
```

## Build Android APK (via WSL)
```bash
# Opção 1: Script automatizado
build_android.bat

# Opção 2: Manual no WSL
wsl
cd /home/usuario/portaria_facial
python3 -m venv venv
source venv/bin/activate
pip install buildozer cython
pip install -r requirements.txt
buildozer android debug
```
APK sai em `bin/portariafacial-1.0.0-arm64-v8a-debug.apk`

## Uso
1. **CADASTRAR MORADOR** → Preencher nome, CPF, tipo, unidade → Posicionar rosto → CAPTURAR
2. **RECONHECER (PORTARIA)** → Apontar câmera para rosto → App fala e mostra info
3. **LISTAR MORADORES** → Ver todos cadastrados
4. **CONFIGURAÇÕES** → Ajustar limiar (0.6 padrão), frases TTS

## Modelo FaceNet
- **MTCNN**: Detecção de rosto + alinhamento (landmarks)
- **InceptionResnetV1 (vggface2)**: Embedding 512-d
- **Similaridade**: Cosseno, limiar padrão 0.60 (ajustável 0.30-0.90)

## Fallback OpenCV
Se `facenet-pytorch` falhar (ex: CPU sem AVX), usa:
- Haar Cascade / SSD DNN para detecção
- Histograma equalizado 512-d para embedding (menos preciso)

## Segurança
- Embeddings salvos como BLOB (float32), não imagens
- Banco SQLite local, sem rede
- CPF como ID único (indexado)
- Logs só no dispositivo

## Hardware sugerido para portaria
- Tablet Android 10"+ com câmera frontal boa
- Suporte fixo + iluminação frontal
- Relé/ESP32 para abrir porta (GPIO via USB/Bluetooth - futuro)

## Próximos passos
- [ ] Integração relé/ESP32 (abrir porta física)
- [ ] Sync backup criptografado (Google Drive local)
- [ ] Multi-câmera (entrada + saída)
- [ ] Dashboard web local (Flask + WebView)
- [ ] App iOS (Kivy-iOS)