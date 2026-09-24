import cv2
import numpy as np
import torch
import torch.nn as nn
from typing import Optional, Tuple, List

try:
    from facenet_pytorch import MTCNN, InceptionResnetV1
    HAS_FACENET = True
except ImportError:
    HAS_FACENET = False
    print("facenet-pytorch nao instalado. Usando fallback OpenCV DNN.")

class FaceRecognizer:
    def __init__(self, device: str = 'cpu'):
        self.device = device
        self.face_detector = None
        self.embedder = None
        self.input_size = (160, 160)
        self._init_models()

    def _init_models(self):
        if HAS_FACENET:
            self.face_detector = MTCNN(
                image_size=160,
                margin=20,
                min_face_size=40,
                thresholds=[0.6, 0.7, 0.7],
                factor=0.709,
                post_process=True,
                device=self.device
            )
            self.embedder = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        else:
            self._init_opencv_fallback()

    def _init_opencv_fallback(self):
        proto = "deploy.prototxt"
        model = "res10_300x300_ssd_iter_140000.caffemodel"
        if os.path.exists(proto) and os.path.exists(model):
            self.face_detector = cv2.dnn.readNetFromCaffe(proto, model)
        else:
            self.face_detector = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        self.embedder = None

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        if HAS_FACENET and self.face_detector:
            boxes, _ = self.face_detector.detect(frame)
            if boxes is not None:
                return [(int(b[0]), int(b[1]), int(b[2]-b[0]), int(b[3]-b[1])) for b in boxes]
        elif hasattr(self.face_detector, 'detectMultiScale'):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
            return [(x, y, w, h) for (x, y, w, h) in faces]
        else:
            h, w = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123))
            self.face_detector.setInput(blob)
            detections = self.face_detector.forward()
            faces = []
            for i in range(detections.shape[2]):
                conf = detections[0, 0, i, 2]
                if conf > 0.5:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (x1, y1, x2, y2) = box.astype(int)
                    faces.append((x1, y1, x2-x1, y2-y1))
            return faces
        return []

    def get_embedding(self, frame: np.ndarray) -> Optional[np.ndarray]:
        faces = self.detect_faces(frame)
        if not faces:
            return None
        x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
        face_img = frame[y:y+h, x:x+w]
        if HAS_FACENET and self.embedder:
            face_tensor = self._preprocess_face(face_img)
            with torch.no_grad():
                embedding = self.embedder(face_tensor.unsqueeze(0).to(self.device))
            return embedding.cpu().numpy().flatten()
        else:
            return self._opencv_embedding(face_img)

    def _preprocess_face(self, face_img: np.ndarray) -> torch.Tensor:
        face_resized = cv2.resize(face_img, self.input_size)
        face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
        face_norm = (face_rgb - 127.5) / 128.0
        return torch.from_numpy(face_norm.transpose(2, 0, 1)).float()

    def _opencv_embedding(self, face_img: np.ndarray) -> np.ndarray:
        face_resized = cv2.resize(face_img, (128, 128))
        face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        face_eq = cv2.equalizeHist(face_gray)
        features = face_eq.flatten().astype(np.float32) / 255.0
        if len(features) > 512:
            features = features[:512]
        elif len(features) < 512:
            features = np.pad(features, (0, 512 - len(features)))
        return features

    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        emb1 = emb1 / (np.linalg.norm(emb1) + 1e-10)
        emb2 = emb2 / (np.linalg.norm(emb2) + 1e-10)
        return float(np.dot(emb1, emb2))

    def recognize(self, frame: np.ndarray, db) -> Optional[Tuple[dict, float]]:
        embedding = self.get_embedding(frame)
        if embedding is None:
            return None
        known = db.get_all_embeddings()
        if not known:
            return None
        best_match = None
        best_score = -1.0
        for person in known:
            score = self.cosine_similarity(embedding, person['embedding'])
            if score > best_score:
                best_score = score
                best_match = person
        return (best_match, best_score) if best_match else None

    def release(self):
        pass

import os