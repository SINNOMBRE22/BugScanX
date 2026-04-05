import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from bugscanx.utils.prompts import get_input
from .logger import SubFinderConsole
from .sources import get_sources
from .utils import DomainValidator, CursorManager


class SubFinder:
    def __init__(self):
        self.console = SubFinderConsole()
        self.completed = 0
        self.cursor_manager = CursorManager()

    def _fetch_from_source(self, source, domain):
        """Llama a cada fuente (Crt.sh, AlienVault, etc.) y filtra los resultados"""
        try:
            found = source.fetch(domain)
            return DomainValidator.filter_valid_subdomains(found, domain)
        except Exception:
            return set()

    @staticmethod
    def save_subdomains(subdomains, output_file):
        """Guarda la lista de subdominios únicos y ordenados"""
        if subdomains:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write("\n".join(sorted(subdomains)) + "\n")

    def process_domain(self, domain, output_file, sources, total):
        """Procesa un dominio individual usando múltiples hilos para las fuentes"""
        if not DomainValidator.is_valid_domain(domain):
            self.completed += 1
            return set()

        self.console.print_domain_start(domain)
        self.console.print_progress(self.completed, total)

        # Usamos 6 hilos para consultar las APIs simultáneamente
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [
                executor.submit(self._fetch_from_source, source, domain)
                for source in sources
            ]
            results = [f.result() for f in as_completed(futures)]

        subdomains = set().union(*results) if results else set()

        self.console.update_domain_stats(domain, len(subdomains))
        self.console.print_domain_complete(domain, len(subdomains))
        self.save_subdomains(subdomains, output_file)

        self.completed += 1
        self.console.print_progress(self.completed, total)
        return subdomains

    def run(self, domains, output_file, sources):
        """Inicia el proceso general de búsqueda para todos los dominios proporcionados"""
        if not domains:
            self.console.print_error("No se proporcionaron dominios válidos")
            return

        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        self.completed = 0
        all_subdomains = set()
        total = len(domains)

        with self.cursor_manager:
            # Procesa hasta 3 dominios base al mismo tiempo
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(self.process_domain, domain, output_file, sources, total)
                    for domain in domains
                ]
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        all_subdomains.update(result)
                    except Exception as e:
                        # Error al procesar un dominio específico
                        self.console.print(f"Error procesando dominio: {str(e)}")

            self.console.print_final_summary(output_file)
            return all_subdomains


def main():
    """Función principal con el menú interactivo traducido"""
    domains = []
    sources = get_sources()
    
    # Traducción del menú de selección
    input_type = get_input("Selecciona el modo de entrada", input_type="choice", choices=["Manual", "Archivo (File)"])
    
    if input_type == "Manual":
        domain_input = get_input("Ingresa el/los dominios (separados por coma)", validators="required")
        domains = [d.strip() for d in domain_input.split(',') if DomainValidator.is_valid_domain(d.strip())]
        default_output = f"{domains[0]}_subdominios.txt" if domains else "subdominios.txt"
    else:
        file_path = get_input("Nombre del archivo", input_type="file", validators="file")
        with open(file_path, 'r', encoding='utf-8') as f:
            domains = [d.strip() for d in f if DomainValidator.is_valid_domain(d.strip())]
        default_output = f"{file_path.rsplit('.', 1)[0]}_subdominios.txt"

    # Nombre del archivo donde se guardará la "mina de oro" (los bugs)
    output_file = get_input("Nombre del archivo de salida", default=default_output, validators="required")
    print()
    
    subfinder = SubFinder()
    subfinder.run(domains, output_file, sources)
