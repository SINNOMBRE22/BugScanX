import ssl
import socket
import http.client
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from rich import print
from bugscanx.utils.prompts import get_input

class HostScanner:
    # Diccionario de proveedores de CDN con sus huellas digitales (Headers y CNAMEs)
    CDN_PROVIDERS = {
        "Cloudflare": {
            "headers": ["cf-ray", "cf-cache-status", "cf-request-id", "cf-visitor", "cf-connecting-ip", "cf-ipcountry", "cf-railgun", "cf-polished", "cf-apo-via"],
            "cname": ["cloudflare.net", "cloudflare.com", "cloudflare-dns.com"]
        },
        "Amazon CloudFront": {
            "headers": ["x-amz-cf-id", "x-amz-cf-pop", "x-amz-request-id"],
            "cname": ["cloudfront.net", "amazonaws.com"]
        },
        "Google": {
            "headers": ["x-goog-cache-status", "x-goog-generation", "x-goog-metageneration", "x-guploader-uploadid"],
            "cname": ["googleusercontent.com", "googlevideo.com", "google.com", "gstatic.com", "googleapis.com"]
        },
        "Akamai": {
            "headers": ["x-akamai-transformed", "akamai-cache-status", "akamai-origin-hop", "x-akamai-request-id", "x-akamai-ssl-client-sid", "akamai-grn", "x-akamai-config-log-detail"],
            "cname": ["akamai.net", "edgekey.net", "edgesuite.net", "akamaized.net", "akamaiedge.net", "akamaitechnologies.com", "akamaihd.net"]
        },
        "Fastly": {
            "headers": ["fastly-debug", "x-served-by", "x-cache-hits", "x-timer", "fastly-ff", "x-fastly-request-id"],
            "cname": ["fastly.net", "fastlylb.net"]
        },
        "Microsoft Azure": {
            "headers": ["x-azure-ref", "x-azure-requestid", "x-msedge-ref", "x-ec-custom-error", "x-azure-fdid"],
            "cname": ["azureedge.net", "msedge.net", "azure-edge.net", "trafficmanager.net", "azurefd.net"]
        },
        "BunnyCDN": {
            "headers": ["cdn-pullzone", "cdn-uid", "cdn-requestid", "cdn-cache", "cdn-zone", "bunnycdn-cache-tag"],
            "cname": ["b-cdn.net"]
        },
        "Sucuri": {
            "headers": ["x-sucuri-id", "x-sucuri-cache", "x-sucuri-block", "server-sucuri"],
            "cname": ["sucuri.net"]
        },
        "Imperva": {
            "headers": ["x-iinfo", "incap-ses", "visid-incap"],
            "cname": ["incapdns.net", "imperva.com", "impervadns.net"]
        }
    }

    def __init__(self, host, protocol="https", method_list=None):
        self.host = host
        self.protocol = protocol
        self.url = f"{protocol}://{host}"
        self.method_list = method_list
        self.http_headers = {}

    def get_ips(self):
        """Obtiene y muestra las direcciones IP vinculadas al host"""
        try:
            ips = socket.getaddrinfo(self.host, None)
            unique_ips = list(set(ip[4][0] for ip in ips))
            print("[bold white]\nDirecciones IP:[/bold white]")
            for ip in unique_ips:
                print(f"  • {ip}")
            return True
        except socket.gaierror as e:
            print(f"[bold red] Error al resolver el host: {e}[/bold red]")
            return False

    def get_cname_records(self):
        """Intenta obtener registros CNAME para identificar CDNs"""
        try:
            result = []
            answers = socket.getaddrinfo(self.host, None)
            for answer in answers:
                try:
                    cname = socket.gethostbyaddr(answer[4][0])[0]
                    result.append(cname.lower())
                except (socket.herror, socket.gaierror):
                    continue
            return result
        except (socket.herror, socket.gaierror):
            return []

    def get_cdn(self):
        """Detecta si el host usa una Red de Entrega de Contenidos (CDN)"""
        try:
            detected_cdns = set()
            # Usamos los headers obtenidos en get_http_info si están disponibles
            if self.http_headers:
                headers = {k.lower(): v.lower() for k, v in self.http_headers.items()}
            else:
                response = requests.get(self.url, timeout=5)
                headers = {k.lower(): v.lower() for k, v in response.headers.items()}

            cnames = self.get_cname_records()

            for provider, indicators in self.CDN_PROVIDERS.items():
                # Revisión por Headers
                if any(header.lower() in headers.keys() for header in indicators['headers']):
                    detected_cdns.add(provider)
                    continue
                # Revisión por CNAME
                if any(cname_pattern in cname for cname in cnames 
                      for cname_pattern in indicators['cname']):
                    detected_cdns.add(provider)

            if detected_cdns:
                print("[bold white]\nCDNs Detectadas:[/bold white]")
                for cdn in detected_cdns:
                    print(f"  • {cdn}")
            else:
                print("[bold white]\nNo se detectó una CDN conocida[/bold white]")

        except requests.exceptions.RequestException as e:
            print(f"[bold red] Error al verificar CDN: {e}[/bold red]")

    def get_http_info(self):
        """Prueba los diferentes métodos HTTP (GET, POST, etc.)"""
        def check_method(method):
            try:
                response = requests.request(method, self.url, timeout=5)
                return method, response.status_code, dict(response.headers)
            except requests.exceptions.RequestException as e:
                return method, 0, {'error': str(e)}

        with ThreadPoolExecutor(max_workers=len(self.method_list)) as executor:
            futures = {
                executor.submit(check_method, method): method 
                for method in self.method_list
            }

            for future in as_completed(futures):
                method, status_code, headers = future.result()

                if method == "GET" and status_code > 0 and 'error' not in headers:
                    self.http_headers = headers

                status_desc = http.client.responses.get(status_code, 'Código Desconocido')
                print(f"\n[bold yellow]Método: {method}[/bold yellow] | [bold magenta]Estado: {status_code} {status_desc}[/bold magenta]")

                if 'error' in headers:
                    print(f"  [bold red]Error: {headers['error']}[/bold red]")
                else:
                    if headers:
                        print("  [bold white]Encabezados (Headers):[/bold white]")
                        for header_name, header_value in headers.items():
                            print(f"    {header_name}: {header_value}")

    def get_sni_info(self):
        """Extrae información del certificado SSL y la negociación TLS"""
        if self.protocol != "https":
            return

        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.host, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    print(f"\n[bold green]--- Información SSL/TLS ---[/bold green]")
                    print(f"[bold white]Versión SSL:[/bold white] {ssock.version()}")
                    print(f"[bold white]Cifrado:[/bold white] {ssock.cipher()[0]}")
                    print(f"[bold white]Bits:[/bold white] {ssock.cipher()[1]}")

                    cert = ssock.getpeercert()
                    
                    def parse_cert_field(field):
                        # Limpiamos el formato del certificado para que sea legible
                        data = {}
                        for item in field:
                            if isinstance(item, tuple) and len(item) > 0:
                                sub_item = item[0]
                                data[sub_item[0]] = sub_item[1]
                        return data

                    print(f"[bold white]Sujeto:[/bold white] {parse_cert_field(cert.get('subject', []))}")
                    print(f"[bold white]Emisor:[/bold white] {parse_cert_field(cert.get('issuer', []))}")
                    print(f"[bold white]Número de Serie:[/bold white] {cert.get('serialNumber', 'N/A')}")

        except Exception as e:
            print(f"[bold red] Error al obtener info SSL: {e}[/bold red]")

    def scan(self):
        """Ejecuta el análisis completo"""
        if not self.get_ips():
            return
        self.get_http_info()
        self.get_cdn()
        self.get_sni_info()

def main():
    """Interfaz de usuario traducida"""
    host = get_input("Ingresa el host a analizar", validators="required")
    protocol = get_input("Selecciona el protocolo", input_type="choice", choices=["http", "https"])
    available_methods = ["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"]
    method_list = get_input(
        "Selecciona los métodos HTTP a probar",
        input_type="choice",
        multiselect=True, 
        choices=available_methods
    )

    scanner = HostScanner(host, protocol, method_list)
    scanner.scan()
