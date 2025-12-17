# 📄 Extractor de Cédulas Colombianas

Herramienta automatizada para convertir PDFs escaneados de cédulas de ciudadanía colombianas a imágenes PNG de alta calidad, con recorte automático de fondo blanco y mejora de resolución.

## 🎯 Características

-   ✅ **Lista y selecciona** PDFs desde la carpeta `data/`
-   ✅ **Conversión automática** de PDF a PNG (300 DPI)
-   ✅ **Detección inteligente** del contenido escaneado
-   ✅ **Recorte automático** de fondo blanco
-   ✅ **Mejora de resolución** sin pérdida de calidad (150%)
-   ✅ **Interfaz de consola** intuitiva y fácil de usar
-   ✅ **Procesamiento de ambas páginas** del documento

## 📋 Requisitos Previos

### 1. Python 3.8+

Verifica tu versión:

```bash
python --version
```

### 2. Poppler

Necesario para convertir PDFs a imágenes.

**Windows:**

1. Descarga Poppler desde: https://github.com/oschwartz10612/poppler-windows/releases/
2. Extrae en `C:\Program Files\Poppler`
3. Agrega a PATH: `C:\Program Files\Poppler\poppler-xx.xx.x\Library\bin`

**Verificar instalación:**

```bash
where.exe pdftoppm
```

## 🚀 Instalación

1. **Clona el repositorio:**

```bash
git clone https://github.com/Juanm0331123/Tesseract-OCR-Docs.git
cd "Extracción Tesseract"
```

2. **Crea el entorno virtual:**

```bash
python -m venv venv
```

3. **Activa el entorno virtual:**

**Windows:**

```bash
.\venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

4. **Instala las dependencias:**

```bash
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto

```
Extracción Tesseract/
│
├── data/                    # Coloca aquí tus PDFs
│   ├── .gitkeep
│   └── *.pdf               # PDFs a procesar (ignorados en git)
│
├── output/                  # Imágenes procesadas
│   ├── .gitkeep
│   └── *.png               # Resultados (ignorados en git)
│
├── venv/                    # Entorno virtual (ignorado en git)
│
├── extractor.py            # Módulo principal con funciones
├── main.py                 # Script de ejecución (legacy)
├── run.py                  # Script alternativo
├── requirements.txt        # Dependencias del proyecto
├── .gitignore             # Archivos ignorados por git
└── README.md              # Este archivo
```

## 💻 Uso

1. **Coloca tus PDFs** en la carpeta `data/`

2. **Ejecuta el script:**

```bash
python extractor.py
```

3. **Selecciona el PDF** del menú numerado

4. **Revisa los resultados** en la carpeta `output/`

### Ejemplo de Ejecución

```bash
(venv) PS> python extractor.py

=== PDF's DISPONIBLES ===
1. Jessica.pdf
2. Jhojan.pdf
3. Miguel.pdf

Selecciona el número del PDF a procesar: 1

==================================================
Procesando: Jessica.pdf
==================================================

Convirtiendo PDF a imágenes...
  ✓ Página 1 guardada
  ✓ Página 2 guardada

==================================================
Recortando fondo blanco y agrandando imágenes...
==================================================

Procesando: Jessica_pagina_1.png
  ✓ Imagen procesada y guardada: Jessica_pagina_1_recortada.png

Procesando: Jessica_pagina_2.png
  ✓ Imagen procesada y guardada: Jessica_pagina_2_recortada.png

==================================================
✓ Proceso completado exitosamente
✓ Revisa la carpeta 'output' para ver los resultados
==================================================
```

## 📦 Archivos Generados

Para cada página del PDF se generan 2 archivos:

-   `{nombre}_pagina_{n}.png` - Imagen original en alta resolución
-   `{nombre}_pagina_{n}_recortada.png` - Imagen procesada (recortada y mejorada)

## 🛠️ Tecnologías Utilizadas

-   **pdf2image** - Conversión de PDF a imágenes
-   **Pillow (PIL)** - Manipulación de imágenes
-   **OpenCV** - Procesamiento y recorte inteligente
-   **NumPy** - Operaciones matriciales
-   **Poppler** - Motor de renderizado de PDF

## ⚙️ Configuración Avanzada

### Ajustar DPI de Conversión

En [`extractor.py`](extractor.py#L28), línea 28:

```python
imagenes = convert_from_path(ruta_pdf, dpi=300)  # Cambiar DPI aquí
```

### Ajustar Factor de Escalado

En [`extractor.py`](extractor.py#L110-L111), líneas 110-111:

```python
nuevo_ancho = int(pil_img.width * 1.5)  # Cambiar multiplicador
nuevo_alto = int(pil_img.height * 1.5)
```

### Ajustar Margen de Recorte

En [`extractor.py`](extractor.py#L98), línea 98:

```python
margen = 20  # Píxeles de margen alrededor del contenido
```

### Ajustar Umbral de Detección

En [`extractor.py`](extractor.py#L87), línea 87:

```python
_, binaria = cv2.threshold(gris, 240, 255, cv2.THRESH_BINARY_INV)
# Reducir 240 para detectar más contenido
# Aumentar 240 para ser más estricto
```

## 🔍 Solución de Problemas

### Error: "Poppler not found"

**Solución:** Instala Poppler y agrégalo al PATH del sistema.

### Error: "No module named 'cv2'"

**Solución:**

```bash
pip install opencv-python-headless
```

### Imágenes muy grandes

**Solución:** Reduce el DPI en la conversión o el factor de escalado.

### Recorte incorrecto

**Solución:** Ajusta el umbral de detección (threshold) en la función `recortar_fondo_blanco`.

### Contenido cortado

**Solución:** Aumenta el valor de `margen` en la función de recorte.

## 📝 Notas Importantes

-   Los PDFs en `data/` y las imágenes en `output/` están ignorados en git por privacidad
-   Solo se mantienen los archivos `.gitkeep` para preservar la estructura
-   Las imágenes originales y procesadas se mantienen para comparación
-   El proceso no modifica los PDFs originales

## 🔐 Privacidad y Seguridad

⚠️ **IMPORTANTE:** Este proyecto está diseñado para procesar documentos de identidad sensibles.

-   Nunca subas PDFs o imágenes de cédulas al repositorio
-   El `.gitignore` está configurado para proteger estos archivos
-   Usa este código solo en entornos seguros y controlados
-   Elimina los archivos procesados cuando ya no los necesites

## 📄 Licencia

Este proyecto es de uso personal y educativo.

## 👤 Autor

Juan León - Proyecto de Extracción de Documentos
