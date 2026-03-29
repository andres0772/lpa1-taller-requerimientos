"""
Tests para las clases de entidad (clases.py).
Validan que cada clase se comporta correctamente de forma aislada.
"""

import pytest
from clases import Destino, Hotel, Habitacion, Cliente, Reserva, Calificacion


# ============================================================
#  TESTS: Destino
# ============================================================


class TestDestino:
    """R1: El sistema debe cargar destinos desde la tabla de tarifas."""

    def test_crear_destino(self, destino_miami):
        assert destino_miami.nombre == "Miami"
        assert destino_miami.tarifa_pasaje == 334
        assert destino_miami.precio_silver == 122
        assert destino_miami.precio_gold == 151
        assert destino_miami.precio_platinum == 183

    def test_obtener_precio_silver(self, destino_miami):
        assert destino_miami.obtener_precio("silver") == 122

    def test_obtener_precio_gold(self, destino_miami):
        assert destino_miami.obtener_precio("gold") == 151

    def test_obtener_precio_platinum(self, destino_miami):
        assert destino_miami.obtener_precio("platinum") == 183

    def test_obtener_precio_case_insensitive(self, destino_miami):
        """Las categorías deben funcionar sin importar mayúsculas/minúsculas."""
        assert destino_miami.obtener_precio("SILVER") == 122
        assert destino_miami.obtener_precio("Gold") == 151

    def test_obtener_precio_categoria_invalida(self, destino_miami):
        """Una categoría inválida debe lanzar ValueError (no retornar 0 silenciosamente)."""
        with pytest.raises(ValueError):
            destino_miami.obtener_precio("diamante")

    def test_str(self, destino_miami):
        assert str(destino_miami) == "Miami"


# ============================================================
#  TESTS: Calificacion
# ============================================================


class TestCalificacion:
    """R14: El sistema debe permitir calificaciones 1-5 con comentarios."""

    def test_crear_calificacion(self):
        cal = Calificacion(4, "Muy bueno")
        assert cal.puntuacion == 4
        assert cal.comentario == "Muy bueno"

    def test_puntuacion_se_clampea_a_1(self):
        """Puntuaciones fuera de rango se corrigen automáticamente."""
        cal = Calificacion(0)
        assert cal.puntuacion == 1

    def test_puntuacion_se_clampea_a_5(self):
        cal = Calificacion(99)
        assert cal.puntuacion == 5

    def test_str_con_estrellas(self):
        cal = Calificacion(3, "Regular")
        resultado = str(cal)
        assert "★★★" in resultado
        assert "Regular" in resultado

    def test_sin_comentario(self):
        cal = Calificacion(5)
        assert cal.comentario == ""


# ============================================================
#  TESTS: Habitacion
# ============================================================


class TestHabitacion:
    """R5, R6, R7: Habitaciones con categoría, estado y disponibilidad."""

    def test_crear_habitacion(self, hotel_ejemplo):
        hab = hotel_ejemplo.habitaciones[0]
        assert hab.numero == 101
        assert hab.categoria == "silver"
        assert hab.capacidad == 2
        assert hab.activa is True

    def test_habitacion_conoce_su_hotel(self, hotel_ejemplo):
        """La referencia bidireccional habitacion.hotel debe existir."""
        hab = hotel_ejemplo.habitaciones[0]
        assert hab.hotel is hotel_ejemplo
        assert hab.hotel.nombre == "Sol Caribe"

    def test_disponible_sin_reservas(self, hotel_ejemplo):
        hab = hotel_ejemplo.habitaciones[0]
        assert hab.esta_disponible(1, 5) is True

    def test_no_disponible_si_inactiva(self, hotel_ejemplo):
        """R6: Una habitación inactiva no está disponible."""
        hab = hotel_ejemplo.habitaciones[0]
        hab.activa = False
        assert hab.esta_disponible(1, 5) is False

    def test_no_disponible_si_reservada(self, hotel_ejemplo, cliente_ejemplo):
        """R7: Una habitación con reserva en esas fechas no está disponible."""
        hab = hotel_ejemplo.habitaciones[0]
        reserva = Reserva(1, 5, cliente_ejemplo, hab, 500)
        hab.reservas.append(reserva)

        # Se superpone
        assert hab.esta_disponible(3, 7) is False
        # No se superpone (después)
        assert hab.esta_disponible(5, 10) is True
        # No se superpone (antes)
        assert hab.esta_disponible(0, 1) is True

    def test_calificacion_promedio_sin_calificaciones(self, hotel_ejemplo):
        hab = hotel_ejemplo.habitaciones[0]
        assert hab.calificacion_promedio() == 0

    def test_calificacion_promedio(self, hotel_ejemplo):
        hab = hotel_ejemplo.habitaciones[0]
        hab.calificaciones.append(Calificacion(4))
        hab.calificaciones.append(Calificacion(5))
        assert hab.calificacion_promedio() == 4.5


# ============================================================
#  TESTS: Hotel
# ============================================================


class TestHotel:
    """R2, R3: Registro de hoteles con activación/desactivación."""

    def test_crear_hotel(self, hotel_ejemplo):
        assert hotel_ejemplo.nombre == "Sol Caribe"
        assert hotel_ejemplo.destino.nombre == "Miami"
        assert hotel_ejemplo.activo is True

    def test_hotel_tiene_tres_habitaciones(self, hotel_ejemplo):
        assert len(hotel_ejemplo.habitaciones) == 3

    def test_esta_activo(self, hotel_ejemplo):
        """R3: Verificar estado activo/inactivo."""
        assert hotel_ejemplo.esta_activo() is True
        hotel_ejemplo.activo = False
        assert hotel_ejemplo.esta_activo() is False

    def test_calificacion_promedio(self, hotel_ejemplo):
        hotel_ejemplo.calificaciones.append(Calificacion(5))
        hotel_ejemplo.calificaciones.append(Calificacion(3))
        assert hotel_ejemplo.calificacion_promedio() == 4.0

    def test_str(self, hotel_ejemplo):
        assert str(hotel_ejemplo) == "Sol Caribe (Miami)"


# ============================================================
#  TESTS: Cliente
# ============================================================


class TestCliente:
    """R8: Registro de clientes."""

    def test_crear_cliente(self, cliente_ejemplo):
        assert cliente_ejemplo.nombre == "Juan Pérez"
        assert cliente_ejemplo.email == "juan@email.com"
        assert cliente_ejemplo.telefono == "+54-11-5555-1234"

    def test_cliente_sin_reservas(self, cliente_ejemplo):
        assert len(cliente_ejemplo.reservas) == 0

    def test_str(self, cliente_ejemplo):
        assert "Juan Pérez" in str(cliente_ejemplo)
        assert "juan@email.com" in str(cliente_ejemplo)


# ============================================================
#  TESTS: Reserva
# ============================================================


class TestReserva:
    """R10, R13: Reservas y cancelaciones."""

    def test_crear_reserva(self, hotel_ejemplo, cliente_ejemplo):
        hab = hotel_ejemplo.habitaciones[0]
        reserva = Reserva(1, 5, cliente_ejemplo, hab, 500)
        assert reserva.fecha_inicio == 1
        assert reserva.fecha_fin == 5
        assert reserva.costo_total == 500
        assert reserva.estado == "pendiente"

    def test_cancelar_reserva(self, hotel_ejemplo, cliente_ejemplo):
        """R13: Cancelar una reserva cambia su estado y la quita del calendario."""
        hab = hotel_ejemplo.habitaciones[0]
        reserva = Reserva(1, 5, cliente_ejemplo, hab, 500)
        hab.reservas.append(reserva)
        cliente_ejemplo.reservas.append(reserva)

        resultado = reserva.cancelar()
        assert resultado is True
        assert reserva.estado == "cancelada"
        assert reserva not in hab.reservas
        assert reserva not in cliente_ejemplo.reservas

    def test_cancelar_reserva_ya_cancelada(self, hotel_ejemplo, cliente_ejemplo):
        hab = hotel_ejemplo.habitaciones[0]
        reserva = Reserva(1, 5, cliente_ejemplo, hab, 500)
        reserva.cancelar()

        resultado = reserva.cancelar()
        assert resultado is False

    def test_str(self, hotel_ejemplo, cliente_ejemplo):
        hab = hotel_ejemplo.habitaciones[0]
        hab.hotel = hotel_ejemplo
        reserva = Reserva(1, 5, cliente_ejemplo, hab, 500)
        texto = str(reserva)
        assert "Juan Pérez" in texto
        assert "500" in texto
