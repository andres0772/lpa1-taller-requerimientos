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

    def test_registrar_hotel_campos_completos(self, agencia_vacia):
        """R2: Todos los campos del hotel deben guardarse correctamente."""
        hotel = agencia_vacia.registrar_hotel(
            "Hotel Test",
            "Miami",
            "Calle 123",
            "+1-305-555-0101",
            "info@test.com",
            "Un hotel de prueba",
            ["wifi", "piscina"],
            "https://foto.com/hotel.jpg",
            "Playa Norte",
            "33139",
        )
        assert hotel.nombre == "Hotel Test"
        assert hotel.destino.nombre == "Miami"
        assert hotel.direccion == "Calle 123"
        assert hotel.telefono == "+1-305-555-0101"
        assert hotel.email == "info@test.com"
        assert hotel.descripcion == "Un hotel de prueba"
        assert hotel.servicios == ["wifi", "piscina"]
        assert hotel.foto_url == "https://foto.com/hotel.jpg"
        assert hotel.barrio == "Playa Norte"
        assert hotel.codigo_postal == "33139"
        assert hotel.activo is True


# ============================================================
#  TESTS: Registro de clientes (R8)
# ============================================================


class TestRegistrarCliente:
    """R11: El sistema debe permitir registrar clientes."""

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

    def test_registrar_cliente_campos_completos(self, agencia_vacia):
        """R11: Todos los campos del cliente deben guardarse correctamente."""
        cliente = agencia_vacia.registrar_cliente(
            "Ana López", "+54-11-5555-9999", "ana@mail.com", "Av. Libertador 1234"
        )
        assert cliente.nombre == "Ana López"
        assert cliente.telefono == "+54-11-5555-9999"
        assert cliente.email == "ana@mail.com"
        assert cliente.direccion == "Av. Libertador 1234"


# ============================================================
#  TESTS: Búsqueda de habitaciones (R9)
# ============================================================


class TestBuscarHabitaciones:
    """R12: El sistema debe permitir buscar habitaciones por criterios."""

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

    def test_buscar_por_precio_min(self, agencia_con_datos):
        """R12: Filtrar por precio mínimo de categoría."""
        resultados = agencia_con_datos.buscar_habitaciones(precio_min=200)
        for hotel, hab in resultados:
            precio = hotel.destino.obtener_precio(hab.categoria)
            assert precio >= 200

    def test_buscar_por_precio_max(self, agencia_con_datos):
        """R12: Filtrar por precio máximo de categoría."""
        resultados = agencia_con_datos.buscar_habitaciones(precio_max=150)
        for hotel, hab in resultados:
            precio = hotel.destino.obtener_precio(hab.categoria)
            assert precio <= 150

    def test_buscar_por_precio_rango(self, agencia_con_datos):
        """R12: Filtrar por rango de precios."""
        resultados = agencia_con_datos.buscar_habitaciones(
            precio_min=100, precio_max=150
        )
        assert len(resultados) > 0
        for hotel, hab in resultados:
            precio = hotel.destino.obtener_precio(hab.categoria)
            assert 100 <= precio <= 150

    def test_buscar_por_calificacion_min(self, agencia_con_datos):
        """R12: Filtrar por calificación mínima."""
        # Dar calificaciones a una habitación específica
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )
        agencia_con_datos.pagar_reserva(reserva)
        agencia_con_datos.calificar_estancia("test@mail.com", "Playa Maya", 101, 4)

        # Buscar con calificacion_min=3 → la habitación calificada debe aparecer
        resultados = agencia_con_datos.buscar_habitaciones(calificacion_min=3)
        numeros = [hab.numero for (_, hab) in resultados]
        assert 101 in numeros

        # Buscar con calificacion_min=5 → la habitación con promedio 4 NO debe aparecer
        resultados_altos = agencia_con_datos.buscar_habitaciones(calificacion_min=5)
        numeros_altos = [hab.numero for (_, hab) in resultados_altos]
        assert 101 not in numeros_altos


# ============================================================
#  TESTS: Reservas (R10, R11)
# ============================================================


class TestReservas:
    """R14: Realizar reservas. R10: Calcular costo correctamente."""

    def test_realizar_reserva_exitosa(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        resultado = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )
        assert not isinstance(resultado, str)  # No es error
        assert resultado.estado == "pendiente"  # arranca pendiente

    def test_costo_calculado_correctamente(self, agencia_con_datos):
        """
        R10: costo = (pasaje + precio_cat) × temporada × huespedes × (1 - descuento)
        La tabla de tarifas tiene UN precio por categoría (no es por noche).
        Cancún: pasaje=350, silver=105, base = 455
        Temporada Alta Verano (días 1-31): ×1.3
        1 huésped: ×1.0
        Oferta Playa Maya (días 1-31): -10%
        Total: 455 × 1.3 × 1.0 × 0.9 = 532.35 ≈ 532
        """
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )
        # Base: 350 + 105 = 455
        # × temporada 1.3 = 591.5
        # × huéspedes 1.0 = 591.5
        # × descuento 0.9 (10% off) = 532.35 ≈ 532
        assert reserva.costo_total == 532

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
#  TESTS: Pagar reserva (R15)
# ============================================================


class TestPagarReserva:
    """R15: El sistema debe permitir pagar una reserva pendiente."""

    def test_pagar_reserva_exitoso(self, agencia_con_datos):
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 40, 44
        )
        assert reserva.estado == "pendiente"

        resultado = agencia_con_datos.pagar_reserva(reserva)
        assert resultado["exito"] is True
        assert reserva.estado == "pagada"

    def test_hotel_anticipado_tiene_condicion_correcta(self, agencia_con_datos):
        """R15: Hoteles deben tener condición de pago configurada."""
        sol_caribe = next(
            h for h in agencia_con_datos.hoteles if h.nombre == "Sol Caribe"
        )
        assert sol_caribe.condicion_pago == "anticipado"

        playa = next(h for h in agencia_con_datos.hoteles if h.nombre == "Playa Maya")
        assert playa.condicion_pago == "al_llegar"

    def test_hotel_al_llegar_permite_reservar_sin_pagar(self, agencia_con_datos):
        """R15: Hotel con condición 'al_llegar' permite reserva pendiente."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        # Playa Maya tiene condicion_pago = "al_llegar"
        reserva = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 40, 44, pagar_ahora=False
        )
        assert not isinstance(reserva, str)
        assert reserva.estado == "pendiente"
        # Se puede pagar después
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
    """R16: El sistema debe procesar cancelaciones."""

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
    """R17, R18: Calificar estancias y calcular promedios."""

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
    """R4: Ofertas/promociones por temporada con descuento y rango de fechas."""

    def test_oferta_aplica_descuento(self, agencia_con_datos):
        """R4: Una oferta vigente debe reducir el costo final."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        # Sol Caribe NO tiene ofertas → calcular costo sin descuento
        agencia_con_datos.realizar_reserva("test@mail.com", "Sol Caribe", 101, 1, 5)
        # Agregar oferta del 15% a Sol Caribe para días 1-31
        from clases import Oferta
        from app import parsear_fecha

        agencia_con_datos.hoteles[0].ofertas.append(
            Oferta("Test oferta", parsear_fecha("01/01"), parsear_fecha("31/01"), 0.15)
        )
        # Misma habitación (201), mismas fechas, CON oferta del 15%
        r_con = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Sol Caribe", 201, 1, 5
        )
        # Base: 334 + 151(gold) = 485, × 1.3(temporada) = 630.5, × 0.85(oferta) = 535.925 ≈ 536
        assert r_con.costo_total == 536

    def test_oferta_fuera_de_rango_no_aplica(self, agencia_con_datos):
        """R4: Oferta vigente días 1-31 NO debe aplicar en día 40."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        # Día 40 está fuera del rango de oferta de Playa Maya (1-31)
        # Playa Maya rooms: 101, 102, 201, 301
        r_sin_oferta = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 102, 40, 44
        )
        assert not isinstance(r_sin_oferta, str)
        # Verificar que no se aplicó descuento de oferta
        # Base: 350 + 105 = 455, × 0.85 (baja primavera) = 386.75 ≈ 387
        assert r_sin_oferta.costo_total == 387

    def test_oferta_porcentaje_exacto(self, agencia_con_datos):
        """R4: El descuento de la oferta debe ser el porcentaje correcto."""
        agencia_con_datos.registrar_cliente("Test", "123", "test@mail.com", "Dir")
        # Playa Maya, silver(105), día 5 (Alta Verano 1.3, oferta 10%)
        # Base: 350 + 105 = 455, × 1.3 = 591.5, × 0.9 = 532.35 ≈ 532
        r_con_oferta = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 1, 5
        )
        assert r_con_oferta.costo_total == 532

        # Misma habitación, día 40 (Baja Primavera 0.85, sin oferta)
        # Base: 350 + 105 = 455, × 0.85 = 386.75 ≈ 387
        r_sin_oferta = agencia_con_datos.realizar_reserva(
            "test@mail.com", "Playa Maya", 101, 40, 44
        )
        assert r_sin_oferta.costo_total == 387


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
