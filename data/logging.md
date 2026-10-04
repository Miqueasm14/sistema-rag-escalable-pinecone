---
categoria: observabilidad
modulo: logging
---

# logging: registro de eventos de una aplicación

El módulo `logging` permite registrar lo que hace un programa con distintos niveles de importancia y enviar esos registros a la consola, a archivos u otros destinos. A diferencia de `print`, los mensajes se pueden filtrar por nivel, llevan fecha y origen, y se configuran en un solo lugar sin tocar el resto del código.

## Niveles

Cada mensaje tiene un nivel, asociado a un número:

| Nivel | Valor | Uso típico |
|---|---|---|
| `DEBUG` | 10 | Detalle para diagnosticar problemas |
| `INFO` | 20 | Confirmación de que las cosas funcionan |
| `WARNING` | 30 | Algo inesperado, pero el programa sigue |
| `ERROR` | 40 | Una operación falló |
| `CRITICAL` | 50 | Error grave; el programa podría no continuar |

Un logger solo emite los mensajes de su nivel o superior. El logger raíz arranca en `WARNING`, por eso, sin configuración, los mensajes `info` y `debug` no aparecen.

## Obtener un logger

La convención es crear un logger por módulo:

```python
import logging

logger = logging.getLogger(__name__)
```

Usar `__name__` hace que el nombre del logger coincida con el del módulo (por ejemplo `app.db.conexion`), lo que permite saber de dónde viene cada mensaje y configurar partes de la aplicación por separado.

## Configuración rápida con basicConfig

`logging.basicConfig` configura el logger raíz en una línea:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
```

Parámetros frecuentes: `level` (nivel mínimo), `format` (plantilla de cada línea), `datefmt` (formato de la fecha) y `filename` (si se indica, los mensajes van a ese archivo en lugar de a la consola).

Un detalle importante: `basicConfig` **no hace nada si el logger raíz ya tiene handlers configurados**. Por eso, si una librería o una llamada anterior ya configuró el logging, una segunda llamada a `basicConfig` se ignora en silencio y parece que "no funciona". Desde Python 3.8 se puede pasar `force=True`, que elimina los handlers existentes y aplica la nueva configuración.

## Handlers y formatters

Para configuraciones más completas se arman las piezas por separado:

- Un **handler** decide a dónde va el mensaje: `StreamHandler` (consola), `FileHandler` (archivo) o `RotatingFileHandler` (del submódulo `logging.handlers`), que rota el archivo cuando supera `maxBytes` y conserva `backupCount` copias anteriores.
- Un **formatter** decide cómo se ve cada línea.

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler("app.log", maxBytes=1_000_000, backupCount=3)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
```

Cada handler también tiene su propio nivel: se puede mandar todo a un archivo y solo los errores a la consola.

## Registrar excepciones

Dentro de un bloque `except`, `logger.exception("mensaje")` registra el mensaje con nivel `ERROR` e incluye automáticamente el traceback completo. Es preferible a registrar solo `str(e)`, que pierde la información de dónde ocurrió el error.

## Formato diferido de mensajes

Se recomienda pasar los valores como argumentos en lugar de usar f-strings:

```python
logger.debug("Procesando usuario %s con %d items", usuario, cantidad)
```

Con esta forma, el texto final solo se construye si el mensaje realmente se va a emitir. Con una f-string, el formateo ocurre siempre, aunque el nivel `DEBUG` esté desactivado.

## Propagación

Los loggers forman una jerarquía según sus nombres separados por puntos: `app.db` es hijo de `app`. Un mensaje se maneja en su logger y luego se propaga hacia los padres hasta el raíz. Si un logger y su padre tienen handlers, el mensaje aparece duplicado; se evita con `logger.propagate = False`. En una librería, la recomendación es agregar solo un `logging.NullHandler()` y dejar que la aplicación que la usa decida la configuración.
