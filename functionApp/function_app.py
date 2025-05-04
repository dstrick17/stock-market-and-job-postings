import logging
import requests
import json
from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential
import datetime
import os
import pytz
import azure.functions as func

app = func.FunctionApp()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define your Event Hub connection details # Primary key from instance
connection_str = "CONNECTION STRING TO EVENT HUBS"
eventhub_name = "team7eventhub"

# Define your Alpha Vantage API key and URL
api_key = "ENTER API KEY"



stock_symbol = {
    # ETFs (3 broad market indicators for sectors)
    "QQQ": "Technology",
    "XLF": "Finance",
    "XLV": "Healthcare",

    # Tech (8 total)
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.",
    "TSLA": "Tesla Inc.",
    "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms, Inc.",
    "INTC": "Intel Corporation",

    # Healthcare (7 total)
    "JNJ": "Johnson & Johnson",
    "PFE": "Pfizer Inc.",
    "MRK": "Merck & Co., Inc.",
    "UNH": "UnitedHealth Group",
    "ABT": "Abbott Laboratories",
    "CVS": "CVS Health Corporation",
    "MDT": "Medtronic plc",

    # Finance (7 total)
    "JPM": "JPMorgan Chase & Co.",
    "BAC": "Bank of America Corporation",
    "GS": "Goldman Sachs Group Inc.",
    "MS": "Morgan Stanley",
    "WFC": "Wells Fargo & Company",
    "AXP": "American Express Company",
    "C": "Citigroup Inc.",
}

def get_stock_market_data(symbol, company_name):
    """
    Fetch stock market data for the given symbol from the Alpha Vantage API.
    Returns a dictionary with the stock data if successful, or an error message.
    """
    stock_market_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"

    try:
        response = requests.get(stock_market_url) 
        response.raise_for_status()
        data = response.json()
        
        time_series_key = "Time Series (Daily)"
        if time_series_key not in data:
            logging.error(f"Unexpected API response for {symbol}: {data}")
            return {"error": f"Unable to fetch data for {symbol} ({company_name})."}

        # Find the latest date from the time series
        latest_date = max(data[time_series_key].keys())
        stock_data = data[time_series_key][latest_date]


        # Get current UTC time with timezone awareness
        current_time = datetime.datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
        print(f"\nCompany: {company_name} ({symbol})")
        print(f"Date: {latest_date}")
        print(f"Time Retrieved: {current_time}")
        print(f"Open: {stock_data['1. open']}")
        print(f"High: {stock_data['2. high']}")
        print(f"Low: {stock_data['3. low']}")
        print(f"Close: {stock_data['4. close']}")
        print(f"Volume: {stock_data['5. volume']}")
        print("-" * 40)

        return {
            "company": company_name,
            "symbol": symbol,
            "date": latest_date,
            "time_retrieved": current_time,
            "open": stock_data.get("1. open"),
            "high": stock_data.get("2. high"),
            "low": stock_data.get("3. low"),
            "close": stock_data.get("4. close"),
            "volume": stock_data.get("5. volume")
        }



    except requests.RequestException as e:
        logging.error(f"Request failed for {symbol}: {e}")
        return {"error": f"Request failed: {e}"}
    except (KeyError, ValueError) as e:
        logging.error(f"Data processing error for {symbol}: {e}")
        return {"error": f"Data processing error: {e}"}

    
def send_to_eventhub(data):
    """
    Send the provided data to Azure Event Hub.
    """
    try:
        producer = EventHubProducerClient.from_connection_string(
            conn_str=connection_str, eventhub_name=eventhub_name
        )
        event_data_batch = producer.create_batch()
        
        # Ensure data is small enough for batch
        try:
            event_data_batch.add(EventData(json.dumps(data)))
        except ValueError:
            logging.error("Data is too large for a single Event Hub batch.")
            return

        producer.send_batch(event_data_batch)
        producer.close()
        logging.info(f"Data for {data['symbol']} sent to Event Hub successfully.")
    except Exception as e:
        logging.error(f"Error sending data to Event Hub: {e}")
        raise

@app.timer_trigger(schedule="0 0 10 * * *", arg_name="mytimer", run_on_startup=True, use_monitor=True)
def main(mytimer: func.TimerRequest) -> None:

    """
    Azure Function to fetch stock market data and send it to Event Hub.
    Runs every hour based on the defined schedule.
    """
    try:
        if mytimer.past_due:
            logging.info("The timer is past due!")
        for symbol, company_name in stock_symbol.items():
            logging.info(f"Fetching data for {company_name} ({symbol})")
            stock_market_data = get_stock_market_data(symbol, company_name)
            if stock_market_data and "error" not in stock_market_data:
                send_to_eventhub(stock_market_data)
            else:
                logging.error(f"Error fetching data for {company_name} ({symbol})")

    except Exception as e:
        logging.error(f"Failed to send data to Event Hub: {e}")
   
        logging.info("Starting function execution...")



# Run the function for testing
if __name__ == "__main__":
    for symbol, company_name in stock_symbol.items():
        get_stock_market_data(symbol, company_name)


