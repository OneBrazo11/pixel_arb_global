import streamlit as st
import pandas as pd
import requests
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="PIXEL GLOBAL ODDS HUNTER", layout="wide", page_icon="🚀")

st.markdown("""
<style>
    .success-box {padding: 10px; background-color: #d4edda; color: #155724; border-radius: 5px; margin-bottom: 10px; border: 1px solid #c3e6cb;}
    .warning-box {padding: 10px; background-color: #f8f9fa; color: #383d41; border-radius: 5px; margin-bottom: 10px; border: 1px solid #d6d8db;}
    .best-price {font-weight: bold; font-size: 1.2em; color: #155724;}
    .surebet-alert {padding: 15px; background-color: #28a745; color: white; border-radius: 8px; font-weight: bold; text-align: center; margin-bottom: 15px;}
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS Y THE ODDS API ---
try:
    API_KEY = st.secrets["ODDS_API_KEY"]
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Base_Datos_GOH").sheet1
except Exception as e:
    st.error("⚠️ Error conectando a la base de datos o API. Revisa los secretos en Streamlit.")
    st.stop()

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.licencia = ""
    st.session_state.creditos = 0

# --- MURO DE PAGO ---
if not st.session_state.autenticado:
    st.title("🔒 Acceso a PIXEL GLOBAL ODDS HUNTER")
    licencia_input = st.text_input("Introduce tu Licencia Whop (Ej: USER-001):", type="password")
    
    if st.button("Ingresar", type="primary"):
        df = pd.DataFrame(sheet.get_all_records())
        usuario = df[df['License_Key'] == licencia_input]
        
        if not usuario.empty:
            estado = str(usuario.iloc[0]['Estado']).strip().lower()
            creditos = int(usuario.iloc[0]['Creditos'])
            
            if estado == "activo" and creditos > 0:
                st.session_state.autenticado = True
                st.session_state.licencia = licencia_input
                st.session_state.creditos = creditos
                st.rerun()
            else:
                st.error("❌ Licencia inactiva o sin créditos suficientes.")
        else:
            st.error("❌ Licencia no encontrada.")

# --- APP PRINCIPAL ---
else:
    st.sidebar.success(f"🟢 Conectado | Créditos: {st.session_state.creditos}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    tab1, tab2 = st.tabs(["📡 Escáner de Cuotas", "🧮 Calculadora Surebets"])

    # ==========================
    # PESTAÑA 1: ESCÁNER
    # ==========================
    with tab1:
        st.markdown("### 📡 Radar de Apuestas: Búsqueda de Valor y Arbitraje.")
        
        def get_active_sports(key):
            try: return requests.get(f"https://api.the-odds-api.com/v4/sports?apiKey={key}").json()
            except: return []

        def get_odds_global(key, sport, market):
            params = {'apiKey': key, 'regions': 'us,uk,eu,au', 'markets': market, 'oddsFormat': 'decimal'}
            try:
                r = requests.get(f"https://api.the-odds-api.com/v4/sports/{sport}/odds", params=params)
                return (r.json(), None) if r.status_code == 200 else (None, r.text)
            except Exception as e: return None, str(e)

        st.sidebar.markdown("---")
        sports_data = get_active_sports(API_KEY)
        
        if sports_data:
            sport_options = {s['title']: s['key'] for s in sports_data}
            
            search_filter = st.sidebar.text_input("🔍 Filtrar Liga (Ej: NBA):", value="")
            
            if search_filter != "":
                filtered_options = [x for x in sport_options.keys() if search_filter.lower() in x.lower()]
            else:
                filtered_options = list(sport_options.keys())

            if filtered_options:
                selected_sport_name = st.sidebar.selectbox("Elige:", filtered_options)
                selected_sport_key = sport_options[selected_sport_name]

                bet_type = st.sidebar.selectbox("Tipo de Apuesta:", ["Ganador (Moneyline)", "Hándicap (Spread)", "Totales (Over/Under)", "Par / Impar (Even/Odd)"])
                period_type = st.sidebar.selectbox("Periodo:", ["Partido Completo", "1ra Mitad (1H)", "2da Mitad (2H)"])

                api_market = "h2h"
                if "Hándicap" in bet_type: api_market = "spreads"
                elif "Totales" in bet_type: api_market = "totals"
                elif "Par / Impar" in bet_type: api_market = "even_odd"

                if "1ra Mitad" in period_type: api_market += "_h1"
                elif "2da Mitad" in period_type: api_market += "_h2"

                if st.button("🚀 BUSCAR CUOTAS (-1 Crédito)", type="primary"):
                    if st.session_state.creditos <= 0:
                        st.error("No tienes créditos.")
                    else:
                        with st.spinner("Descontando crédito y buscando cuotas..."):
                            cell = sheet.find(st.session_state.licencia)
                            fila = cell.row
                            st.session_state.creditos -= 1
                            sheet.update_cell(fila, 3, st.session_state.creditos) 

                            data, error = get_odds_global(API_KEY, selected_sport_key, api_market)

                            if error: st.error(f"Error API: {error}")
                            elif not data: st.warning("No hay cuotas activas para este mercado ahora mismo.")
                            else:
                                st.success(f"¡Encontrados {len(data)} eventos!")
                                for game in data:
                                    home = game['home_team']
                                    away = game['away_team']
                                    odds_pool = {} 

                                    for book in game['bookmakers']:
                                        book_name = book['title']
                                        for market in book['markets']:
                                            if market['key'] == api_market:
                                                for outcome in market['outcomes']:
                                                    label = f"{outcome['name']} ({outcome.get('point', '')})" if outcome.get('point', '') else outcome['name']
                                                    if label not in odds_pool: odds_pool[label] = []
                                                    odds_pool[label].append({'Casa': book_name, 'Cuota': outcome['price']})

                                    if odds_pool:
                                        with st.expander(f"{home} vs {away} | {period_type}", expanded=True):
                                            best_odds_for_arbitrage = []
                                            for sel, entries in odds_pool.items():
                                                df = pd.DataFrame(entries)
                                                if not df.empty: best_odds_for_arbitrage.append(df['Cuota'].max())
                                            
                                            if len(best_odds_for_arbitrage) > 1:
                                                implied_prob_sum = sum(1 / odd for odd in best_odds_for_arbitrage)
                                                if implied_prob_sum < 1.0:
                                                    profit_margin = (1.0 / implied_prob_sum - 1.0) * 100
                                                    st.markdown(f"<div class='surebet-alert'>🔥 ¡SUREBET DETECTADA! Ganancia asegurada: {profit_margin:.2f}%</div>", unsafe_allow_html=True)

                                            cols = st.columns(len(odds_pool))
                                            for idx, (selection, entries) in enumerate(odds_pool.items()):
                                                df = pd.DataFrame(entries)
                                                if df.empty: continue
                                                max_odd = df['Cuota'].max()
                                                best_books = ", ".join(df[df['Cuota'] == max_odd]['Casa'].tolist()[:3])
                                                
                                                with cols[idx % len(cols)]:
                                                    st.markdown(f"<div class='success-box'>**{selection}**<br><span class='best-price'>💎 {max_odd}</span><br><small>{best_books}</small></div>", unsafe_allow_html=True)
                                            
                                            # --- TABLA DETALLADA RESTAURADA ---
                                            all_rows = [{'Selección': sel, 'Casa': e['Casa'], 'Cuota': e['Cuota']} for sel, entries in odds_pool.items() for e in entries]
                                            if all_rows:
                                                try:
                                                    df_pivot = pd.DataFrame(all_rows).pivot(index='Casa', columns='Selección', values='Cuota')
                                                    st.dataframe(df_pivot.style.highlight_max(axis=0, color='#d4edda'), use_container_width=True)
                                                except:
                                                    st.dataframe(pd.DataFrame(all_rows))

    # ==========================
    # PESTAÑA 2: CALCULADORA
    # ==========================
    with tab2:
        st.markdown("### 🧮 Calculadora de Arbitraje Exacto")
        inversion = st.number_input("💰 Capital Total a Invertir ($):", min_value=1.0, value=100.0, step=10.0)
        opciones = st.radio("Resultados posibles:", [2, 3], horizontal=True)

        col1, col2, col3 = st.columns(3)
        with col1: cuota1 = st.number_input("Cuota Opción 1:", min_value=1.01, value=2.0, step=0.1)
        with col2: cuota2 = st.number_input("Cuota Opción 2:", min_value=1.01, value=2.0, step=0.1)
        with col3: cuota3 = st.number_input("Cuota 3 (Empate):", min_value=1.01, value=2.0, step=0.1) if opciones == 3 else 0.0

        if st.button("🚀 CALCULAR INVERSIÓN", type="primary"):
            margen_total = (1/cuota1) + (1/cuota2) + ((1/cuota3) if opciones == 3 else 0.0)
            if margen_total < 1.0:
                rentabilidad = (1.0 / margen_total) - 1.0
                st.success(f"🔥 SUREBET CONFIRMADA: {rentabilidad*100:.2f}% de rentabilidad.")
                st.info(f"👉 Apostar en Cuota 1: ${(inversion + (inversion * rentabilidad)) / cuota1:.2f}")
                st.info(f"👉 Apostar en Cuota 2: ${(inversion + (inversion * rentabilidad)) / cuota2:.2f}")
                if opciones == 3: st.info(f"👉 Apostar en Cuota 3: ${(inversion + (inversion * rentabilidad)) / cuota3:.2f}")
            else:
                st.error("❌ NO HAY ARBITRAJE.")
