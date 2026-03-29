"""
Tests de integración: flujos completos que combinan múltiples operaciones.
Simulan escenarios reales de uso del sistema.
"""

import pytest
from app import AgenciaViajes


class TestFlujoCompletoReserva:
    """Simula el flujo completo de un cliente: buscar, reservar, calificar."""

    def test_flujo_basico(self, agencia_con_datos):
        """
        Escenario: Juan busca habitaciones en Miami, reserva, y califica.
        """
        agencia = agencia_con_datos

        # 1. Registrar cliente
        cliente = agencia.registrar_cliente("Juan", "123", "juan@mail.com", "Dir")
        assert cliente is not None

        # 2. Buscar habitaciones en Miami
        resultados = agencia.buscar_habitaciones(destino_nombre="Miami")
        assert len(resultados) > 0

        hotel, hab = resultados[0]
        assert hotel.destino.nombre == "Miami"

        # 3. Realizar reserva (con temporada y huéspedes)
        reserva = agencia.realizar_reserva(
            "juan@mail.com", hotel.nombre, hab.numero, 10, 15
        )
        assert not isinstance(reserva, str)
        assert reserva.costo_total > 0  # el costo se calcula con temporada/ofertas
        assert reserva.cant_huespedes == 1

        # 4. Ver reservas del cliente
        reservas = agencia.obtener_reservas_cliente("juan@mail.com")
        assert len(reservas) == 1
        assert reservas[0] is reserva

        # 5. Pagar la reserva
        pago = agencia.pagar_reserva(reserva)
        assert pago["exito"] is True
        assert reserva.estado == "pagada"

        # 6. Calificar la estancia
        cal = agencia.calificar_estancia(
            "juan@mail.com", hotel.nombre, hab.numero, 4, "Muy bueno"
        )
        assert not isinstance(cal, str)
        assert hab.calificacion_promedio() == 4.0


class TestFlujoCancelacion:
    """Simula el flujo de reserva y cancelación."""

    def test_reservar_y_cancelar(self, agencia_con_datos):
        agencia = agencia_con_datos
        agencia.registrar_cliente("Ana", "123", "ana@mail.com", "Dir")

        # Reservar
        reserva = agencia.realizar_reserva("ana@mail.com", "Playa Maya", 101, 1, 5)
        assert not isinstance(reserva, str)

        # Verificar que la habitación está ocupada
        disponibles = agencia.buscar_habitaciones(
            destino_nombre="Cancún", fecha_inicio=1, fecha_fin=5
        )
        habitaciones_ocupadas = [h.numero for (_, h) in disponibles if h.numero == 101]
        assert len(habitaciones_ocupadas) == 0  # No aparece porque está ocupada

        # Cancelar
        agencia.cancelar_reserva(reserva)
        assert reserva.estado == "cancelada"

        # Verificar que la habitación se liberó
        disponibles = agencia.buscar_habitaciones(
            destino_nombre="Cancún", fecha_inicio=1, fecha_fin=5
        )
        habitaciones_libres = [h.numero for (_, h) in disponibles if h.numero == 101]
        assert 101 in habitaciones_libres


class TestFlujoMultipleReservas:
    """Simula múltiples clientes reservando la misma habitación."""

    def test_dos_clientes_misma_habitacion(self, agencia_con_datos):
        agencia = agencia_con_datos
        agencia.registrar_cliente("A", "1", "a@mail.com", "Dir")
        agencia.registrar_cliente("B", "2", "b@mail.com", "Dir")

        # Cliente A reserva noches 1-5
        r1 = agencia.realizar_reserva("a@mail.com", "Playa Maya", 201, 1, 5)
        assert not isinstance(r1, str)

        # Cliente B intenta reservar noches 3-7 (se superpone) → debe fallar
        r2 = agencia.realizar_reserva("b@mail.com", "Playa Maya", 201, 3, 7)
        assert isinstance(r2, str)  # Es un error

        # Cliente B reserva noches 5-9 (NO se superpone) → debe funcionar
        r3 = agencia.realizar_reserva("b@mail.com", "Playa Maya", 201, 5, 9)
        assert not isinstance(r3, str)


class TestFlujoDesactivar:
    """Simula desactivar hoteles y habitaciones."""

    def test_hotel_inactivo_no_aparece_en_busqueda(self, agencia_con_datos):
        agencia = agencia_con_datos

        # Antes: hay hoteles en Cancún
        antes = agencia.buscar_habitaciones(destino_nombre="Cancún")
        assert len(antes) > 0

        # Desactivar el hotel
        agencia.hoteles[1].activo = False

        # Después: no hay hoteles en Cancún
        despues = agencia.buscar_habitaciones(destino_nombre="Cancún")
        assert len(despues) == 0

    def test_habitacion_inactiva_no_aparece_en_busqueda(self, agencia_con_datos):
        agencia = agencia_con_datos

        # Contar habitaciones activas en Cancún
        antes = agencia.buscar_habitaciones(destino_nombre="Cancún")
        count_antes = len(antes)

        # Desactivar una habitación
        agencia.hoteles[1].habitaciones[0].activa = False

        # Debe haber una menos
        despues = agencia.buscar_habitaciones(destino_nombre="Cancún")
        assert len(despues) == count_antes - 1
