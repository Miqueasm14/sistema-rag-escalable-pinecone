---
categoria: serializacion
modulo: json
---

# json: serialización de datos en formato JSON

El módulo `json` convierte objetos de Python a texto JSON (serializar) y texto JSON a objetos de Python (deserializar). Es la forma estándar de guardar configuraciones, intercambiar datos con APIs web o persistir estructuras simples.

## Las cuatro funciones principales

- `json.dumps(obj)`: convierte un objeto a una cadena JSON (la "s" final es de *string*).
- `json.dump(obj, archivo)`: escribe el JSON directamente en un archivo abierto.
- `json.loads(cadena)`: convierte una cadena JSON en un objeto de Python.
- `json.load(archivo)`: lee y convierte el contenido de un archivo abierto.

```python
import json

datos = {"usuario": "ana", "edad": 31, "activo": True}
texto = json.dumps(datos)
recuperado = json.loads(texto)
```

## Correspondencia de tipos

Al serializar, cada tipo de Python se traduce a un tipo de JSON:

| Python | JSON |
|---|---|
| `dict` | objeto |
| `list` y `tuple` | array |
| `str` | string |
| `int` y `float` | number |
| `True` / `False` | `true` / `false` |
| `None` | `null` |

La traducción no es simétrica: una tupla se serializa como array, pero al deserializar vuelve como `list`. Además, en JSON las claves de un objeto siempre son cadenas, así que un diccionario con claves enteras (`{1: "a"}`) vuelve como `{"1": "a"}`. Las claves que no son de tipo básico, como las tuplas, provocan un `TypeError`, salvo que se pase `skipkeys=True` para omitirlas.

## Caracteres no ASCII: ensure_ascii

Por defecto, `json.dumps` usa `ensure_ascii=True`, que escapa todo carácter fuera de ASCII. La palabra "año" se escribe entonces como `"año"`. Es JSON válido, pero difícil de leer. Para conservar los caracteres tal cual hay que pasar `ensure_ascii=False`:

```python
json.dumps({"ciudad": "Córdoba"}, ensure_ascii=False)
# '{"ciudad": "Córdoba"}'
```

Cuando se escribe en un archivo con `ensure_ascii=False`, el archivo debe abrirse con `encoding="utf-8"`; de lo contrario, en Windows la escritura puede fallar con un `UnicodeEncodeError`.

## Formato de salida

- `indent=2` (o cualquier entero) genera una salida con saltos de línea e indentación, legible para personas.
- `sort_keys=True` ordena alfabéticamente las claves, útil para comparar archivos o generar salidas reproducibles.
- `separators=(",", ":")` elimina los espacios después de comas y dos puntos, para obtener el JSON más compacto posible.

## Tipos que no son serializables

Objetos como `datetime`, `Decimal` o instancias de clases propias no tienen una representación JSON directa. Intentar serializarlos lanza `TypeError: Object of type datetime is not JSON serializable`. La solución es el parámetro `default`, una función que recibe el objeto problemático y devuelve algo serializable:

```python
from datetime import datetime

def convertir(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Tipo no serializable: {type(obj).__name__}")

json.dumps({"creado": datetime.now()}, default=convertir)
```

Para el proceso inverso, `json.loads` acepta `object_hook`, una función que recibe cada diccionario decodificado y puede transformarlo, por ejemplo, en una instancia de una clase propia.

## Errores al leer

Si el texto no es JSON válido, `json.loads` y `json.load` lanzan `json.JSONDecodeError`, que es una subclase de `ValueError`. La excepción incluye los atributos `msg`, `lineno` y `colno`, que indican qué falló y en qué línea y columna, lo que facilita encontrar el problema en archivos grandes. Un error típico es usar comillas simples: JSON solo admite comillas dobles para las cadenas.
