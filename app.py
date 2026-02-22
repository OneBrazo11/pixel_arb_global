import streamlit as st

st.set_page_config(page_title="Calculadora Surebets", page_icon="🧮")

st.title("🧮 Calculadora de Arbitraje Exacto")
st.markdown("Calcula el monto exacto (Stake) a invertir en cada cuota para asegurar ganancia, sin importar el resultado.")

# --- ENTRADA DE DATOS ---
inversion = st.number_input("💰 Capital Total a Invertir ($):", min_value=1.0, value=100.0, step=10.0)

opciones = st.radio("Número de resultados posibles en el evento:", [2, 3], horizontal=True)

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1: 
    cuota1 = st.number_input("Cuota Opción 1:", min_value=1.01, value=2.0, step=0.1)
with col2: 
    cuota2 = st.number_input("Cuota Opción 2:", min_value=1.01, value=2.0, step=0.1)
with col3: 
    if opciones == 3:
        cuota3 = st.number_input("Cuota Opción 3 (Empate):", min_value=1.01, value=2.0, step=0.1)
    else:
        cuota3 = 0.0

# --- CÁLCULO MATEMÁTICO ---
if st.button("🚀 CALCULAR INVERSIÓN", type="primary"):
    
    prob1 = 1 / cuota1
    prob2 = 1 / cuota2
    prob3 = (1 / cuota3) if opciones == 3 else 0.0
    
    margen_total = prob1 + prob2 + prob3
    
    st.markdown("---")
    
    if margen_total < 1.0:
        rentabilidad = (1.0 / margen_total) - 1.0
        ganancia_neta = inversion * rentabilidad
        retorno_total = inversion + ganancia_neta
        
        st.success(f"🔥 ¡SUREBET MATEMÁTICA CONFIRMADA! (Rentabilidad: {rentabilidad*100:.2f}%)")
        st.metric("Beneficio Neto Asegurado", f"${ganancia_neta:.2f}")
        
        st.markdown("### 📌 Distribución exacta de tu capital:")
        
        stake1 = retorno_total / cuota1
        stake2 = retorno_total / cuota2
        
        st.info(f"👉 **Apostar en Cuota 1 ({cuota1}):** ${stake1:.2f}")
        st.info(f"👉 **Apostar en Cuota 2 ({cuota2}):** ${stake2:.2f}")
        
        if opciones == 3:
            stake3 = retorno_total / cuota3
            st.info(f"👉 **Apostar en Cuota 3 ({cuota3}):** ${stake3:.2f}")
            
        # Pensamiento crítico sobre las cuentas
        st.warning("""
        **OJO CON LOS DECIMALES:** Apostar cantidades extrañas como `$43.27` levanta sospechas inmediatas en las casas de apuestas y te pueden limitar la cuenta por 'arbitrajista'. 
        Es recomendable redondear al dólar entero más cercano (ej. `$43.00` o `$45.00`), aunque esto signifique que la ganancia varíe ligeramente dependiendo de quién gane.
        """)
        
    else:
        perdida = (1.0 - (1.0 / margen_total)) * 100
        st.error(f"❌ NO HAY ARBITRAJE. La casa tiene un margen de beneficio del {perdida:.2f}%. Perderías dinero a largo plazo.")
