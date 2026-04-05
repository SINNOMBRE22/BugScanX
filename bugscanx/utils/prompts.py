import os
from InquirerPy import get_style
from InquirerPy.prompts import (
    ListPrompt as select,
    FilePathPrompt as filepath,
    InputPrompt as text,
    ConfirmPrompt as confirm,
)
from .validators import create_validator, VALIDATORS

# --- Configuración Estética (Aesthetic) ---
# Definimos los colores para que combinen con tu estilo Tech-Noir
DEFAULT_STYLE = get_style(
    {
        "question": "#87CEEB",         # Azul cielo para las preguntas
        "answer": "#00FF7F",           # Verde neón para las respuestas
        "answered_question": "#808080", # Gris para lo que ya se contestó
    },
    style_override=False,
)


def get_input(
    message,
    input_type="text",
    default=None,
    validators=None,
    choices=None,
    multiselect=False,
    transformer=None,
    style=DEFAULT_STYLE,
    instruction="",
    mandatory=True,
    **kwargs
):
    """
    Función maestra para obtener datos del usuario (texto, archivos o listas).
    """
    def auto_strip(result):
        # Limpiamos espacios innecesarios automáticamente
        return result.strip() if isinstance(result, str) else result

    # Configuración base del prompt
    params = {
        "message": f" {message.strip()}" + (":" if not instruction else ""),
        "default": "" if default is None else str(default),
        "qmark": "", # Quitamos los signos de interrogación por defecto para que sea más limpio
        "amark": "",
        "style": style,
        "instruction": instruction + (":" if instruction else ""),
        "mandatory": mandatory,
        "transformer": transformer,
    }

    # Validación de datos (ej. verificar que un archivo existe o que sea un número)
    if validators:
        if isinstance(validators, str) and validators in VALIDATORS:
            params["validate"] = create_validator(*VALIDATORS[validators])
        elif isinstance(validators, (list, tuple)):
            params["validate"] = create_validator(*validators)

    # --- Lógica según el tipo de entrada ---

    if input_type == "choice":
        # Menú de selección (Lista)
        params.update({
            "choices": choices,
            "multiselect": multiselect,
            "show_cursor": kwargs.get("show_cursor", False),
        })
        return select(**params).execute()

    elif input_type == "file":
        # Selector de archivos (muy útil para cargar listas de hosts)
        params["only_files"] = kwargs.get("only_files", True)
        return auto_strip(filepath(**params).execute())

    else:
        # Entrada de texto normal
        return auto_strip(text(**params).execute())


def get_confirm(message, default=True, style=DEFAULT_STYLE, **kwargs):
    """Lanza una pregunta de Sí/No"""
    return confirm(
        message=message,
        default=default,
        qmark="",
        amark="",
        style=style,
        **kwargs
    ).execute()


def clear_screen():
    """Limpia la terminal (compatible con Windows y Linux/Android)"""
    os.system('cls' if os.name == 'nt' else 'clear')
