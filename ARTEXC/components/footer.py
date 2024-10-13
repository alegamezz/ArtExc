import reflex as rx


def footer():
    return rx.box(
        rx.vstack(
            rx.text("© 2024 ArtExc by AG", font_weight="bold", font_size=["0.8rem", "0.9rem", "1rem"], color="#FFFFFF"),  # Blanco
            rx.text("All rights reserved", font_size=["0.7rem", "0.8rem", "0.9rem"], color="#D1D1D1"),  # Gris claro
            rx.hstack(
                rx.link("Privacy Policy", font_size=["0.8rem", "0.9rem", "1rem"], href="#", color="#38B2AC", _hover={"text_decoration": "underline"}),  # Verde-azulado
                rx.link("Terms of Service", font_size=["0.8rem", "0.9rem", "1rem"], href="#", color="#38B2AC", _hover={"text_decoration": "underline"}),
                rx.link("Contact Us",font_size=["0.8rem", "0.9rem", "1rem"], href="#", color="#38B2AC", _hover={"text_decoration": "underline"}),
                spacing="1.5rem",
            ),
              # Tamaño más pequeño para móviles

        ),
        padding="1rem",
        background="teal", 
        width="100%",
        align_items="center",
        justify_content="center",
    )