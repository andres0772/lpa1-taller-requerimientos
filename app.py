import unicodedata

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from clases import (
    Calificacion,
    Cliente,
    Destino,
    Habitacion,
    Hotel,
    Oferta,
    Reserva,
    Temporada,
)
from datos import TARIFAS

console = Console()


def normalizar(texto):
    """Quita acentos y pasa a minúsculas para comparar sin problemas."""
    nfkd = unicodedata.normalize("NFKD", texto)
    sin_acentos = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sin_acentos.lower()


# ============================================================
#  UTILIDADES DE FECHA
#  Internamente usamos "día del año" (1-365) para comparar.
#  El usuario escribe "DD/MM" y ve "DD/MM".
# ============================================================

DIAS_POR_MES = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def parsear_fecha(texto):
    """
    Convierte "DD/MM" a día del año (int).
    Retorna None si el formato es inválido.
    Ejemplo: "15/03" → 31+28+15 = 74
    """
    partes = texto.strip().split("/")
    if len(partes) != 2:
        return None
    if not (partes[0].isdigit() and partes[1].isdigit()):
        return None
    dia = int(partes[0])
    mes = int(partes[1])
    if mes < 1 or mes > 12:
        return None
    if dia < 1 or dia > DIAS_POR_MES[mes]:
        return None
    # Sumar días de los meses anteriores
    dia_del_ano = sum(DIAS_POR_MES[:mes]) + dia
    return dia_del_ano


def formato_fecha(dia_del_ano):
    """
    Convierte día del año (int) a "DD/MM".
    Ejemplo: 74 → "15/03"
    """
    restante = dia_del_ano
    for mes in range(1, 13):
        if restante <= DIAS_POR_MES[mes]:
            return f"{restante:02d}/{mes:02d}"
        restante -= DIAS_POR_MES[mes]
    return f"{dia_del_ano}"  # fallback


# ============================================================
#  CLASE: AgenciaViajes (el motor del sistema)
#  Orquesta todas las entidades y contiene la lógica de negocio.
#  No sabe nada de la interfaz (rich, menús, etc.)
# ============================================================


class AgenciaViajes:
    """
    Motor principal del sistema.
    Coordina destinos, hoteles, clientes y reservas.
    """

    def __init__(self):
        self.destinos = {}  # nombre -> Destino
        self.hoteles = []  # lista de Hotel
        self.clientes = []  # lista de Cliente
        # Temporadas regionales (aplican a todos los hoteles)
        # Luciana: "existe un calendario regional que la mayoría
        #  de los hoteles sigue"
        self.temporadas_regionales = []

    # --------------------------------------------------------
    #  Carga inicial de destinos desde la tabla de tarifas
    # --------------------------------------------------------

    def cargar_tarifas(self):
        """
        R1: Carga los destinos desde la tabla de tarifas.
        Cada fila de TARIFAS se convierte en un objeto Destino.
        """
        for nombre, pasaje, silver, gold, platinum in TARIFAS:
            self.destinos[nombre] = Destino(nombre, pasaje, silver, gold, platinum)

    # --------------------------------------------------------
    #  Registro de hoteles (R2)
    # --------------------------------------------------------

    def registrar_hotel(
        self,
        nombre,
        nombre_destino,
        direccion,
        telefono,
        email,
        descripcion,
        servicios=None,
        foto_url=None,
        barrio=None,
        codigo_postal=None,
    ):
        """
        R2: Registra un hotel asociado a un destino existente.
        Retorna el Hotel creado o None si el destino no existe.
        """
        # Búsqueda case-insensitive del destino
        destino = None
        for dest in self.destinos.values():
            if normalizar(dest.nombre) == normalizar(nombre_destino):
                destino = dest
                break
        if destino is None:
            return None
        hotel = Hotel(
            nombre,
            destino,
            direccion,
            telefono,
            email,
            descripcion,
            servicios,
            foto_url,
            barrio,
            codigo_postal,
        )
        self.hoteles.append(hotel)
        return hotel

    # --------------------------------------------------------
    #  Registro de clientes (R11)
    # --------------------------------------------------------

    def registrar_cliente(self, nombre, telefono, email, direccion):
        """
        R11: Registra un nuevo cliente en el sistema.
        Retorna el Cliente creado o None si el email ya existe.
        """
        email_norm = email.lower()
        if any(c.email.lower() == email_norm for c in self.clientes):
            return None
        cliente = Cliente(nombre, telefono, email_norm, direccion)
        self.clientes.append(cliente)
        return cliente

    # --------------------------------------------------------
    #  Búsqueda de habitaciones (R12)
    # --------------------------------------------------------

    def buscar_habitaciones(
        self,
        destino_nombre=None,
        fecha_inicio=None,
        fecha_fin=None,
        categoria=None,
        capacidad_min=None,
        precio_min=None,
        precio_max=None,
        calificacion_min=None,
    ):
        """
        R12: Busca habitaciones disponibles combinando criterios.
        Retorna lista de tuplas (Hotel, Habitacion).
        """
        resultados = []
        for hotel in self.hoteles:
            # R3: solo hoteles activos aparecen en búsquedas
            if not hotel.esta_activo():
                continue
            # Filtrar por destino si se especificó
            if destino_nombre and normalizar(hotel.destino.nombre) != normalizar(
                destino_nombre
            ):
                continue
            for hab in hotel.habitaciones:
                # R6: solo habitaciones activas
                if not hab.activa:
                    continue
                # R7: verificar disponibilidad en fechas
                if fecha_inicio and fecha_fin:
                    if not hab.esta_disponible(fecha_inicio, fecha_fin):
                        continue
                # Filtrar por categoría
                if categoria and hab.categoria != categoria.lower():
                    continue
                # Filtrar por capacidad mínima
                if capacidad_min and hab.capacidad < capacidad_min:
                    continue
                # filtrar por precio (comparación sobre precio base de categoría)
                if precio_min is not None or precio_max is not None:
                    precio = hotel.destino.obtener_precio(hab.categoria)
                    if precio_min is not None and precio < precio_min:
                        continue
                    if precio_max is not None and precio > precio_max:
                        continue
                # esto filtra por calificacion minima
                if calificacion_min is not None:
                    if hab.calificacion_promedio() < calificacion_min:
                        continue

                resultados.append((hotel, hab))
        return resultados

    # --------------------------------------------------------
    #  Realizar reserva (R14, R10)
    # --------------------------------------------------------

    def realizar_reserva(
        self,
        cliente_email,
        hotel_nombre,
        hab_numero,
        fecha_inicio,
        fecha_fin,
        cant_huespedes=1,
        pagar_ahora=False,
    ):
        """
        R14: Realiza una reserva.
        Si el hotel requiere pago anticipado, pagar_ahora debe ser True.
        Retorna la Reserva creada o un mensaje de error (str).
        """
        # Buscar cliente
        cliente = next(
            (c for c in self.clientes if c.email.lower() == cliente_email.lower()), None
        )
        if cliente is None:
            return "Cliente no encontrado"

        # Buscar hotel
        hotel = next((h for h in self.hoteles if h.nombre == hotel_nombre), None)
        if hotel is None:
            return "Hotel no encontrado"
        if not hotel.esta_activo():
            return "El hotel está inactivo"

        # Buscar habitación
        habitacion = next(
            (h for h in hotel.habitaciones if h.numero == hab_numero), None
        )
        if habitacion is None:
            return "Habitación no encontrada"

        # Validar que fecha_fin > fecha_inicio
        if fecha_inicio >= fecha_fin:
            return "La fecha de fin debe ser mayor a la de inicio"

        # Verificar disponibilidad (R7)
        if not habitacion.esta_disponible(fecha_inicio, fecha_fin):
            return "La habitación no está disponible en esas fechas"

        # Validar cantidad de huéspedes
        if cant_huespedes < 1:
            return "La cantidad de huéspedes debe ser al menos 1"

        # Validar capacidad (entrevista: "no se exceda la capacidad máxima")
        if cant_huespedes > habitacion.capacidad:
            return (
                f"La capacidad máxima es {habitacion.capacidad} "
                f"huéspedes, solicitó {cant_huespedes}"
            )

        # R10: calcular costo base
        # La tabla de tarifas tiene UN precio por categoría (no es por noche).
        # Factores que modifican: temporada, huéspedes, ofertas.
        precio_categoria = hotel.destino.obtener_precio(habitacion.categoria)
        costo_base = hotel.destino.tarifa_pasaje + precio_categoria

        # NUEVO: aplicar multiplicador de temporada
        # Luciana: "el precio puede cambiar... También influye la temporada"
        mult_temporada = self._obtener_multiplicador_temporada(hotel, fecha_inicio)
        costo_con_temporada = costo_base * mult_temporada

        # NUEVO: ajuste por cantidad de huéspedes
        # Luciana: "el precio puede cambiar dependiendo de la cantidad
        #  de personas que se alojen"
        mult_huespedes = self._obtener_multiplicador_huespedes(
            cant_huespedes, habitacion.capacidad
        )
        costo_con_huespedes = costo_con_temporada * mult_huespedes

        # NUEVO: aplicar ofertas/descuentos vigentes
        descuento = self._obtener_descuento_oferta(hotel, fecha_inicio)
        costo_total = round(costo_con_huespedes * (1 - descuento))

        # Crear reserva (arranca como pendiente)
        reserva = Reserva(
            fecha_inicio, fecha_fin, cliente, habitacion, costo_total, cant_huespedes
        )

        # Si se solicitó pagar ahora, marcar como pagada
        if pagar_ahora:
            reserva.estado = "pagada"

        cliente.reservas.append(reserva)
        habitacion.reservas.append(reserva)

        return reserva

    # --------------------------------------------------------
    #  Pagar reserva (R15)
    #  Luciana: "algunos hoteles requieren el pago completo por
    #   adelantado, mientras que otros permiten pagar al llegar"
    # --------------------------------------------------------

    def pagar_reserva(self, reserva):
        """
        R15: Marca una reserva como pagada.
        Retorna dict con: {exito: bool, mensaje: str}
        """
        if reserva.estado == "pagada":
            return {"exito": False, "mensaje": "La reserva ya está pagada"}
        if reserva.estado == "cancelada":
            return {
                "exito": False,
                "mensaje": "No se puede pagar una reserva cancelada",
            }
        reserva.estado = "pagada"
        return {"exito": True, "mensaje": f"Pago confirmado: ${reserva.costo_total}"}

    def _obtener_multiplicador_temporada(self, hotel, fecha):
        """
        Busca el multiplicador de temporada para una fecha.
        Prioridad: temporada del hotel > temporada regional > 1.0
        """
        # Primero buscar en temporadas del hotel
        for temp in hotel.temporadas:
            if temp.contiene(fecha):
                return temp.multiplicador
        # Si no, buscar en temporadas regionales
        for temp in self.temporadas_regionales:
            if temp.contiene(fecha):
                return temp.multiplicador
        return 1.0  # temporada normal (sin ajuste)

    def _obtener_multiplicador_huespedes(self, cant_huespedes, capacidad):
        """
        Ajusta el precio según la cantidad de huéspedes.
        Más huéspedes = mayor precio (hasta la capacidad máxima).
        """
        if capacidad == 0:
            return 1.0
        # Cada huésped adicional agrega 10% al precio base
        # (después del primero)
        return 1.0 + (cant_huespedes - 1) * 0.10

    def _obtener_descuento_oferta(self, hotel, fecha):
        """
        Busca ofertas vigentes para el hotel en la fecha dada.
        Retorna el mayor descuento disponible.
        """
        mayor_descuento = 0
        for oferta in hotel.ofertas:
            if oferta.esta_vigente(fecha) and oferta.descuento > mayor_descuento:
                mayor_descuento = oferta.descuento
        return mayor_descuento

    # --------------------------------------------------------
    #  Cancelar reserva (R16)
    #  Luciana: "Los reembolsos dependen de la política de
    #   cancelación de cada hotel. Algunos hoteles cobran una
    #   penalidad por cancelación, mientras que otros ofrecen
    #   reembolsos completos si se cancela con suficiente anticipación."
    # --------------------------------------------------------

    def cancelar_reserva(self, reserva):
        """
        R16: Cancela una reserva aplicando la política del hotel.
        Retorna un dict con: {exito: bool, reembolso: float, mensaje: str}
        """
        if reserva.estado == "cancelada":
            return {"exito": False, "reembolso": 0, "mensaje": "Ya estaba cancelada"}

        politica = (
            reserva.habitacion.politica_cancelacion
            or reserva.habitacion.hotel.politica_cancelacion
            or "moderada"  # default si ningún hotel/habitación configuró política
        )
        costo = reserva.costo_total

        if politica == "flexible":
            reembolso = costo
            mensaje = "Cancelación flexible: reembolso completo"
        elif politica == "moderada":
            reembolso = round(costo * 0.5)
            mensaje = f"Cancelación moderada: reembolso del 50% (${reembolso})"
        else:  # estricta
            reembolso = 0
            mensaje = "Cancelación estricta: sin reembolso"

        # Usar el método cancelar() de Reserva (no duplicar lógica)
        reserva.cancelar()

        return {"exito": True, "reembolso": reembolso, "mensaje": mensaje}

    # --------------------------------------------------------
    #  Calificar estancia (R17, R18)
    # --------------------------------------------------------

    def calificar_estancia(
        self,
        cliente_email,
        hotel_nombre,
        hab_numero,
        puntuacion,
        comentario="",
        fecha_actual=None,
    ):
        """
        R17: Permite al cliente calificar una estancia.
        Verifica que el cliente tenga una reserva completada en esa habitación.
        Si se proporciona fecha_actual, verifica que la estadía ya terminó.
        """
        cliente = next(
            (c for c in self.clientes if c.email.lower() == cliente_email.lower()), None
        )
        if cliente is None:
            return "Cliente no encontrado"

        hotel = next((h for h in self.hoteles if h.nombre == hotel_nombre), None)
        if hotel is None:
            return "Hotel no encontrado"

        habitacion = next(
            (h for h in hotel.habitaciones if h.numero == hab_numero), None
        )
        if habitacion is None:
            return "Habitación no encontrada"

        # Verificar que el cliente tenga una reserva pagada NO calificada en esta habitación
        reserva_valida = None
        for r in cliente.reservas:
            if r.habitacion == habitacion and r.estado == "pagada" and not r.calificada:
                reserva_valida = r
                break

        if reserva_valida is None:
            return (
                "El cliente no tiene reservas pagadas sin calificar en esta habitación"
            )

        # Si se proporciona fecha_actual, verificar que la estadía ya terminó
        if fecha_actual is not None and reserva_valida.fecha_fin > fecha_actual:
            return (
                f"La estadía aún no ha terminado "
                f"(termina en día {reserva_valida.fecha_fin})"
            )

        calificacion = Calificacion(puntuacion, comentario)
        habitacion.calificaciones.append(calificacion)
        # Crear copia separada para el hotel (no compartir por referencia)
        hotel.calificaciones.append(Calificacion(puntuacion, comentario))

        # Marcar la reserva como calificada (solo se puede calificar una vez)
        reserva_valida.calificada = True

        return calificacion

    # --------------------------------------------------------
    #  Utilidades para mostrar datos
    # --------------------------------------------------------

    def listar_destinos(self):
        """Retorna todos los destinos ordenados por nombre."""
        return sorted(self.destinos.values(), key=lambda d: d.nombre)

    def listar_hoteles_activos(self):
        """Retorna solo los hoteles activos."""
        return [h for h in self.hoteles if h.esta_activo()]

    def obtener_reservas_cliente(self, cliente_email):
        """Retorna las reservas activas de un cliente."""
        cliente = next(
            (c for c in self.clientes if c.email.lower() == cliente_email.lower()), None
        )
        if cliente is None:
            return []
        return [r for r in cliente.reservas if r.estado != "cancelada"]


# ============================================================
#  DATOS DE EJEMPLO
#  Precargamos algunos hoteles y habitaciones para poder probar.
#  En un sistema real, esto se haría desde el menú.
# ============================================================


def _foto_destino(nombre_destino):
    """Retorna la ruta de la foto del destino desde static/."""
    # normalizar ya quita acentos y pasa a minúsculas
    nombre_archivo = normalizar(nombre_destino)
    return f"static/{nombre_archivo}.png"


def cargar_datos_ejemplo(agencia):
    """Carga datos de prueba para poder usar el sistema inmediatamente."""

    # Hoteles en Miami
    agencia.registrar_hotel(
        "Sol Caribe",
        "Miami",
        "123 Ocean Drive",
        "+1-305-555-0101",
        "info@solcaribe.com",
        "Hotel frente al mar con vista al Atlántico",
        ["piscina", "restaurante", "spa", "wifi"],
        foto_url=_foto_destino("Miami"),
        barrio="Soulth Beach",
        codigo_postal="33139",
    )
    sol = agencia.hoteles[-1]
    sol.agregar_habitacion(
        Habitacion(
            101,
            "Habitación estándar vista ciudad",
            "silver",
            2,
            ["wifi", "tv"],
        )
    )
    sol.agregar_habitacion(
        Habitacion(
            201,
            "Habitación superior vista mar",
            "gold",
            3,
            ["wifi", "tv", "minibar"],
        )
    )
    sol.agregar_habitacion(
        Habitacion(
            301,
            "Suite presidencial",
            "platinum",
            4,
            ["wifi", "tv", "minibar", "jacuzzi", "terraza"],
        )
    )

    # Hoteles en Cancún
    agencia.registrar_hotel(
        "Playa Maya",
        "Cancún",
        "456 Blvd. Kukulcán",
        "+52-998-555-0202",
        "reservas@playamaya.com",
        "Resort todo incluido en la zona hotelera",
        ["piscina", "restaurante", "bar", "gimnasio", "wifi"],
        foto_url=_foto_destino("Cancún"),
    )
    playa = agencia.hoteles[-1]
    playa.agregar_habitacion(
        Habitacion(
            101,
            "Habitación garden view",
            "silver",
            2,
            ["wifi", "tv", "aire acondicionado"],
        )
    )
    playa.agregar_habitacion(
        Habitacion(
            102,
            "Habitación garden view",
            "silver",
            2,
            ["wifi", "tv", "aire acondicionado"],
        )
    )
    playa.agregar_habitacion(
        Habitacion(
            201, "Habitación ocean view", "gold", 3, ["wifi", "tv", "minibar", "balcón"]
        )
    )
    playa.agregar_habitacion(
        Habitacion(
            301, "Suite junior", "platinum", 4, ["wifi", "tv", "minibar", "jacuzzi"]
        )
    )

    # Hoteles en Paris
    agencia.registrar_hotel(
        "Le Petit Palace",
        "Paris",
        "78 Avenue des Champs-Élysées",
        "+33-1-555-0303",
        "contact@lepetitpalace.fr",
        "Hotel boutique en el corazón de París",
        ["restaurante", "wifi", "conserjería"],
        foto_url=_foto_destino("Paris"),
    )
    palace = agencia.hoteles[-1]
    palace.agregar_habitacion(
        Habitacion(1, "Chambre Classique", "silver", 2, ["wifi", "tv"])
    )
    palace.agregar_habitacion(
        Habitacion(2, "Chambre Supérieure", "gold", 2, ["wifi", "tv", "minibar"])
    )
    palace.agregar_habitacion(
        Habitacion(
            3,
            "Suite Royale",
            "platinum",
            3,
            ["wifi", "tv", "minibar", "vista Torre Eiffel"],
        )
    )

    # Cliente de ejemplo
    agencia.registrar_cliente(
        "Juan Pérez", "+54-11-5555-1234", "juan@email.com", "Av. Corrientes 1234, CABA"
    )

    # -------------------------------------------------------
    #  NUEVO: Temporadas regionales
    #  Luciana: "existe un calendario regional que la mayoría
    #   de los hoteles sigue"
    # -------------------------------------------------------
    agencia.temporadas_regionales.append(
        Temporada("Alta Verano", parsear_fecha("01/01"), parsear_fecha("31/01"), 1.3)
    )
    agencia.temporadas_regionales.append(
        Temporada(
            "Baja Primavera", parsear_fecha("01/02"), parsear_fecha("28/02"), 0.85
        )
    )
    agencia.temporadas_regionales.append(
        Temporada("Alta Navidad", parsear_fecha("01/03"), parsear_fecha("20/03"), 1.5)
    )

    # -------------------------------------------------------
    #  NUEVO: Temporadas específicas de un hotel
    #  Luciana: "Cada hotel tiene su propio calendario de temporadas"
    # -------------------------------------------------------
    playa = next(h for h in agencia.hoteles if h.nombre == "Playa Maya")
    playa.temporadas.append(
        Temporada(
            "Temporada Playa Maya", parsear_fecha("10/01"), parsear_fecha("20/01"), 1.2
        )
    )

    # -------------------------------------------------------
    #  NUEVO: Condiciones de pago y política de cancelación
    #  Luciana: "algunos hoteles requieren el pago completo por
    #   adelantado, mientras que otros permiten pagar al llegar"
    # -------------------------------------------------------
    agencia.hoteles[0].condicion_pago = "anticipado"  # Sol Caribe
    agencia.hoteles[0].politica_cancelacion = "flexible"
    agencia.hoteles[1].condicion_pago = "al_llegar"  # Playa Maya
    agencia.hoteles[1].politica_cancelacion = "moderada"
    agencia.hoteles[2].condicion_pago = "anticipado"  # Le Petit Palace
    agencia.hoteles[2].politica_cancelacion = "estricta"

    # -------------------------------------------------------
    #  NUEVO: Ofertas y promociones
    #  Luciana: "Muchos hoteles tienen promociones por temporada,
    #   como descuentos en temporada baja o paquetes especiales"
    # -------------------------------------------------------
    agencia.hoteles[1].ofertas.append(
        Oferta(
            "Descuento verano en Cancún",
            parsear_fecha("01/01"),
            parsear_fecha("31/01"),
            0.10,
        )
    )
    agencia.hoteles[2].ofertas.append(
        Oferta("Promoción París", parsear_fecha("01/02"), parsear_fecha("28/02"), 0.15)
    )


# ============================================================
#  FUNCIONES DE LA INTERFAZ (RICH)
#  Estas funciones usan rich para mostrar datos bonitos.
#  NO contienen lógica de negocio — solo presentación.
# ============================================================


def mostrar_destinos(agencia):
    """Muestra la tabla de destinos con tarifas (igual que el README)."""
    tabla = Table(title="🌍 Destinos Disponibles", box=box.ROUNDED)
    tabla.add_column("Destino", style="cyan bold")
    tabla.add_column("Pasaje", justify="right", style="yellow")
    tabla.add_column("Silver", justify="right", style="white")
    tabla.add_column("Gold", justify="right", style="gold1")
    tabla.add_column("Platinum", justify="right", style="magenta")

    for destino in agencia.listar_destinos():
        tabla.add_row(
            destino.nombre,
            f"${destino.tarifa_pasaje}",
            f"${destino.precio_silver}",
            f"${destino.precio_gold}",
            f"${destino.precio_platinum}",
        )
    console.print(tabla)


def mostrar_hoteles(agencia, destino_nombre=None):
    """Muestra los hoteles activos, opcionalmente filtrados por destino."""
    hoteles = agencia.listar_hoteles_activos()
    if destino_nombre:
        hoteles = [
            h
            for h in hoteles
            if normalizar(h.destino.nombre) == normalizar(destino_nombre)
        ]

    if not hoteles:
        console.print("[yellow]No se encontraron hoteles.[/yellow]")
        # Mostrar qué destinos SÍ tienen hoteles
        destinos_con_hoteles = sorted(
            set(h.destino.nombre for h in agencia.listar_hoteles_activos())
        )
        if destinos_con_hoteles:
            console.print(
                f"[dim]Destinos con hoteles: {', '.join(destinos_con_hoteles)}[/dim]"
            )
        return

    for hotel in hoteles:
        cal = hotel.calificacion_promedio()
        estrellas = f"★ {cal}/5" if cal > 0 else "Sin calificaciones"

        tabla = Table(
            title=f"🏨 {hotel.nombre} — {hotel.destino.nombre}", box=box.SIMPLE_HEAVY
        )
        tabla.add_column("Hab.", justify="center", style="cyan")
        tabla.add_column("Descripción")
        tabla.add_column("Categoría", justify="center")
        tabla.add_column("Cap.", justify="center")
        tabla.add_column("Estado", justify="center")
        tabla.add_column("Calificación", justify="center")

        for hab in hotel.habitaciones:
            estado = (
                "[green]Disponible[/green]" if hab.activa else "[red]Inactiva[/red]"
            )
            cal_hab = hab.calificacion_promedio()
            cal_str = f"★ {cal_hab}" if cal_hab > 0 else "-"

            color_cat = {"silver": "white", "gold": "gold1", "platinum": "magenta"}
            cat_color = color_cat.get(hab.categoria, "white")

            tabla.add_row(
                str(hab.numero),
                hab.descripcion,
                f"[{cat_color}]{hab.categoria.upper()}[/{cat_color}]",
                str(hab.capacidad),
                estado,
                cal_str,
            )

        console.print(tabla)
        console.print(f"  📍 {hotel.direccion}")
        if hotel.barrio:
            console.print(f"     Barrio: {hotel.barrio}, CP: {hotel.codigo_postal}")
        console.print(f"  📞 {hotel.telefono} | ✉ {hotel.email}")
        console.print(f"  🏷 Servicios: {', '.join(hotel.servicios)}")
        if hotel.foto_url:
            console.print(f"  📸 Foto: {hotel.foto_url}")
        console.print(f"  ⭐ {estrellas}")

        # NUEVO: condiciones de pago y cancelación
        pago_str = {"anticipado": "Pago anticipado", "al_llegar": "Pago al llegar"}
        cancel_str = {
            "flexible": "[green]Flexible (reembolso completo)[/green]",
            "moderada": "[yellow]Moderada (50% reembolso)[/yellow]",
            "estricta": "[red]Estricta (sin reembolso)[/red]",
        }
        console.print(
            f"  💳 Pago: {pago_str.get(hotel.condicion_pago, hotel.condicion_pago)}"
        )
        console.print(
            f"  📋 Cancelación: {cancel_str.get(hotel.politica_cancelacion, hotel.politica_cancelacion)}"
        )

        # NUEVO: ofertas vigentes
        if hotel.ofertas:
            ofertas_str = ", ".join(str(o) for o in hotel.ofertas)
            console.print(f"  🏷 Ofertas: {ofertas_str}")

        # NUEVO: temporadas del hotel
        if hotel.temporadas:
            temps_str = ", ".join(str(t) for t in hotel.temporadas)
            console.print(f"  📅 Temporadas: {temps_str}")

        console.print()


def mostrar_busqueda(resultados, agencia=None):
    """
    Muestra los resultados de una búsqueda de habitaciones.
    Si se pasa agencia, permite el flujo completo: buscar → ver detalle → reservar.
    """
    if not resultados:
        console.print(
            "[yellow]No se encontraron habitaciones con esos criterios.[/yellow]"
        )
        return

    tabla = Table(title="🔍 Resultados de Búsqueda", box=box.ROUNDED)
    tabla.add_column("#", justify="center", style="dim")
    tabla.add_column("Hotel", style="cyan")
    tabla.add_column("Destino", style="blue")
    tabla.add_column("Hab.", justify="center")
    tabla.add_column("Descripción")
    tabla.add_column("Categoría", justify="center")
    tabla.add_column("Cap.", justify="center")
    tabla.add_column("Precio", justify="right", style="yellow")

    for i, (hotel, hab) in enumerate(resultados, 1):
        precio = hotel.destino.obtener_precio(hab.categoria)
        color_cat = {"silver": "white", "gold": "gold1", "platinum": "magenta"}
        cat_color = color_cat.get(hab.categoria, "white")

        tabla.add_row(
            str(i),
            hotel.nombre,
            hotel.destino.nombre,
            str(hab.numero),
            hab.descripcion,
            f"[{cat_color}]{hab.categoria.upper()}[/{cat_color}]",
            str(hab.capacidad),
            f"${precio}",
        )

    console.print(tabla)

    # R13: ver detalle de habitación
    num = console.input("\nSeleccionar habitación (#) o Enter para volver: ").strip()
    if num.isdigit() and 1 <= int(num) <= len(resultados):
        hotel, hab = resultados[int(num) - 1]
        mostrar_detalle_habitacion(hotel, hab)

        # Caso de uso 1, paso 5: ofrecer reserva directa
        if agencia:
            resp = (
                console.input("¿Desea reservar esta habitación? (s/n): ")
                .strip()
                .lower()
            )
            if resp == "s":
                flujo_reservar(agencia, hotel, hab)
    elif num:
        console.print("[red]Selección inválida. Ingrese un número de la lista.[/red]")


def mostrar_detalle_habitacion(hotel, hab):
    """
    R13: Muestra el detalle completo de una habitación:
    descripción, características, servicios, calificación y comentarios.
    Luciana: "Puede ver una descripción detallada de la habitación,
    incluyendo sus características, servicios incluidos, fotos y,
    por supuesto, la calificación y los comentarios de otros huéspedes."
    """
    precio = hotel.destino.obtener_precio(hab.categoria)
    color_cat = {"silver": "white", "gold": "gold1", "platinum": "magenta"}
    cat_color = color_cat.get(hab.categoria, "white")

    # Contenido del panel
    contenido = (
        f"[bold]{hotel.nombre}[/bold] — Habitación {hab.numero}\n\n"
        f"  📍 Destino: {hotel.destino.nombre}\n"
        f"  📝 Descripción: {hab.descripcion}\n"
        f"  🏷 Categoría: [{cat_color}]{hab.categoria.upper()}[/{cat_color}]\n"
        f"  👥 Capacidad: {hab.capacidad} huéspedes\n"
        f"  💰 Precio: ${precio}\n"
        f"  🔧 Servicios: {', '.join(hab.servicios) if hab.servicios else 'Ninguno'}\n"
        f"  ✅ Estado: {'Activa' if hab.activa else 'Inactiva'}"
    )
    if hab.foto_url:
        contenido += f"\n  📸 Foto: {hab.foto_url}"

    console.print(
        Panel.fit(contenido, title="🏠 Detalle de Habitación", border_style="cyan")
    )

    # Mostrar calificaciones
    if hab.calificaciones:
        cal_prom = hab.calificacion_promedio()
        estrellas = "★" * int(cal_prom) + "☆" * (5 - int(cal_prom))
        console.print(f"\n  ⭐ Calificación promedio: {estrellas} ({cal_prom}/5)")
        console.print(f"  💬 Comentarios ({len(hab.calificaciones)}):")
        for cal in hab.calificaciones:
            console.print(f"    {cal}")
    else:
        console.print("\n  [dim]Sin calificaciones aún[/dim]")

    console.print()


def flujo_reservar(agencia, hotel, hab):
    """
    Caso de uso 1, pasos 5-8: Flujo de reserva directa desde la búsqueda.
    El cliente ya vio los detalles de la habitación y quiere reservar.
    """
    console.print(f"\n[bold]Reservar {hotel.nombre} - Habitación {hab.numero}[/bold]")

    # Datos del cliente
    email = console.input("Email del cliente: ").strip()

    # Fechas
    ini = console.input("Fecha inicio (DD/MM, ej: 15/01): ").strip()
    fin = console.input("Fecha fin (DD/MM, ej: 20/01): ").strip()
    fecha_ini = parsear_fecha(ini)
    fecha_fin = parsear_fecha(fin)
    if fecha_ini is None or fecha_fin is None:
        console.print("[red]Formato de fecha inválido. Use DD/MM.[/red]")
        return

    # Huéspedes
    cap_str = console.input("Cantidad de huéspedes: ").strip()
    cant_huespedes = int(cap_str) if cap_str.isdigit() else 1

    # Pago: la reserva siempre arranca como PENDIENTE
    # Luciana: "El cliente confirma su selección y procede a realizar el pago"
    # Son DOS pasos: confirmar (reservar) → pagar
    pagar_ahora = False
    if hotel.condicion_pago == "anticipado":
        console.print("[yellow]⚠ Este hotel requiere pago anticipado.[/yellow]")
        resp = console.input("¿Pagar ahora? (s/n): ").strip().lower()
        pagar_ahora = resp == "s"
    else:
        resp = console.input("¿Pagar ahora? (s/n): ").strip().lower()
        pagar_ahora = resp == "s"

    # Realizar reserva
    resultado = agencia.realizar_reserva(
        email,
        hotel.nombre,
        hab.numero,
        fecha_ini,
        fecha_fin,
        cant_huespedes,
        pagar_ahora,
    )

    if isinstance(resultado, str):
        console.print(f"[red]✗ Error: {resultado}[/red]")
    else:
        console.print(f"\n[green]✓ Reserva realizada![/green]")
        console.print(f"  {resultado}")
        console.print(f"  [yellow]Estado: {resultado.estado.upper()}[/yellow]")
        if resultado.estado == "pendiente":
            console.print("  ℹ Use opción 10 cuando desee pagar esta reserva.")


def mostrar_reservas(reservas):
    """Muestra las reservas de un cliente."""
    if not reservas:
        console.print("[yellow]No tiene reservas activas.[/yellow]")
        return

    tabla = Table(title="📋 Sus Reservas", box=box.ROUNDED)
    tabla.add_column("#", justify="center", style="dim")
    tabla.add_column("Hotel", style="cyan")
    tabla.add_column("Hab.", justify="center")
    tabla.add_column("Desde", style="green")
    tabla.add_column("Hasta", style="green")
    tabla.add_column("Total", justify="right", style="yellow")
    tabla.add_column("Estado", justify="center")

    for i, r in enumerate(reservas, 1):
        estado_color = {"pagada": "green", "pendiente": "yellow", "cancelada": "red"}
        color = estado_color.get(r.estado, "white")
        tabla.add_row(
            str(i),
            r.habitacion.hotel.nombre,
            str(r.habitacion.numero),
            formato_fecha(r.fecha_inicio),
            formato_fecha(r.fecha_fin),
            f"${r.costo_total}",
            f"[{color}]{r.estado.upper()}[/{color}]",
        )
    console.print(tabla)


# ============================================================
#  MENÚ PRINCIPAL
#  El bucle que muestra opciones y ejecuta acciones.
# ============================================================


def menu_principal():
    """Bucle principal del sistema."""

    # Inicializar la agencia
    agencia = AgenciaViajes()
    agencia.cargar_tarifas()  # R1
    cargar_datos_ejemplo(agencia)  # datos de prueba

    console.print(
        Panel.fit(
            "[bold cyan]✈  SISTEMA DE AGENCIA DE VIAJES  ✈[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()

    while True:
        console.print(
            Panel.fit(
                "[bold]MENÚ PRINCIPAL[/bold]\n\n"
                "  [cyan]1[/cyan]  - Ver destinos y tarifas\n"
                "  [cyan]2[/cyan]  - Ver hoteles y habitaciones\n"
                "  [cyan]3[/cyan]  - Buscar habitaciones\n"
                "  [cyan]4[/cyan]  - Registrar cliente\n"
                "  [cyan]5[/cyan]  - Registrar hotel\n"
                "  [cyan]6[/cyan]  - Registrar habitación\n"
                "  [cyan]7[/cyan]  - Desactivar hotel/habitación\n"
                "  [cyan]8[/cyan]  - Realizar reserva\n"
                "  [cyan]9[/cyan]  - Ver mis reservas\n"
                "  [cyan]10[/cyan] - Pagar reserva\n"
                "  [cyan]11[/cyan] - Cancelar reserva\n"
                "  [cyan]12[/cyan] - Calificar estancia\n"
                "  [cyan]0[/cyan]  - Salir",
                title="🌍 Agencia de Viajes",
                border_style="cyan",
            )
        )

        opcion = console.input(
            "\n[bold cyan]Seleccione una opción:[/bold cyan] "
        ).strip()

        # -------------------------------------------------
        #  Opción 1: Ver destinos y tarifas
        # -------------------------------------------------
        if opcion == "1":
            mostrar_destinos(agencia)

        # -------------------------------------------------
        #  Opción 2: Ver hoteles y habitaciones
        # -------------------------------------------------
        elif opcion == "2":
            destino = console.input("Filtrar por destino (enter para todos): ").strip()
            destino = destino if destino else None
            mostrar_hoteles(agencia, destino)

        # -------------------------------------------------
        #  Opción 3: Buscar habitaciones (R12)
        # -------------------------------------------------
        elif opcion == "3":
            console.print("\n[bold]Buscar habitaciones[/bold]")
            destino = console.input("Destino (enter para todos): ").strip() or None
            categoria = (
                console.input(
                    "Categoría (silver/gold/platinum, enter para todas): "
                ).strip()
                or None
            )
            cap_str = console.input(
                "Capacidad mínima (enter para cualquiera): "
            ).strip()
            capacidad = int(cap_str) if cap_str.isdigit() else None

            precio_str = console.input("Precio mínimo (enter para omitir): ").strip()
            precio_min = int(precio_str) if precio_str.isdigit() else None

            precio_str2 = console.input("Precio máximo (enter para omitir): ").strip()
            precio_max = int(precio_str2) if precio_str2.isdigit() else None

            calif_str = console.input(
                "Calificación mínima 1-5 (enter para omitir): "
            ).strip()
            calificacion_min = (
                float(calif_str) if calif_str and calif_str.isdigit() else None
            )

            fechas_str = console.input("¿Filtrar por fechas? (s/n): ").strip().lower()
            fecha_ini = fecha_fin = None
            if fechas_str == "s":
                ini = console.input("Fecha inicio (DD/MM, ej: 15/01): ").strip()
                fin = console.input("Fecha fin (DD/MM, ej: 20/01): ").strip()
                fecha_ini = parsear_fecha(ini)
                fecha_fin = parsear_fecha(fin)
                if fecha_ini is None or fecha_fin is None:
                    console.print("[red]Formato de fecha inválido. Use DD/MM.[/red]")
                    continue

            resultados = agencia.buscar_habitaciones(
                destino_nombre=destino,
                fecha_inicio=fecha_ini,
                fecha_fin=fecha_fin,
                categoria=categoria,
                capacidad_min=capacidad,
                precio_min=precio_min,
                precio_max=precio_max,
                calificacion_min=calificacion_min,
            )
            mostrar_busqueda(resultados, agencia)

        # -------------------------------------------------
        #  Opción 4: Registrar cliente (R11)
        # -------------------------------------------------
        elif opcion == "4":
            console.print("\n[bold]Registro de Cliente[/bold]")
            nombre = console.input("Nombre completo: ").strip()
            telefono = console.input("Teléfono: ").strip()
            email = console.input("Email: ").strip()
            direccion = console.input("Dirección: ").strip()

            if not all([nombre, telefono, email, direccion]):
                console.print("[red]Todos los campos son obligatorios.[/red]")
                continue

            cliente = agencia.registrar_cliente(nombre, telefono, email, direccion)
            if cliente is None:
                console.print("[red]✗ Ya existe un cliente con ese email.[/red]")
                continue
            console.print(f"\n[green]✓ Cliente registrado:[/green] {cliente}")

        # -------------------------------------------------
        #  Opción 5: Registrar hotel (R2)
        # -------------------------------------------------
        elif opcion == "5":
            console.print("\n[bold]Registro de Hotel[/bold]")

            # Mostrar destinos disponibles
            destinos_disp = list(agencia.destinos.keys())
            console.print(f"Destinos disponibles: {', '.join(sorted(destinos_disp))}")

            nombre = console.input("Nombre del hotel: ").strip()
            destino_nombre = console.input("Destino: ").strip()
            direccion = console.input("Dirección: ").strip()
            telefono = console.input("Teléfono: ").strip()
            email = console.input("Email: ").strip()
            descripcion = console.input("Descripción: ").strip()
            servicios_str = console.input("Servicios (separados por coma): ").strip()
            servicios = [s.strip() for s in servicios_str.split(",") if s.strip()]
            foto_url = console.input("URL foto (enter para omitir): ").strip() or None
            barrio = console.input("Barrio (enter para omitir): ").strip() or None
            codigo_postal = (
                console.input("Código postal (enter para omitir): ").strip() or None
            )

            if not all(
                [nombre, destino_nombre, direccion, telefono, email, descripcion]
            ):
                console.print("[red]Los campos obligatorios están incompletos.[/red]")
                continue

            hotel = agencia.registrar_hotel(
                nombre,
                destino_nombre,
                direccion,
                telefono,
                email,
                descripcion,
                servicios,
                foto_url=foto_url,
                barrio=barrio,
                codigo_postal=codigo_postal,
            )
            if hotel is None:
                console.print(f"[red]✗ Destino '{destino_nombre}' no encontrado.[/red]")
            else:
                # Luciana: "Las condiciones de pago y cancelación pueden
                #  variar de un hotel a otro"
                console.print("\n  Condiciones del hotel:")
                pago = (
                    console.input("  Condición de pago (anticipado/al_llegar): ")
                    .strip()
                    .lower()
                )
                if pago in ("anticipado", "al_llegar"):
                    hotel.condicion_pago = pago
                cancel = (
                    console.input(
                        "  Política de cancelación (flexible/moderada/estricta): "
                    )
                    .strip()
                    .lower()
                )
                if cancel in ("flexible", "moderada", "estricta"):
                    hotel.politica_cancelacion = cancel

                console.print(f"\n[green]✓ Hotel registrado:[/green] {hotel}")
                console.print(
                    f"  Pago: {hotel.condicion_pago} | Cancelación: {hotel.politica_cancelacion}"
                )

        # -------------------------------------------------
        #  Opción 6: Registrar habitación (R5)
        # -------------------------------------------------
        elif opcion == "6":
            console.print("\n[bold]Registro de Habitación[/bold]")

            # Mostrar hoteles disponibles
            if not agencia.hoteles:
                console.print("[yellow]No hay hoteles registrados.[/yellow]")
                continue

            for h in agencia.hoteles:
                console.print(f"  - {h.nombre} ({h.destino.nombre})")

            hotel_nombre = console.input("Nombre del hotel: ").strip()
            hotel = next((h for h in agencia.hoteles if h.nombre == hotel_nombre), None)
            if hotel is None:
                console.print(f"[red]✗ Hotel '{hotel_nombre}' no encontrado.[/red]")
                continue

            num_str = console.input("Número de habitación: ").strip()
            if not num_str.isdigit():
                console.print("[red]Número inválido.[/red]")
                continue

            descripcion = console.input("Descripción: ").strip()
            categoria = (
                console.input("Categoría (silver/gold/platinum): ").strip().lower()
            )
            if categoria not in ("silver", "gold", "platinum"):
                console.print(
                    "[red]Categoría inválida. Use silver, gold o platinum.[/red]"
                )
                continue

            cap_str = console.input("Capacidad: ").strip()
            if not cap_str.isdigit() or int(cap_str) < 1:
                console.print("[red]Capacidad inválida.[/red]")
                continue

            servicios_str = console.input("Servicios (separados por coma): ").strip()
            servicios = [s.strip() for s in servicios_str.split(",") if s.strip()]
            foto_url = console.input("URL foto (enter para omitir): ").strip() or None

            hab = Habitacion(
                int(num_str),
                descripcion,
                categoria,
                int(cap_str),
                servicios,
                foto_url=foto_url,
            )
            hotel.agregar_habitacion(hab)
            console.print(
                f"\n[green]✓ Habitación {num_str} registrada en {hotel_nombre}.[/green]"
            )

        # -------------------------------------------------
        #  Opción 7: Desactivar hotel/habitación (R3, R6)
        # -------------------------------------------------
        elif opcion == "7":
            console.print("\n[bold]Desactivar[/bold]")
            console.print("  [cyan]a[/cyan] - Desactivar hotel")
            console.print("  [cyan]b[/cyan] - Desactivar habitación")
            sub = console.input("Opción: ").strip().lower()

            if sub == "a":
                for h in agencia.hoteles:
                    estado = (
                        "[green]activo[/green]" if h.activo else "[red]inactivo[/red]"
                    )
                    console.print(f"  - {h.nombre} ({h.destino.nombre}) [{estado}]")
                hotel_nombre = console.input("Nombre del hotel: ").strip()
                hotel = next(
                    (h for h in agencia.hoteles if h.nombre == hotel_nombre), None
                )
                if hotel is None:
                    console.print(f"[red]✗ Hotel '{hotel_nombre}' no encontrado.[/red]")
                    continue
                hotel.activo = not hotel.activo
                estado = "activado" if hotel.activo else "desactivado"
                console.print(f"[green]✓ Hotel {estado}.[/green]")

            elif sub == "b":
                hotel_nombre = console.input("Nombre del hotel: ").strip()
                hotel = next(
                    (h for h in agencia.hoteles if h.nombre == hotel_nombre), None
                )
                if hotel is None:
                    console.print(f"[red]✗ Hotel '{hotel_nombre}' no encontrado.[/red]")
                    continue
                for hab in hotel.habitaciones:
                    estado = (
                        "[green]activa[/green]" if hab.activa else "[red]inactiva[/red]"
                    )
                    console.print(
                        f"  - Hab. {hab.numero}: {hab.descripcion} [{estado}]"
                    )
                num_str = console.input("Número de habitación: ").strip()
                if not num_str.isdigit():
                    console.print("[red]Número inválido.[/red]")
                    continue
                hab = next(
                    (h for h in hotel.habitaciones if h.numero == int(num_str)), None
                )
                if hab is None:
                    console.print(f"[red]✗ Habitación {num_str} no encontrada.[/red]")
                    continue
                hab.activa = not hab.activa
                estado = "activada" if hab.activa else "desactivada"
                console.print(f"[green]✓ Habitación {estado}.[/green]")

            else:
                console.print("[red]Opción no válida. Use 'a' o 'b'.[/red]")

        # -------------------------------------------------
        #  Opción 8: Realizar reserva (R14, R10)
        # -------------------------------------------------
        elif opcion == "8":
            console.print("\n[bold]Realizar Reserva[/bold]")
            email = console.input("Email del cliente: ").strip()
            hotel_nombre = console.input("Nombre del hotel: ").strip()

            # Validar hotel ANTES de pedir más datos
            hotel = next((h for h in agencia.hoteles if h.nombre == hotel_nombre), None)
            if hotel is None:
                console.print(f"[red]✗ Hotel '{hotel_nombre}' no encontrado.[/red]")
                continue

            hab_num_str = console.input("Número de habitación: ").strip()

            if not hab_num_str.isdigit():
                console.print("[red]Número de habitación inválido.[/red]")
                continue

            ini = console.input("Fecha inicio (DD/MM, ej: 15/01): ").strip()
            fin = console.input("Fecha fin (DD/MM, ej: 20/01): ").strip()

            fecha_ini = parsear_fecha(ini)
            fecha_fin = parsear_fecha(fin)
            if fecha_ini is None or fecha_fin is None:
                console.print("[red]Formato de fecha inválido. Use DD/MM.[/red]")
                continue

            cap_str = console.input("Cantidad de huéspedes: ").strip()
            cant_huespedes = int(cap_str) if cap_str.isdigit() else 1

            # Pago: la reserva siempre arranca como PENDIENTE
            pagar_ahora = False
            if hotel.condicion_pago == "anticipado":
                console.print("[yellow]⚠ Este hotel requiere pago anticipado.[/yellow]")
            resp = console.input("¿Pagar ahora? (s/n): ").strip().lower()
            pagar_ahora = resp == "s"

            resultado = agencia.realizar_reserva(
                email,
                hotel_nombre,
                int(hab_num_str),
                fecha_ini,
                fecha_fin,
                cant_huespedes,
                pagar_ahora,
            )

            if isinstance(resultado, str):
                console.print(f"[red]✗ Error: {resultado}[/red]")
            else:
                console.print(f"\n[green]✓ Reserva realizada![/green]")
                console.print(f"  {resultado}")
                console.print(f"  [yellow]Estado: {resultado.estado.upper()}[/yellow]")
                if resultado.estado == "pendiente":
                    console.print("  ℹ Use opción 10 cuando desee pagar esta reserva.")

        # -------------------------------------------------
        #  Opción 9: Ver reservas
        # -------------------------------------------------
        elif opcion == "9":
            email = console.input("Email del cliente: ").strip()
            reservas = agencia.obtener_reservas_cliente(email)
            mostrar_reservas(reservas)

        # -------------------------------------------------
        #  Opción 10: Pagar reserva (R15)
        #  Luciana: "Una vez que el pago se confirma,
        #   la reserva queda formalizada."
        # -------------------------------------------------
        elif opcion == "10":
            email = console.input("Email del cliente: ").strip()
            reservas = agencia.obtener_reservas_cliente(email)
            # Mostrar solo las pendientes
            pendientes = [r for r in reservas if r.estado == "pendiente"]
            if not pendientes:
                console.print("[yellow]No tiene reservas pendientes de pago.[/yellow]")
                continue
            mostrar_reservas(pendientes)

            num_str = console.input("Número de reserva a pagar: ").strip()
            if (
                not num_str.isdigit()
                or int(num_str) < 1
                or int(num_str) > len(pendientes)
            ):
                console.print("[red]Número de reserva inválido.[/red]")
                continue

            reserva = pendientes[int(num_str) - 1]
            resultado = agencia.pagar_reserva(reserva)
            if resultado["exito"]:
                console.print(f"[green]✓ {resultado['mensaje']}[/green]")
                # Mostrar política de pago del hotel
                condicion = reserva.habitacion.hotel.condicion_pago
                if condicion == "anticipado":
                    console.print("  [dim](Pago anticipado - reserva confirmada)[/dim]")
                else:
                    console.print("  [dim](Pago al llegar - reserva confirmada)[/dim]")
            else:
                console.print(f"[red]✗ {resultado['mensaje']}[/red]")

        # -------------------------------------------------
        #  Opción 11: Cancelar reserva (R16)
        # -------------------------------------------------
        elif opcion == "11":
            email = console.input("Email del cliente: ").strip()
            reservas = agencia.obtener_reservas_cliente(email)
            mostrar_reservas(reservas)

            if not reservas:
                continue

            num_str = console.input("Número de reserva a cancelar: ").strip()
            if (
                not num_str.isdigit()
                or int(num_str) < 1
                or int(num_str) > len(reservas)
            ):
                console.print("[red]Número de reserva inválido.[/red]")
                continue

            reserva = reservas[int(num_str) - 1]
            resultado = agencia.cancelar_reserva(reserva)
            if resultado["exito"]:
                console.print(f"[green]✓ {resultado['mensaje']}[/green]")
                if resultado["reembolso"] > 0:
                    console.print(f"  Reembolso: ${resultado['reembolso']}")
            else:
                console.print(f"[red]✗ {resultado['mensaje']}[/red]")

        # -------------------------------------------------
        #  Opción 12: Calificar (R17, R18)
        # -------------------------------------------------
        elif opcion == "12":
            console.print("\n[bold]Calificar Estancia[/bold]")
            email = console.input("Email del cliente: ").strip()
            hotel_nombre = console.input("Nombre del hotel: ").strip()
            hab_num_str = console.input("Número de habitación: ").strip()
            punt_str = console.input("Puntuación (1-5): ").strip()
            comentario = console.input("Comentario (opcional): ").strip()

            if not hab_num_str.isdigit() or not punt_str.isdigit():
                console.print("[red]Datos inválidos.[/red]")
                continue

            puntuacion = int(punt_str)
            if puntuacion < 1 or puntuacion > 5:
                console.print("[red]La puntuación debe ser entre 1 y 5.[/red]")
                continue

            resultado = agencia.calificar_estancia(
                email, hotel_nombre, int(hab_num_str), puntuacion, comentario
            )

            if isinstance(resultado, str):
                console.print(f"[red]✗ Error: {resultado}[/red]")
            else:
                console.print(
                    f"\n[green]✓ Calificación registrada:[/green] {resultado}"
                )

        # -------------------------------------------------
        #  Opción 0: Salir
        # -------------------------------------------------
        elif opcion == "0":
            console.print("\n[cyan]¡Gracias por usar la Agencia de Viajes! ✈[/cyan]")
            break

        else:
            console.print("[red]Opción no válida. Intente de nuevo.[/red]")

        console.print()


# ============================================================
#  PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    menu_principal()
