---
categoria: estructuras-de-datos
modulo: collections
---

# collections: contenedores de datos especializados

El módulo `collections` ofrece alternativas a los contenedores básicos de Python (`dict`, `list`, `tuple`, `set`) para casos de uso frecuentes, con mejor rendimiento o un código más simple.

## Counter: contar elementos

`Counter` es un diccionario pensado para contar objetos hasheables:

```python
from collections import Counter

palabras = ["rojo", "azul", "rojo", "verde", "rojo"]
conteo = Counter(palabras)
conteo.most_common(2)   # [('rojo', 3), ('azul', 1)]
```

Características útiles:

- Consultar una clave que no existe devuelve `0` en lugar de lanzar `KeyError`.
- `most_common(n)` devuelve los `n` elementos más frecuentes, ordenados de mayor a menor.
- `update()` suma conteos nuevos, y se pueden sumar o restar contadores con `+` y `-`.

## defaultdict: valores por defecto automáticos

`defaultdict` recibe una función "fábrica" que se llama cuando se accede a una clave inexistente, y guarda ese valor automáticamente:

```python
from collections import defaultdict

por_categoria = defaultdict(list)
for producto, categoria in ventas:
    por_categoria[categoria].append(producto)
```

Con un `dict` común habría que comprobar si la clave existe o usar `setdefault(clave, [])` en cada iteración. Las fábricas más comunes son `list`, `int` (empieza en 0, útil para contar), `set` y `dict`. Atención: acceder a una clave inexistente la crea, incluso si solo se la estaba leyendo.

## deque: cola de doble extremo

`deque` (pronunciado "deck") es una cola que permite agregar y quitar elementos en ambos extremos en tiempo constante, O(1):

- `append()` y `pop()` operan en el extremo derecho.
- `appendleft()` y `popleft()` operan en el extremo izquierdo.

Una lista común también tiene `pop(0)` e `insert(0, x)`, pero esas operaciones son O(n), porque desplazan todos los elementos. Por eso `deque` es la estructura indicada para colas FIFO, recorridos en anchura (BFS) y cualquier caso con inserciones y extracciones frecuentes en los dos extremos.

Con el parámetro `maxlen`, el `deque` tiene un tamaño máximo: al agregar un elemento cuando está lleno, descarta automáticamente el del extremo opuesto. Es una forma simple de guardar "los últimos N eventos":

```python
from collections import deque

ultimos = deque(maxlen=3)
for evento in ["a", "b", "c", "d"]:
    ultimos.append(evento)
# deque(['b', 'c', 'd'], maxlen=3)
```

## namedtuple: tuplas con nombre

`namedtuple` crea una clase de tupla cuyos campos se acceden por nombre además de por posición:

```python
from collections import namedtuple

Punto = namedtuple("Punto", ["x", "y"])
p = Punto(3, 4)
p.x          # 3
p._asdict()  # {'x': 3, 'y': 4}
p._replace(x=10)   # Punto(x=10, y=4)
```

Como toda tupla, es inmutable y ocupa poca memoria. `_replace` no modifica el original: devuelve una copia con los campos cambiados. Para estructuras con tipos declarados y valores por defecto más flexibles, una alternativa moderna es `dataclasses.dataclass` o `typing.NamedTuple`.

## OrderedDict y ChainMap

Desde Python 3.7, los diccionarios comunes conservan el orden de inserción, así que `OrderedDict` ya no es necesario solo por eso. Sigue siendo útil por sus métodos extra: `move_to_end(clave)` mueve una clave al final (o al principio con `last=False`) y `popitem(last=False)` saca el primer elemento, lo que facilita implementar cachés LRU.

`ChainMap` agrupa varios diccionarios y los busca en orden como si fueran uno solo, sin copiarlos. Es útil para resolver configuraciones por capas, por ejemplo argumentos de línea de comandos, luego variables de entorno y por último valores por defecto.
