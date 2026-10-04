---
categoria: archivos-y-rutas
modulo: pathlib
---

# pathlib: rutas del sistema de archivos orientadas a objetos

El módulo `pathlib` representa las rutas del sistema de archivos como objetos en lugar de cadenas de texto. Reemplaza la mayoría de los usos de `os.path` con una interfaz más legible y que funciona igual en Windows, Linux y macOS.

## Clases principales

La clase más usada es `Path`. Al instanciarla, Python elige automáticamente la variante concreta del sistema operativo: `WindowsPath` en Windows y `PosixPath` en Linux o macOS. Existen además las clases "puras" (`PurePath`, `PureWindowsPath`, `PurePosixPath`), que permiten manipular rutas sin acceder nunca al disco; son útiles, por ejemplo, para procesar rutas de Windows desde un programa que corre en Linux.

Dos constructores alternativos muy comunes son `Path.cwd()`, que devuelve el directorio de trabajo actual, y `Path.home()`, que devuelve la carpeta personal del usuario.

## Construir y descomponer rutas

Las rutas se unen con el operador `/`, que reemplaza a `os.path.join`:

```python
from pathlib import Path

base = Path.home() / "proyectos" / "informe"
archivo = base / "datos.csv"
```

Cada ruta expone sus partes como atributos:

- `name`: el nombre final con extensión (`"datos.csv"`).
- `stem`: el nombre sin la extensión (`"datos"`).
- `suffix`: la extensión, incluido el punto (`".csv"`).
- `parent`: la carpeta que contiene a la ruta.
- `parts`: una tupla con cada componente de la ruta.

Para derivar rutas nuevas se usan `with_suffix(".json")`, que cambia la extensión, y `with_name("otro.csv")`, que cambia el nombre final. El método `resolve()` devuelve la ruta absoluta, resolviendo enlaces simbólicos y componentes `..`.

## Consultar el disco

Los métodos `exists()`, `is_file()` e `is_dir()` consultan si la ruta existe y de qué tipo es. El método `stat()` devuelve metadatos del archivo; por ejemplo, `stat().st_size` es el tamaño en bytes y `stat().st_mtime` la fecha de última modificación como timestamp.

## Crear carpetas con mkdir

`Path.mkdir()` crea un directorio. Tiene dos parámetros importantes:

- `parents`: si es `True`, crea también todas las carpetas intermedias que falten, como `mkdir -p` en Linux. Con el valor por defecto (`False`), falla con `FileNotFoundError` si la carpeta padre no existe.
- `exist_ok`: si es `True`, no lanza ningún error cuando el directorio ya existe. Con el valor por defecto (`False`), intentar crear una carpeta existente lanza `FileExistsError`.

La combinación habitual para "asegurarse de que una carpeta exista" es:

```python
Path("salida/reportes/2026").mkdir(parents=True, exist_ok=True)
```

## Leer y escribir archivos

Para archivos pequeños no hace falta abrirlos manualmente:

- `read_text(encoding="utf-8")` devuelve todo el contenido como cadena.
- `write_text(datos, encoding="utf-8")` escribe una cadena, reemplazando el contenido previo.
- `read_bytes()` y `write_bytes()` hacen lo mismo con datos binarios.

Conviene pasar siempre `encoding="utf-8"`: si se omite, Python usa la codificación por defecto del sistema, que en Windows puede no ser UTF-8 y corromper caracteres como la ñ. Para archivos grandes o lectura línea a línea, `Path.open()` devuelve un objeto archivo igual al de la función `open()`.

## Recorrer directorios

- `iterdir()` devuelve los elementos directos de una carpeta, sin entrar en subcarpetas.
- `glob("*.md")` busca archivos que coincidan con un patrón dentro de la carpeta.
- `rglob("*.py")` hace la misma búsqueda de forma recursiva, en todas las subcarpetas.

```python
for script in Path("src").rglob("*.py"):
    print(script.name, script.stat().st_size)
```

## Renombrar y borrar

`rename(destino)` mueve o renombra un archivo. `unlink()` borra un archivo; desde Python 3.8 acepta `missing_ok=True` para no fallar si el archivo no existe. `rmdir()` solo borra carpetas vacías: para eliminar un árbol completo hay que usar `shutil.rmtree()`, ya que `pathlib` no ofrece un borrado recursivo.
