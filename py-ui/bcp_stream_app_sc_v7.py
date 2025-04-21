import streamlit as st
import base64
import fitz  # PyMuPDF
import requests
import json

# -------------------------------
# Mostrar PDF en visor integrado
# -------------------------------
def show_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# -------------------------------
# Analizar líneas clave, referencias y negrita con mejora
# -------------------------------
def extract_info_from_pdf(uploaded_file, keywords):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    all_lines = []
    entidades_detectadas = set()
    lineas_clave = []
    referencias = []
    bold_texts = set()

    for page in doc:
        lines = page.get_text("text").split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            lowered_line = line.lower()
            if any(lowered_line == k.lower().replace(":", "") or lowered_line == k.lower() for k in keywords):
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    line = line + " " + next_line
                    i += 1

            all_lines.append(line)

            for keyword in keywords:
                if keyword.lower() in line.lower():
                    lineas_clave.append(line)
                    parts = line.split(":")
                    if len(parts) > 1:
                        entidad = parts[1].strip()
                        if entidad:
                            entidades_detectadas.add(entidad)
            i += 1

        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    if span.get("flags", 0) in [20, 21] or "Bold" in span.get("font", ""):
                        text = span["text"].strip()
                        if text:
                            bold_texts.add(text)

    for linea in all_lines:
        for entidad in entidades_detectadas:
            if entidad in linea and linea not in lineas_clave:
                referencias.append(linea)

    return {
        "lineas_clave": lineas_clave,
        "entidades": list(entidades_detectadas),
        "referencias": referencias,
        "negritas": list(bold_texts),
    }

# -------------------------------
# Interfaz principal
# -------------------------------
st.set_page_config(page_title="🧠 Buscador y Analizador PDF", layout="centered")
st.title("🧠 Buscador Semántico + Análisis Inteligente de Documentos PDF")
st.markdown("Consulta documentos por texto libre y analiza archivos PDF con IA.")

# -------------------------------
# PRIMER BLOQUE - Búsqueda semántica
# -------------------------------
st.markdown("## 🔍 Consulta Semántica")
proyecto = st.selectbox("Seleccione el Proyecto:", options=["YAPE", "MBBK"])
consulta = st.text_input(
    f"Ingrese su consulta sobre {proyecto}:",
    placeholder="Ejemplo: Firewall del Área Perimetral"
)
k = st.slider("Número de resultados:", min_value=1, max_value=5, value=3)

if st.button("Buscar"):
    if not consulta.strip():
        st.warning("Por favor, ingrese una consulta válida.")
    else:
        st.info(f"Proyecto seleccionado: {proyecto}")
        full_query = f"{consulta} {proyecto}"
        url = f"http://127.0.0.1:8000/buscar/?query={full_query}&k={k}"
        try:
            response = requests.get(url)
            data = response.json()
            st.subheader("📄 Resultados:")
            for i, r in enumerate(data["resultados"]):
                st.markdown(f"**{i+1}.** *{r['documento']}*")
                st.progress(r['similitud'])
        except Exception as e:
            st.error(f"Error al consultar la API: {e}")

# -------------------------------
# SEGUNDO BLOQUE - Análisis del PDF
# -------------------------------
st.markdown("---")
st.markdown("## 📄 Análisis Avanzado de PDF")

uploaded_pdf = st.file_uploader("📄 Sube un archivo PDF para analizar", type=["pdf"])

if uploaded_pdf:
    st.download_button(
        label="📥 Descargar PDF",
        data=uploaded_pdf,
        file_name=uploaded_pdf.name,
        mime="application/pdf"
    )

    uploaded_pdf.seek(0)
    show_pdf(uploaded_pdf)

    st.markdown("### 🔎 Resultados del Análisis del PDF")
    keywords = ["API:", "Microservicios:", "BasedeDatos:"]

    uploaded_pdf.seek(0)
    resultados = extract_info_from_pdf(uploaded_pdf, keywords)

    st.subheader("📌 Líneas Clave Detectadas:")
    if resultados["lineas_clave"]:
        for i, linea in enumerate(resultados["lineas_clave"]):
            st.markdown(f"**{i+1}.** {linea}")
    else:
        st.info("No se encontraron líneas clave.")

    st.subheader("📎 Referencias Detectadas en el Texto:")
    if resultados["referencias"]:
        for i, ref in enumerate(resultados["referencias"]):
            st.markdown(f"**{i+1}.** {ref}")
    else:
        st.info("No se encontraron referencias a entidades clave.")

    st.subheader("🖍️ Texto Detectado en Negrita:")
    negritas_limpias = [t for t in resultados["negritas"] if t.strip()]
    if negritas_limpias:
        for i, bold in enumerate(negritas_limpias):
            st.markdown(f"**{i+1}.** {bold}")
    else:
        st.info("No se detectó texto en negrita.")