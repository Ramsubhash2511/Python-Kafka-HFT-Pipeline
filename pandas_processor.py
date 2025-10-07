import pandas as pd
from kafka import KafkaConsumer
import json
import redis
import time

# --- Configuration ---
KAFKA_TOPIC = "crypto-market-data"
KAFKA_SERVER = "localhost:9092"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
WINDOW_SIZE = 10 # Number of minutes to keep for calculations

# --- Connect to Services ---
try:
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='latest' # Start reading from the latest message
    )
    print("Successfully connected to Kafka.")
except Exception as e:
    print(f"Error connecting to Kafka: {e}")
    exit()

try:
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    # Ping the server to check the connection
    r.ping()
    print("Successfully connected to Redis.")
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    exit()

# --- Main Processing Loop ---
# This list will act as our in-memory, rolling window of data
data_window = []

print("Starting to consume messages from Kafka...")
for message in consumer:
    # 1. Add new data point to our window
    trade_data = message.value
    data_window.append(trade_data)
    
    # 2. Keep the window size fixed by removing the oldest element
    if len(data_window) > WINDOW_SIZE:
        data_window.pop(0)

    # 3. Convert the current window to a Pandas DataFrame for easy calculation
    df = pd.DataFrame(data_window)

    # Ensure data types are correct for calculations
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['volume'] = pd.to_numeric(df['volume'])
    
    # 4. Calculate Key Metrics
    # Moving Average
    moving_average = df['close'].mean()
    
    # Volatility (as standard deviation of close prices)
    volatility = df['close'].std()
    
    # Volume-Weighted Average Price (VWAP)
    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
    df['tpv'] = df['typical_price'] * df['volume']
    vwap = df['tpv'].sum() / df['volume'].sum()

    # 5. Get the timestamp of the most recent trade
    latest_timestamp = trade_data['timestamp']

    # 6. Print to console and write the latest metrics to Redis
    print(f"[{latest_timestamp}] | MA: {moving_average:.2f} | Volatility: {volatility:.2f} | VWAP: {vwap:.2f}")

    # Write to Redis using a simple key structure
    r.set("latest:moving_average", f"{moving_average:.2f}")
    r.set("latest:volatility", f"{volatility:.2f}")
    r.set("latest:vwap", f"{vwap:.2f}")
    r.set("latest:timestamp", latest_timestamp)

    # Add a small delay to prevent overwhelming the CPU, optional
    # time.sleep(0.1)
