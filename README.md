# Sistema de Agencia de Viajes

![commits](https://badgen.net/github/commits/clubdecomputacion/lpa1-taller-requerimientos?icon=github) 
![last_commit](https://img.shields.io/github/last-commit/clubdecomputacion/lpa1-taller-requerimientos)

- ver [badgen](https://badgen.net/) o [shields](https://shields.io/) para otros tipos de _badges_

## Autor

- [@estudiante](https://www.github.com/estudiante)

## Descripción del Proyecto

Sistema de consola para una **agencia de viajes** que permite gestionar destinos turísticos, hoteles, habitaciones, clientes y reservas. Los clientes pueden buscar paquetes de viaje (pasaje + hospedaje) por destino, categoría y fechas. El sistema calcula el costo total considerando tarifas predefinidas, temporadas, cantidad de huéspedes y ofertas vigentes. Incluye gestión de pagos (anticipado o al llegar), cancelaciones con políticas diferenciadas por hotel (flexible/moderada/estricta), y un sistema de calificaciones por habitación y hotel.

## Documentación

Revisar la documentación en [`./docs`](./docs)

### Requerimientos Funcionales

> **Fuente:** 🏨 = Entrevista | 📊 = Tabla de tarifas
> Cada requerimiento tiene la cita de la entrevista que lo justifica.

#### Gestión de Destinos
- **R1** 📊: El sistema debe cargar los destinos desde la tabla de tarifas, con su nombre, precio del pasaje y precios por categoría de habitación (Silver, Gold, Platinum).

#### Gestión de Hoteles
- **R2** 🏨: El sistema debe permitir registrar un hotel con nombre, dirección, teléfono, email, ubicación geográfica, descripción y servicios ofrecidos.
  > *Luciana: "necesitamos información básica como el nombre, dirección, teléfono y correo electrónico. Además, consideramos muy importante la ubicación geográfica... una descripción detallada de los servicios como restaurante, piscina, gimnasio"*
- **R3** 🏨: El sistema debe permitir activar e inactivar hoteles. Un hotel inactivo no aparece en búsquedas ni puede recibir reservas.
  > *Felipe: "Un hotel puede estar cerrado por reformas o por alguna otra razón." Luciana: "Solo los hoteles y habitaciones activos pueden ser considerados para las reservas."*
- **R4** 🏨: El sistema debe permitir crear ofertas y promociones por hotel, con un porcentaje de descuento aplicable en un rango de fechas.
  > *Luciana: "Muchos hoteles tienen promociones por temporada, como descuentos en temporada baja o paquetes especiales."*

#### Gestión de Habitaciones
- **R5** 🏨: El sistema debe permitir registrar habitaciones en un hotel con número, descripción, categoría (Silver/Gold/Platinum), capacidad máxima y servicios incluidos.
  > *Luciana: "Cada habitación tiene un registro detallado con su tipo, descripción, precio, servicios incluidos, capacidad y hasta fotos."*
- **R6** 🏨: El sistema debe permitir activar e inactivar habitaciones. Una habitación inactiva no está disponible para reservas.
  > *Luciana: "Una habitación puede estar inactiva por mantenimiento, remodelación, o incluso por desinfección después de una ocupación. Mientras una habitación está en este estado, no puede ser reservada."*
- **R7** 🏨: El sistema debe mantener un calendario de disponibilidad por habitación, mostrando las fechas en las que está reservada y las que están disponibles.
  > *Luciana: "Cada habitación tiene un calendario detallado que indica las fechas en las que está reservada y las que están disponibles."*

#### Temporadas y Precios
- **R8** 🏨: El sistema debe permitir definir temporadas (regionales y por hotel) con un multiplicador de precios. El precio de una reserva se ajusta según la temporada en la que cae.
  > *Luciana: "Cada hotel tiene su propio calendario de temporadas, pero también existe un calendario regional que la mayoría de los hoteles sigue. Este calendario nos ayuda a establecer los precios y las promociones para cada temporada."*
- **R9** 🏨: El precio de una reserva debe variar según la cantidad de huéspedes, sin exceder la capacidad máxima de la habitación.
  > *Luciana: "El precio puede cambiar dependiendo de la cantidad de personas que se alojen en la habitación, siempre y cuando no se exceda la capacidad máxima."*
- **R10** 📊: El sistema debe calcular el costo total de una reserva considerando: tarifa del pasaje, precio por categoría, multiplicador de temporada, ajuste por huéspedes y descuentos por ofertas vigentes.
  > *Fórmula: costo = (pasaje + precio_categoría × noches) × temporada × huéspedes × (1 - descuento)*

#### Gestión de Clientes
- **R11** 🏨: El sistema debe permitir registrar clientes con nombre completo, número de teléfono, email y dirección.
  > *Luciana: "Al registrarse, solicitamos al cliente su nombre completo, número de teléfono, correo electrónico y dirección."*

#### Búsqueda
- **R12** 🏨: El sistema debe permitir buscar habitaciones disponibles combinando criterios: destino, fechas, categoría y capacidad.
  > *Felipe: "El cliente puede buscar habitaciones por fecha, ubicación, calificación o precio. Incluso puede combinar varios criterios para afinar su búsqueda."*
- **R13** 🏨: Al seleccionar una habitación, el sistema debe mostrar su descripción, características, servicios incluidos, calificación y comentarios.
  > *Luciana: "Puede ver una descripción detallada de la habitación, incluyendo sus características, servicios incluidos, fotos y, por supuesto, la calificación y los comentarios de otros huéspedes."*

#### Reservas y Pagos
- **R14** 🏨: El sistema debe permitir realizar una reserva seleccionando un destino, una habitación disponible, las fechas y la cantidad de huéspedes. La reserva arranca en estado pendiente.
- **R15** 🏨📊: El sistema debe permitir pagar una reserva pendiente, cambiando su estado a pagada. Las condiciones de pago varían por hotel (pago anticipado o al llegar).
  > *Luciana: "El cliente confirma su selección y procede a realizar el pago. Una vez que el pago se confirma, la reserva queda formalizada." / "Algunos hoteles requieren el pago completo por adelantado, mientras que otros permiten pagar al llegar."*
- **R16** 🏨: El sistema debe procesar cancelaciones de reservas aplicando la política de cancelación del hotel (flexible: reembolso completo, moderada: 50%, estricta: sin reembolso).
  > *Luciana: "Los reembolsos dependen de la política de cancelación de cada hotel. Algunos hoteles cobran una penalidad por cancelación, mientras que otros ofrecen reembolsos completos."*

#### Calificaciones y Comentarios
- **R17** 🏨: El sistema debe permitir a los clientes dejar calificaciones (1-5) y comentarios sobre su estancia, asociados a una habitación específica. Solo se puede calificar una reserva pagada.
  > *Luciana: "Después de cada estancia, invitamos a los clientes a evaluar su experiencia y dejar sus comentarios. Estos comentarios se asocian a cada habitación."*
- **R18** 🏨: El sistema debe calcular y mostrar la calificación promedio de cada habitación y del hotel en general.
  > *Luciana: "Calculamos una calificación promedio para cada habitación y una calificación general para todo el hotel."*

### Casos de Uso

> Los requerimientos (arriba) describen QUÉ hace el sistema.
> Los casos de uso (abajo) describen CÓMO el usuario interactúa con él.
> Fuente: la entrevista describe estos flujos de uso.

#### Caso de Uso 1: Buscar y Reservar una Habitación
> *Felipe: "El cliente puede buscar habitaciones por fecha, ubicación, calificación o precio."
> Luciana: "Una vez que el cliente encuentra una habitación que le interesa, puede hacer clic en ella para ver más detalles."
> Luciana: "El cliente confirma su selección y procede a realizar el pago. Una vez que el pago se confirma, la reserva queda formalizada."*

| Paso | Acción | Requerimiento |
|------|--------|---------------|
| 1 | El cliente busca habitaciones indicando destino, fechas, categoría y/o capacidad | R12 |
| 2 | El sistema muestra las habitaciones disponibles con sus datos | R12 |
| 3 | El cliente selecciona una habitación para ver sus detalles | R13 |
| 4 | El sistema muestra descripción, servicios, precio, calificaciones y comentarios | R13 |
| 5 | El cliente confirma y hace la reserva indicando fechas y cantidad de huéspedes | R14 |
| 6 | El sistema crea la reserva en estado PENDIENTE | R14 |
| 7 | El cliente paga la reserva | R15 |
| 8 | El sistema cambia el estado a PAGADA | R15 |

**Flujo alternativo 5a:** El sistema muestra una advertencia si el hotel requiere pago anticipado. El usuario elige si pagar ahora o después (opción 10).

#### Caso de Uso 2: Cancelar una Reserva
> *Luciana: "Los reembolsos dependen de la política de cancelación de cada hotel. Algunos hoteles cobran una penalidad por cancelación, mientras que otros ofrecen reembolsos completos."*

| Paso | Acción | Requerimiento |
|------|--------|---------------|
| 1 | El cliente ve sus reservas activas | R14 |
| 2 | El cliente selecciona la reserva a cancelar | R16 |
| 3 | El sistema aplica la política de cancelación del hotel y muestra el reembolso | R16 |
| 4 | El sistema libera la habitación en el calendario | R7 |

**Políticas de reembolso:**
- Flexible: 100% de reembolso
- Moderada: 50% de reembolso
- Estricta: sin reembolso

#### Caso de Uso 3: Calificar una Estancia
> *Luciana: "Después de cada estancia, invitamos a los clientes a evaluar su experiencia y dejar sus comentarios. Estos comentarios se asocian a cada habitación."*

| Paso | Acción | Requerimiento |
|------|--------|---------------|
| 1 | El cliente selecciona una reserva pagada completada | R17 |
| 2 | El cliente da una puntuación (1-5) y un comentario | R17 |
| 3 | El sistema guarda la calificación asociada a la habitación y al hotel | R17 |
| 4 | El sistema recalcula el promedio de la habitación y del hotel | R18 |

**Regla:** Solo se puede calificar una reserva con estado PAGADA.

#### Caso de Uso 4: Registrar un Nuevo Hotel
> *Luciana: "Para registrar un nuevo hotel, necesitamos información básica como el nombre, dirección, teléfono y correo electrónico. Además, consideramos muy importante la ubicación geográfica, una descripción detallada de los servicios."*

| Paso | Acción | Requerimiento |
|------|--------|---------------|
| 1 | El administrador ingresa los datos del hotel (nombre, destino, dirección, etc.) | R2 |
| 2 | El sistema valida que el destino existe en la tabla de tarifas | R1 |
| 3 | El sistema registra el hotel como ACTIVO | R2, R3 |
| 4 | El administrador agrega habitaciones al hotel (número, categoría, capacidad, servicios) | R5 |

#### Caso de Uso 5: Gestionar Temporadas y Ofertas
> *Luciana: "Cada hotel tiene su propio calendario de temporadas, pero también existe un calendario regional."
> Luciana: "Muchos hoteles tienen promociones por temporada, como descuentos en temporada baja."*

| Paso | Acción | Requerimiento |
|------|--------|---------------|
| 1 | Se definen temporadas regionales con rango de fechas y multiplicador de precios | R8 |
| 2 | Se definen temporadas específicas por hotel (opcional, sobreescribe la regional) | R8 |
| 3 | Se crean ofertas con porcentaje de descuento y rango de fechas | R4 |
| 4 | Al buscar/reservar, el sistema aplica automáticamente el multiplicador y descuento vigente | R10 |

#### Caso de Uso 6: Desactivar Hotel o Habitación
> *Felipe: "Un hotel puede estar cerrado por reformas o por alguna otra razón."
> Luciana: "Una habitación puede estar inactiva por mantenimiento, remodelación, o incluso por desinfección."*

| Paso | Acción | Requerimiento |
|------|--------|---------------|
| 1 | El administrador selecciona un hotel o habitación | R3 / R6 |
| 2 | El sistema cambia el estado a INACTIVO | R3 / R6 |
| 3 | El hotel/habitación inactiva deja de aparecer en búsquedas | R3 / R6 |
| 4 | Las reservas existentes de esa habitación no se afectan | R7 |

#### Relación Casos de Uso → Requerimientos

```
Caso de Uso 1 (Reservar)    → R1, R10, R12, R13, R14, R15
Caso de Uso 2 (Cancelar)    → R7, R16
Caso de Uso 3 (Calificar)   → R17, R18
Caso de Uso 4 (Registrar)   → R1, R2, R3, R5
Caso de Uso 5 (Temporadas)  → R4, R8, R9, R10
Caso de Uso 6 (Desactivar)  → R3, R6, R7
```

### Diseño

> **Sobre el diagrama:** El README tiene una versión simplificada.
> La versión completa con todos los atributos está en [`./docs/diagrama_clases.txt`](./docs/diagrama_clases.txt).
> Esto es una buena práctica: en el README ponés lo esencial, en docs el detalle.

```
   📊 de la tabla de tarifas              🏨 de la entrevista

┌───────────────────────┐
│       Destino         │
│  nombre               │           ┌───────────────────────┐
│  tarifa_pasaje        │ 1      *  │        Hotel          │
│  precio_silver        ├───────────┤  nombre, direccion    │
│  precio_gold          │           │  telefono, email      │
│  precio_platinum      │           │  descripcion          │
└───────────────────────┘           │  servicios, activo    │
                                    │  condicion_pago       │
┌───────────────────────┐           │  politica_cancelacion │
│      Temporada        │           └───────────┬───────────┘
│  nombre               │                       │ 1
│  fecha_inicio         │ *                     │
│  fecha_fin            ├──────┐                │ *
│  multiplicador        │      │    ┌───────────┴───────────┐
└───────────────────────┘      │    │      Habitacion       │
                               │    │  numero, descripcion  │
┌───────────────────────┐      │    │  categoria (S/G/P)    │
│        Oferta         │      │    │  capacidad, servicios │
│  descripcion          │ *    │    │  activa               │
│  fecha_inicio         ├──────┘    └───────────┬───────────┘
│  fecha_fin            │                       │
│  descuento            │                       │
└───────────────────────┘                       │

┌───────────────────────┐                       │
│       Cliente         │ 1         ┌───────────┴───────────┐
│  nombre               │     *     │      Reserva          │
│  telefono             ├───────────┤  fecha_inicio         │
│  email                │           │  fecha_fin            │
│  direccion            │           │  cant_huespedes       │
└───────────┬───────────┘           │  costo_total          │
            │                       │  estado               │
            │ 1                     └───────────────────────┘
            │ *
            └───────────────────────────┘

                                    ┌───────────────────────┐
                                    │    Calificacion       │
                                    │  puntuacion (1-5)     │
                                    │  comentario           │
                                    │  (asociada a hotel o  │
                                    │   habitacion)         │
                                    └───────────────────────┘
```

**Fórmula de costo (R10):**
```
costo = (pasaje + precio_categoría × noches) × mult_temporada × mult_huéspedes × (1 - descuento)
```


### Tárifas

|destino|pasajes|silver|gold|platinum|
|:---|---:|---:|---:|---:|
|Aruba|418|134|167|191|
|Bahamas|423|112|183|202|
|Cancún|350|105|142|187|
|Hawaii|858|210|247|291|
|Jamaica|380|115|134|161|
|Madrid|496|190|230|270|
|Miami|334|122|151|183|
|Moscu|634|131|153|167|
|NewYork|495|104|112|210|
|Panamá|315|119|138|175|
|Paris|512|210|260|290|
|Rome|478|184|220|250|
|Seul|967|205|245|265|
|Sidney|1045|170|199|230|
|Taipei|912|220|245|298|
|Tokio|989|189|231|255|

## Instalación

1. Clonar el proyecto

    ```bash
    git clone https://github.com/clubdecomputacion/lpa1-taller-requerimientos.git
    ```

2. Crear y activar entorno virtual

    ```bash
    cd lpa1-taller-requerimientos
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Instalar librerías y dependencias

    ```bash
    pip install -r requirements.txt
    ```
    
## Ejecución

1. Ejecutar el proyecto

    ```bash
    python3 app.py
    ```

