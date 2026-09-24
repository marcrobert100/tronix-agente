import cv2
import numpy as np
import sqlite3
import os
import pyttsx3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'portaria.db')

SCHEMA = '''
CREATE TABLE IF NOT EXISTS pessoas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    tipo TEXT NOT NULL,
    unidade TEXT,
    embedding BLOB NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs_acesso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pessoa_id INTEGER,
    nome TEXT,
    cpf TEXT,
    reconhecido BOOLEAN,
    similaridade REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pessoa_id) REFERENCES pessoas(id)
);
'''

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def add_person(self, nome, cpf, tipo, unidade, embedding):
        emb_bytes = embedding.astype(np.float32).tobytes()
        cur = self.conn.execute(
            'INSERT INTO pessoas (nome, cpf, tipo, unidade, embedding) VALUES (?, ?, ?, ?, ?)',
            (nome, cpf, tipo, unidade, emb_bytes)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_all_people(self):
        cur = self.conn.execute('SELECT id, nome, cpf, tipo, unidade, embedding FROM pessoas')
        results = []
        for row in cur.fetchall():
            d = dict(row)
            d['embedding'] = np.frombuffer(d['embedding'], dtype=np.float32)
            results.append(d)
        return results

    def log_access(self, pessoa_id, nome, cpf, reconhecido, similaridade):
        self.conn.execute(
            'INSERT INTO logs_acesso (pessoa_id, nome, cpf, reconhecido, similaridade) VALUES (?, ?, ?, ?, ?)',
            (pessoa_id, nome, cpf, reconhecido, similaridade)
        )
        self.conn.commit()

    def get_logs(self, limit=20):
        cur = self.conn.execute(
            'SELECT * FROM logs_acesso ORDER BY timestamp DESC LIMIT ?', (limit,)
        )
        return [dict(row) for row in cur.fetchall()]


class SimpleFaceRecognizer:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        print("Usando OpenCV Haar Cascade (fallback simples)")

    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
        return [(x, y, w, h) for (x, y, w, h) in faces]

    def get_embedding(self, frame):
        faces = self.detect_faces(frame)
        if not faces:
            return None, None
        x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
        face_img = frame[y:y+h, x:x+w]
        face_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        face_resized = cv2.resize(face_gray, (128, 128))
        face_eq = cv2.equalizeHist(face_resized)
        features = face_eq.flatten().astype(np.float32) / 255.0
        if len(features) > 512:
            features = features[:512]
        elif len(features) < 512:
            features = np.pad(features, (0, 512 - len(features)))
        return features, (x, y, w, h)

    def cosine_similarity(self, emb1, emb2):
        emb1 = emb1 / (np.linalg.norm(emb1) + 1e-10)
        emb2 = emb2 / (np.linalg.norm(emb2) + 1e-10)
        return float(np.dot(emb1, emb2))

    def recognize(self, frame, db, threshold=0.6):
        embedding, bbox = self.get_embedding(frame)
        if embedding is None:
            return None, None, 0.0
        known = db.get_all_people()
        if not known:
            return None, None, 0.0
        best_match = None
        best_score = -1.0
        for person in known:
            score = self.cosine_similarity(embedding, person['embedding'])
            if score > best_score:
                best_score = score
                best_match = person
        if best_match and best_score >= threshold:
            return best_match, bbox, best_score
        return None, bbox, best_score


class TTSEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 0.9)
        voices = self.engine.getProperty('voices')
        for v in voices:
            if 'brazil' in v.name.lower() or 'portuguese' in v.name.lower() or 'pt' in v.id.lower():
                self.engine.setProperty('voice', v.id)
                break

    def speak(self, text):
        print(f"[TTS] {text}")
        self.engine.say(text)
        self.engine.runAndWait()


def cadastrar_pessoa(db, recognizer, tts):
    print("\n=== CADASTRAR MORADOR ===")
    nome = input("Nome completo: ").strip()
    if not nome:
        return
    cpf = input("CPF (11 digitos): ").strip()
    if len(cpf) != 11 or not cpf.isdigit():
        print("CPF invalido")
        return
    print("Tipo: 1=Morador 2=Visitante 3=Funcionario")
    t = input("Escolha (1/2/3): ").strip()
    tipo = {'1': 'Morador', '2': 'Visitante', '3': 'Funcionario'}.get(t, 'Morador')
    unidade = input("Bloco/Ap (opcional): ").strip()

    print("\nPosicione o rosto na camera e pressione ESPACO para capturar...")
    cap = cv2.VideoCapture(0)
    embedding = None
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        faces = recognizer.detect_faces(frame)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, "ESPACO=capturar  ESC=cancelar", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.imshow('Cadastro', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        if key == 32:  # SPACE
            emb, _ = recognizer.get_embedding(frame)
            if emb is not None:
                embedding = emb
                print("Rosto capturado!")
            else:
                print("Nenhum rosto detectado, tente novamente")
            break
    cap.release()
    cv2.destroyAllWindows()

    if embedding is not None:
        try:
            db.add_person(nome, cpf, tipo, unidade, embedding)
            print(f"SUCESSO: {nome} cadastrado!")
            tts.speak(f"{nome} cadastrado com sucesso")
        except Exception as e:
            print(f"ERRO: {e}")


def modo_portaria(db, recognizer, tts, threshold=0.6):
    print("\n=== MODO PORTARIA ===")
    print("Pressione Q para sair")
    cap = cv2.VideoCapture(0)
    last_spoken = {}
    cooldown = 3.0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        pessoa, bbox, score = recognizer.recognize(frame, db, threshold)

        if bbox:
            x, y, w, h = bbox
            if pessoa:
                color = (0, 255, 0)
                label = f"{pessoa['nome']} ({score:.2%})"
                now = datetime.now().timestamp()
                key = pessoa['id']
                if key not in last_spoken or now - last_spoken[key] > cooldown:
                    last_spoken[key] = now
                    frase = f"Acesso liberado, {pessoa['nome']}"
                    tts.speak(frase)
                    db.log_access(pessoa['id'], pessoa['nome'], pessoa['cpf'], True, score)
            else:
                color = (0, 0, 255)
                label = f"DESCONHECIDO ({score:.2%})"
                tts.speak("Acesso negado. Nao cadastrado.")
                db.log_access(None, "Desconhecido", "", False, score)

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, label, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.putText(frame, f"Limiar: {threshold:.2f}  Q=sair", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow('Portaria Facial', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def listar_moradores(db):
    print("\n=== MORADORES CADASTRADOS ===")
    pessoas = db.get_all_people()
    if not pessoas:
        print("Nenhum morador cadastrado")
        return
    for p in pessoas:
        print(f"  {p['id']}: {p['nome']} | CPF: {p['cpf']} | {p['tipo']} | {p['unidade'] or '-'}")


def ver_logs(db):
    print("\n=== ULTIMOS ACESSOS ===")
    logs = db.get_logs(20)
    if not logs:
        print("Nenhum log")
        return
    for l in logs:
        status = "OK" if l['reconhecido'] else "NEGADO"
        print(f"  {l['timestamp']} | {l['nome']} | {status} | sim={l['similaridade']:.2%}")


def main():
    db = Database()
    recognizer = SimpleFaceRecognizer()
    tts = TTSEngine()

    print("""
==========================================
   PORTARIA FACIAL - CONSOLE TEST
==========================================
1. Cadastrar morador
2. Modo portaria (reconhecimento)
3. Listar moradores
4. Ver logs de acesso
5. Sair
""")

    while True:
        op = input("Escolha (1-5): ").strip()
        if op == '1':
            cadastrar_pessoa(db, recognizer, tts)
        elif op == '2':
            modo_portaria(db, recognizer, tts)
        elif op == '3':
            listar_moradores(db)
        elif op == '4':
            ver_logs(db)
        elif op == '5':
            break
        else:
            print("Opcao invalida")

    print("Encerrando...")

if __name__ == '__main__':
    main()