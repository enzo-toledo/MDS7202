"""
Frontend de ChaucherApp: interfaz de priorización de tickets de soporte.

App de Gradio (modalidad gr.Blocks) que recoge los atributos de un ticket
y de su usuario, y llama al backend para predecir el nivel de prioridad.
"""

import datetime as dt

import gradio as gr
import requests
from services import enviar_prediccion

# --------------------------------------------------------------------------- #
# Opciones de los campos categóricos
# --------------------------------------------------------------------------- #
CANALES = ["Correo", "Página Web", "Whatsapp"]
CATEGORIAS = ["Cobros", "Cuenta", "Fraude", "Otro", "Pregunta general", "Técnica"]
TIPOS_CUENTA = ["Free", "Premium", "Business"]

# Colores por nivel de prioridad para la tarjeta de resultado.
COLORES_PRIORIDAD = {
    "baja": ("#10B981", "Prioridad baja: puede resolverse en el flujo normal."),
    "media": ("#F59E0B", "Prioridad media: atender dentro de los tiempos habituales."),
    "alta": ("#F97316", "Prioridad alta: conviene atenderlo pronto."),
    "critica": ("#EF4444", "Prioridad crítica: requiere atención inmediata."),
}

# --------------------------------------------------------------------------- #
# Paleta de la marca
# --------------------------------------------------------------------------- #
COLOR_PRIMARIO = "#1AA5C7"  # cian-teal (la moneda del logo)
COLOR_PRIMARIO_OSCURO = "#127D98"
COLOR_ACENTO = "#6D5DF5"  # violeta holográfico de las pantallas
COLOR_TEXTO = "#1E293B"  # slate oscuro (texto)

CSS = f"""
#encabezado {{
    background: linear-gradient(120deg, {COLOR_PRIMARIO} 0%, #4B6FE3 55%, {COLOR_ACENTO} 100%);
    color: white;
    padding: 22px 28px;
    border-radius: 16px;
    margin-bottom: 8px;
}}
#encabezado h1 {{ margin: 0; font-size: 1.6rem; }}
#encabezado p  {{ margin: 6px 0 0 0; opacity: 0.92; }}
.seccion-titulo {{
    color: #2B3A67;
    font-weight: 700;
    font-size: 1.05rem;
    border-left: 4px solid {COLOR_PRIMARIO};
    padding-left: 10px;
    margin-bottom: 4px;
}}
#tarjeta-resultado {{ min-height: 90px; }}
"""


def _tarjeta(titulo: str, subtitulo: str, color: str) -> str:
    """Genera el HTML de una tarjeta de resultado con el color indicado."""
    return f"""
    <div style="
        background:{color};
        color:white;
        border-radius:14px;
        padding:20px 24px;
        text-align:center;
        box-shadow:0 4px 14px rgba(0,0,0,0.12);">
        <div style="font-size:0.85rem; text-transform:uppercase; letter-spacing:1px; opacity:0.9;">
            Nivel de prioridad
        </div>
        <div style="font-size:2rem; font-weight:800; margin:4px 0;">{titulo}</div>
        <div style="font-size:0.95rem; opacity:0.95;">{subtitulo}</div>
    </div>
    """


def clasificar(asunto, contenido, canal, categoria, fecha, tipo_cuenta, antiguedad):
    """
    Handler del botón. Valida la entrada, llama al backend y devuelve el HTML
    de la tarjeta de resultado.

    Solo `asunto` y `contenido` se envían al modelo (ver services.py); el resto
    de campos se recogen para tener una ficha de ticket completa y realista.
    """
    if not (asunto and asunto.strip()) or not (contenido and contenido.strip()):
        return _tarjeta(
            "Faltan datos",
            "Ingresa al menos el asunto y el contenido del ticket.",
            "#64748B",
        )

    try:
        prioridad = enviar_prediccion(asunto, contenido)
    except requests.exceptions.RequestException as e:
        return _tarjeta(
            "Sin conexión con el servicio",
            f"No se pudo contactar al backend: {e}",
            "#64748B",
        )

    clave = str(prioridad).strip().lower()
    color, descripcion = COLORES_PRIORIDAD.get(clave, ("#64748B", ""))
    return _tarjeta(prioridad, descripcion, color)


def contar_caracteres(contenido):
    """Actualiza en vivo el N° de caracteres del contenido (feature N_Caracteres_Ticket)."""
    return len(contenido or "")


tema = gr.themes.Soft(
    primary_hue=gr.themes.Color(
        c50="#E6F7FB",
        c100="#C3ECF4",
        c200="#93DCEB",
        c300="#5FC8DE",
        c400="#33B3CE",
        c500=COLOR_PRIMARIO,
        c600=COLOR_PRIMARIO_OSCURO,
        c700="#0E6379",
        c800="#0A4C5D",
        c900="#073744",
        c950="#04222A",
    ),
    secondary_hue="indigo",
    neutral_hue="slate",
).set(body_text_color=COLOR_TEXTO)


with gr.Blocks(title="ChaucherApp · Priorización de Tickets", theme=tema, css=CSS) as demo:
    gr.HTML(
        """
        <div id="encabezado">
            <h1>💰 ChaucherApp · Priorización de Tickets</h1>
            <p>Clasifica la prioridad de un ticket de soporte a partir de su contenido.</p>
        </div>
        """
    )

    with gr.Row():
        # ------------------------- Columna de entrada ------------------------ #
        with gr.Column(scale=3):
            gr.HTML('<div class="seccion-titulo">📩 Atributos del ticket</div>')
            with gr.Group():
                asunto = gr.Textbox(
                    label="Asunto",
                    placeholder="Ej: Cobro desconocido en mi tarjeta",
                )
                contenido = gr.Textbox(
                    label="Contenido",
                    placeholder="Describe el problema tal como lo reportó el usuario...",
                    lines=6,
                )
                with gr.Row():
                    canal = gr.Dropdown(
                        label="Canal",
                        choices=CANALES,
                        value="Whatsapp",
                    )
                    categoria = gr.Dropdown(
                        label="Categoría del problema",
                        choices=CATEGORIAS,
                        value="Cobros",
                    )
                with gr.Row():
                    fecha = gr.Textbox(
                        label="Fecha de envío",
                        value=dt.date.today().isoformat(),
                        placeholder="AAAA-MM-DD",
                    )
                    n_caracteres = gr.Number(
                        label="N° de caracteres (auto)",
                        value=0,
                        interactive=False,
                    )

            gr.HTML('<div class="seccion-titulo">👤 Atributos del usuario</div>')
            with gr.Group():
                with gr.Row():
                    tipo_cuenta = gr.Dropdown(
                        label="Tipo de cuenta",
                        choices=TIPOS_CUENTA,
                        value="Free",
                    )
                    antiguedad = gr.Slider(
                        label="Antigüedad de la cuenta (días)",
                        minimum=0,
                        maximum=1200,
                        step=1,
                        value=120,
                    )

            boton = gr.Button("Clasificar prioridad", variant="primary", size="lg")

        # ------------------------- Columna de salida ------------------------- #
        with gr.Column(scale=2):
            gr.HTML('<div class="seccion-titulo">🎯 Resultado</div>')
            resultado = gr.HTML(
                value=_tarjeta(
                    "—",
                    "Completa el ticket y presiona «Clasificar prioridad».",
                    "#B8C4D6",
                ),
                elem_id="tarjeta-resultado",
            )

    # ------------------------------- Eventos -------------------------------- #
    contenido.change(contar_caracteres, inputs=contenido, outputs=n_caracteres)

    boton.click(
        clasificar,
        inputs=[asunto, contenido, canal, categoria, fecha, tipo_cuenta, antiguedad],
        outputs=resultado,
    )


if __name__ == "__main__":
    # server_name=0.0.0.0 para que sea accesible desde fuera del contenedor.
    demo.launch(server_name="0.0.0.0", server_port=7860)
