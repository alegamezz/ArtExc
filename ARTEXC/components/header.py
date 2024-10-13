
import reflex as rx

def header():
    return rx.box(
        rx.hstack(
                    # Logo o Título de la Aplicación
                    rx.text("ArtExc by AG", 
                font_weight="bold", 
                font_size=["1rem", "1.1rem", "1.25rem"],  # Tamaño más pequeño para móviles
                color="#FFFFFF"
        ),
        rx.hstack(
            rx.link("Inicio", href="/", color="#FFFFFF", font_size=["0.8rem", "0.9rem", "1rem"]),
            rx.link("Galería", href="/gallery", color="#FFFFFF", font_size=["0.8rem", "0.9rem", "1rem"]),
            rx.text("Sonia Blasco", color="#FFFFFF", font_size=["0.8rem", "0.9rem", "1rem"]),
            spacing="1.5rem",  
        ),
            justify_content="space-between",
            align_items="center",
            width="100%",
        ),
        padding="0rem 0.5rem",
        background="teal",
        box_shadow="0 2px 4px rgba(0, 0, 0, 0.1)",
        position="fixed",
        top="0",
        width="100%",
        z_index="1000",
    )