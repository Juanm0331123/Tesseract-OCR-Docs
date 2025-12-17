from extractor import listar_pdfs, mostrar_menu_pdfs, convertir_pdf_a_imagenes, recortar_fondo_blanco, extraer_fecha_expedicion, configurar_tesseract
import os

def main():
    carpeta_data = "data"
    carpeta_output = "output"

    os.makedirs(carpeta_output, exist_ok=True)

    pdfs = listar_pdfs(carpeta_data)

    if not pdfs:
        print("No se encontraron archivos PDF en la carpeta 'data'")
        return

    pdf_seleccionado = mostrar_menu_pdfs(pdfs)
    ruta_pdf = os.path.join(carpeta_data, pdf_seleccionado)

    print(f"\n{'='*50}")
    print(f"Procesando: {pdf_seleccionado}")
    print(f"{'='*50}")

    rutas_imagenes = convertir_pdf_a_imagenes(ruta_pdf, carpeta_output)

    print(f"\n{'='*50}")
    print("Recortando fondo blanco y agrandando imágenes...")
    print(f"{'='*50}")

    for ruta_img in rutas_imagenes:
        recortar_fondo_blanco(ruta_img)

    print(f"\n{'='*50}")
    print("✓ Proceso completado exitosamente")
    print(f"✓ Revisa la carpeta 'output' para ver los resultados")
    print(f"{'='*50}")

    if len(rutas_imagenes) >= 2:
        configurar_tesseract()
        base2 = os.path.splitext(rutas_imagenes[1])[0]
        ruta_rec2 = f"{base2}_recortada.png"
        ruta_txt2 = f"{base2}_texto.png"

        print(f"\n{'='*50}")
        print("Extrayendo fecha de expedición de la segunda página...")
        print(f"{'='*50}")

        fecha = extraer_fecha_expedicion(ruta_rec2)
        if not fecha:
            fecha = extraer_fecha_expedicion(ruta_txt2)

        print(f"FECHA EXPEDICIÓN: {fecha if fecha else 'NO ENCONTRADA'}")
