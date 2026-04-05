import datetime
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from .utils import RequestHandler


class SubdomainSource(RequestHandler, ABC):
    def __init__(self, name):
        super().__init__()
        self.name = name

    @abstractmethod
    def fetch(self, domain):
        """Método base para extraer subdominios de cada fuente"""
        pass


class CrtshSource(SubdomainSource):
    def __init__(self):
        super().__init__("Crt.sh")

    def fetch(self, domain):
        """Busca en registros de certificados SSL (Transparencia de Certificados)"""
        subdomains = set()
        # Consulta crt.sh y pide la respuesta en formato JSON
        response = self.get(f"https://crt.sh/?q=%25.{domain}&output=json")
        if response and response.headers.get('Content-Type') == 'application/json':
            for entry in response.json():
                subdomains.update(entry['name_value'].splitlines())
        return subdomains


class HackertargetSource(SubdomainSource):
    def __init__(self):
        super().__init__("Hackertarget")

    def fetch(self, domain):
        """Usa la API gratuita de Hackertarget para búsqueda de hosts"""
        subdomains = set()
        response = self.get(f"https://api.hackertarget.com/hostsearch/?q={domain}")
        if response and 'text' in response.headers.get('Content-Type', ''):
            subdomains.update(
                [line.split(",")[0] for line in response.text.splitlines()]
            )
        return subdomains


class RapidDnsSource(SubdomainSource):
    def __init__(self):
        super().__init__("RapidDNS")

    def fetch(self, domain):
        """Extrae subdominios mediante scraping de la web de RapidDNS"""
        subdomains = set()
        response = self.get(f"https://rapiddns.io/subdomain/{domain}?full=1")
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('td'):
                text = link.get_text(strip=True)
                if text.endswith(f".{domain}"):
                    subdomains.add(text)
        return subdomains


class AnubisDbSource(SubdomainSource):
    def __init__(self):
        super().__init__("AnubisDB")

    def fetch(self, domain):
        """Consulta la base de datos de Anubis para subdominios conocidos"""
        subdomains = set()
        response = self.get(f"https://jldc.me/anubis/subdomains/{domain}")
        if response:
            try:
                subdomains.update(response.json())
            except Exception:
                pass
        return subdomains


class AlienVaultSource(SubdomainSource):
    def __init__(self):
        super().__init__("AlienVault")

    def fetch(self, domain):
        """Utiliza el Passive DNS de AlienVault OTX (muy potente)"""
        subdomains = set()
        response = self.get(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns")
        if response:
            for entry in response.json().get("passive_dns", []):
                hostname = entry.get("hostname")
                if hostname:
                    subdomains.add(hostname)
        return subdomains


class CertSpotterSource(SubdomainSource):
    def __init__(self):
        super().__init__("CertSpotter")

    def fetch(self, domain):
        """Otra fuente de transparencia de certificados para mayor precisión"""
        subdomains = set()
        response = self.get(f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names")
        if response:
            for cert in response.json():
                subdomains.update(cert.get('dns_names', []))
        return subdomains


class C99Source(SubdomainSource):
    def __init__(self):
        super().__init__("C99")

    def fetch(self, domain):
        """Escanea los últimos 7 días de registros en SubdomainFinder de C99"""
        subdomains = set()
        # Genera fechas de la última semana
        dates = [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                for i in range(7)]

        for date in dates:
            url = f"https://subdomainfinder.c99.nl/scans/{date}/{domain}"
            response = self.get(url)
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.select('td a.link.sd'):
                    text = link.get_text(strip=True)
                    if text.endswith(f".{domain}"):
                        subdomains.add(text)
                # Si encontramos algo en una fecha, paramos para no saturar
                if subdomains:
                    break
        return subdomains


def get_sources():
    """Retorna la lista de todas las fuentes disponibles para el escaneo"""
    return [
        CrtshSource(),
        HackertargetSource(),
        RapidDnsSource(),
        AnubisDbSource(),
        AlienVaultSource(),
        CertSpotterSource(),
        # C99Source()  # Se deja comentado por si la web de C99 presenta bloqueos
    ]
