import os
import sys
from abc import ABC, abstractmethod
from queue import Queue, Empty
from threading import Thread, RLock


class Logger:
    # Colores para la interfaz estética que tanto te gusta (Cyberpunk style)
    COLORS = {
        'ORANGE': '\033[33m',
        'MAGENTA': '\033[35m',
        'CYAN': '\033[36m',
        'LGRAY': '\033[37m',
        'GRAY': '\033[90m',
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
    }
    RESET = '\033[0m'
    CLEAR_LINE = '\033[2K'

    def __init__(self):
        self._lock = RLock()

    @classmethod
    def colorize(cls, text, color):
        return f"{cls.COLORS.get(color, '')}{text}{cls.RESET}"

    def replace(self, message):
        """Reemplaza la línea actual en la terminal (para la barra de progreso)"""
        try:
            cols = os.get_terminal_size().columns
        except OSError:
            cols = 80
        msg = f"{message[:cols - 3]}..." if len(message) > cols else message
        with self._lock:
            sys.stdout.write(f'{self.CLEAR_LINE}{msg}{self.RESET}\r')
            sys.stdout.flush()

    def log(self, message):
        """Escribe un log permanente en la terminal"""
        with self._lock:
            sys.stderr.write(f'\r{self.CLEAR_LINE}{message}{self.RESET}\n')
            sys.stderr.flush()


class CursorManager:
    """Oculta el cursor mientras escanea para que se vea más limpio"""
    def __enter__(self):
        print('\033[?25l', end='', flush=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('\033[?25h', end='', flush=True)


class MultiThread(ABC):
    def __init__(self, threads=50):
        self._lock = RLock()
        self._queue = Queue(maxsize=5000)

        self._total = 0
        self._scanned = 0
        self._success = []
        self._success_count = 0

        self.threads = threads
        self.logger = Logger()

    def set_total(self, total):
        self._total = total

    def start(self):
        print()
        with CursorManager():
            try:
                self.init()
                # Creamos los hilos trabajadores
                workers = [
                    Thread(target=self._worker, daemon=True)
                    for _ in range(self.threads)
                ]
                for t in workers:
                    t.start()

                # Generador de tareas (hosts a escanear)
                task_gen = self.generate_tasks()
                try:
                    while True:
                        task = next(task_gen)
                        self._queue.put(task)
                except StopIteration:
                    pass

                self._queue.join()
                self.complete()
            except KeyboardInterrupt:
                # Si cancelas con Ctrl+C, detiene todo limpiamente
                pass
        print()

    def _worker(self):
        while True:
            try:
                task = self._queue.get(timeout=1)
            except Empty:
                return

            try:
                self.task(task)
            except Exception:
                pass
            finally:
                with self._lock:
                    self._scanned += 1
                self._queue.task_done()

    def success(self, item):
        """Registra un host encontrado con éxito"""
        with self._lock:
            self._success.append(item)
            self._success_count += 1

    def get_success(self):
        return self._success

    def progress(self, *extra):
        """Muestra el progreso en tiempo real"""
        parts = [
            f"{self._scanned / max(1, self._total) * 100:.2f}%",
            f"Escaneados: {self._scanned} / {self._total}",
            f"Encontrados: {self._success_count}"
        ] + [str(x) for x in extra if x]
        self.logger.replace(" - ".join(parts))

    def complete(self):
        # Traducción del mensaje final
        self.progress(self.logger.colorize("Escaneo finalizado", "GREEN"))

    @abstractmethod
    def generate_tasks(self): pass

    @abstractmethod
    def init(self): pass

    @abstractmethod
    def task(self, task): pass
