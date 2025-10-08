# Python-Kafka-HFT-Pipeline
---

This project demonstrates a **complete, real-time data engineering pipeline** designed to simulate a **High-Frequency Trading (HFT)** environment.
It ingests high-volume cryptocurrency market data, processes it in real-time to calculate key metrics like **VWAP**, and stores results in:

* **Redis** for low-latency access
* **Snowflake** for historical analysis

All components are containerized with **Docker** for easy setup and reproducibility.

---
## Video Demo 


https://github.com/user-attachments/assets/ff20403a-100f-4793-8920-22e8bf7cd674


---

## ⚙️ Project Architecture

The pipeline follows an **event-driven architecture**, moving data from source to destinations with minimal latency.

<img width="2065" height="1188" alt="arch" src="https://github.com/user-attachments/assets/09d14209-ba66-47d2-be60-5ff9bab6718b" />

### **Data Flow**

1. **Python Producer (`producer.py`)**
   Reads a CSV file of historical market data and streams it row-by-row to a Kafka topic, simulating a live feed.

2. **Apache Kafka (Docker)**
   Acts as a durable, high-throughput message broker that decouples data producers and consumers.

3. **Python Processor (`pandas_processor.py`)**
   Consumes Kafka messages in real-time, maintains a rolling window in a Pandas DataFrame, and computes metrics such as **Volume-Weighted Average Price (VWAP)**.

4. **Redis (Docker)**
   Fast in-memory database where the processor writes the latest VWAP — ideal for millisecond-level access in trading strategies.

5. **Snowflake Loader (`snowloader.py`)**
   Performs batch uploads to a Snowflake data warehouse for historical and analytical queries.

---
## 📊 Dataset Details

### **Bitcoin (BTC) Minute-Level Price Data (2017–2025)**

**BTC Price from 17 August 2017 to 19 February 2025**

#### **About the Dataset**

This dataset contains **minute-level Bitcoin (BTC) price and volume data** spanning from **August 17, 2017 to February 19, 2025**.
It includes key trading indicators such as **Open**, **High**, **Low**, **Close**, and **Volume** for each minute — offering a detailed and continuous view of BTC market activity across several years.

#### **Inspiration**

Created to support:

* Financial modeling and quantitative research
* Algorithmic and high-frequency trading simulations
* Time-series forecasting and volatility analysis
* Cryptocurrency market behavior studies

#### **Source & Context**

The dataset was sourced from **[Kaggle](https://www.kaggle.com/)** and compiled from reliable cryptocurrency data providers.
It was **preprocessed** and cleaned to ensure consistent timestamps, uniform price fields, and accurate volume data.
The dataset serves as a **high-resolution benchmark** for data scientists, quants, and crypto researchers.

#### **File Information**

* **Filename:** `processed_trading_data2.csv`
* **Size:** 331.38 MB
* **Format:** CSV (minute-level OHLCV data)

#### **Metadata**

* **Usability:** 10.00
* **License:** CC0 – Public Domain
* **Expected Update Frequency:** Quarterly
* **Tags:** Currencies · Foreign Exchange · Crypto · Market Data
---

## 🧰 Technologies Used

| Layer                     | Technology                        |
| :------------------------ | :-------------------------------- |
| **Data Ingestion**        | Python (`kafka-python`, `pandas`) |
| **Streaming Platform**    | Apache Kafka                      |
| **Real-time Processing**  | Python + Pandas                   |
| **Low-Latency Storage**   | Redis                             |
| **Data Warehouse (OLAP)** | Snowflake                         |
| **Containerization**      | Docker & Docker Compose           |

---

## 🧩 Setup and Installation

### **Prerequisites**

* Python **3.9+**
* Docker Desktop
* A Snowflake account (free tier works)

---

### **1. Clone the Repository**

```bash
git clone <your-repository-url>
cd <your-repository-name>
```

### **2. Configure Environment Variables**

Create a `.env` file in the project root with your Snowflake credentials and CSV path:

```ini
# .env
SNOWFLAKE_USER=YOUR_USERNAME
SNOWFLAKE_PASSWORD=YOUR_PASSWORD
SNOWFLAKE_ACCOUNT=YOUR_ACCOUNT_IDENTIFIER  # e.g. xyz12345.us-east-1
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=HFT_WH
SNOWFLAKE_DATABASE=HFT_PROJECT_DB
SNOWFLAKE_SCHEMA=RAW_DATA
SNOWFLAKE_TABLE=CRYPTO_MARKET_DATA
CSV_FILE_PATH=path/to/BTC_1min.csv
PROJECT_DIR=D:/paisa_hi_paisa/HFT
```

> ⚠️ Add `.env` to `.gitignore` to avoid committing credentials.

---

### **3. Install Dependencies**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

---

### **4. Start Docker Services**

```bash
docker-compose up -d
```

---

## 🚀 Running the Pipeline

### **1. Create a Kafka Topic**

```bash
docker exec -it hft-kafka-1 /opt/kafka/bin/kafka-topics.sh --create --topic crypto-market-data --zookeeper zookeeper:2181 --partitions 1 --replication-factor 1
```

### **2. Start the Data Producer**

```bash
python producer.py
```

### **3. Start the Real-Time Processor**

```bash
python pandas_processor.py
```

### **4. (Optional) Load Data into Snowflake**

```bash
python snowloader.py
```

---

## 📊 Analyzing the Data

### **Real-Time (Redis)**

Check VWAP values in Redis:

```bash
docker exec -it <redis-container> redis-cli
KEYS "vwap:*"
GET "vwap:2017-08-17 04:05:00"
```

### **Historical (Snowflake)**

Example queries in Snowflake worksheet:

#### Most Volatile Days

```sql
SELECT
    DATE_TRUNC('DAY', TIMESTAMP) AS trade_day,
    MAX(HIGH) - MIN(LOW) AS daily_price_swing,
    SUM(VOLUME) AS total_volume
FROM
    HFT_PROJECT_DB.PUBLIC.CRYPTO_MARKET_DATA -- Corrected schema to RAW_DATA
GROUP BY
    trade_day
ORDER BY
    daily_price_swing DESC
LIMIT 4;
```

---

## 🧠 Notes & Tips

* Ensure Docker Desktop has access to your project drive.
* Validate timestamp formats with `test_timestamp_conversion.py` and `test_datetime.csv`.
* Keep credentials secure; never commit `.env` files.
* For Windows path issues, verify that your `PROJECT_DIR` is properly shared in Docker Desktop.

