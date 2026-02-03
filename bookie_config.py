# Lista maestra de casas de apuestas soportadas
SUPPORTED_BOOKIES = [
    "1win", "Betwinner", "Betsson", "Olimpo Bet", 
    "Betano", "1xbet", "Pinnacle", "Betplay", 
    "Novibet", "William Hill", "Codere", "Stake", "Rushbet"
]

# Estructura de normalización de nombres de equipos
# (Vital para que el bot sepa que 'Real Madrid' es lo mismo que 'R. Madrid')
TEAM_MAPPING = {
    "Man City": "Manchester City",
    "Man. City": "Manchester City",
    "Utd": "United",
    # Agrega aquí tus normalizaciones a medida que encuentres errores
}
