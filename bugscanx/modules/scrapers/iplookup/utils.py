import time
import ipaddress
import random
from threading import Lock

import requests

# Importamos las cabeceras y agentes de usuario para evitar bloqueos
from bugscanx.utils.http import HEADERS, USER_AGENTS


class RateLimiter:
    """Controla la velocidad de las peticiones para evitar baneos"""
    def __init__(self, requests_per_second: float):
        self.delay = 1.0 / requests_per_second
        self.last_request = 0
        self._lock = Lock()

    def acquire(self):
        with self._lock:
            now = time.time()
            if now - self.last_request < self.delay:
                time.sleep(self.delay - (now - self.last_request))
            self.last_request = time.time()


class RequestHandler:
    """Maneja las peticiones HTTP (GET/POST) de forma segura"""
    def __init__(self):
        self.session = requests.Session()
        # Desactivamos la verificación SSL para mayor velocidad y evitar errores
        self.session.verify = False
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        # Limitamos a 1 petición por segundo por defecto
        self.rate_limiter = RateLimiter(1.0)

    def _get_headers(self):
        """Genera cabeceras aleatorias para cada petición"""
        headers = HEADERS.copy()
        headers["user-agent"] = random.choice(USER_AGENTS)
        return headers

    def get(self, url, timeout=10):
        self.rate_limiter.acquire()
        try:
            response = self.session.get(url, timeout=timeout, headers=self._get_headers())
            if response.status_code == 200:
                return response
        except requests.RequestException:
            pass
        return None

    def post(self, url, data=None):
        self.rate_limiter.acquire()
        try:
            response = self.session.post(url, data=data, headers=self._get_headers())
            if response.status_code == 200:
                return response
        except requests.RequestException:
            pass
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


class CursorManager:
    """Oculta y muestra el cursor de la terminal para una mejor estética"""
    def __enter__(self):
        print('\033[?25l', end='', flush=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('\033[?25h', end='', flush=True)


def process_cidr(cidr):
    """Convierte un rango CIDR (ej. 192.168.1.0/24) en una lista de IPs individuales"""
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError:
        return []


def process_input(input_str):
    """Detecta si la entrada es una IP única o un rango CIDR"""
    if '/' in input_str:
        return process_cidr(input_str)
    else:
        return [input_str]


def process_file(file_path):
    """Lee un archivo de texto y procesa todas las IPs o rangos que contenga"""
    ips = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                clean_line = line.strip()
                if clean_line:
                    ips.extend(process_input(clean_line))
        return ips
    except Exception:
        return []
