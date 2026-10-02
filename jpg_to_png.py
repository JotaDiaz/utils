from PIL import Image
from pathlib import Path
import sys


def convertir_carpeta(carpeta):
    carpeta = Path(carpeta)

    if not carpeta.is_dir():
        print(f"Error: no existe la carpeta: {carpeta}")
        return

    archivos = list(carpeta.glob("*.jpg")) + list(carpeta.glob("*.jpeg"))
    archivos += list(carpeta.glob("*.JPG")) + list(carpeta.glob("*.JPEG"))

    if not archivos:
        print("No se encontraron imágenes JPG.")
        return

    for archivo in archivos:
        salida = archivo.with_suffix(".png")

        try:
            with Image.open(archivo) as imagen:
                imagen.save(salida, "PNG")

            print(f"✓ {archivo.name} -> {salida.name}")

        except Exception as e:
            print(f"✗ Error con {archivo.name}: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python jpg_a_png.py /ruta/a/carpeta")
        sys.exit(1)

    convertir_carpeta(sys.argv[1])