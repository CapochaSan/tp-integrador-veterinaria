from __future__ import annotations
import flet as ft


def mostrar_mensaje(page: ft.Page, texto: str, es_error: bool = False) -> None:
    """Muestra una notificación SnackBar simple en la parte inferior."""
    color = ft.colors.RED_700 if es_error else ft.colors.GREEN_700
    snack = ft.SnackBar(
        content=ft.Text(texto, color=ft.colors.WHITE),
        bgcolor=color,
        duration=4000,
    )
    page.open(snack)
