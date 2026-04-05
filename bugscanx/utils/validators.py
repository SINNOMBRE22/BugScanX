import os
import ipaddress
from prompt_toolkit.validation import Validator, ValidationError

def create_validator(*validators):
    """Crea un validador personalizado basado en las funciones pasadas"""
    class CustomValidator(Validator):
        def validate(self, document):
            text = document.text.strip()
            for validator in validators:
                if callable(validator):
                    result = validator(text)
                    if result is not True:
                        # Si el validador devuelve un string, ese es el mensaje de error
                        error_message = result if isinstance(result, str) else "Entrada inválida"
                        raise ValidationError(
                            message=error_message,
                            cursor_position=len(text)
                        )
    return CustomValidator()

# --- Funciones de Validación ---

def required(text):
    """Verifica que el campo no esté vacío"""
    return True if text.strip() else "Este campo es obligatorio."

def is_file(text):
    """Verifica si el archivo existe en el sistema (VPS o Celular)"""
    return os.path.isfile(text) or f"Archivo no encontrado: {text}"

def is_cidr(text):
    """Valida rangos de red CIDR (ej. 192.168.1.0/24)"""
    if not text.strip():
        return "El rango CIDR no puede estar vacío"

    # Permite múltiples rangos separados por comas
    cidrs = [cidr.strip() for cidr in text.split(',')]

    for cidr in cidrs:
        if not cidr:
            continue
        try:
            # La librería ipaddress verifica que el formato sea correcto
            ipaddress.ip_network(cidr, strict=False)
        except ValueError:
            return f"Rango CIDR inválido: {cidr}"

    return True

def is_digit(text, allow_comma=True):
    """Verifica que la entrada sea un número (puertos, hilos, etc.)"""
    if not allow_comma and ',' in text:
        return "Solo se permite un valor único"

    clean_text = text.strip().replace(',', '').replace(' ', '')
    if not clean_text or not clean_text.isdigit():
        return f"Número inválido: {text}"
    return True

# --- Diccionario de Validadores Listos para Usar ---
VALIDATORS = {
    'required': [required],
    'file': [required, is_file],
    'number': [required, is_digit],
    'cidr': [required, is_cidr],
}
