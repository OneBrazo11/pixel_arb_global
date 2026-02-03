import streamlit as st
import pandas as pd
import time
from main import ArbitrageEngine, fetch_live_data_mock

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="PixelArb Global",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS (MODO DARK/PIXEL TRADER) ---
st.markdown("""
    <style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .stMetric { background-color: #1E1E1E; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONFIGURACIÓN ---
with st.sidebar:
    st.title("🎛️ Centro de Control")
    st.markdown("---")
    bankroll_input = st.number_input("Capital Disponible ($)", min_value=100, value=500, step=50)
    min_roi = st.slider("ROI Mínimo (%)", 0.0, 10.0, 1.0)
    
    st.markdown("### 📡 Estado del Sistema")
    st.info("Conectado a 13 Bookies Globales")
    
    scan_btn = st.button("ESCANEAR AHORA 🚀", type="primary")

# --- ÁREA PRINCIPAL ---
st.title("⚡ PixelArb Global | Matriz de Arbitraje")
st.markdown(f"Gestionando capital de: **${bankroll_input}**")

if scan_btn:
    with st.spinner('Escaneando Pinnacle, 1xBet, Stake y más...'):
        # 1. Instanciar el motor con el capital del usuario
        bot = ArbitrageEngine(bankroll=bankroll_input)
        
        # 2. Obtener datos (Simulados por ahora, luego reales)
        # Nota: Aquí llamamos a la función que creaste en main.py
        raw_data = fetch_live_data_mock()
        
        # 3. Procesar arbitraje
        for event, odds_matrix in raw_data.items():
            bot.calculate_arbitrage(event, "Winner (1x2/ML)", odds_matrix)
        
        # Simular pequeño delay para efecto visual
        time.sleep(1.5)

    # --- MOSTRAR RESULTADOS ---
    if bot.opportunities:
        # Filtrar por ROI mínimo seleccionado
        df = pd.DataFrame(bot.opportunities)
        df_filtered = df[df['ROI (%)'] >= min_roi]
        
        if not df_filtered.empty:
            st.success(f"¡Se encontraron {len(df_filtered)} oportunidades rentables!")
            
            # Métricas Clave
            col1, col2, col3 = st.columns(3)
            best_arb = df_filtered.loc[df_filtered['ROI (%)'].idxmax()]
            
            col1.metric("Mejor ROI", f"{best_arb['ROI (%)']}%")
            col2.metric("Beneficio Neto", f"${best_arb['Beneficio']}")
            col3.metric("Evento Top", best_arb['Evento'])
            
            # Tabla Interactiva
            st.markdown("### 📊 Tabla de Ejecución")
            st.dataframe(
                df_filtered.style.background_gradient(subset=['ROI (%)'], cmap='Greens'),
                use_container_width=True
            )
            
            st.markdown("---")
            st.warning("⚠️ Recuerda verificar las cuotas manualmente antes de apostar.")
        else:
            st.warning(f"Hay surebets, pero ninguna supera tu filtro del {min_roi}% de ROI.")
    else:
        st.error("No se encontraron oportunidades en este escaneo. El mercado está eficiente.")

else:
    st.info("👈 Presiona 'ESCANEAR AHORA' en la barra lateral para buscar surebets.")
