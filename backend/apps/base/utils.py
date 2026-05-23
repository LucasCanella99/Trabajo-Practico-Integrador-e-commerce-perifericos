from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
import os

def optimizar_imagen(campo_imagen, max_width=800, quality=85):
    """
    Recibe un campo de imagen, lo procesa en memoria RAM,
    lo achica y lo comprime a formato WebP antes de enviarlo a Supabase.
    """
    if not campo_imagen:
        return None
        
    # 1. Abrimos la imagen original usando la librería Pillow
    img = Image.open(campo_imagen)
    
    # 2. Si la imagen tiene transparencias (como un PNG), le ponemos fondo blanco
    # Esto evita errores raros al convertir el formato a WebP
    if img.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode == 'P':
        img = img.convert('RGB')

    # 3. Si la foto es gigante (más de 800px de ancho), la redimensionamos proporcionalmente
    if img.width > max_width:
        output_size = (max_width, int((max_width / img.width) * img.height))
        img = img.resize(output_size, Image.Resampling.LANCZOS)
        
    # 4. Guardamos el resultado comprimido en un archivo virtual en la memoria (BytesIO)
    buffer = BytesIO()
    img.save(buffer, format='WEBP', quality=quality, optimize=True)
    buffer.seek(0)
    
    # 5. Le cambiamos el nombre original (.jpg o .png) para que termine en .webp
    nombre_original = os.path.splitext(campo_imagen.name)[0]
    nuevo_nombre = f"{nombre_original}.webp"
    
    # Devolvemos el archivo optimizado listo para que Django lo guarde
    return ContentFile(buffer.read(), name=nuevo_nombre)