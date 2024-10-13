"""The home page of the app."""
import reflex as rx
import reflex_chakra as rxc
from ARTEXC.components.footer import footer
from ARTEXC.components.header import header
from ARTEXC.states import ArticleState

def share_on_instagram(path):
    # Función que abre Instagram con la imagen preparada para compartir.
    # Utiliza `navigator.share` si está disponible o un esquema de URL para abrir Instagram
    return rx.fragment(
        rx.button(
            "Compartir en Instagram",
            color_scheme="pink",
            size="md",
            on_click=lambda: rx.window.navigator.share(
                title="Subir a Instagram",
                text="Compartir esta imagen en Instagram",
                url=rx.get_upload_url(path)
            )
        )
    )




def show_images():
    return rx.container(
        rx.cond(
            ArticleState.image_paths,
            rx.vstack(
                rx.flex(
                    rx.foreach(
                        ArticleState.image_paths,
                        lambda path: rx.box(
                            rx.image(
                                src=rx.get_upload_url(path),
                                height="[auto, 400px]",
                                width="auto",
                                margin_top=["1em", "2em"],  # Más margen superior en pantallas pequeñas, mayor en grandes
                                margin_right="[0em, 1em]",  # Más margen derecho en pantallas pequeñas, mayor en grandes
                                margin_left="[0em, 1em]",  # Más margen derecho en pantallas pequeñas, mayor en grandes
                                position="relative", 
                                border_radius="8px", 
                                spacing="1em", 
                                box_shadow="0 4px 15px rgba(0, 0, 0, 0.4)",  
                            ),
                            rx.radix.icon_button(
                                "download",  
                                position="absolute",
                                bottom="10px",  
                                right="10px",  
                                on_click=rx.download(url=rx.get_upload_url(path)),  
                                color_scheme="teal",
                                size="2",
                            ),
                            position="relative",  
                            display="inline-block",  
                            width=["100%", "48%"],  
                            margin="1%",
                        ),
                    ),
                    wrap="wrap",  
                    justify_content="center",
                    aign_items="center",
                    width="100%",
                ),
                width="100%",
                align_items="center",
                justify_content="center",
            ),
        ),
        width="100%",
        align_items="center",
        justify_content="center",
    )


@rx.page(route="/")
def index():
    return rx.vstack(
        header(),
        rx.spacer(),
        rx.vstack(
            height="70px",
        ),

        rx.image(
            src="/logo.png",
            height="150px",
            width="150px",  # Haz que el ancho y alto sean iguales para crear un círculo
            margin_bottom="1em",
            box_shadow="0 4px 15px rgba(0, 0, 0, 0.4)",  
            transition="all 0.3s ease-in-out",  # Agrega una transición suave
            _hover={"transform": "scale(1.1)"},  # Efecto de zoom al pasar el cursor
            border_radius="50%",  # Hace que la imagen sea un círculo
            object_fit="cover",  # Asegura que la imagen se ajuste bien dentro del círculo
        ),

    
        rx.container(
            

            rx.text_area(
                placeholder="Ingresa el artículo aquí...",
                on_change=ArticleState.set_article_text, 
                rows="10",
                width="100%",
                margin_bottom="1em",
                background_color="#FFF1F3",
                style={
                    "& textarea::placeholder": {
                        "color": "gray",
                        "font_weight": "bold",
                    },
                    "& textarea": {
                        "color": "gray", 
                    },
                }
            ),  
            
            rx.vstack(
                rx.hstack(
                    rx.button(
                        rx.hstack(
                            rx.spinner(loading=ArticleState.loading_sentences | ArticleState.loading_images), 
                            rx.text(
                                rx.cond(
                                    ArticleState.loading_sentences, 
                                    "Eligiendo frases...", 
                                    rx.cond(
                                        ArticleState.loading_images, 
                                        f"Generando imágenes... ({ArticleState.num_of_generated_images}/4)",
                                        "Procesar artículo"
                                    ),
                                ),
                                size="2", 
                                font_weight="bold",
                                color=rx.cond(ArticleState.article_text, "white", "gray"),
                            )
                        ),
                        color_scheme="teal",
                        on_click=ArticleState.process_article,  
                        width="[30%, 90%]",
                        disabled=rx.cond(ArticleState.article_text, False, True), 
                        #first layer, z index   
                        z_index="1000",
                        
                         
                    ),
                    # Botón para cambiar fondos solo si las imágenes ya han sido generadas
                    rx.cond(
                        ArticleState.generated_images & (ArticleState.num_of_generated_images == 4),
                        rx.button(
                            "Cambiar de fondos", 
                            color_scheme="purple",
                            variant="soft", 
                            on_click=ArticleState.change_backgrounds,  # Llama la nueva función
                            width="[30%, 90%]",
                        ),
                    ),
                    justify_content="space-between",
                    width="100%",
                ),
                align_items="center",
                width="100%",
            ),


            

            # Mostrar las imágenes generadas
            rx.cond(
                ArticleState.generated_images & (ArticleState.num_of_generated_images == 4),
                show_images()
            ),
        

            padding="2em",
            width="100%",
            margin="auto",
            box_shadow="lg",
        ),                
        rx.spacer(),
        rx.spacer(),

        footer(),
        width="100%",
        align_items="center",
        min_height="100vh",

        background_color="#FEEBEE", 

    
    )
        

