import os
from pdf2image import convert_from_path
from PIL import Image
import numpy as np
import cv2

def listar_pdfs(carpeta):
    pdfs = [f for f in os.listdir(carpeta) if f.lower().endswith('.pdf')]
    return pdfs

def mostrar_menu_pdfs(pdfs):
    print("\n=== PDF's DISPONIBLES ===")
    for i, pdf in enumerate(pdfs, 1):
        print(f"{i}. {pdf}")
    
    while True:
        try:
            opcion = int(input("\nSelecciona el número del PDF a procesar: "))
            if 1 <= opcion <= len(pdfs):
                return pdfs[opcion - 1]
            else:
                print("Número inválido. Intenta de nuevo.")
        except ValueError:
            print("Entrada inválida. Por favor ingresa un número.")
                
def convertir_pdf_a_imagenes(ruta_pdf, carpeta_salida):
    print(f"\nConvirtiendo PDF a imágenes...")
    imagenes = convert_from_path(ruta_pdf, dpi=300)
    
    rutas_imagenes = []
    nombre_base = os.path.splitext(os.path.basename(ruta_pdf))[0]
    
    for i, imagen in enumerate(imagenes, 1):
        ruta_salida = os.path.join(carpeta_salida, f"{nombre_base}_pagina_{i}.png")
        imagen.save(ruta_salida, 'PNG')
        rutas_imagenes.append(ruta_salida)
        print(f"  ✓ Página {i} guardada")
    
    return rutas_imagenes

def recortar_fondo_blanco(ruta_imagen):
    print(f"\nProcesando: {os.path.basename(ruta_imagen)}")

    img = cv2.imread(ruta_imagen)
    if img is None:
        return None

    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    S = hsv[:, :, 1]
    V = hsv[:, :, 2]

    mask = ((S > 10) | (V < 245)).astype(np.uint8) * 255
    mask = cv2.medianBlur(mask, 5)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25)), iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)), iterations=1)

    contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return None

    contornos = sorted(contornos, key=cv2.contourArea, reverse=True)
    area_min = (h * w) * 0.01
    candidato = None
    for c in contornos:
        if cv2.contourArea(c) >= area_min:
            candidato = c
            break
    if candidato is None:
        candidato = contornos[0]

    rect = cv2.minAreaRect(candidato)
    box = cv2.boxPoints(rect).astype(np.float32)

    s = box.sum(axis=1)
    diff = np.diff(box, axis=1)
    tl = box[np.argmin(s)]
    br = box[np.argmax(s)]
    tr = box[np.argmin(diff)]
    bl = box[np.argmax(diff)]
    src = np.array([tl, tr, br, bl], dtype=np.float32)

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxW = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxH = int(max(heightA, heightB))

    if maxW < 10 or maxH < 10:
        return None

    dst = np.array([[0, 0], [maxW - 1, 0], [maxW - 1, maxH - 1], [0, maxH - 1]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    warp = cv2.warpPerspective(img, M, (maxW, maxH), flags=cv2.INTER_CUBIC)

    hsv2 = cv2.cvtColor(warp, cv2.COLOR_BGR2HSV)
    S2 = hsv2[:, :, 1]
    V2 = hsv2[:, :, 2]
    mask2 = ((S2 > 10) | (V2 < 245)).astype(np.uint8) * 255
    mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15)), iterations=1)

    ys, xs = np.where(mask2 > 0)
    if len(xs) > 0 and len(ys) > 0:
        x1, x2 = xs.min(), xs.max()
        y1, y2 = ys.min(), ys.max()
        margen = max(6, int(0.01 * min(maxW, maxH)))
        x1 = max(0, x1 - margen)
        y1 = max(0, y1 - margen)
        x2 = min(maxW - 1, x2 + margen)
        y2 = min(maxH - 1, y2 + margen)
        warp = warp[y1:y2 + 1, x1:x2 + 1]

    pil_img = Image.fromarray(cv2.cvtColor(warp, cv2.COLOR_BGR2RGB))
    nuevo_ancho = int(pil_img.width * 1.5)
    nuevo_alto = int(pil_img.height * 1.5)
    resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
    pil_img_grande = pil_img.resize((nuevo_ancho, nuevo_alto), resample)

    nombre_base = os.path.splitext(ruta_imagen)[0]
    ruta_salida = f"{nombre_base}_recortada.png"
    pil_img_grande.save(ruta_salida, 'PNG')

    img_rec = cv2.cvtColor(np.array(pil_img_grande), cv2.COLOR_RGB2BGR)
    texto = mejorar_texto(img_rec)
    ruta_texto = f"{nombre_base}_texto.png"
    cv2.imwrite(ruta_texto, texto)

    print(f"  ✓ Imagen recortada: {os.path.basename(ruta_salida)}")
    print(f"  ✓ Imagen texto: {os.path.basename(ruta_texto)}")
    return ruta_salida

def mejorar_texto(img_bgr):
    h, w = img_bgr.shape[:2]

    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l2 = clahe.apply(l)
    img = cv2.cvtColor(cv2.merge([l2, a, b]), cv2.COLOR_LAB2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (0, 0), 25)
    norm = cv2.divide(gray, blur, scale=255)

    norm = clahe.apply(norm)
    den = cv2.bilateralFilter(norm, 9, 75, 75)

    g = cv2.GaussianBlur(den, (0, 0), 1.2)
    sharp = cv2.addWeighted(den, 1.8, g, -0.8, 0)

    bs = max(31, (min(h, w) // 25) | 1)
    if bs % 2 == 0:
        bs += 1

    b1 = cv2.adaptiveThreshold(sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, bs, 8)
    b2 = cv2.adaptiveThreshold(sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, bs, 8)

    s1 = int((b1 < 128).sum())
    s2 = int((b2 < 128).sum())
    binaria = b2 if s2 < s1 else b1

    return limpiar_binaria(binaria)

def limpiar_binaria(binaria):
    b = binaria.copy()
    h, w = b.shape[:2]

    if (b < 128).mean() > 0.5:
        b = 255 - b

    m = max(8, int(0.01 * min(h, w)))
    b[:m, :] = 255
    b[-m:, :] = 255
    b[:, :m] = 255
    b[:, -m:] = 255

    fg = (b == 0).astype(np.uint8)
    num, labels, stats, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)

    min_area = max(25, int(h * w * 0.000015))
    max_area = int(h * w * 0.12)

    remove = np.zeros(num, dtype=np.uint8)
    for i in range(1, num):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        ww = stats[i, cv2.CC_STAT_WIDTH]
        hh = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        extent = area / float(ww * hh)

        edge_touch = (x <= m) or (y <= m) or (x + ww >= w - m) or (y + hh >= h - m)

        if area < min_area:
            remove[i] = 1
        elif area > max_area:
            remove[i] = 1
        elif extent > 0.80 and area > max(300, min_area * 6):
            remove[i] = 1
        elif edge_touch and area > min_area:
            remove[i] = 1

    to_remove = remove[labels].astype(bool)
    b[to_remove] = 255

    k1 = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    k2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    b = cv2.morphologyEx(b, cv2.MORPH_OPEN, k1, iterations=1)
    b = cv2.morphologyEx(b, cv2.MORPH_CLOSE, k2, iterations=1)

    return b

def configurar_tesseract():
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    return pytesseract.pytesseract.tesseract_cmd

def extraer_fecha_expedicion(ruta_imagen):
    import re
    import cv2
    import numpy as np

    try:
        import pytesseract
    except Exception:
        raise RuntimeError("Falta pytesseract. Instala pytesseract y Tesseract OCR en el sistema.")

    img = cv2.imread(ruta_imagen)
    if img is None:
        return None

    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    h, w = gray.shape[:2]
    y1, y2 = int(h * 0.20), int(h * 0.70)
    x1, x2 = int(w * 0.18), int(w * 0.92)
    roi = gray[y1:y2, x1:x2]

    roi = cv2.resize(roi, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    roi = cv2.GaussianBlur(roi, (0, 0), 1.0)

    thr = cv2.adaptiveThreshold(roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 41, 11)
    if (thr < 128).mean() > 0.5:
        thr = 255 - thr

    k = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thr = cv2.morphologyEx(thr, cv2.MORPH_OPEN, k, iterations=1)

    config = "--oem 3 --psm 6 -c preserve_interword_spaces=1"
    try:
        txt = pytesseract.image_to_string(thr, lang="spa", config=config)
    except Exception:
        txt = pytesseract.image_to_string(thr, config=config)

    txt = re.sub(r"[^\w\s\-]", " ", txt.upper())
    txt = re.sub(r"\s+", " ", txt).strip()

    meses = {
        "ENE": "ENE", "FEB": "FEB", "MAR": "MAR", "ABR": "ABR", "MAY": "MAY", "JUN": "JUN",
        "JUL": "JUL", "AGO": "AGO", "SEP": "SEP", "SET": "SEP", "OCT": "OCT", "NOV": "NOV", "DIC": "DIC",
        "JAN": "ENE", "APR": "ABR", "AUG": "AGO", "DEC": "DIC"
    }

    patrones = [
        r"\b(\d{1,2})\s*[- ]\s*([A-Z]{3})\s*[- ]\s*(\d{4})\b",
        r"\b(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4})\b"
    ]

    candidatos = []

    for pat in patrones:
        for m in re.finditer(pat, txt):
            g = m.groups()
            if len(g) == 3 and g[1].isalpha():
                d = int(g[0])
                mon = meses.get(g[1], g[1])
                y = int(g[2])
                if 1900 <= y <= 2100 and 1 <= d <= 31 and mon in meses.values():
                    candidatos.append((y, d, mon))
            elif len(g) == 3 and g[1].isdigit():
                d = int(g[0])
                mon_num = int(g[1])
                y = int(g[2])
                if 1900 <= y <= 2100 and 1 <= d <= 31 and 1 <= mon_num <= 12:
                    mon_map = ["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SEP","OCT","NOV","DIC"]
                    candidatos.append((y, d, mon_map[mon_num - 1]))

    if not candidatos:
        return None

    y, d, mon = sorted(candidatos, key=lambda t: (t[0], t[1]), reverse=True)[0]
    return f"{d} {mon} {y}"