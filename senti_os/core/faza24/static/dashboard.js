const sysEl = document.getElementById("system_status");
const logEl = document.getElementById("logs_output");

// Dynamic WebSocket URL generation (works for localhost and remote access)
function getWebSocketURL(endpoint) {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    return `${protocol}//${host}/ws${endpoint}`;
}

// WebSocket connection with auto-reconnect and error handling
function connectSystemWS() {
    const url = getWebSocketURL("/system");
    const ws = new WebSocket(url);

    ws.onopen = () => {
        console.log("System WebSocket connected");
        sysEl.textContent = "Connected...";
    };

    ws.onmessage = (msg) => {
        try {
            const data = JSON.parse(msg.data);
            sysEl.textContent = JSON.stringify(data, null, 2);
        } catch (e) {
            console.error("Failed to parse system data:", e);
            sysEl.textContent = "Error parsing system data";
        }
    };

    ws.onerror = (error) => {
        console.error("System WebSocket error:", error);
        sysEl.textContent = "WebSocket error - check console";
    };

    ws.onclose = () => {
        console.log("System WebSocket closed, reconnecting in 3s...");
        sysEl.textContent = "Disconnected - Reconnecting...";
        setTimeout(connectSystemWS, 3000);
    };
}

function connectLogsWS() {
    const url = getWebSocketURL("/logs");
    const ws = new WebSocket(url);

    ws.onopen = () => {
        console.log("Logs WebSocket connected");
        logEl.textContent = "Connected...";
    };

    ws.onmessage = (msg) => {
        try {
            const data = JSON.parse(msg.data);
            logEl.textContent = JSON.stringify(data, null, 2);
        } catch (e) {
            console.error("Failed to parse log data:", e);
            logEl.textContent = "Error parsing log data";
        }
    };

    ws.onerror = (error) => {
        console.error("Logs WebSocket error:", error);
        logEl.textContent = "WebSocket error - check console";
    };

    ws.onclose = () => {
        console.log("Logs WebSocket closed, reconnecting in 3s...");
        logEl.textContent = "Disconnected - Reconnecting...";
        setTimeout(connectLogsWS, 3000);
    };
}

// Initialize connections
connectSystemWS();
connectLogsWS();
