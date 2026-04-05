from rich.console import Console


class SubFinderConsole(Console):
    def __init__(self):
        super().__init__()
        self.total_subdomains = 0
        self.domain_stats = {}

    def print_domain_start(self, domain):
        # Mensaje al iniciar la búsqueda de un dominio base
        self.print(f"[cyan]Procesando: {domain}[/cyan]")

    def update_domain_stats(self, domain, count):
        self.domain_stats[domain] = count
        self.total_subdomains += count

    def print_domain_complete(self, domain, count):
        # Mensaje cuando termina de encontrar subdominios de un host
        self.print(f"[green]{domain}: {count} subdominios encontrados[/green]")

    def print_final_summary(self, output_file):
        """Muestra el resumen total de la recolección de subdominios"""
        print("\r\033[K", end="")
        self.print(f"\n[green]Total: [bold]{self.total_subdomains}[/bold] subdominios encontrados")
        self.print(f"[green]Resultados guardados en: {output_file}[/green]")

    def print_progress(self, current, total):
        # Muestra cuánto falta para terminar la lista de dominios
        self.print(f"Progreso: {current} / {total}", end="\r")

    def print_error(self, message):
        # Para errores de conexión o de las fuentes (APIs)
        self.print(f"[red]Error: {message}[/red]")
