import json
import sys
import time
import uuid
import websocket

def on_open(ws):
    print("WebSocket connection opened.")
    # Create a unique ticket for this subscription
    ticket = str(uuid.uuid4())
    # Modify the codes list to include the market you want.
    # For example, "KRW-BTC" or "KRW-AAVE".
    subscription_message = [
        {"ticket": ticket},
        {
            "type": "ticker",
            "codes": ["KRW-SC"],  # Change this to your desired market(s)
            "isOnlyRealtime": False
        }
    ]
    ws.send(json.dumps(subscription_message))

def on_message(ws, message):
    # Parse the incoming message
    data = json.loads(message)

    # Check if the message is a ticker type
    if data.get("type") == "ticker":
        # print("Received one ticker snapshot (one tick):")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Once we receive our single tick, we can close the connection
        # ws.close()

def on_error(ws, error):
    print("WebSocket error:", error, file=sys.stderr)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed.")

if __name__ == "__main__":
    # Create a WebSocket app and define our callbacks
    ws = websocket.WebSocketApp(
        "wss://api.upbit.com/websocket/v1",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    # Run the WebSocket event loop; it will end when we close the connection
    ws.run_forever()