# SwingTradeIA 📈

> **Projeto 3 do meu Roadmap de IA** — Plataforma de suporte à decisão para Swing Trade em ações brasileiras (B3) com agente de Aprendizado por Reforço (DQN — Deep Q-Network).

---

## 📌 Sobre o projeto

O **SwingTradeIA** é um projeto que desenvolvi para colocar em prática conceitos de **Inteligência Artificial aplicada ao mercado financeiro**. A ideia central é combinar análise técnica clássica com um agente de RL (Reinforcement Learning) treinado com dados históricos da B3, gerando recomendações de **Comprar**, **Manter** ou **Vender** para ações brasileiras.

O sistema **não executa ordens automáticas** — ele funciona como uma ferramenta de **análise e apoio à decisão**, apresentando indicadores quantitativos e o sinal do modelo de IA para que o trader tome a decisão final.

### O que o sistema faz

- 📊 Busca e processa dados históricos de ações da B3 em tempo real via **yfinance**
- 🤖 Roda um agente **DQN (Deep Q-Network)** para gerar sinais de trading com nível de confiança
- 📈 Exibe um **gráfico candlestick interativo** com todo o histórico disponível
- 🔢 Calcula e apresenta indicadores técnicos: **RSI, MACD, Bollinger Bands, Médias Móveis e Volume**
- 📋 Acompanha uma **watchlist** com as principais ações da B3

> ⚠️ **Aviso importante**: Este projeto é de cunho **educacional e de portfólio**. Os sinais gerados não constituem recomendação de investimento. Opere por sua conta e risco.

---

## 🖼️ Screenshots

<img width="1913" height="597" alt="Image" src="https://github.com/user-attachments/assets/eaf51d6c-b387-4a86-8ce9-4db27cca2048" />

<img width="1581" height="329" alt="Image" src="https://github.com/user-attachments/assets/07cf092b-fc31-4aeb-b0d7-515a1fb1dfff" />

<img width="1580" height="839" alt="Image" src="https://github.com/user-attachments/assets/bf1ae776-7473-4e37-8064-eb85b1d081c8" />

---

## 🏗️ Stack Tecnológica

| Camada          | Tecnologia                              |
|-----------------|-----------------------------------------|
| Frontend        | Angular 17 + LightweightCharts (TradingView) |
| Backend         | C# .NET 8 Web API                       |
| AI / ML         | Python FastAPI + PyTorch + yfinance     |
| Banco de Dados  | PostgreSQL 16 (via Entity Framework Core) |
| Infraestrutura  | Docker + Docker Compose + Nginx         |

### Arquitetura geral

```
Browser (Angular)
      │
      ▼
Backend C# .NET 8  ──── PostgreSQL 16
      │
      ▼
AI Service Python (FastAPI)
  ├── yfinance  → busca dados B3
  ├── indicators.py  → RSI, MACD, Bollinger, MA, Volume
  └── dqn_agent.py  → recomendação BUY / HOLD / SELL
```

O frontend nunca se comunica diretamente com o serviço de IA — tudo passa pelo backend, que age como gateway.

---

## 🚀 Instalação e execução

### Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando
- [Git](https://git-scm.com/)

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/SwingTradeIA.git
cd SwingTradeIA
```

### 2. Configure as variáveis de ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env
```

O arquivo `.env` já vem com valores padrão para desenvolvimento local. Edite apenas se quiser personalizar senhas ou portas:

```env
# PostgreSQL
POSTGRES_USER=swingtrade_user
POSTGRES_PASSWORD=swingtrade_pass
POSTGRES_DB=swingtrade_db

# Backend
ASPNETCORE_ENVIRONMENT=Development
CONNECTION_STRING=Host=postgres;Port=5432;Database=swingtrade_db;Username=swingtrade_user;Password=swingtrade_pass
AI_SERVICE_URL=http://ai-service:8000

# AI Service
PYTHONUNBUFFERED=1
```

### 3. Suba todos os serviços com Docker

```bash
docker compose up -d
```

O Docker vai subir quatro containers: **PostgreSQL**, **backend .NET**, **ai-service Python** e **frontend Angular via Nginx**.

### 4. Acesse a aplicação

| Serviço          | URL                                  |
|------------------|--------------------------------------|
| Interface Web    | http://localhost:4200                |
| API Backend      | http://localhost:5000/swagger        |
| AI Service (docs)| http://localhost:8000/docs           |

> 💡 Na primeira execução, o banco é criado e populado automaticamente com as 15 ações da watchlist padrão.

---

## 🖥️ Como usar

Depois de subir os serviços, acesse **http://localhost:4200**. A interface é dividida em dois painéis:

### Painel esquerdo — Lista de ações

- Mostra as principais ações da B3 monitoradas pelo sistema
- Use o campo de busca para encontrar um ticker específico
- Cada linha exibe o preço atual, variação do dia e o **sinal do modelo** (🟢 COMPRAR / 🟡 MANTER / 🔴 VENDER)
- Clique em qualquer ação para carregar o gráfico e a análise completa

### Painel direito — Análise completa

- **Gráfico candlestick** com todo o histórico disponível (pode chegar a 20+ anos)
  - Selecione o período: 1M | 3M | 6M | 1A | 2A | 5A | MAX
  - Overlays: Média Móvel 9, Média Móvel 21, Bandas de Bollinger
- **Sinal do DQN**: recomendação do agente com percentual de confiança
- **Indicadores técnicos**: RSI, MACD, Bollinger Bands, cruzamentos de médias e ratio de volume
- **Dados de mercado**: abertura, máxima, mínima, fechamento e variação nas últimas 52 semanas

### Principais ações monitoradas (watchlist padrão)

| Ticker | Empresa               | Setor               |
|--------|-----------------------|---------------------|
| PETR4  | Petrobras PN          | Petróleo & Gás      |
| VALE3  | Vale ON               | Mineração           |
| ITUB4  | Itaú Unibanco PN      | Financeiro          |
| BBDC4  | Bradesco PN           | Financeiro          |
| ABEV3  | Ambev ON              | Bebidas             |
| WEGE3  | WEG ON                | Industrial          |
| RENT3  | Localiza ON           | Mobilidade          |
| MGLU3  | Magazine Luiza ON     | Varejo              |
| BBAS3  | Banco do Brasil ON    | Financeiro          |
| EGIE3  | Engie Brasil ON       | Energia Elétrica    |
| VIVT3  | Telefônica ON         | Telecomunicações    |
| SUZB3  | Suzano ON             | Papel & Celulose    |
| LREN3  | Lojas Renner ON       | Varejo              |
| HAPV3  | Hapvida ON            | Saúde               |
| RADL3  | Raia Drogasil ON      | Saúde               |

---

## 🧠 Retreinando o modelo DQN

O modelo vem com pesos pré-treinados em `ai-service/app/models/dqn_weights.pth`. Se quiser retreinar com dados mais recentes ou em outros ativos, siga os passos abaixo.

### Pré-requisitos para o treinamento

```bash
# Crie um ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r ai-service/requirements.txt
```

### Treinando o modelo

```bash
cd modelo

# Treinar para um ticker específico (ex: PETR4)
python train.py --ticker PETR4 --episodes 1000

# Treinar com mais episódios para maior convergência
python train.py --ticker VALE3 --episodes 2000

# Ver todos os parâmetros disponíveis
python train.py --help
```

O script `train.py` vai:
1. Buscar o histórico completo do ticker via **yfinance**
2. Criar o ambiente customizado de trading (`environment.py`)
3. Treinar as redes **Policy + Target** com Replay Buffer
4. Salvar os pesos em `ai-service/app/models/dqn_weights.pth`

### Avaliando o modelo treinado

```bash
# Compara o agente DQN vs estratégia Buy & Hold
python evaluate.py --ticker PETR4
```

O relatório de avaliação mostra o retorno acumulado do agente em comparação com simplesmente comprar e segurar o ativo.

### Estrutura dos scripts de treinamento

```
modelo/
├── train.py          # Loop principal de treinamento (DQN)
├── environment.py    # Ambiente Gymnasium customizado de trading
├── dqn_network.py    # Arquitetura das redes Policy e Target (PyTorch)
├── replay_buffer.py  # Memória de experiências (Experience Replay)
└── evaluate.py       # Avaliação: agente DQN vs Buy & Hold
```

---

## 📊 Indicadores técnicos utilizados

| Indicador       | Configuração    | Interpretação                                         |
|-----------------|-----------------|-------------------------------------------------------|
| RSI             | 14 períodos     | > 70 → sobrecomprado / < 30 → sobrevendido            |
| MACD            | 12 / 26 / 9     | Cruzamento da linha com o sinal = entrada/saída       |
| Bollinger Bands | 20 períodos, 2σ | Preço abaixo da banda inferior = possível compra      |
| SMA 9 / SMA 21  | 9 e 21 períodos | Golden cross = alta / Death cross = baixa             |
| Volume Ratio    | Vol / MA20Vol   | > 1.5 = volume acima da média, confirma o movimento   |

---

## 📁 Estrutura do projeto

```
SwingTradeIA/
├── frontend/         # Angular 17 — interface web
├── backend/          # C# .NET 8 — API REST + gateway
├── ai-service/       # Python FastAPI — dados (yfinance) + DQN
├── modelo/           # Scripts de treinamento offline do DQN
├── infrastructure/   # Dockerfiles e configuração Nginx
├── docs/             # Documentação adicional e referência de API
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 📝 Licença

MIT License — Projeto educacional e de portfólio.
