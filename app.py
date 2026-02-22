import streamlit as st
import pandas as pd
import requests

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="GLOBAL ODDS HUNTER", layout="wide", page_icon="🚀")

# Estilos CSS
st.markdown("""
<style>
    .metric-card {background-color: #1e1e1e; border-radius: 10px; padding: 15px; text-align: center;}
    .big-font {font-size: 20px !important; font-weight: bold;}
    .success-box {padding: 10px; background-color: #d4edda; color: #155724; border-radius: 5px; margin-bottom: 10px; border: 1px solid #c3e6cb;}
    .warning-box {padding: 10px; background-color: #f8f9fa; color: #383d41; border-radius: 5px; margin-bottom: 10px; border: 1px solid #d6d8db;}
    .best-price {font-weight: bold; font-size: 1.2em; color: #155724;}
    .surebet-alert {padding: 15px; background-color: #28a745; color: white; border-radius: 8px; font-weight: bold; text-align: center; margin-bottom: 15px; border: 2px solid #1e7e34;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 GLOBAL ODDS HUNTER")
st.markdown("### 📡 Radar de Apuestas: Búsqueda de Valor y Arbitraje.")

# --- BARRA LATERAL (API KEY) ---
st.sidebar.header("🔑 Llave de Acceso")
api_key = st.sidebar.text_input("Tu API Key:", type="password")

if not api_key:
    st.warning("👈 Ingresa tu API Key en la barra lateral y presiona Enter.")
    st.stop()

# --- FUNCIONES ---
def get_quota_status(key):
    try:
        url = f"https://api.the-odds-api.com/v4/sports/?apiKey={key}"
        r = requests.get(url)
        return r.headers.get("x-requests-remaining", "0"), r.headers.get("x-requests-used", "0")
    except:
        return "?", "?"

def get_active_sports(key):
    url = f"https://api.the-odds-api.com/v4/sports?apiKey={key}"
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def get_odds_global(key, sport, market):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {'apiKey': key, 'regions': 'us,uk,eu,au', 'markets': market, 'oddsFormat': 'decimal'}
    try:
        r = requests.get(url, params=params)
        return (r.json(), None) if r.status_code == 200 else (None, r.text)
    except Exception as e:
        return None, str(e)

# --- PANEL DE CRÉDITOS ---
rem, used = get_quota_status(api_key)
col1, col2, col3 = st.columns(3)
col1.metric("💰 Créditos Restantes", rem)
col2.metric("📉 Créditos Usados", used)
col3.info("💡 Consejo: Usa el selector de Periodo para ahorrar créditos.")

if str(rem) == "0":
    st.error("⛔ SALDO AGOTADO. Crea una cuenta nueva.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("1. Liga")

sports_data = get_active_sports(api_key)
if not sports_data:
    st.error("Error cargando deportes. Revisa tu API Key.")
    st.stop()

sport_options = {s['title']: s['key'] for s in sports_data}
search_filter = st.sidebar.text_input("🔍 Filtrar (Ej: NBA):")
filtered_options = [x for x in sport_options.keys() if search_filter.lower() in x.lower()] if search_filter else list(sport_options.keys())

if not filtered_options:
    st.sidebar.warning("No encontrado.")
    st.stop()

selected_sport_name = st.sidebar.selectbox("Elige:", filtered_options)
selected_sport_key = sport_options[selected_sport_name]

# --- SELECTORES DE MERCADO ---
st.sidebar.subheader("2. Estrategia de Caza")
bet_type = st.sidebar.selectbox("Tipo de Apuesta:", ["Ganador (Moneyline)", "Hándicap (Spread)", "Totales (Over/Under)", "Par / Impar (Even/Odd)", "Doble Oportunidad (Double Chance)", "Empate No Válido (Draw No Bet)"])
period_type = st.sidebar.selectbox("Periodo:", ["Partido Completo", "1ra Mitad (1H)", "2da Mitad (2H)", "1er Cuarto (1Q)", "2do Cuarto (2Q)", "3er Cuarto (3Q)", "4to Cuarto (4Q)"])

# KEY API
api_market = "h2h"
if "Hándicap" in bet_type: api_market = "spreads"
elif "Totales" in bet_type: api_market = "totals"
elif "Par / Impar" in bet_type: api_market = "even_odd"
elif "Doble Oportunidad" in bet_type: api_market = "double_chance"
elif "Empate No Válido" in bet_type: api_market = "draw_no_bet"

if "1ra Mitad" in period_type: api_market += "_h1"
elif "2da Mitad" in period_type: api_market += "_h2"
elif "1er Cuarto" in period_type: api_market += "_q1"
elif "2do Cuarto" in period_type: api_market += "_q2"
elif "3er Cuarto" in period_type: api_market += "_q3"
elif "4to Cuarto" in period_type: api_market += "_q4"

st.sidebar.info(f"🔎 Mercado: **{api_market}**")

# --- ESCÁNER ---
st.markdown("---")
st.header(f"📡 Escáner: {selected_sport_name} - {period_type}")

if st.button("🚀 BUSCAR CUOTAS", type="primary"):
    with st.spinner("Rastreando cuotas y calculando arbitraje..."):
        data, error = get_odds_global(api_key, selected_sport_key, api_market)

        if error:
            st.error(f"Error API: {error}")
        elif not data:
            st.warning("No hay cuotas activas para este mercado ahora mismo.")
        else:
            st.success(f"¡Encontrados {len(data)} eventos!")
            
            for game in data:
                home = game['home_team']
                away = game['away_team']
                odds_pool = {} 

                # 1. Agrupar todas las cuotas
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
                        
                        # 2. Extraer la MEJOR cuota absoluta para cada resultado posible
                        best_odds_for_arbitrage = []
                        for sel, entries in odds_pool.items():
                            df = pd.DataFrame(entries)
                            if not df.empty:
                                best_odds_for_arbitrage.append(df['Cuota'].max())
                        
                        # 3. Calcular Arbitraje (Surebet)
                        if len(best_odds_for_arbitrage) > 1:
                            implied_prob_sum = sum(1 / odd for odd in best_odds_for_arbitrage)
                            
                            if implied_prob_sum < 1.0:
                                profit_margin = (1.0 / implied_prob_sum - 1.0) * 100
                                html_alert = f"""
                                <div class='surebet-alert'>
                                    🔥 ¡SUREBET DETECTADA! Ganancia asegurada: {profit_margin:.2f}%
                                </div>
                                """
                                st.markdown(html_alert, unsafe_allow_html=True)
                            else:
                                edge = (implied_prob_sum - 1.0) * 100
                                st.caption(f"Margen a favor de las casas (Edge): {edge:.2f}% | No hay arbitraje.")

                        # 4. Mostrar las cuotas en columnas
                        cols = st.columns(len(odds_pool))
                        for idx, (selection, entries) in enumerate(odds_pool.items()):
                            df = pd.DataFrame(entries)
                            if df.empty: continue
                            
                            max_odd = df['Cuota'].max()
                            best_books = ", ".join(df[df['Cuota'] == max_odd]['Casa'].tolist()[:3])
                            is_value = max_odd > (df['Cuota'].mean() * 1.04)
                            
                            with cols[idx % len(cols)]:
                                st.markdown(f"**{selection}**")
                                box_class = 'success-box' if is_value else 'warning-box'
                                extra_text = "<br><small style='color:green'>VALOR DETECTADO</small>" if is_value else ""
                                html_box = f"<div class='{box_class}'><span class='best-price'>💎 {max_odd}</span><br><small>{best_books}</small>{extra_text}</div>"
                                st.markdown(html_box, unsafe_allow_html=True)

                        # 5. Tabla detallada
                        all_rows = [{'Selección': sel, 'Casa': e['Casa'], 'Cuota': e['Cuota']} for sel, entries in odds_pool.items() for e in entries]
                        if all_rows:
                            try:
                                df_pivot = pd.DataFrame(all_rows).pivot(index='Casa', columns='Selección', values='Cuota')
                                st.dataframe(df_pivot.style.highlight_max(axis=0, color='#d4edda'), use_container_width=True)
                            except:
                                st.dataframe(pd.DataFrame(all_rows))
