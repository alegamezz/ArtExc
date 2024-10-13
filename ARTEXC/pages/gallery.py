#will contain all the images in plantillas
import reflex as rx

from ARTEXC.components.footer import footer
from ARTEXC.components.header import header
from ARTEXC.states import ArticleState, GalleryState



@rx.page(route="/gallery", on_load=GalleryState.on_load,)
def gallery():
    return rx.vstack(
        header(),
        rx.spacer(),
        rx.spacer(),
        rx.vstack(
            rx.spacer(),
            rx.text("Galería de imágenes", size="7", color="teal", font_weight="bold"),
            rx.upload(
                rx.text("Arrastra y suelta imágenes aquí o haz click para seleccionar", size="3", color="gray"),
                border="1px dotted rgb(107,99,246)",
                multiple=True,
                accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"]},
                max_files=5,
                on_drop=GalleryState.handle_upload(rx.upload_files()),
                width=["80%", "100%"],
                border_radius="8px",
            ),
            align_items="center",
            width=["100%", "50%"],
        ),
        rx.flex(
            rx.foreach(
                GalleryState.images,
                lambda image: rx.vstack(
                    rx.image(
                        src=rx.get_upload_url(image),
                        height="200px",
                        width="200px",
                        object_fit="cover",
                        margin="1em",
                        border_radius="8px",  
                        box_shadow="0 4px 15px rgba(0, 0, 0, 0.4)",  
                    ),
                    rx.alert_dialog.root(
                        rx.alert_dialog.trigger(
                            rx.radix.icon_button(
                                "trash",  
                                position="absolute",
                                bottom="20px",  
                                right="20px",  
                                color_scheme="ruby",
                                size="1",
                            ),
                        ),
                        rx.alert_dialog.content(
                            rx.alert_dialog.title("Confirmar eliminación"),
                            rx.alert_dialog.description(
                                rx.vstack(
                                    rx.text("¿Estás seguro que quieres eliminar esta imagen?"),
                                    rx.spacer(),
                                    rx.image(
                                        src=rx.get_upload_url(image),
                                        height="150px",
                                        width="150px",
                                        object_fit="cover",
                                        border_radius="8px",  
                                        box_shadow="0 4px 15px rgba(0, 0, 0, 0.4)",  
                                    ),
                                    rx.spacer(),
                                    align_items="center",
                                )
                            ),
                            rx.flex(
                                rx.alert_dialog.cancel(
                                    rx.button("Cancelar", variant="soft", color_scheme="gray"),
                                ),
                                rx.alert_dialog.action(
                                    rx.button(
                                        "Eliminar",
                                        color_scheme="red",
                                        on_click=GalleryState.delete_image(image),
                                    ),
                                ),
                                spacing="3",
                                justify="end",
                            ),
                        ),
                    ),
                    align_items="center",
                    position="relative",
                ),
            ),
            flex_wrap="wrap",
            justify="center",
        ),

        footer(),
        spacing="2em",
        align_items="center",
        min_height="100vh",

        background_color="#FEEBEE", 
    )