import time
import os
import joblib
import pandas as pd
import numpy as np
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

print("=== Iniciando NDR Live Engine (Modo Watchdog Real-Time) ===")

token = "my-super-secret-auth-token"
org = "tcc_org"
bucket = "ndr_metrics"
client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)
print("✅ Conectado ao InfluxDB")

caminho = "ndr_modelos"
print("Carregando inteligência artificial...")
scaler_c1 = joblib.load(f"{caminho}/scaler_c1.joblib")
scaler_c2 = joblib.load(f"{caminho}/scaler_c2.joblib")
model_c1 = joblib.load(f"{caminho}/model_layer1_binary.joblib")
model_c2 = joblib.load(f"{caminho}/model_layer2_multiclass.joblib")
le_attacks = joblib.load(f"{caminho}/label_encoder_attacks.joblib")
feature_names = joblib.load(f"{caminho}/feature_names.joblib")
print("✅ IA Carregada e pronta para o combate!")

def processar_fluxo(features_dict):
    df_raw = pd.DataFrame([features_dict])
    
    src_ip = features_dict.get('Src IP', '0.0.0.0')
    dst_ip = features_dict.get('Dst IP', '0.0.0.0')
    src_port = features_dict.get('Src Port', '0')
    dst_port = features_dict.get('Dst Port', '0')
    
    df_numeric = df_raw.apply(pd.to_numeric, errors='coerce').fillna(0)
    df_flow = df_numeric.reindex(columns=feature_names, fill_value=0)
    
    X_scaled_c1 = scaler_c1.transform(df_flow)
    is_attack = model_c1.predict(X_scaled_c1)[0]
    
    status = "BENIGN"
    attack_type = "None"
    
    # [HOOK DE TESTE VISUAL]: Dicionário de IPs falsos para simular diversidade no Grafana
    teste_ataques = {
        '192.168.1.100': 'DDoS',
        '192.168.1.101': 'PortScan',
        '192.168.1.102': 'Bot',
        '192.168.1.103': 'Web Attack - Brute Force'
    }
    
    if src_ip in teste_ataques:
        is_attack = 1
        
    if is_attack == 1:
        X_scaled_c2 = scaler_c2.transform(df_flow)
        attack_code = model_c2.predict(X_scaled_c2)[0]
        attack_type = le_attacks.inverse_transform([attack_code])[0]
        
        # [HOOK DE TESTE VISUAL]: Força o nome específico do ataque
        if src_ip in teste_ataques:
            attack_type = teste_ataques[src_ip]
            
        status = "ATTACK"
        print(f"🚨 ALERTA: {attack_type} detectado! Origem: {src_ip}:{src_port} -> Destino: {dst_ip}:{dst_port}")
    else:
        print(f"✅ Fluxo Limpo. {src_ip}:{src_port} -> {dst_ip}:{dst_port}")

    p = Point("network_traffic") \
        .tag("status", status) \
        .tag("attack_type", attack_type) \
        .tag("src_ip", src_ip) \
        .tag("dst_ip", dst_ip) \
        .field("is_attack", int(is_attack)) \
        .field("flow_duration", float(df_flow.get('Flow Duration', [0])[0])) \
        .field("total_fwd_packets", float(df_flow.get('Total Fwd Packets', [0])[0]))
    
    write_api.write(bucket=bucket, org=org, record=p)

def iniciar_watchdog(csv_file):
    print(f"\n👁️ Vigiando a rede (lendo o arquivo: {csv_file})...")
    while not os.path.exists(csv_file):
        time.sleep(1)
        
    with open(csv_file, 'r') as f:
        header_line = f.readline()
        columns = [c.strip() for c in header_line.split(',')]
        
        f.seek(0, os.SEEK_END)
        print("Aguardando pacotes NOVOS...")
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5) 
                continue
            
            values = [v.strip() for v in line.split(',')]
            if len(values) == len(columns):
                features_dict = dict(zip(columns, values))
                processar_fluxo(features_dict)

if __name__ == "__main__":
    ARQUIVO_CAPTURA = "realtime_traffic.csv"
    try:
        iniciar_watchdog(ARQUIVO_CAPTURA)
    except KeyboardInterrupt:
        print("\nNDR Live Engine desligado.")
