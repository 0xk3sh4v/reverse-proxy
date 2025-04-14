import websocket
import threading
import requests
import json

# host this using nohup, this needs to be on a background thread simply requesting API on port 4545

machine = "localhost"
localapiport = 4545
PROXY_WS_URL = "ws://217.160.125.127:9516"

def on_message(ws, message):
    try:
        method, path, ip, body = message.split("||", 3)
        print(f"[Received] {method} {path} from IP {ip} with body: {body[:30]}...")

        headers = {
            "X-Forwarded-For": ip,
            "Content-Type": "application/json"  # optional, depends on your API
        }

        response = requests.request(
            method,
            f"http://{machine}:{localapiport}{path}",
            data=body,
            headers=headers
        )

        result = {
            "status": response.status_code,
            "headers": {
                "Content-Type": response.headers.get("Content-Type", "text/plain"),
                "Access-Control-Allow-Origin": "*"  # Allowed all cross origin requests
            },
            "body": response.text
        }

        ws.send(json.dumps(result))

    except Exception as e:
        print("Error handling message:", e)
        error_result = {
            "status": 500,
            "headers": {
                "Content-Type": "text/plain",
                "Access-Control-Allow-Origin": "*"
            },
            "body": f"Error: {str(e)}"
        }
        ws.send(json.dumps(error_result))
        
def on_open(ws):
    print("[+] Connected to proxy WebSocket")

def on_close(ws, close_status_code, close_msg):
    print("[-] Disconnected from proxy:", close_status_code, close_msg)

def on_error(ws, error):
    print("[!] WebSocket error:", error)

def start_client():
    ws = websocket.WebSocketApp(
        PROXY_WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_close=on_close,
        on_error=on_error
    )

    ws.run_forever()

start_client()
