import joblib
import pandas as pd
import time
import random

features = joblib.load('ndr_modelos/feature_names.joblib')
df = pd.DataFrame([[0.0]*len(features)], columns=features)

print("Iniciando Injeção Contínua de Teste (Pressione Ctrl+C para parar)...")

# Mistura de tráfego (Maioria é benigno para gerar um gráfico realista)
opcoes_de_ips = [
    # IPs Benignos (Usuários normais na rede)
    ('192.168.1.10', 443), ('192.168.1.11', 80), ('192.168.1.15', 8080),
    ('192.168.1.10', 443), ('192.168.1.11', 80), ('192.168.1.15', 8080),
    ('192.168.1.10', 443), ('192.168.1.11', 80), ('192.168.1.15', 8080),
    
    # IPs de Ataque (Ondas maliciosas)
    ('192.168.1.100', 12345), # Simulador de DDoS
    ('192.168.1.101', 54321), # Simulador de PortScan
    ('192.168.1.102', 4444),  # Simulador de Bot
    ('192.168.1.103', 80)     # Simulador de Brute Force
]

try:
    while True:
        # Sorteia um IP da lista acima
        ip_origem, porta = random.choice(opcoes_de_ips)
        
        df['Src IP'] = [ip_origem]
        df['Dst IP'] = ['10.0.0.5']         
        df['Src Port'] = [porta]
        df['Dst Port'] = [80]
        
        df.to_csv('realtime_traffic.csv', mode='a', index=False, header=False)
        print(f"Pacote disparado de {ip_origem}:{porta}")
        
        # Pausa aleatória entre 0.5s e 2s para parecer tráfego orgânico no Grafana
        time.sleep(random.uniform(0.5, 2.0))
except KeyboardInterrupt:
    print("\nSimulação de Rede encerrada.")
