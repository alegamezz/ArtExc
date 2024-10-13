import random
import openai 
import os
from dotenv import load_dotenv
import reflex as rx
from openai import AsyncOpenAI
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ExifTags

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Si el script está en una subcarpeta, subir un nivel en la jerarquía de carpetas
BASE_DIR = os.path.dirname(BASE_DIR) 


# Cargar las variables de entorno desde el archivo .env
load_dotenv()


# Obtener la API Key desde las variables de entorno

client = AsyncOpenAI()

# Frases clave predefinidas
key_phrases = [
    "Vivir y ser consciente de lo que vives",
    "Recupera el placer de leer antes de dormir",
    "Disfruta de tu casa, de que tus tres hijos vuelven a estar aquí",
    "Sigue escribiendo. Es tu momento."
]

# Ruta de la plantilla de fondo
background_image_path = "/assets/plantillas/p1.png"

# Ruta donde se guardarán las imágenes generadas
output_path = "/assets/generated_images/"

# Fuente para el texto
font_path = "/path/to/your/font.ttf"  # Actualiza esto con la ruta a tu archivo de fuente TTF
font_size = 30  # Tamaño de la fuente



class ArticleState(rx.State):
    article_text: str = ""
    images: list = []
    key_phrases: list = []
    img: list[str] = []
    selected_font: str = "Arial"
    loading_sentences: bool = False
    loading_images: bool = False
    generated_images: bool = False
    num_of_generated_images: int = 0
    image_paths: list[str] = []

    selected_images: list[str] = []

    change_backgrounds_only: bool = False  # Nuevo estado para cambiar fondos

    


    async def change_backgrounds(self):
        '''
        Cambia las imágenes de fondo usando las frases ya extraídas.
        '''
        if not self.key_phrases:
            yield rx.toast.warning("No hay frases para generar imágenes.", position="bottom-center")

        self.loading_images = True
        self.num_of_generated_images = 0
        yield

        # Seleccionar nuevas imágenes de fondo aleatorias
        upload_dir = rx.get_upload_dir()
        available_templates = [
            file for file in os.listdir(upload_dir / "gallery") 
            if file.lower().endswith(('.jpg'))
        ]

        

        if len(available_templates) < 4:
            yield rx.toast.warning("No hay suficientes imágenes en el directorio de plantillas.", position="bottom-center")

        # Selecciona 4 plantillas de manera aleatoria y sin repetición
        self.selected_images = random.sample(available_templates, 4)

        print("Nuevas plantillas seleccionadas:", self.selected_images)

        # Regenerar imágenes con las nuevas plantillas
        for index, phrase in enumerate(self.key_phrases):
            generate_image_with_text(phrase, index, self.selected_font, self.selected_images)
            self.num_of_generated_images += 1
            yield

        self.generated_images = True
        self.loading_images = False
        self.image_paths = [f"{image}" for image in os.listdir(upload_dir) if image.endswith(".png")]

        print("Nuevas imágenes generadas:", self.image_paths)
        yield

    
   

    async def process_article(self):
        '''
        Procesa el artículo para extraer frases clave y generar imágenes.
        '''
        self.loading_sentences = True
        self.generated_images: bool = False
        self.num_of_generated_images: int = 0
        self.key_phrases = []

        yield

        upload_dir = rx.get_upload_dir()
        available_templates = [
            file for file in os.listdir(upload_dir / "gallery") 
            if file.lower().endswith(('.jpg'))
        ]

        

        if len(available_templates) < 4:
            yield rx.toast.warning("No hay suficientes imágenes en el directorio de plantillas.", position="bottom-center")

        # Selecciona 4 plantillas de manera aleatoria y sin repetición
        self.selected_images = random.sample(available_templates, 4)

        print("PLANILLAS SELECCIONADAS:", self.selected_images)

        # if article text is longer than 100 characters proccess it:
        if len(self.article_text) > 100:
            # Extraer frases clave (llamada a la API o usar predefinidas)
            self.key_phrases = await extract_key_phrases(self.article_text)
            # self.key_phrases = key_phrases  # Usar las frases predefinidas
     

            self.loading_sentences = False
            self.loading_images = True
            yield
           

            # Resetear imágenes generadas previamente
            self.images = []

            # Generar una imagen por cada frase clave
            for index, phrase in enumerate(self.key_phrases):
                generate_image_with_text(phrase, index, self.selected_font, self.selected_images)
                self.num_of_generated_images += 1
                
                print("Total de imágenes generadas:", self.num_of_generated_images)
                yield
            
            self.generated_images = True
            self.article_text = ""
            self.loading_images = False

            self.image_paths = [f"{image}" for image in os.listdir(upload_dir) if image.endswith(".png")]

            print("Imágenes generadas:", self.image_paths)

            yield rx.toast.success("Imágenes generadas correctamente.", position="bottom-center")
        
        else:
            self.loading_sentences = False
            self.loading_images = False
            yield rx.toast.warning(
                "El artículo es demasiado corto. Por favor, escribe al menos 100 caracteres.", position="bottom-center"
            )
            



async def extract_key_phrases(article_text):
    '''
    Extrae las cuatro frases más inspiradoras usando OpenAI GPT.
    '''
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente útil que extrae frases inspiradoras de textos."},
                {"role": "user", "content": f"Por favor, extrae las 4 frases más inspiradoras del siguiente artículo. Deben ser frases destacadas, no muy cortas ni excesivamente largas. Devuélveme solo las frases, separadas por ';' y entre comillas:\n\n{article_text}"}
            ],

            max_tokens=200,
            n=1,
            temperature=0.7,
        )
        response_text = response.choices[0].message.content
        
        key_phrases = [phrase.strip() for phrase in response_text.split(';') if phrase]

        print(f"Frases clave extraídas: {key_phrases}")
        return key_phrases

    except Exception as e:
        print(f"Error al obtener frases clave de OpenAI: {e}")
        return []
    

def generate_image_with_text(phrase, index, selected_font, selected_images):
    try:
        # Definir el directorio de subida
        upload_dir = rx.get_upload_dir()  # Asegúrate de definir correctamente el acceso a upload_dir
        output_path = upload_dir

        # Asegurarse de que la carpeta existe
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Obtener la ruta de la imagen de fondo
        background_image_path = os.path.join(BASE_DIR, 'uploaded_files', 'gallery', selected_images[index])

        # Abrir la imagen de fondo
        img = Image.open(background_image_path).convert('RGBA')

        # Crear una capa para la sombra
        shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)

        # Crear una capa para el texto
        text_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)

        # Dimensiones de la imagen
        img_width, img_height = img.size

        # Tamaño del texto principal basado en un porcentaje del ancho de la imagen
        font_size = int(img_width * 0.05)  # El tamaño de la fuente es el 5% del ancho de la imagen
        font_path = os.path.join(BASE_DIR, 'assets', 'fonts', 'SimpleCake.ttf')
        print("DIRECTORIO BASE:", BASE_DIR)
        print("Ruta de la fuente:", font_path)
        if not os.path.exists(font_path):
            print(f"Font file not found: {font_path}")
            font= ImageFont.load_default(font_size)
        else:
            font = ImageFont.truetype(font_path, font_size)

        font2_path = ("/fonts/Montserrat-Bold.ttf")
        if not os.path.exists(font2_path):
            print(f"Font file /fonts/Montserrat directly not found: {font2_path}")
            font2 = ImageFont.load_default()
        else:
            font2 = ImageFont.truetype(font2_path, font_size)
        
        # Tamaño del texto "Sonia Blasco" más pequeño
        italic_font_size = int(font_size * 0.6)  # El tamaño es el 60% del tamaño del texto principal
        italic_font_path = os.path.join(BASE_DIR, 'assets', 'fonts', 'Montserrat-Italic.ttf')
        if not os.path.exists(italic_font_path):
            print(f"Font file not found: {italic_font_path}")
            italic_font = ImageFont.load_default(italic_font_size)
        else:
            italic_font = ImageFont.truetype(italic_font_path, italic_font_size)

        # Ajustar el texto en líneas si es demasiado largo
        wrapped_text = textwrap.fill(phrase, width=33)

        # Calcular el tamaño del texto principal
        lines = wrapped_text.split('\n')
        line_height = font.getbbox('A')[3] - font.getbbox('A')[1]  # Altura de una línea
        extra_line_spacing = int(font_size * 0.2)  # 20% del tamaño de la fuente como espaciado entre líneas

        total_text_height = (line_height + extra_line_spacing) * len(lines) - extra_line_spacing

        # Calcular la posición centrada
        text_x = 0
        text_y = (img_height - total_text_height) / 2

        # Color del texto y sombra
        text_color = (255, 255, 255)  # Blanco
        shadow_color = (0, 0, 0, 100)  # Sombra semi-transparente

        # Desenfoque de sombra
        shadow_offset = 10  # Desplazamiento de la sombra
        blur_radius = 10  # Radio del desenfoque

        # Dibujar la sombra primero en la capa separada
        for line in lines:
            text_bbox = text_draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            line_x = (img_width - text_width) / 2

            # Dibujar sombra en la capa separada
            shadow_draw.text((line_x + shadow_offset, text_y + shadow_offset), line, font=font, fill=shadow_color)

            # Moverse a la siguiente línea
            text_y += line_height + extra_line_spacing

        # Aplicar desenfoque gaussiano a la capa de sombra
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(blur_radius))

        # Combinar la capa de sombra desenfocada con la imagen original
        img = Image.alpha_composite(img, shadow_layer)

        # Reiniciar la posición Y del texto para dibujar el texto principal
        text_y = (img_height - total_text_height) / 2

        # Dibujar el texto principal encima de la imagen combinada
        for line in lines:
            text_bbox = text_draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            line_x = (img_width - text_width) / 2

            # Dibujar el texto original en la capa de texto
            text_draw.text((line_x, text_y), line, font=font, fill=text_color)

            # Moverse a la siguiente línea
            text_y += line_height + extra_line_spacing

        # Añadir el texto "Sonia Blasco" debajo del texto principal
        author_text = "Sonia Blasco"
        author_text_bbox = text_draw.textbbox((0, 0), author_text, font=italic_font)
        author_text_width = author_text_bbox[2] - author_text_bbox[0]
        author_x = (img_width - author_text_width) / 2
        author_y = text_y + 20  # Ajustar según sea necesario

        # Dibujar el texto "Sonia Blasco"
        text_draw.text((author_x, author_y), author_text, font=italic_font, fill=text_color)

        # Combinar la capa de texto con la imagen final
        img = Image.alpha_composite(img, text_layer)

        # Guardar la imagen
        image_filename = f"imagen_{index + 1}.png"
        img.save(os.path.join(output_path, image_filename))

        print(f"Imagen {index + 1} guardada correctamente en {output_path} como {image_filename}.")
    
    except Exception as e:
        print(f"Error al generar la imagen: {e}")

class GalleryState(rx.State):
    images: list[str] = []


    def on_load(self):
        # Obtener el directorio de subida
        upload_dir = rx.get_upload_dir()
        gallery_dir = upload_dir / "gallery"

        # Verificar si la carpeta 'gallery' existe
        if os.path.exists(gallery_dir):
            # Cargar todas las imágenes que existen en la carpeta 'gallery'
            self.images = [f"gallery/{image}" for image in os.listdir(gallery_dir) if image.endswith((".JPG", ".jpg", ".jpeg"))]
        else:
            self.images = []  # Si no hay imágenes, inicializar la lista vacía

        print("Imágenes cargadas:", self.images)
        print("Ruta de carga:", rx.get_upload_dir(), rx.get_upload_url(self.images[0]) if self.images else "No hay imágenes.")



    async def handle_upload(self, files: list[rx.UploadFile]):
        upload_dir = rx.get_upload_dir()
        gallery_dir = upload_dir / "gallery"  # Definimos la ruta de la carpeta 'gallery'

        # Crear la carpeta 'gallery' si no existe
        if not os.path.exists(gallery_dir):
            os.makedirs(gallery_dir)

        # Obtener el siguiente número disponible basado en la cantidad de archivos existentes
        existing_images = [f for f in os.listdir(gallery_dir) if f.endswith(".JPG")]
        next_image_number = len(existing_images) + 1
        next_image_filename = f"{next_image_number}.JPG"

        for file in files:
            upload_data = await file.read()
            outfile = gallery_dir / next_image_filename  # Guardar en la carpeta 'gallery'

            # Guardar el archivo temporalmente
            with open(outfile, "wb") as f:
                f.write(upload_data)

            # Abrir la imagen con PIL
            img = Image.open(outfile)

            # Corregir la rotación según la orientación EXIF
            img = self.correct_image_rotation(img)

            # Ajustar la imagen a formato cuadrado (1:1) recortándola
            img = self.make_square(img)

            # Reducir brillo de la imagen
            img = self.reduce_brightness(img, factor=0.8)  # Reducimos el brillo en un 20%

            if img.mode == 'RGBA':
                # Si la imagen tiene un canal alfa, convertirla a RGB
                img = img.convert('RGB')

            # Guardar la imagen en el formato final (1:1 y brillo ajustado)
            img.save(outfile, format='JPEG')

            # Añadir el nombre del archivo a la lista de imágenes
            self.images.append(next_image_filename)

        # Actualizar la interfaz llamando a `on_load` para forzar la recarga de imágenes
        yield rx.toast.success("Imágenes subidas correctamente.", position="bottom-center")
        self.on_load()

    def correct_image_rotation(self, img: Image) -> Image:
        """
        Corrige la rotación de la imagen según los metadatos EXIF.
        """
        try:
            # Obtener los metadatos EXIF de la imagen
            exif = img._getexif()

            if exif:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break

                exif_orientation = exif.get(orientation)

                # Aplicar la rotación basada en la orientación EXIF
                if exif_orientation == 3:
                    img = img.rotate(180, expand=True)
                elif exif_orientation == 6:
                    img = img.rotate(270, expand=True)
                elif exif_orientation == 8:
                    img = img.rotate(90, expand=True)

        except (AttributeError, KeyError, IndexError):
            # La imagen no tiene datos EXIF, continuar sin hacer nada
            pass

        return img

    def make_square(self, img: Image) -> Image:
        """
        Recorta la imagen para que sea cuadrada (1:1), manteniendo el centro de la imagen.
        """
        width, height = img.size

        # Si la imagen ya es cuadrada, devolverla sin cambios
        if width == height:
            return img
        else:
            # Si la imagen es más ancha que alta, recortar los lados
            if width > height:
                left = (width - height) // 2
                right = left + height
                top = 0
                bottom = height
            # Si la imagen es más alta que ancha, recortar arriba y abajo
            else:
                top = (height - width) // 2
                bottom = top + width
                left = 0
                right = width

            # Recortar la imagen a las coordenadas calculadas
            return img.crop((left, top, right, bottom))

    def reduce_brightness(self, img: Image, factor: float = 0.8) -> Image:
        """
        Reduce el brillo de la imagen con un factor dado (default 0.8).
        """
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)


    async def delete_image(self, image_to_delete: str):
        """
        Elimina la imagen especificada y renombra las imágenes restantes.
        """
        # Obtener la ruta completa de la imagen a eliminar
        upload_dir = rx.get_upload_dir()
        gallery_dir = upload_dir
        image_path = gallery_dir / image_to_delete

        # Verificar si la imagen existe y eliminarla
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"Imagen eliminada: {image_to_delete}")

            # Renombrar las imágenes restantes
            existing_images = sorted(f for f in os.listdir(gallery_dir) if f.endswith(".JPG"))
            for index, existing_image in enumerate(existing_images):
                new_name = f"{index + 1}.JPG"
                os.rename(gallery_dir / existing_image, gallery_dir / new_name)

            # Actualizar la lista de imágenes
            self.images = [f"gallery/{image}" for image in os.listdir(gallery_dir) if image.endswith((".JPG", ".jpg", ".jpeg"))]
            # Actualizar la interfaz llamando a `on_load` para forzar la recarga de imágenes
            yield rx.toast.success("Imagen eliminada correctamente.", position="bottom-center")
            self.on_load()

        else:
            print("Path not found", image_path)
            print("La imagen no existe.")

