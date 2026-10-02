import os 
import sys
import shutil
import argparse


def mover_sin_sobrescribir(origen, carpeta_destino):
    nombre_archivo = os.path.basename(origen)
    nombre, extension = os.path.splitext(nombre_archivo)
    destino = os.path.join(carpeta_destino, nombre_archivo)
    contador = 1

    while os.path.exists(destino):
        nombre_nuevo = f"{nombre} ({contador}){extension}"
        destino = os.path.join(carpeta_destino, nombre_nuevo)
        contador += 1

    shutil.move(origen, destino)


def ordenar_archivos(carpeta):
    img_extensiones = ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp", "svg", "ico", "heic","jfif"]
    video_extension = ["mp4", "mkv", "mov", "avi", "flv", "wmv", "webm", "mpeg", "mpg", "3gp"]
    hoja_calculo_extension = ["xls", "xlsx", "ods", "csv", "tsv", "xlsm"]
    texto_extension = ["txt", "md", "rtf", "log", "ini", "cfg", "json", "yaml", "yml", "xml","doc", "docx","odt","tex","wps"]
    pdf_extension = ["pdf"]
    ruta = carpeta
    carpetas = ['imagenes', 'PDFs', 'videos', 'texto', 'hoja_calculo', 'ZZotros']

    for carpeta in carpetas:
        path_carpeta = os.path.join(ruta, carpeta)

        if not os.path.exists(path_carpeta):
            os.makedirs(path_carpeta)
    
    for archivo in os.listdir(ruta):
        ruta_archivo = os.path.join(ruta, archivo)  

        if os.path.isdir(ruta_archivo):
            continue  

        nombre, extension = os.path.splitext(archivo)
        extension = extension.lower().lstrip('.')

        if extension in img_extensiones:
            destino = os.path.join(ruta, 'imagenes')
            mover_sin_sobrescribir(ruta_archivo, destino)

        elif extension in video_extension:
            destino = os.path.join(ruta, 'videos')
            mover_sin_sobrescribir(ruta_archivo, destino)

        elif extension in hoja_calculo_extension:
            destino = os.path.join(ruta, 'hoja_calculo')
            mover_sin_sobrescribir(ruta_archivo, destino)

        elif extension in texto_extension:
            destino = os.path.join(ruta, 'texto')
            mover_sin_sobrescribir(ruta_archivo, destino)

        elif extension in pdf_extension:
            destino = os.path.join(ruta, 'PDFs')
            mover_sin_sobrescribir(ruta_archivo, destino)
        else:
            destino = os.path.join(ruta, 'ZZotros')
            mover_sin_sobrescribir(ruta_archivo, destino)

    for carpeta in carpetas:
        path_carpeta = os.path.join(ruta, carpeta)
        if os.path.exists(path_carpeta) and not os.listdir(path_carpeta):
            os.rmdir(path_carpeta)


def main():
    parser = argparse.ArgumentParser(description="ingresa la ruta del directorio a ordenar")
    parser.add_argument('ruta', help='ruta del directorio')
    args = parser.parse_args()

    if not os.path.isdir(args.ruta):
        print(f"LA RUTA NO EXISTE ")
        sys.exit(1)
    ordenar_archivos(args.ruta)
    
if __name__ == "__main__":
    main()
