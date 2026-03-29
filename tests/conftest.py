"""
Fixtures compartidas para todos los tests.
Un fixture es un "dato preparado" que pytest te da cuando lo pedís.
"""

import sys
import os
import pytest

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clases import Destino, Hotel, Habitacion, Cliente, Reserva, Calificacion
from app import AgenciaViajes, cargar_datos_ejemplo


# ============================================================
#  FIXTURES de entidades individuales
# ============================================================


@pytest.fixture
def destino_miami():
    """Un destino de ejemplo: Miami."""
    return Destino("Miami", 334, 122, 151, 183)


@pytest.fixture
def destino_cancun():
    """Un destino de ejemplo: Cancún."""
    return Destino("Cancún", 350, 105, 142, 187)


@pytest.fixture
def hotel_ejemplo(destino_miami):
    """Un hotel de ejemplo en Miami."""
    hotel = Hotel(
        "Sol Caribe",
        destino_miami,
        "123 Ocean Drive",
        "+1-305-555-0101",
        "info@solcaribe.com",
        "Hotel frente al mar",
        ["piscina", "restaurante", "wifi"],
    )
    # Agregar habitaciones
    hab_silver = Habitacion(101, "Estándar", "silver", 2, ["wifi", "tv"])
    hab_gold = Habitacion(201, "Superior", "gold", 3, ["wifi", "tv", "minibar"])
    hab_platinum = Habitacion(301, "Suite", "platinum", 4, ["wifi", "jacuzzi"])
    hotel.agregar_habitacion(hab_silver)
    hotel.agregar_habitacion(hab_gold)
    hotel.agregar_habitacion(hab_platinum)
    return hotel


@pytest.fixture
def cliente_ejemplo():
    """Un cliente de ejemplo."""
    return Cliente(
        "Juan Pérez", "+54-11-5555-1234", "juan@email.com", "Av. Corrientes 1234"
    )


# ============================================================
#  FIXTURES de la agencia (con datos precargados)
# ============================================================


@pytest.fixture
def agencia_vacia():
    """Una agencia sin datos, solo con destinos cargados."""
    agencia = AgenciaViajes()
    agencia.cargar_tarifas()
    return agencia


@pytest.fixture
def agencia_con_datos():
    """Una agencia con destinos, hoteles y clientes de ejemplo."""
    agencia = AgenciaViajes()
    agencia.cargar_tarifas()
    cargar_datos_ejemplo(agencia)
    return agencia
