import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ================= CONFIGURACIÓN DE LA PÁGINA =================
st.set_page_config(page_title="EDRunners-Gestor", page_icon="🛒", layout="wide")

# ================= CONEXIÓN A GOOGLE SHEETS =================
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ... (el resto de tu código de configuración visual)

@st.cache_resource
def conectar_sheets():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # ✅ CAMBIO: Lee las credenciales desde st.secrets
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("EDRunners").worksheet("productos")
    return sheet

# ================= DISEÑO VISUAL =================
st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #10b981; margin-bottom: 0px; }
    .sub-header { color: #9ca3af; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">EDRunners™ Gestor de Inventario</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Agrega productos directamente a tu base de datos en Google Sheets.</p>', unsafe_allow_html=True)

# ================= FORMULARIO =================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📦 Detalles del Producto")
    
    with st.form("formulario_producto", clear_on_submit=True):
        nombre = st.text_input("Nombre del Producto (Ej: Samsung Galaxy A17)")
        
        col_cat, col_esp = st.columns(2)
        with col_cat:
            categoria = st.selectbox("Categoría", ["celular", "tv", "gaming", "accesorio", "belleza", "ventilador", "faro led", "camara", "electronica"])
        with col_esp:
            especificaciones = st.text_input("Especificaciones cortas (Ej: 128GB / 4GB RAM)")
            
        st.markdown("### 💰 Precios y Utilidad")
        col_costo, col_util, col_detal, col_mayor = st.columns(4)
        with col_costo:
            costo = st.number_input("Costo ($)", min_value=0.0, step=0.5)
        with col_util:
            utilidad = st.number_input("Utilidad ($)", min_value=0.0, step=0.5)
        with col_detal:
            # Cálculo visual automático
            precio_detal_visual = costo + utilidad
            st.metric("Precio Detal", f"${precio_detal_visual:.2f}")
        with col_mayor:
            # Cálculo visual automático del 10% de descuento
            precio_mayor_visual = precio_detal_visual * 0.9
            st.metric("Precio Mayor", f"${precio_mayor_visual:.2f}")

        st.markdown("### 📦 Inventario y Multimedia")
        col_stock, col_etiqueta = st.columns(2)
        with col_stock:
            stock = st.selectbox("Stock", ["disponible", "pocas", "agotado"])
        with col_etiqueta:
            etiqueta = st.selectbox("Etiqueta Visual", ["", "NUEVO", "OFERTA", "TOP"])
            
        imagen_url = st.text_input("URL de la Imagen (ImgBB)")
        descripcion = st.text_area("Descripción del Producto (Opcional)")
        relacionados = st.text_input("IDs Relacionados (Opcional - ej: SAM-001, TVB-002)")

        # Botón de envío
        submit_button = st.form_submit_button("✅ Agregar a Google Sheets")

# ================= LÓGICA DE GUARDADO =================
if submit_button:
    if not nombre or not imagen_url:
        st.warning("⚠️ El nombre y la URL de la imagen son obligatorios.")
    else:
        with st.spinner("Guardando en Google Sheets..."):
            try:
                # Calcular la nueva fila
                col_orden = sheet.col_values(1)
                productos_reales = [x for x in col_orden[1:] if x != '']
                nuevo_orden_num = len(productos_reales) + 1
                fila = nuevo_orden_num + 1

                nueva_fila = [
                    nuevo_orden_num,
                    f'=SI(C{fila}=""; ""; MAYUSC(IZQUIERDA(C{fila}; 3)) & "-" & TEXTO(A{fila}; "000"))',
                    nombre,
                    categoria,
                    especificaciones,
                    costo,
                    utilidad,
                    f'=F{fila}+G{fila}',
                    f'=H{fila}*(1-0,10)',
                    f'=H{fila}',
                    f'=REDONDEAR(J{fila}*$S$2; 2)', # Asegúrate que B1 es la tasa
                    stock,
                    etiqueta,
                    imagen_url,
                    "",
                    descripcion,
                    relacionados,
                    ""
                ]
                
                sheet.append_row(nueva_fila, value_input_option='USER_ENTERED')
                st.success(f"🎉 ¡Producto '{nombre}' agregado exitosamente a la hoja!")
                st.balloons() # Efecto visual de celebración
            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")

# ================= PANEL DERECHO (VISTA PREVIA) =================
with col2:
    st.info("🔗 **Google Sheets Status:** Conectado")
    st.markdown("---")
    st.subheader("📋 Últimos 5 productos")
    try:
        # Obtener los últimos 5 registros para la vista previa
        registros = sheet.get_all_records()
        ultimos = registros[-5:] if len(registros) >= 5 else registros
        for prod in reversed(ultimos):
            st.markdown(f"**{prod.get('nombre', '')}**")
            st.caption(f"Costo: ${prod.get('costo_usd', '')} | Detal: ${prod.get('precio', '')} | Stock: {prod.get('stock', '')}")
            st.markdown("---")
    except:
        st.write("No hay datos recientes.")
