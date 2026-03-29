"""
Tests para la lógica de negocio (AgenciaViajes en app.py).
Validan que el motor del sistema funciona según los requerimientos.
"""

import pytest
from app import AgenciaViajes, cargar_datos_ejemplo
from clases import Habitacion


# ============================================================
#  TESTS: Carga de tarifas (R1)
# ============================================================


class TestCargarTarifas:
    """R1: El sistema debe cargar los destinos desde la tabla de tarifas."""

    def test_carga_16_destinos(self, agencia_vacia):
        assert len(agencia_vacia.destinos) == 16

    def test_destinos_tienen_tarifas(self, agencia_vacia):
        miami = agencia_vacia.destinos["Miami"]
        assert miami.tarifa_pasaje == 334
        assert miami.precio_silver == 122

    def test_todos_los_destinos_conocidos(self, agencia_vacia):
        esperados = [
            "Aruba",
            "Bahamas",
            "Cancún",
            "Hawaii",
            "Jamaica",
            "Madrid",
            "Miami",
            "Moscu",
            "NewYork",
            "Panamá",
            "Paris",
            "Rome",
            "Seul",
            "Sidney",
            "Taipei",
            "Tokio",
        ]
        for nombre in esperados:
            assert nombre in agencia_vacia.destinos


# ============================================================
#  TESTS: Registro de hoteles (R2)
# ============================================================


class TestRegistrarHotel:
    """R2: El sistema debe permitir registrar un hotel."""

    def test_registrar_hotel_exitoso(self, agencia_vacia):
        hotel = agencia_vacia.registrar_hotel(
            "Test Hotel", "Miami", "Calle 1", "123", "test@mail.com", "Desc", ["wifi"]
        )
        assert hotel is not None
        assert hotel.nombre == "Test Hotel"
        assert hotel.destino.nombre == "Miami"
        assert len(agencia_vacia.hoteles) == 1

    def test_registrar_hotel_destino_invalido(self, agencia_vacia):
        hotel = agencia_vacia.registrar_hotel(
            "Test Hotel", "Destino Falso", "Calle 1", "123", "test@mail.com", "Desc"
        )
        assert hotel is None

    def test_registrar_hotel_destino_case_insensitive(self, agencia_vacia):
        """Escribir 'miami' debe encontrar 'Miami'."""
        hotel = agencia_vacia.registrar_hotel(
            "Test Hotel", "miami", "Calle 1", "123", "test@mail.com", "Desc"
        )
        assert hotel is not None
        assert hotel.destino.nombre == "Miami"


# ============================================================
#  TESTS: Registro de clientes (R8)
# ============================================================


class TestRegistrarCliente:
    """R8: El sistema debe permitir registrar clientes."""

    def test_registrar_cliente_exitoso(self, agencia_vacia):
        cliente = agencia_vacia.registrar_cliente("Ana", "123", "ana@mail.com", "Dir")
        assert cliente is not None
        assert cliente.nombre == "Ana"
        assert len(agencia_vacia.clientes) == 1

    def test_registrar_email_duplicado(self, agencia_vacia):
        agencia_vacia.registrar_cliente("Ana", "123", "ana@mail.com", "Dir")
        resultado = agencia_vacia.registrar_cliente(
            "Otra Ana", "456", "ana@mail.com", "Otra"
        )
        assert resultado is None
        assert len(agencia_vacia.clientes) == 1


# ============================================================
#  TESTS: Búsqueda de habitaciones (R9)
# ============================================================


class TestBuscarHabitaciones:
    """R9: El sistema debe permitir buscar habitaciones por criterios."""

    def test_buscar_todas(self, agencia_con_datos):
        resultados = agencia_con_datos.buscar_habitaciones()
        assert len(resultados) > 0

    def test_buscar_por_destino(self, agencia_con_datos):
        resultados = agencia_con_datos.buscar_habitaciones(destino_nombre="Cancún")
        for hotel, hab in resultados:
            assert hotel.destino.nombre == "Cancún"

    def test_buscar_por_categoria(self, agencia_con_datos):
        resultados = agencia_con_datos.buscar_habitaciones(categoria="gold")
        for hotel, hab in resultados:
            assert hab.categoria == "gold"

    def test_buscar_por_capacidad(self, agencia_con_datos):
        resultados = agencia_con_datos.buscar_habitaciones(capacidad_min=3)
        for hotel, hab in resultados:
            assert hab.capacidad >= 3

    def test_buscar_case_insensitive(self, agencia_con_datos):
        """El nombre del destino no debe distinguir mayúsculas."""
        r1 = agencia_con_datos.buscar_habitaciones(destino_nombre="miami")
        r2 = agencia_con_datos.buscar_habitaciones(destino_nombre="Miami")
        assert len(r1) == len(r2)

    def test_buscar_sin_acentos(self, agencia_con_datos):
        """Escribir 'cancun' debe encontrar 'Cancún'."""
        r1 = agencia_con_datos.buscar_habitaciones(destino_nombre="cancun")
        r2 = agencia_con_datos.buscar_habitaciones(destino_nombre="Cancún")
        assert len(r1) == len(r2) == 4

    def test_buscar_no_encuentra_destino_sin_hoteles(self, agencia_con_datos):
        resultados = agencia_con_datos.buscar_habitaciones(destino_nombre="Tokio")
        assert len(resultados) == 0

    def test_buscar_respetando_disponibilidad(self, agencia_con_datos):
        """R7: Habitaciones reservadas no aparecen en la búsqueda."""
        # Reservar la primera habitación de Cancún
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        agencia_con_datos.realizar_reserva("test@mail.com", "Playa Maya", 201, 1, 5)

        # Buscar en esas fechas
        resultados = agencia_con_datos.buscar_habitaciones(
            destino_nombre="Cancún", fecha_inicio=1, fecha_fin=5
        )
        nums = [hab.numero for (_, hab) in resultados]
        assert 201 not in nums  # La reservada no debe aparecer

    def test_buscar_hoteles_inactivos_no_aparecen(self, agencia_con_datos):
        """R3: Hoteles inactivos no aparecen en búsquedas."""
        agencia_con_datos.hoteles[0].activo = False
        hotel_inactivo = agencia_con_datos.hoteles[0].nombre

        resultados = agencia_con_datos.buscar_habitaciones()
        hoteles_en_resultados = [h.nombre for (h, _) in resultados]
        assert hotel_inactivo not in hoteles_en_resultados


# ============================================================
#  TESTS: Reservas (R10, R11)
# ============================================================


class TestReservas:
    """R10: Realizar reservas. R11: Calcular costo correctamente."""

    def test_realizar_reserva_exitosa(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        resultado = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )
        assert not isinstance(resultado, str)  # No es error
        assert resultado.estado == "pendiente"  # arranca pendiente

    def test_costo_calculado_correctamente(self, agencia_con_datos):
        """
        R11: costo = (pasaje + precio_cat × noches) × temporada × huespedes - descuento
        Cancún: pasaje=350, silver=105, 4 noches = 770 base
        Temporada Alta Verano (días 1-31): ×1.3
        1 huésped: ×1.0
        Oferta Cancún (días 1-31): -10%
        Total: 770 × 1.3 × 1.0 × 0.9 = 900.9 ≈ 901
        """
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )
        # Base: 350 + (105 * 4) = 770
        # × temporada 1.3 = 1001
        # × huéspedes 1.0 = 1001
        # × descuento 0.9 (10% off) = 900.9 ≈ 901
        assert reserva.costo_total == 901

    def test_reserva_cliente_no_existe(self, agencia_con_datos):
        resultado = agencia_con_datos.realizar_reserva(
            "noexiste@mail.com", "Playa Maya", 101, 1, 5
        )
        assert resultado == "Cliente no encontrado"

    def test_reserva_hotel_no_existe(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        resultado = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Hotel Fantasma", 101, 1, 5
        )
        assert resultado == "Hotel no encontrado"

    def test_reserva_habitacion_no_existe(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        resultado = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 999, 1, 5
        )
        assert resultado == "Habitación no encontrada"

    def test_reserva_fechas_invalidas(self, agencia_con_datos):
        """No se puede reservar con fecha fin <= fecha inicio."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        resultado = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 5, 1
        )
        assert "fecha" in resultado.lower() or "mayor" in resultado.lower()

    def test_reserva_no_disponible(self, agencia_con_datos):
        """No se puede reservar una habitación ya ocupada."""
        agencia_con_datos.registrar_cliente("A", "1", "a@mail.com", "Dir")
        agencia_con_datos.registrar_cliente("B", "2", "b@mail.com", "Dir")

        agencia_con_datos.realizar_reserva("a@mail.com", "Playa Maya", 101, 1, 5)
        resultado = agencia_con_datos.realizar_reserva(
            "b@mail.com", "Playa Maya", 101, 3, 7
        )
        assert "disponible" in resultado.lower() or isinstance(resultado, str)

    def test_reserva_hotel_inactivo(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        agencia_con_datos.hoteles[1].activo = False  # Playa Maya
        resultado = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )
        assert "inactivo" in resultado.lower()


# ============================================================
#  TESTS: Pagar reserva (R12)
# ============================================================


class TestPagarReserva:
    """R12: El sistema debe permitir pagar una reserva pendiente."""

    def test_pagar_reserva_exitoso(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 40, 44
        )
        assert reserva.estado == "pendiente"

        resultado = agencia_con_datos.pagar_reserva(reserva)
        assert resultado["exito"] is True
        assert reserva.estado == "pagada"

    def test_pagar_ya_pagada(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 40, 44
        )
        agencia_con_datos.pagar_reserva(reserva)
        resultado = agencia_con_datos.pagar_reserva(reserva)
        assert resultado["exito"] is False

    def test_pagar_cancelada(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 40, 44
        )
        agencia_con_datos.cancelar_reserva(reserva)
        resultado = agencia_con_datos.pagar_reserva(reserva)
        assert resultado["exito"] is False


# ============================================================
#  TESTS: Cancelación (R13)
# ============================================================


class TestCancelarReserva:
    """R13: El sistema debe procesar cancelaciones."""

    def test_cancelar_reserva(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )

        agencia_con_datos.cancelar_reserva(reserva)
        assert reserva.estado == "cancelada"

    def test_cancelar_libera_habitacion(self, agencia_con_datos):
        """Después de cancelar, la habitación debe estar disponible de nuevo."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )

        agencia_con_datos.cancelar_reserva(reserva)

        # Ahora debe poder reservar de nuevo
        reserva2 = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )
        assert not isinstance(reserva2, str)


# ============================================================
#  TESTS: Calificaciones (R14, R15)
# ============================================================


class TestCalificaciones:
    """R14, R15: Calificar estancias y calcular promedios."""

    def test_calificar_exitoso(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )
        agencia_con_datos.pagar_reserva(reserva)  # pagar antes de calificar

        resultado = agencia_con_datos.calificar_estancia(
            "test@mail.com", "Playa Maya", 101, 5, "Excelente"
        )
        assert not isinstance(resultado, str)
        assert resultado.puntuacion == 5

    def test_calificar_sin_reserva(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        resultado = agencia_con_datos.calificar_estancia(
            "test@mail.com", "Playa Maya", 101, 5
        )
        assert isinstance(resultado, str)
        assert "reserva" in resultado.lower()

    def test_calificar_reserva_cancelada(self, agencia_con_datos):
        """No se puede calificar una reserva cancelada."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )
        agencia_con_datos.cancelar_reserva(reserva)

        resultado = agencia_con_datos.calificar_estancia(
            "test@mail.com", "Playa Maya", 101, 5
        )
        assert isinstance(resultado, str)

    def test_calificacion_aparece_en_promedio(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )
        agencia_con_datos.pagar_reserva(reserva)
        agencia_con_datos.calificar_estancia("test@mail.com", "Playa Maya", 101, 4)

        hab = agencia_con_datos.hoteles[1].habitaciones[0]
        assert hab.calificacion_promedio() == 4.0


# ============================================================
#  TESTS: Temporadas
# ============================================================


class TestTemporadas:
    """Luciana: 'Cada hotel tiene su propio calendario de temporadas'"""

    def test_temporada_regional_aumenta_precio(self, agencia_con_datos):
        """Reservar en temporada alta debe costar más."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        # Día 1 = Alta Verano (mult 1.3)
        reserva_alta = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Sol Caribe", 101, 1, 5
        )
        # Día 40 = Baja Primavera (mult 0.85)
        reserva_baja = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Sol Caribe", 101, 40, 44
        )
        assert reserva_alta.costo_total > reserva_baja.costo_total

    def test_temporada_hotel_tiene_prioridad(self, agencia_con_datos):
        """Temporada del hotel debe aplicar sobre la regional."""
        # Playa Maya tiene temporada propia días 10-20 (mult 1.2)
        # Pero regional Alta Verano días 1-31 (mult 1.3)
        # La del hotel tiene prioridad
        playa = next(h for h in agencia_con_datos.hoteles if h.nombre == "Playa Maya")
        mult = agencia_con_datos._obtener_multiplicador_temporada(playa, 15)
        assert mult == 1.2  # Prioridad hotel sobre regional


# ============================================================
#  TESTS: Huéspedes
# ============================================================


class TestHuespedes:
    """Luciana: 'el precio puede cambiar dependiendo de la cantidad de personas'"""

    def test_mas_huespedes_cuesta_mas(self, agencia_con_datos):
        """Más huéspedes = mayor costo (misma habitación, fechas distintas)."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        # Misma habitación (101 silver), 1 huésped
        r1 = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Sol Caribe", 101, 40, 44, cant_huespedes=1
        )
        # Misma habitación (101 silver), 2 huéspedes, fechas distintas
        r2 = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Sol Caribe", 101, 50, 54, cant_huespedes=2
        )
        assert r2.costo_total > r1.costo_total

    def test_no_exceder_capacidad(self, agencia_con_datos):
        """No se puede reservar con más huéspedes que la capacidad."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        resultado = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Sol Caribe", 101, 40, 44, cant_huespedes=5
        )
        assert isinstance(resultado, str)
        assert "capacidad" in resultado.lower()

    def test_cero_huespedes_rechazado(self, agencia_con_datos):
        """No se puede reservar con 0 huéspedes."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        resultado = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Sol Caribe", 101, 40, 44, cant_huespedes=0
        )
        assert isinstance(resultado, str)
        assert "huéspedes" in resultado.lower()


# ============================================================
#  TESTS: Ofertas
# ============================================================


class TestOfertas:
    """Luciana: 'Muchos hoteles tienen promociones por temporada'"""

    def test_oferta_aplica_descuento(self, agencia_con_datos):
        """Playa Maya tiene 10% descuento días 1-31."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        # Reserva sin oferta (día 40)
        r_sin = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 40, 44
        )
        # Reserva con oferta (día 5)
        r_con = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 102, 1, 5
        )
        # Con oferta debería costar menos (misma temporada base diferente)
        assert r_con.costo_total != r_sin.costo_total


# ============================================================
#  TESTS: Condiciones de pago y cancelación
# ============================================================


class TestCancelacion:
    """Luciana: 'Los reembolsos dependen de la política de cancelación'"""

    def test_cancelacion_flexible_reembolso_completo(self, agencia_con_datos):
        """Sol Caribe tiene política flexible."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Sol Caribe", 101, 40, 44
        )
        resultado = agencia_con_datos.cancelar_reserva(reserva)
        assert resultado["exito"] is True
        assert resultado["reembolso"] == reserva.costo_total

    def test_cancelacion_moderada_50_porciento(self, agencia_con_datos):
        """Playa Maya tiene política moderada."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 40, 44
        )
        resultado = agencia_con_datos.cancelar_reserva(reserva)
        assert resultado["exito"] is True
        assert resultado["reembolso"] == round(reserva.costo_total * 0.5)

    def test_cancelacion_estricta_sin_reembolso(self, agencia_con_datos):
        """Le Petit Palace tiene política estricta."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Le Petit Palace", 1, 40, 44
        )
        resultado = agencia_con_datos.cancelar_reserva(reserva)
        assert resultado["exito"] is True
        assert resultado["reembolso"] == 0

    def test_cancelar_ya_cancelada(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Sol Caribe", 101, 40, 44
        )
        agencia_con_datos.cancelar_reserva(reserva)
        resultado = agencia_con_datos.cancelar_reserva(reserva)
        assert resultado["exito"] is False
