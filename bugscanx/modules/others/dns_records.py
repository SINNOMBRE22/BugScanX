from dns import resolver as dns_resolver
from rich import print
from bugscanx.utils.prompts import get_input


def configure_resolver():
    """Configura el resolvedor de DNS estándar"""
    return dns_resolver.Resolver()


def resolve_and_print(domain, record_type):
    """Resuelve un tipo de registro específico y lo imprime con estilo"""
    print(f"\n[green] Registros {record_type}:[/green]")
    try:
        dns_obj = configure_resolver()
        # Intentamos obtener la respuesta del servidor DNS
        answers = dns_obj.resolve(domain, record_type)
        found = False
        
        for answer in answers:
            found = True
            if record_type == "MX":
                # Los registros MX incluyen prioridad (importante para servidores de correo)
                print(
                    f"[cyan]- {answer.exchange} "
                    f"(Prioridad: {answer.preference})[/cyan]"
                )
            else:
                # Registros estándar como A, AAAA o TXT
                print(f"[cyan]- {answer.to_text()}[/cyan]")
        
        if not found:
            print(f"[yellow] No se encontraron registros {record_type}[/yellow]")
            
    except (dns_resolver.NXDOMAIN, dns_resolver.NoAnswer):
        print(f"[yellow] No hay respuesta para registros {record_type}[/yellow]")
    except Exception:
        print(f"[yellow] Error al obtener el registro {record_type}[/yellow]")


def nslookup(domain):
    """Ejecuta una consulta completa de DNS (NSLOOKUP) para un dominio"""
    print(f"[cyan]\n Realizando consulta DNS para: {domain}[/cyan]")

    # Tipos de registros que buscamos por defecto
    record_types = [
        "A",      # IPv4
        "AAAA",   # IPv6
        "CNAME",  # Alias
        "MX",     # Correo
        "NS",     # Servidores de nombres
        "TXT",    # Registros de texto (SPF, verificaciones, etc.)
    ]

    for record_type in record_types:
        resolve_and_print(domain, record_type)


def main():
    """Punto de entrada principal"""
    # Usamos el prompt de SinNombre para pedir el objetivo
    domain = get_input("Ingresa el dominio objetivo (Target)")

    try:
        nslookup(domain)
    except Exception as e:
        print(f"[red] Ocurrió un error durante la consulta DNS: {str(e)}[/red]")
