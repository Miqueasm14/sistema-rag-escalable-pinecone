---
categoria: fechas-y-tiempo
modulo: datetime
---

# datetime: fechas, horas y duraciones

El módulo `datetime` provee clases para representar fechas, horas y diferencias de tiempo, y para convertirlas a texto y desde texto.

## Clases principales

- `date`: una fecha (año, mes, día), sin hora.
- `time`: una hora del día, sin fecha.
- `datetime`: fecha y hora juntas. Es la clase más usada.
- `timedelta`: una duración o diferencia entre dos momentos.
- `timezone`: una zona horaria con desplazamiento fijo respecto de UTC.

`date.today()` devuelve la fecha actual y `datetime.now()` la fecha y hora actuales.

## Objetos naive y aware

Un `datetime` es **naive** cuando no tiene zona horaria asociada (`tzinfo` es `None`) y **aware** cuando sí la tiene. `datetime.now()` sin argumentos devuelve un objeto naive en la hora local de la máquina, lo que genera ambigüedades si el programa corre en servidores de distintos países.

Comparar o restar un datetime naive con uno aware lanza `TypeError`. La recomendación general es trabajar internamente con datetimes aware en UTC y convertir a la hora local solo para mostrar.

## datetime.utcnow está deprecado

Durante años se usó `datetime.utcnow()` para obtener la hora UTC, pero devuelve un objeto **naive**: tiene la hora de UTC sin indicar que está en UTC, lo que provoca errores sutiles al compararlo o convertirlo. Por eso **Python 3.12 deprecó `datetime.utcnow()`** (y también `datetime.utcfromtimestamp()`). El reemplazo es:

```python
from datetime import datetime, timezone

ahora_utc = datetime.now(timezone.utc)   # aware, en UTC
```

Del mismo modo, para timestamps se usa `datetime.fromtimestamp(ts, tz=timezone.utc)`.

## Zonas horarias con zoneinfo

`timezone` solo sirve para desplazamientos fijos. Para zonas reales con horario de verano se usa el módulo `zoneinfo` (Python 3.9+):

```python
from zoneinfo import ZoneInfo

buenos_aires = ZoneInfo("America/Argentina/Buenos_Aires")
local = ahora_utc.astimezone(buenos_aires)
```

`astimezone()` convierte un datetime aware a otra zona sin cambiar el instante que representa. En Windows, `zoneinfo` puede necesitar el paquete `tzdata` instalado con pip, porque el sistema operativo no trae la base de datos de zonas IANA.

## Aritmética con timedelta

`timedelta` representa una duración y acepta `days`, `seconds`, `microseconds`, `milliseconds`, `minutes`, `hours` y `weeks`:

```python
from datetime import timedelta

vencimiento = datetime.now(timezone.utc) + timedelta(days=30)
hace_una_semana = date.today() - timedelta(weeks=1)
```

Restar dos datetimes devuelve un `timedelta`, y `total_seconds()` lo expresa en segundos. `timedelta` no admite meses ni años, porque su duración varía: sumar "un mes" requiere la librería externa `dateutil` (`relativedelta`) o calcularlo a mano con `replace()`.

## Convertir a texto y desde texto

- `strftime(formato)` convierte un datetime a texto: `ahora.strftime("%d/%m/%Y %H:%M")` da `"04/10/2026 15:30"`.
- `datetime.strptime(texto, formato)` hace lo inverso: interpreta un texto según un formato.
- `isoformat()` genera el formato estándar ISO 8601 (`"2026-10-04T15:30:00+00:00"`) y `datetime.fromisoformat()` lo lee de vuelta. Es el formato recomendado para guardar fechas en JSON o en bases de datos.

Códigos frecuentes: `%Y` año con cuatro dígitos, `%m` mes, `%d` día, `%H` hora (00 a 23), `%M` minutos y `%S` segundos.

## Día de la semana

`weekday()` devuelve el día de la semana con lunes = 0 y domingo = 6. `isoweekday()` usa la convención ISO, con lunes = 1 y domingo = 7.
