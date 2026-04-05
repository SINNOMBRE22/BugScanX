import sys
from rich import print
from . import banner, ascii, handler

# Opciones del menú traducidas al español
MENU_OPTIONS = {
    '1': ("ESCANER DE HOSTS", "bold cyan"),
    '2': ("BUSCADOR SUBDOMINIOS", "bold magenta"),
    '3': ("BUSQUEDA DE IP", "bold cyan"),
    '4': ("HERRAMIENTAS DE ARCHIVO", "bold magenta"),
    '5': ("ESCANER DE PUERTOS", "bold white"),
    '6': ("REGISTROS DNS", "bold green"),
    '7': ("INFO DEL HOST", "bold blue"),
    '8': ("AYUDA / HELP", "bold yellow"),
    '9': ("ACTUALIZAR", "bold magenta"),
    '0': ("SALIR", "bold red"),
}

def main():
    try:
        while True:
            # Generar el menú visual
            menu = (
                f"[{color}] [{k}]{' ' if len(k)==1 else ''} {desc}"
                for k, (desc, color) in MENU_OPTIONS.items()
            )
            banner() # Llama al banner (puedes editarlo en banner.py)
            print('\n'.join(menu))

            # Traducción de la entrada de selección
            choice = input("\n \033[36m[-]  Tu Selección: \033[0m")
            if choice not in MENU_OPTIONS:
                continue

            if choice == '0':
                return

            # Muestra el título de la opción elegida en ASCII
            ascii(MENU_OPTIONS[choice][0])
            
            try:
                # Ejecuta la función correspondiente en handler.py (ej: run_1)
                getattr(handler, f'run_{choice}')()
                
                # Traducción del mensaje de espera
                print("\n[yellow] Presiona Enter para continuar...", end="")
                input()
            except KeyboardInterrupt:
                pass
    except (KeyboardInterrupt, EOFError):
        sys.exit()
