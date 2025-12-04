const sysEl = document.getElementById("system_status");
const logEl = document.getElementById("logs_output");

function connectSystemWS() {
    const ws = new WebSocket("ws://localhost:8123/ws/system");
    ws.onmessage = msg => {
        sysEl.textContent = JSON.stringify(JSON.parse(msg.data), null, 2);
    }
}
function connectLogsWS() {
    const ws = new WebSocket("ws://localhost:8123/ws/logs");
    ws.onmessage = msg => {
        logEl.textContent = JSON.stringify(JSON.parse(msg.data), null, 2);
    }
}
connectSystemWS();
connectLogsWS();
