from datos import TARIFAS
from rich.console import Console
from rich.table import Table

console = Console()


# Utilidad de fecha (duplicada de app.py para que __str__ pueda formatear)
DIAS_POR_MES = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def formato_fecha(dia_del_ano):
    """Convierte día del año (int) a 'DD/MM'."""
    restante = dia_del_ano
    for mes in range(1, 13):
        if restante <= DIAS_POR_MES[mes]:
            return f"{restante:02d}/{mes:02d}"
        restante -= DIAS_POR_MES[mes]
    return str(dia_del_ano)


# ============================================================
#  CLASE: Destino
#  Fuente: tabla de tarifas del README
#  Es la representación de una fila de la tabla de tarifas.
# ============================================================


class Destino:
    """Representa un destino turístico con sus tarifas."""

    def __init__(
        self, nombre, tarifa_pasaje, precio_silver, precio_gold, precio_platinum
    ):
        self.nombre = nombre
        self.tarifa_pasaje = tarifa_pasaje
        self.precio_silver = precio_silver
        self.precio_gold = precio_gold
        self.precio_platinum = precio_platinum

    def obtener_precio(self, categoria):
        """Devuelve el precio según la categoría de habitación."""
        precios = {
            "silver": self.precio_silver,
            "gold": self.precio_gold,
            "platinum": self.precio_platinum,
        }
        cat_lower = categoria.lower()
        if cat_lower not in precios:
            raise ValueError(f"Categoría desconocida: {categoria}")
        return precios[cat_lower]

    def __str__(self):
        return self.nombre


# ============================================================
#  CLASE: Calificacion
#  Fuente: entrevista - Luciana dice:
#  "Las calificaciones y los comentarios son fundamentales.
#   Después de cada estancia, invitamos a los clientes a
#   evaluar su experiencia y dejar sus comentarios."
# ============================================================


class Calificacion:
    """Una calificación (1-5) con comentario opcional."""

    def __init__(self, puntuacion, comentario=""):
        self.puntuacion = max(1, min(5, puntuacion))  # clamp to 1-5
        self.comentario = comentario

    def __str__(self):
        estrellas = "★" * self.puntuacion + "☆" * (5 - self.puntuacion)
        return f"{estrellas} - {self.comentario}"


# ============================================================
#  CLASE: Habitacion
#  Fuente: entrevista - Luciana dice:
#  "Cada habitación tiene un registro detallado con su tipo,
#   descripción, precio, servicios incluidos, capacidad y
#   hasta fotos."
#  La categoría (silver/gold/platinum) viene de la tabla de tarifas.
# ============================================================


class Habitacion:
    """Una habitación dentro de un hotel."""

    def __init__(self, numero, descripcion, categoria, capacidad, servicios=None):
        self.numero = numero
        self.descripcion = descripcion
        self.categoria = categoria.lower()  # silver, gold, platinum
        self.capacidad = capacidad
        self.servicios = servicios or []
        self.activa = True
        self.hotel = None  # se asigna cuando se agrega a un Hotel
        self.reservas = []  # lista de objetos Reserva
        self.calificaciones = []  # lista de objetos Calificacion

    def esta_disponible(self, fecha_inicio, fecha_fin):
        """
        Verifica si la habitación está disponible en el rango de fechas.
        Una habitación NO está disponible si:
          - está inactiva (mantenimiento, remodelación, etc.)
          - ya tiene una reserva que se superpone con las fechas
        """
        if not self.activa:
            return False
        for reserva in self.reservas:
            # Dos rangos se superponen si:
            #   inicio1 < fin2 AND inicio2 < fin1
            if fecha_inicio < reserva.fecha_fin and reserva.fecha_inicio < fecha_fin:
                return False
        return True

    def calificacion_promedio(self):
        """Calcula el promedio de calificaciones de esta habitación."""
        if not self.calificaciones:
            return 0
        total = sum(c.puntuacion for c in self.calificaciones)
        return round(total / len(self.calificaciones), 1)


# ============================================================
#  CLASE: Hotel
#  Fuente: entrevista - Luciana dice:
#  "Para registrar un nuevo hotel, necesitamos información
#   básica como el nombre, dirección, teléfono y correo
#   electrónico. Además, consideramos muy importante la
#   ubicación geográfica... una descripción detallada de
#   los servicios como restaurante, piscina, gimnasio"
# ============================================================


class Hotel:
    """Un hotel perteneciente a un destino."""

    def __init__(
        self, nombre, destino, direccion, telefono, email, descripcion, servicios=None
    ):
        self.nombre = nombre
        self.destino = destino  # objeto Destino
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.descripcion = descripcion
        self.servicios = servicios or []
        self.activo = True
        self.habitaciones = []  # lista de objetos Habitacion
        self.calificaciones = []  # lista de objetos Calificacion

        # NUEVO: condiciones de pago (R12)
        # Luciana: "algunos hoteles requieren el pago completo por
        #  adelantado, mientras que otros permiten pagar al llegar"
        self.condicion_pago = "anticipado"  # "anticipado" o "al_llegar"

        # NUEVO: política de cancelación (R13)
        # Luciana: "Los reembolsos dependen de la política de
        #  cancelación de cada hotel"
        self.politica_cancelacion = "moderada"  # "flexible", "moderada", "estricta"

        # NUEVO: temporadas específicas del hotel
        # Luciana: "Cada hotel tiene su propio calendario de temporadas"
        self.temporadas = []  # lista de objetos Temporada

        # NUEVO: ofertas/promociones del hotel
        # Luciana: "Muchos hoteles tienen promociones por temporada"
        self.ofertas = []  # lista de objetos Oferta

    def esta_activo(self):
        return self.activo

    def calificacion_promedio(self):
        """Calcula el promedio general del hotel."""
        if not self.calificaciones:
            return 0
        total = sum(c.puntuacion for c in self.calificaciones)
        return round(total / len(self.calificaciones), 1)

    def agregar_habitacion(self, habitacion):
        """Agrega una habitación a este hotel y establece la referencia bidireccional."""
        habitacion.hotel = self
        self.habitaciones.append(habitacion)

    def __str__(self):
        return f"{self.nombre} ({self.destino.nombre})"


# ============================================================
#  CLASE: Reserva
#  Fuente: entrevista - Luciana dice:
#  "El cliente confirma su selección y procede a realizar
#   el pago. Una vez que el pago se confirma, la reserva
#   queda formalizada."
#  Fórmula de costo viene de la tabla de tarifas (R11):
#  costo_total = tarifa_pasaje + (precio_categoria × noches)
# ============================================================


class Reserva:
    """Una reserva de habitación hecha por un cliente."""

    def __init__(
        self,
        fecha_inicio,
        fecha_fin,
        cliente,
        habitacion,
        costo_total,
        cant_huespedes=1,
    ):
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.cliente = cliente  # objeto Cliente
        self.habitacion = habitacion  # objeto Habitacion
        self.costo_total = costo_total
        self.cant_huespedes = cant_huespedes
        self.estado = "pendiente"  # pendiente, pagada, cancelada

    def cancelar(self):
        """Cancela la reserva y la quita del calendario de la habitación."""
        if self.estado == "cancelada":
            return False
        self.estado = "cancelada"
        if self in self.habitacion.reservas:
            self.habitacion.reservas.remove(self)
        if self in self.cliente.reservas:
            self.cliente.reservas.remove(self)
        return True

    def __str__(self):
        ini = formato_fecha(self.fecha_inicio)
        fin = formato_fecha(self.fecha_fin)
        return (
            f"Reserva: {self.cliente.nombre} -> "
            f"{self.habitacion.hotel.nombre} hab.{self.habitacion.numero} "
            f"({ini} a {fin}) - "
            f"${self.costo_total} [{self.estado}]"
        )


# ============================================================
#  CLASE: Cliente
#  Fuente: entrevista - Luciana dice:
#  "Al registrarse, solicitamos al cliente su nombre completo,
#   número de teléfono, correo electrónico y dirección"
# ============================================================


class Cliente:
    """Un cliente registrado en la agencia."""

    def __init__(self, nombre, telefono, email, direccion):
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.reservas = []  # lista de objetos Reserva

    def __str__(self):
        return f"{self.nombre} ({self.email})"


# ============================================================
#  CLASE: Temporada
#  Fuente: entrevista - Luciana dice:
#  "Cada hotel tiene su propio calendario de temporadas, pero
#   también existe un calendario regional que la mayoría de
#   los hoteles sigue. Este calendario nos ayuda a establecer
#   los precios y las promociones para cada temporada."
#  Una temporada tiene un rango de fechas y un multiplicador
#  de precios (alta = más caro, baja = más barato).
# ============================================================


class Temporada:
    """Una temporada con rango de fechas y multiplicador de precios."""

    def __init__(self, nombre, fecha_inicio, fecha_fin, multiplicador):
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.multiplicador = multiplicador  # ej: 1.5 = +50%, 0.8 = -20%

    def contiene(self, fecha):
        """Verifica si una fecha cae dentro de esta temporada."""
        return self.fecha_inicio <= fecha <= self.fecha_fin

    def __str__(self):
        tipo = "alta" if self.multiplicador > 1.0 else "baja"
        porcentaje = int((self.multiplicador - 1) * 100)
        signo = "+" if porcentaje > 0 else ""
        return f"{self.nombre} ({tipo}, {signo}{porcentaje}%)"


# ============================================================
#  CLASE: Oferta
#  Fuente: entrevista - Luciana dice:
#  "Las ofertas son fundamentales. Muchos hoteles tienen
#   promociones por temporada, como descuentos en temporada
#   baja o paquetes especiales."
#  Una oferta es un descuento aplicable a un hotel en un
#  rango de fechas específico.
# ============================================================


class Oferta:
    """Una promoción o descuento para un hotel en un rango de fechas."""

    def __init__(self, descripcion, fecha_inicio, fecha_fin, descuento):
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.descuento = descuento  # porcentaje: 0.10 = 10% descuento

    def esta_vigente(self, fecha):
        """Verifica si la oferta aplica en una fecha dada."""
        return self.fecha_inicio <= fecha <= self.fecha_fin

    def __str__(self):
        porcentaje = int(self.descuento * 100)
        return (
            f"{self.descripcion} (-{porcentaje}%, {self.fecha_inicio}-{self.fecha_fin})"
        )
