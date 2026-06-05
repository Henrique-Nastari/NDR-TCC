# 🛡️ Real-Time NDR System (Network Detection and Response)

![NDR Architecture](https://img.shields.io/badge/Architecture-Two--Stage%20ML-blue)
![Python](https://img.shields.io/badge/Python-3.14-green)
![Docker](https://img.shields.io/badge/Docker-Grafana%20%7C%20InfluxDB-orange)

Sistema completo de Detecção e Resposta a Ameaças de Rede (NDR) desenvolvido como Trabalho de Conclusão de Curso (TCC).

## 🧠 Arquitetura de Machine Learning

```mermaid
flowchart TD
    A["Fluxo de Rede (features)"] --> B["Camada 1: Classificador Binário"]
    B -->|BENIGN| C["Tráfego Normal"]
    B -->|ATTACK| D["Camada 2: Classificador Multiclasse"]
    D --> E["Tipo de Ataque Identificado"]
    
    style B fill:#1e3a5f,stroke:#4a9eff,color:#fff
    style D fill:#3a1e5f,stroke:#9a4aff,color:#fff
    style C fill:#1e5f3a,stroke:#4aff9a,color:#fff
    style E fill:#5f1e3a,stroke:#ff4a9a,color:#fff
```

O sistema foi treinado com o dataset **CICIDS2017** e opera em um pipeline de **Duas Camadas**:
1. **Camada 1 (O Porteiro):** Modelo `XGBoost` otimizado para detecção ultrarrápida binária (`BENIGN` vs `ATTACK`).
2. **Camada 2 (O Especialista):** Modelo `Random Forest` multiclasse responsável por assinar e classificar a ameaça em 12 categorias distintas (DDoS, PortScan, Botnet, Infiltration, etc).

## 🏗️ Fluxo de Funcionamento e Laboratório de Defesa

```mermaid
flowchart LR
    A["Ubuntu 26.04\n(Host Principal)\nDocker + NDR + Atacante"] -->|Ataques| B["VM Lubuntu\n(VirtualBox - Bridge)\nNginx Server"]
    A -->|Captura tráfego\nna interface| C["CICFlowMeter\n(Python)"]
    C --> D["Modelos ML\n(Camada 1 + 2)"]
    D --> E["InfluxDB\n(métricas)"]
    E --> F["Grafana\n(dashboard)"]
    
    style A fill:#1e3a5f,stroke:#4a9eff,color:#fff
    style B fill:#5f3a1e,stroke:#ff9a4a,color:#fff
    style D fill:#3a1e5f,stroke:#9a4aff,color:#fff
    style F fill:#1e5f3a,stroke:#4aff9a,color:#fff
```

1. O tráfego de rede é capturado em tempo real (via CICFlowMeter).
2. O script `ndr_live.py` (Watchdog) intercepta as métricas matemáticas do pacote.
3. Se o Porteiro (Camada 1) detectar anomalia, o pacote é enviado ao Especialista (Camada 2).
4. O diagnóstico final (incluindo IP de Origem e Destino) é injetado no banco temporal **InfluxDB**.
5. Um painel interativo no **Grafana** exibe os alertas e as tabelas de ameaças instantaneamente.

## 🛠️ Tecnologias Utilizadas
* **Machine Learning:** Scikit-Learn, LightGBM, XGBoost, Pandas.
* **Infraestrutura:** Docker, Docker Compose.
* **Observabilidade:** InfluxDB, Grafana (Flux Query Language).

## 🚀 Como Subir o Projeto
1. Suba o Banco de Dados e o Painel:
   ```bash
   docker compose up -d
   ```
2. Instale as dependências:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Inicie o Motor Vigilante (Watchdog):
   ```bash
   python ndr_live.py
   ```
