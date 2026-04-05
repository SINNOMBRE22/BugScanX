import re
import random
import requests
from bugscanx.utils.http import HEADERS, USER_AGENTS


class RequestHandler:
    """Maneja las peticiones a las APIs de subdominios"""
    def __init__(self):
        self.session = requests.Session()
        # Ignoramos errores de SSL para mayor compatibilidad
        self.session.verify = False
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    def _get_headers(self):
        """Rotación de User-Agents para evitar bloqueos"""
        headers = HEADERS.copy()
        headers["user-agent"] = random.choice(USER_AGENTS)
        return headers

    def get(self, url, timeout=10):
        try:
            response = self.session.get(url, timeout=timeout, headers=self._get_headers())
            if response.status_code == 200:
                return response
        except requests.RequestException:
            pass
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


class DomainValidator:
    """Valida que los dominios y subdominios tengan un formato correcto"""
    # Expresión regular para verificar dominios válidos
    DOMAIN_REGEX = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
        r'[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]$'
    )

    @classmethod
    def is_valid_domain(cls, domain):
        """Verifica si el texto ingresado es un dominio real"""
        return bool(
            domain
            and isinstance(domain, str)
            and cls.DOMAIN_REGEX.match(domain)
        )

    @staticmethod
    def filter_valid_subdomains(subdomains, domain):
        """
        Filtra la lista de resultados para asegurar que todos 
        pertenezcan al dominio objetivo (ej. que terminen en .telcel.com)
        """
        if not domain or not isinstance(domain, str):
            return set()

        domain_suffix = f".{domain}"
        result = set()

        for sub in subdomains:
            if not isinstance(sub, str):
                continue

            # El subdominio es válido si es igual al dominio o termina con el sufijo
            if sub == domain or sub.endswith(domain_suffix):
                result.add(sub)

        return result


class CursorManager:
    """Controla la visibilidad del cursor en la terminal (Aesthetic)"""
    def __enter__(self):
        # Oculta el cursor
        print('\033[?25l', end='', flush=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Muestra el cursor al finalizar
        print('\033[?25h', end='', flush=True)
