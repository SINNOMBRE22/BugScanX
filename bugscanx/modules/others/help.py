from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()

def show_detailed_help():
    """Muestra todas las secciones de ayuda"""
    help_sections = [
        show_overview(),
        show_host_scanner_help(),
        show_subfinder_help(),
        show_ip_lookup_help(),
        show_file_toolkit_help(),
        show_port_scanner_help(),
        show_dns_records_help(),
        show_host_info_help(),
        show_usage_examples(),
        show_tips_and_tricks()
    ]

    for section in help_sections:
        console.print(section)
        console.print()

def show_overview():
    overview_text = """
# 🎯 BugScanX - Herramienta Todo-en-Uno para Descubrir Bug Hosts

**BugScanX** es una suite completa diseñada para encontrar hosts SNI/HTTP funcionales para aplicaciones de túnel (VPN). Ayuda a investigadores de seguridad y administradores de red a descubrir "bugs" para diversas configuraciones de túneles.

## ✨ Características Clave
- Escaneo de hosts avanzado con múltiples modos.
- Enumeración profesional de subdominios.
- Inteligencia completa sobre direcciones IP.
- Potente kit de herramientas para gestión de archivos.
- Escaneo de puertos de alto rendimiento.
- Análisis detallado de DNS y SSL.
"""
    return Panel(
        Markdown(overview_text),
        title="[bold blue]Resumen General[/bold blue]",
        border_style="bold blue",
        expand=True
    )

def show_host_scanner_help():
    scanner_text = """
# 🔍 HOST SCANNER - Descubrimiento Avanzado de Bugs

El Escáner de Hosts es la función más potente de BugScanX para validar hosts funcionales.

## Modos de Escaneo

### 1. Modo Directo (Direct)
- Escaneo estándar de bug hosts HTTP/HTTPS.
- **Uso**: Prueba hosts con varios métodos HTTP.
- **Ideal para**: Descubrimiento general de bugs.

### 2. Modo Directo Sin 302 (DirectNon302)
- **Especial**: Excluye respuestas de redirección (HTTP 302).
- **Crítico para**: Encontrar hosts limpios que no redirigen el tráfico.

### 3. Modo SSL/SNI
- Verificación de nombres de host SNI y análisis TLS.
- **Propósito**: Identificar hosts compatibles con túneles HTTPS/SSL.

### 4. Modo Prueba de Proxy (ProxyTest)
- Prueba de actualización a Websocket.
- **Función**: Valida la compatibilidad con proxies y túneles WS.

## Parámetros de Configuración
- **Puertos**: 80, 443, 8080, 8443 (comunes en túneles).
- **Hilos (Threads)**: 1-100 (se recomiendan 50 para estabilidad).
- **Métodos HTTP**: GET, POST, HEAD, etc.
"""
    return Panel(
        Markdown(scanner_text),
        title="[bold cyan]HOST SCANNER[/bold cyan]",
        border_style="bold cyan",
        expand=True
    )

def show_file_toolkit_help():
    toolkit_text = """
# 📁 FILE TOOLKIT - Gestión de Archivos

Procesamiento profesional de listas de hosts y datos.

## Operaciones Principales
1. **Dividir Archivos**: Divide listas grandes en partes pequeñas.
2. **Unir Archivos**: Combina resultados de varios escaneos en uno solo.
3. **Limpiar Archivo**: Extrae solo dominios e IPs de archivos con texto mezclado.
4. **Quitar Duplicados**: Elimina entradas repetidas y ordena los resultados.
5. **Filtrar por TLD**: Separa dominios por extensión (.mx, .com, etc.).
6. **Dominio a IP**: Resolución DNS masiva para convertir hosts en direcciones IP.
"""
    return Panel(
        Markdown(toolkit_text),
        title="[bold magenta]FILE TOOLKIT[/bold magenta]",
        border_style="bold magenta",
        expand=True
    )

def show_usage_examples():
    examples_text = """
# 💡 Ejemplos Prácticos de Uso

## Flujo de Trabajo para buscar Bugs

### Paso 1: Descubrimiento Inicial
Lanza el **SUBFINDER** con el dominio objetivo (ej. `empresa.com.mx`) para obtener una lista inicial de subdominios.

### Paso 2: Validación de Hosts
Usa el **HOST SCANNER** en modo `DirectNon302` con la lista de subdominios. Esto filtrará solo los hosts que responden correctamente sin redirigir.

### Paso 3: Expansión de Red
Usa **IP LOOKUP** con las IPs de los hosts encontrados para descubrir otros dominios alojados en el mismo servidor.
"""
    return Panel(
        Markdown(examples_text),
        title="[bold yellow]Ejemplos de Uso[/bold yellow]",
        border_style="bold yellow",
        expand=True
    )

def show_tips_and_tricks():
    tips_text = """
# 🎯 Consejos y Mejores Prácticas

- **Configuración de Hilos**: Empieza con 20 hilos y sube según la capacidad de tu red o VPS.
- **Prioridad DirectNon302**: Siempre empieza con este modo; los resultados son más fiables para configuraciones VPN.
- **Mantenimiento de Listas**: Escanea tus listas periódicamente, ya que los bugs pueden caerse en cualquier momento.
- **Uso Ético**: Escanea solo objetivos autorizados y respeta los límites de velocidad para no saturar servidores.
"""
    return Panel(
        Markdown(tips_text),
        title="[bold green]Consejos Pro[/bold green]",
        border_style="bold green",
        expand=True
    )

def main():
    """Función principal del menú de ayuda"""
    print("\n[bold cyan]Selecciona una opción de ayuda:[/bold cyan]")
    choice = console.input("""
[1] Documentación Completa (Todas las secciones)
[2] Resumen Rápido
[3] Guía del Host Scanner
[4] Guía del Subfinder
[5] Ejemplos y Consejos

[bold cyan] Tu elección (1-5): [/bold cyan]""")

    console.print()

    if choice == "1":
        show_detailed_help()
    elif choice == "2":
        console.print(show_overview())
    elif choice == "3":
        console.print(show_host_scanner_help())
    elif choice == "4":
        console.print(show_subfinder_help())
    elif choice == "5":
        console.print(show_usage_examples())
        console.print(show_tips_and_tricks())
    else:
        console.print(show_overview())

    # Tabla de referencia rápida traducida
    table = Table(title="[bold]Referencia Rápida de Funciones[/bold]", border_style="bright_blue")
    table.add_column("Opción", style="bold cyan")
    table.add_column("Función", style="bold white")
    table.add_column("Ideal para...", style="green")
    table.add_column("Entrada", style="yellow")

    features = [
        ("1", "HOST SCANNER", "Descubrir y validar bugs SNI", "Archivos/CIDR"),
        ("2", "SUBFINDER", "Encontrar subdominios", "Dominios"),
        ("3", "IP LOOKUP", "Inteligencia de IPs inversas", "IPs/CIDR"),
        ("4", "FILE TOOLKIT", "Limpiar y organizar listas", "Archivos TXT"),
        ("5", "PORT SCANNER", "Descubrir servicios abiertos", "Hosts/IPs"),
        ("6", "DNS RECORDS", "Analizar registros DNS", "Dominios"),
        ("7", "HOST INFO", "Análisis detallado de un host", "Hosts/URLs"),
        ("0", "SALIR", "Cerrar la aplicación", "N/A")
    ]

    for opt, feat, best, inp in features:
        table.add_row(opt, feat, best, inp)

    console.print(table)
    console.print()
    console.print(
        Panel(
            Text(
                "¡Gracias por elegir BugScanX de SinNombre! 🚀\n\n"
                "💡 ¿Dudas o problemas? ¡Contribuciones bienvenidas!\n"
                "🎯 ¡Feliz cacería de bugs!"
            ),
            border_style="bold blue",
            title="[bold blue]Soporte y Comunidad[/bold blue]"
        )
    )
