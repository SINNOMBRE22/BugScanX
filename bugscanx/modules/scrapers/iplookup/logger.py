from rich.console import Console


class IPLookupConsole(Console):
    def __init__(self):
        super().__init__()
        self.total_domains = 0
        self.ip_stats = {}

    def print_ip_start(self, ip):
        # Mensaje al iniciar el escaneo de una IP específica
        self.print(f"[cyan]Procesando: {ip}[/cyan]")

    def update_ip_stats(self, ip, count):
        self.ip_stats[ip] = count
        self.total_domains += count

    def print_ip_complete(self, ip, count):
        # Mensaje cuando termina de encontrar dominios en una IP
        self.print(f"[green]{ip}: {count} dominios encontrados[/green]")

    def print_final_summary(self, output_file):
        """Muestra el resumen total al finalizar todo el proceso"""
        print("\r\033[K", end="")
        self.print(f"\n[green]Total: [bold]{self.total_domains}[/bold] dominios encontrados")
        self.print(f"[green]Resultados guardados en: {output_file}[/green]")

    def print_progress(self, current, total):
        # Barra de progreso simple en la parte inferior
        self.print(f"Progreso: {current} / {total}", end="\r")

    def print_error(self, message):
        # Mensajes de error en rojo
        self.print(f"[red]Error: {message}[/red]")
