import time
import random
from tabulate import tabulate
from colorama import Fore, Style, init

# Inicializar colores
init(autoreset=True)

class ArbitrageEngine:
    def __init__(self, bankroll=100):
        self.bankroll = bankroll
        self.opportunities = []

    def calculate_arbitrage(self, event, market_type, odds_data):
        """
        odds_data espera un dict: {'BookieName': {'1': 2.10, '2': 1.80}}
        """
        # 1. Encontrar mejor cuota para Opción 1 (Local/Over)
        best_odds_1 = 0
        bookie_1 = ""
        
        # 2. Encontrar mejor cuota para Opción 2 (Visitante/Under)
        best_odds_2 = 0
        bookie_2 = ""

        for bookie, odds in odds_data.items():
            if odds.get('1', 0) > best_odds_1:
                best_odds_1 = odds['1']
                bookie_1 = bookie
            
            if odds.get('2', 0) > best_odds_2:
                best_odds_2 = odds['2']
                bookie_2 = bookie

        # 3. Matemática de Arbitraje
        if best_odds_1 > 0 and best_odds_2 > 0:
            implied_prob = (1/best_odds_1) + (1/best_odds_2)
            
            if implied_prob < 1.0: # ¡SUREBET ENCONTRADA!
                roi = (1/implied_prob * 100) - 100
                
                # Calcular Stakes (Gestión de Capital)
                stake_1 = (self.bankroll * (1/best_odds_1)) / implied_prob
                stake_2 = (self.bankroll * (1/best_odds_2)) / implied_prob
                
                arb_obj = {
                    "Evento": event,
                    "Mercado": market_type,
                    "ROI (%)": round(roi, 2),
                    "Casa 1": bookie_1,
                    "Cuota 1": best_odds_1,
                    "Stake 1": round(stake_1, 2),
                    "Casa 2": bookie_2,
                    "Cuota 2": best_odds_2,
                    "Stake 2": round(stake_2, 2),
                    "Beneficio": round((stake_1 * best_odds_1) - self.bankroll, 2)
                }
                self.opportunities.append(arb_obj)

    def print_results(self):
        if not self.opportunities:
            print(Fore.YELLOW + "No se encontraron oportunidades de arbitraje en este escaneo.")
            return

        print(Fore.GREEN + f"\n=== OPORTUNIDADES ENCONTRADAS (Bankroll: ${self.bankroll}) ===")
        # Ordenar por mayor beneficio
        sorted_arbs = sorted(self.opportunities, key=lambda x: x['ROI (%)'], reverse=True)
        
        headers = sorted_arbs[0].keys()
        rows = [x.values() for x in sorted_arbs]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

# --- SIMULACIÓN DE DATOS (AQUÍ CONECTARÁS TUS SCRAPERS REALES) ---
# Como programador sabes que Betplay y Stake tienen estructuras HTML diferentes.
# He creado esta función para simular que ya extrajiste los datos.

def fetch_live_data_mock():
    """
    Simula la extracción de datos de las 13 casas.
    En producción, reemplazarás esto con llamadas a Selenium/Requests para cada casa.
    """
    print(Fore.CYAN + "Escaneando 13 casas de apuestas globales...")
    time.sleep(1) # Simula latencia de red
    
    # Datos Simulados para el ejemplo
    fake_odds_db = {
        "Lakers vs Celtics": {
            "Pinnacle": {'1': 1.90, '2': 1.90},
            "1xbet":    {'1': 2.05, '2': 1.85}, # Cuota alta al Local
            "Betano":   {'1': 1.88, '2': 1.92},
            "Stake":    {'1': 1.80, '2': 2.10}, # Cuota alta al Visitante -> ARBITRAJE CON 1XBET
            "Betplay":  {'1': 1.85, '2': 1.85},
            "William Hill": {'1': 1.95, '2': 1.91}
        },
        "Real Madrid vs Barcelona": {
            "Codere":   {'1': 2.50, '2': 1.50},
            "Betsson":  {'1': 2.40, '2': 1.55},
            "1win":     {'1': 2.65, '2': 1.45}, # Cuota muy alta Local
            "Rushbet":  {'1': 2.30, '2': 1.68}  # Cuota alta Visitante -> POSIBLE ARBITRAJE
        }
    }
    return fake_odds_db

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    bot = ArbitrageEngine(bankroll=500) # Bankroll simulado de $500
    
    # 1. Obtener Datos (Mock o Real)
    data = fetch_live_data_mock()
    
    # 2. Procesar Datos
    for event, odds_matrix in data.items():
        bot.calculate_arbitrage(event, "Winner (1x2/ML)", odds_matrix)
    
    # 3. Mostrar Resultados
    bot.print_results()
