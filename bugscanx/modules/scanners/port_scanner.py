import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)
from bugscanx.utils.prompts import get_input

console = Console()

# Puertos comunes que solemos usar en Netfree/VPS (SSH, HTTP, SSL, etc.)
COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143,
    443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080,
    8443, 8888
]


def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            # Retorna el puerto si la conexión es exitosa (0)
            return port if sock.connect_ex((ip, port)) == 0 else None
    except:
        return None


def main():
    # Traducción de la entrada de objetivo
    target = get_input("Ingresa el Objetivo (IP/Dominio)", validators="required")
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        console.print(
            "\n[bold red] Error al resolver el nombre de host",
            "\n[bold red] Por favor, verifica el objetivo e intenta de nuevo.",
        )
        return

    # Traducción de los tipos de escaneo
    scan_type = get_input(
        "Selecciona el tipo de escaneo",
        input_type="choice",
        choices=["Puertos comunes", "Todos los puertos (1-65535)"]
    )
    ports = COMMON_PORTS if scan_type == "Puertos comunes" else range(1, 65535)

    console.print(
        f"\n[bold green] Información del Objetivo:[/]\n"
        f" • Host: {target}\n"
        f" • IP: {ip}\n"
    )
    console.print(f"[bold blue] Iniciando escaneo...[/]\n")

    open_ports = []
    with Progress(
        TextColumn("[bold blue]│[/] {task.description}"),
        BarColumn(complete_style="green"),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
        transient=True,
    ) as progress:
        # Traducción de la barra de progreso
        task = progress.add_task(" Escaneando puertos", total=len(ports))

        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(scan_port, ip, port) for port in ports]
            for future in as_completed(futures):
                if result := future.result():
                    open_ports.append(result)
                    # Mensaje cuando encuentra un puerto abierto
                    progress.console.print(f" [green]✓[/] Puerto {result} está abierto")
                progress.advance(task)

    if not open_ports:
        console.print("\n[yellow] No se encontraron puertos abiertos.[/]\n")
    else:
        # Añadí un pequeño resumen al final
        console.print(f"\n[bold green] Escaneo finalizado. Se encontraron {len(open_ports)} puertos abiertos.[/]\n")
