import os
import threading
from pyfiglet import Figlet
from rich import print

def import_modules():
    """Carga de módulos en segundo plano para máxima velocidad al iniciar."""
    def task():
        try:
            from bugscanx.modules.scanners import host_scanner
            from bugscanx.modules.scrapers.subfinder import subfinder
        except Exception:
            pass
    threading.Thread(target=task, daemon=True).start()

# Fuente compacta para los títulos de sección
figlet = Figlet(font="calvin_s")

def clear_screen():
    """Limpia la terminal de tu servidor Vultr o Termux."""
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    """
    Banner con diseño de líneas decorativas.
    Aquí es donde definimos el estilo visual de SN PLUS.
    """
    clear_screen()
    # Línea superior decorativa
    print("[bold cyan]" + "═" * 55 + "[/bold cyan]")
    
    # Logo Principal
    print("""
    [bold red]╔╗ [/bold red][turquoise2]╦ ╦╔═╗╔═╗╔═╗╔═╗╔╗╔═╗ ╦[/turquoise2]
    [bold red]╠╩╗[/bold red][turquoise2]║ ║║ ╦╚═╗║  ╠═╣║║║╔╩╦╝[/turquoise2]
    [bold red]╚═╝[/bold red][turquoise2]╚═╝╚═╝╚═╝╚═╝╩ ╩╝╚╝╩ ╚═[/turquoise2]
    """)
    
    # Línea divisoria central con efecto de degradado visual
    print("[bold magenta]  " + "─" * 20 + " [💠] " + "─" * 20 + "[/bold magenta]")
    
    # Información del Desarrollador (SinNombre / Ayan)
    print("    [bold cyan]⚡ Dᴇᴠᴇʟᴏᴘᴇ r:[/bold cyan] [bold white](SɪɴNᴏᴍʙʀᴇ)[/bold white]")
    print("    [bold cyan]📡 Tᴇʟᴇɢʀᴀᴍ   :[/bold cyan] [bold magenta]https://t.me/SIN_NOMBRE22[/bold magenta]")
    print("    [bold cyan]🛠️  Vᴇʀsɪóɴ    :[/bold cyan] [bold yellow]SN-SCAN 2026[/bold yellow]")
    
    # Línea inferior decorativa
    print("[bold cyan]\n" + "═" * 55 + "[/bold cyan]")

def ascii(text, color="bold magenta", indentation=2):
    """Genera los encabezados ASCII cuando entras a una función."""
    clear_screen()
    # Línea de entrada a sección
    print(f"[{color}]" + "»" * 10 + f" ENTRANDO A: {text.upper()} " + "«" * 10 + f"[/{color}]")
    
    ascii_banner = figlet.renderText(text)
    shifted_banner = "\n".join((" " * indentation) + line
                              for line in ascii_banner.splitlines())
    print(f"[{color}]{shifted_banner}[/{color}]")
    
    # Línea de cierre de encabezado
    print(f"[bold cyan]" + "─" * 50 + "[/bold cyan]\n")

# Ejecución inicial
import_modules()
