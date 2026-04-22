import os
import cairosvg
from pathlib import Path

def convert_svgs_to_png(directory, scale_factor=4.0):
    """
    Convierte todos los SVG de un directorio a PNG en alta calidad.
    :param directory: Ruta de la carpeta
    :param scale_factor: Multiplicador de tamaño (4.0 = 4 veces más grande que el original)
    """
    path = Path(directory)
    svg_files = list(path.glob("*.svg"))
    
    if not svg_files:
        print("No se encontraron archivos SVG en esta carpeta.")
        return

    print(f"--- Iniciando conversión de {len(svg_files)} archivos ---")

    for svg_file in svg_files:
        output_path = svg_file.with_suffix(".png")
        
        try:
            cairosvg.svg2png(
                url=str(svg_file), 
                write_to=str(output_path),
                scale=scale_factor
            )
            print(f" Convertido: {svg_file.name} -> {output_path.name} (Scale: {scale_factor}x)")
        except Exception as e:
            print(f" Error al convertir {svg_file.name}: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = os.getcwd()

    convert_svgs_to_png(folder_path, scale_factor=5.0)
    print("--- Proceso finalizado ---")