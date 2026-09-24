try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False
    pyttsx3 = None
import threading
import queue

class TTSEngine:
    def __init__(self):
        self.engine = None
        self.queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        self._init_engine()

    def _init_engine(self):
        if not HAS_PYTTSX3:
            return
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 180)
            self.engine.setProperty('volume', 0.9)
            voices = self.engine.getProperty('voices')
            for v in voices:
                if 'brazil' in v.name.lower() or 'portuguese' in v.name.lower() or 'pt' in v.id.lower():
                    self.engine.setProperty('voice', v.id)
                    break
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()
        except Exception as e:
            print(f"TTS init error: {e}")
            self.engine = None

    def _worker(self):
        while self.running:
            try:
                text = self.queue.get(timeout=0.5)
                if text is None:
                    break
                if self.engine:
                    self.engine.say(text)
                    self.engine.runAndWait()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"TTS error: {e}")

    def speak(self, text: str):
        if self.engine and self.running:
            self.queue.put(text)

    def stop(self):
        self.running = False
        self.queue.put(None)
        if self.worker_thread:
            self.worker_thread.join(timeout=1.0)
        if self.engine:
            self.engine.stop()