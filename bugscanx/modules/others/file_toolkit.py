import os
import re
import socket
import ipaddress
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich import print
from rich.panel import Panel
from rich.padding import Padding
from rich.progress import Progress, TimeElapsedColumn
from bugscanx.utils.prompts import get_input, get_confirm, clear_screen
from bugscanx import ascii


def read_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except Exception as e:
        print(f"[red] Error al leer el archivo {file_path}: {e}[/red]")
        return []


def write_lines(file_path, lines):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(f"{line}\n" for line in lines)
        return True
    except Exception as e:
        print(f"[red] Error al escribir en el archivo {file_path}: {e}[/red]")
        return False


def split_file():
    file_path = get_input("Ingresa el nombre del archivo", input_type="file", validators="file")
    parts = int(get_input("Número de partes", validators="number"))
    lines = read_lines(file_path)
    if not lines:
        return

    lines_per_file = len(lines) // parts
    file_base = os.path.splitext(file_path)[0]
    created_files = []

    for i in range(parts):
        start_idx = i * lines_per_file
        end_idx = None if i == parts - 1 else (i + 1) * lines_per_file
        part_file = f"{file_base}_parte_{i + 1}.txt"

        if write_lines(part_file, lines[start_idx:end_idx]):
            created_files.append((part_file, len(lines[start_idx:end_idx])))

    if created_files:
        print("\n[bold cyan]RESULTADOS DE DIVISIÓN[/bold cyan]")
        print(f"[green]Se dividió '{os.path.basename(file_path)}' en {len(created_files)} partes:[/green]")
        for f_path, line_count in created_files:
            print(f"[green] • {os.path.basename(f_path)}: {line_count} líneas[/green]")
        print()


def merge_files():
    directory = get_input("Ingresa la ruta del directorio", default=os.getcwd())

    if get_confirm(" ¿Unir todos los archivos .txt?"):
        files_to_merge = [f for f in os.listdir(directory) if f.endswith('.txt')]
    else:
        filenames = get_input("Archivos a unir (separados por coma)")
        files_to_merge = [f.strip() for f in filenames.split(',') if f.strip()]

    if not files_to_merge:
        print("[red] No se encontraron archivos para unir[/red]")
        return

    output_file = get_input("Nombre del archivo de salida")
    output_path = os.path.join(directory, output_file)
    lines = []
    for filename in files_to_merge:
        file_path = os.path.join(directory, filename)
        lines.extend(read_lines(file_path))

    if write_lines(output_path, lines):
        print("\n[bold cyan]RESULTADOS DE UNIÓN[/bold cyan]")
        print(f"[green]Se unieron {len(files_to_merge)} archivos en '{output_file}'[/green]")
        print(f"[green] • Total de líneas: {len(lines)}[/green]")
        print(f"[green] • Ubicación: {directory}[/green]")
        print()


def clean_file():
    input_file = get_input("Archivo de entrada", input_type="file", validators="file")
    domain_output_file = get_input("Archivo de salida para dominios")
    ip_output_file = get_input("Archivo de salida para IPs")

    content = read_lines(input_file)
    if not content:
        return

    domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}\b'
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

    domains = sorted(set(re.findall(domain_pattern, '\n'.join(content))))
    ips = sorted(set(re.findall(ip_pattern, '\n'.join(content))))

    domains_success = write_lines(domain_output_file, domains)
    ips_success = write_lines(ip_output_file, ips)

    if domains_success or ips_success:
        print(f"\n[bold cyan]RESULTADOS DE LIMPIEZA[/bold cyan]")
        print(f"[green]Resultados para '{os.path.basename(input_file)}':[/green]")
        if domains_success:
            print(f"[green] • {len(domains)} dominios únicos extraídos en '{os.path.basename(domain_output_file)}'[/green]")
        if ips_success:
            print(f"[green] • {len(ips)} direcciones IP únicas extraídas en '{os.path.basename(ip_output_file)}'[/green]")
        print()


def remove_duplicates():
    file_path = get_input("Archivo de entrada", input_type="file", validators="file")
    lines = read_lines(file_path)
    if not lines:
        return

    unique_lines = sorted(set(lines))
    duplicates_removed = len(lines) - len(unique_lines)

    if write_lines(file_path, unique_lines):
        print(f"\n[bold cyan]RESULTADOS DE DEPURACIÓN[/bold cyan]")
        print(f"[green]Duplicados eliminados de '{os.path.basename(file_path)}':[/green]")
        print(f"[green] • Conteo original: {len(lines)} líneas[/green]")
        print(f"[green] • Conteo único: {len(unique_lines)} líneas[/green]")
        print(f"[green] • Eliminados: {duplicates_removed} líneas[/green]")
        print()


def filter_by_tlds():
    file_path = get_input("Archivo de entrada", input_type="file", validators="file")
    tlds_input = get_input("Ingresa las extensiones TLD", instruction="(ej: com, net, mx)")

    domains = read_lines(file_path)
    if not domains:
        return

    tld_dict = defaultdict(list)
    for domain in domains:
        parts = domain.split('.')
        if len(parts) > 1:
            tld = parts[-1].lower()
            tld_dict[tld].append(domain)

    base_name = os.path.splitext(file_path)[0]
    if tlds_input.lower() != 'all':
        target_tlds = [tld.strip().lstrip('.').lower() 
                      for tld in tlds_input.split(',')]
    else:
        target_tlds = list(tld_dict.keys())

    print(f"\n[bold cyan]RESULTADOS FILTRO TLD[/bold cyan]")
    print(f"[green]Filtrando dominios por TLD en '{os.path.basename(file_path)}':[/green]")

    for tld in target_tlds:
        if tld in tld_dict:
            tld_file = f"{base_name}_{tld}.txt"
            if write_lines(tld_file, sorted(tld_dict[tld])):
                print(f"[green] • Creado '{os.path.basename(tld_file)}' con {len(tld_dict[tld])} dominios[/green]")
        else:
            print(f"[yellow] • No se hallaron dominios con TLD .{tld}[/yellow]")
    print()


def filter_by_keywords():
    file_path = get_input("Archivo de entrada", input_type="file", validators="file")
    keywords = [k.strip().lower() for k in get_input("Ingresa palabra(s) clave").split(',')]
    output_file = get_input("Archivo de salida")

    lines = read_lines(file_path)
    if not lines:
        return

    filtered_lines = [
        line for line in lines if any(k in line.lower() for k in keywords)
    ]

    if write_lines(output_file, filtered_lines):
        print(f"\n[bold cyan]RESULTADOS FILTRO PALABRAS CLAVE[/bold cyan]")
        print(f"[green]Contenido filtrado con éxito:[/green]")
        print(f"[green] • Líneas de entrada: {len(lines)}[/green]")
        print(f"[green] • Líneas coincidentes: {len(filtered_lines)}[/green]")
        print(f"[green] • Palabras usadas: {', '.join(keywords)}[/green]")
        print(f"[green] • Archivo de salida: '{os.path.basename(output_file)}'[/green]")
        print()


def cidr_to_ip():
    cidr_input = get_input("Ingresa el rango CIDR", validators="cidr")
    output_file = get_input("Archivo de salida")

    try:
        network = ipaddress.ip_network(cidr_input.strip(), strict=False)
        ip_addresses = [str(ip) for ip in network.hosts()]
    except ValueError as e:
        print(f"[red] Rango CIDR inválido: {cidr_input} - {str(e)}[/red]")
        return

    if ip_addresses and write_lines(output_file, ip_addresses):
        print(f"\n[bold cyan]RESULTADOS CIDR[/bold cyan]")
        print(f"[green]Conversión de CIDR a IPs completada:[/green]")
        print(f"[green] • Rango CIDR: {cidr_input}[/green]")
        print(f"[green] • Total de IPs: {len(ip_addresses)}[/green]")
        print(f"[green] • Archivo de salida: '{os.path.basename(output_file)}'[/green]")
        print()


def domains_to_ip():
    file_path = get_input("Archivo de entrada", input_type="file", validators="file")
    output_file = get_input("Archivo de salida")

    domains = read_lines(file_path)
    if not domains:
        return

    ip_addresses = set()
    resolved_count = failed_count = 0
    socket.setdefaulttimeout(1)

    with Progress(
        *Progress.get_default_columns(), TimeElapsedColumn(), transient=True
    ) as progress:
        task = progress.add_task("[yellow] Resolviendo", total=len(domains))

        with ThreadPoolExecutor(max_workers=100) as executor:
            def resolve_domain(domain):
                try:
                    ip = socket.gethostbyname_ex(domain.strip())[2][0]
                    return domain, ip
                except (socket.gaierror, socket.timeout):
                    return domain, None

            futures = [
                executor.submit(resolve_domain, d) for d in domains
            ]
            for future in as_completed(futures):
                domain, ip = future.result()
                if ip:
                    ip_addresses.add(ip)
                    resolved_count += 1
                else:
                    failed_count += 1
                progress.update(task, advance=1)

    if ip_addresses and write_lines(output_file, sorted(ip_addresses)):
        print(f"\n[bold cyan]RESULTADOS RESOLUCIÓN DNS[/bold cyan]")
        print(f"[green]Dominios resueltos con éxito:[/green]")
        print(f"[green] • Dominios de entrada: {len(domains)}[/green]")
        print(f"[green] • Resueltos con éxito: {resolved_count}[/green]")
        print(f"[green] • Errores de resolución: {failed_count}[/green]")
        print(f"[green] • IPs únicas obtenidas: {len(ip_addresses)}[/green]")
        print(f"[green] • Archivo de salida: '{os.path.basename(output_file)}'[/green]")
        print()
    else:
        print("\n[red]No se pudo resolver ningún dominio o hubo un error al escribir el archivo[/red]\n")


def main():
    options = {
        "1": ("DIVIDIR ARCHIVO", split_file, "bold cyan"),
        "2": ("UNIR ARCHIVOS", merge_files, "bold blue"),
        "3": ("LIMPIAR ARCHIVO (EXTRAER DOMINIOS/IP)", clean_file, "bold cyan"),
        "4": ("ELIMINAR DUPLICADOS", remove_duplicates, "bold yellow"),
        "5": ("FILTRAR POR EXTENSIÓN TLD", filter_by_tlds, "bold magenta"),
        "6": ("FILTRAR POR PALABRA CLAVE", filter_by_keywords, "bold yellow"),
        "7": ("CONVERTIR CIDR A IP", cidr_to_ip, "bold green"),
        "8": ("RESOLVER DOMINIO A IP", domains_to_ip, "bold blue"),
        "0": ("VOLVER", lambda: None, "bold red"),
    }

    while True:
        print("\n".join(
            f"[{color}] [{key}] {desc}" for key, (desc, _, color) in options.items()
        ))

        choice = input("\n\033[36m [-] Tu Selección: \033[0m").strip()

        if choice == '0':
            raise KeyboardInterrupt

        action = options.get(choice)
        if not action:
            ascii("FILE TOOLKIT")
            continue

        desc, func, color = action

        try:
            clear_screen()
            print(Padding(Panel.fit(
                f"[{color}]{desc}[/{color}]",
                border_style=color
            ), (0, 0, 1, 2)))
            func()
            print("\n[yellow] Presiona Enter para continuar...", end="")
            input()
        except KeyboardInterrupt:
            pass
        finally:
            ascii("FILE TOOLKIT")
