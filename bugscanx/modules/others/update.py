import os
import subprocess
import sys
import time
from dataclasses import dataclass
from importlib.metadata import version
from packaging.version import Version, parse as parse_version

from rich.console import Console
from bugscanx.utils.prompts import get_confirm


@dataclass
class VersionInfo:
    current_version: str
    latest_stable: str = None
    latest_prerelease: str = None
    prerelease_is_newer: bool = False


class VersionManager:
    def __init__(self, package_name="bugscan-x"):
        self.package_name = package_name
        self.console = Console()

    def _is_prerelease(self, version_str):
        """Detecta si una versión es beta o pre-lanzamiento"""
        try:
            return Version(version_str).is_prerelease
        except Exception:
            return False

    def _parse_pip_output(self, output):
        """Analiza la salida de pip para encontrar versiones disponibles"""
        lines = output.splitlines()
        versions = {}
        available_versions = []

        for line in lines:
            line = line.strip()
            if line.startswith('Available versions:'):
                available_versions = [
                    v.strip(' ,') 
                    for v in line.split(':', 1)[1].split()
                ]
            elif line.startswith('INSTALLED:'):
                versions['installed'] = line.split(':')[1].strip()
            elif line.startswith('LATEST:'):
                versions['latest'] = line.split(':')[1].strip()

        return versions, available_versions

    def check_updates(self):
        """Busca actualizaciones en los servidores de PyPI"""
        try:
            with self.console.status(
                "[yellow]Buscando actualizaciones...",
                spinner="dots"
            ):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "index",
                        "versions",
                        self.package_name,
                        "--pre",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=15,
                )

                versions_info, all_versions = self._parse_pip_output(result.stdout)
                if not all_versions:
                    self.console.print("[red] No se encontró información de versiones")
                    return None

                current_version = versions_info.get('installed') or version(self.package_name)
                current_ver = parse_version(current_version)
                stable_versions = [v for v in all_versions if not self._is_prerelease(v)]

                latest_stable = stable_versions[0] if stable_versions else None
                latest_prerelease = all_versions[0] if all_versions else None

                # Si ya estamos en la última versión
                if not latest_prerelease or current_ver >= parse_version(latest_prerelease):
                    self.console.print(f"[green] Estás actualizado: {current_version}")
                    return None

                return VersionInfo(
                    current_version=current_version,
                    latest_stable=latest_stable,
                    latest_prerelease=latest_prerelease,
                    prerelease_is_newer=(
                        latest_stable 
                        and latest_prerelease
                        and self._is_prerelease(latest_prerelease)
                        and parse_version(latest_prerelease) > parse_version(latest_stable)
                    )
                )

        except subprocess.TimeoutExpired:
            self.console.print("[red] Tiempo de espera agotado. Revisa tu conexión a internet.")
        except subprocess.CalledProcessError:
            self.console.print("[red] Error al consultar actualizaciones")
        except Exception:
            self.console.print("[red] Error inesperado al buscar actualizaciones")
        return None

    def install_update(self, install_prerelease=False):
        """Ejecuta pip para instalar la nueva versión"""
        try:
            with self.console.status("[yellow]Instalando actualización...", spinner="point"):
                cmd = [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    self.package_name,
                ]
                if install_prerelease:
                    cmd.insert(-1, "--pre")

                subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=60,
                )
                self.console.print("[green] ¡Actualización completada con éxito!")
                return True
        except Exception as e:
            self.console.print(f"[red] Falló la instalación: {str(e)}")
            return False

    def restart_application(self):
        """Reinicia el script automáticamente para aplicar los cambios"""
        self.console.print("[yellow] Reiniciando aplicación...")
        time.sleep(1)
        os.execv(sys.executable, [sys.executable] + sys.argv)


def main():
    manager = VersionManager()
    try:
        version_info = manager.check_updates()
        if not version_info:
            return

        if version_info.prerelease_is_newer:
            # Aviso especial para versiones Beta
            manager.console.print(
                f"[yellow] Nueva versión Pre-release disponible: {version_info.current_version} → {version_info.latest_prerelease}"
            )
            manager.console.print("[red] Advertencia: Las versiones Beta pueden ser inestables y contener errores.")
            if not get_confirm(" Entiendo los riesgos, actualizar de todos modos"):
                # Si el usuario dice que NO a la beta, pero hay una estable más nueva, ofrecerla
                if version_info.latest_stable and parse_version(version_info.latest_stable) > parse_version(version_info.current_version):
                    if get_confirm(f" ¿Actualizar a la versión estable {version_info.latest_stable}?"):
                        if manager.install_update(install_prerelease=False):
                            manager.restart_application()
                return
            else:
                if manager.install_update(install_prerelease=True):
                    manager.restart_application()
        else:
            # Actualización estable estándar
            manager.console.print(
                f"[yellow] Actualización disponible: {version_info.current_version} → {version_info.latest_stable}"
            )
            if not get_confirm(" ¿Actualizar ahora?"):
                return
            if manager.install_update(install_prerelease=False):
                manager.restart_application()

    except KeyboardInterrupt:
        manager.console.print("[yellow] Actualización cancelada por el usuario.")
    except Exception as e:
        manager.console.print(f"[red] Error durante el proceso: {str(e)}")
