"""Validadores reutilizables."""

from decimal import Decimal

from django.core.exceptions import ValidationError


def validate_positive_amount(value: Decimal) -> None:
    """Impide importes negativos o iguales a cero."""
    if value <= 0:
        raise ValidationError("El importe debe ser mayor que cero.")

