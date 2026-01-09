// --- SECURITY SYSTEM ---
function attemptLogin() {
    const pin = document.getElementById("access-pin").value;
    const msg = document.getElementById("login-msg");
    const overlay = document.getElementById("login-overlay");

    if (pin === "1234") {
        // Success Animation
        msg.style.color = "#00ff00";
        msg.innerText = "ACCESS GRANTED. INITIALIZING TWIN...";
        
        // Play sound (simulating biometric beep)
        const audio = new AudioContext(); 
        const osc = audio.createOscillator();
        const gain = audio.createGain();
        osc.connect(gain); gain.connect(audio.destination);
        osc.frequency.value = 1200; 
        osc.start(); 
        gain.gain.exponentialRampToValueAtTime(0.00001, audio.currentTime + 0.5);
        
        setTimeout(() => {
            overlay.style.transition = "opacity 1s";
            overlay.style.opacity = "0";
            setTimeout(() => overlay.remove(), 1000);
            
            // Speak Welcome
            speakAlert("Welcome Operator. System Online.");
        }, 800);
        
    } else {
        // Failure
        msg.style.color = "#ff0000";
        msg.innerText = "ACCESS DENIED. INCIDENT LOGGED.";
        document.getElementById("access-pin").value = "";
        
        // Shake Effect
        const box = document.querySelector(".login-box");
        box.style.transform = "translateX(10px)";
        setTimeout(() => box.style.transform = "translateX(-10px)", 50);
        setTimeout(() => box.style.transform = "translateX(0)", 100);
    }
}

// Add 'Enter' key support
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("access-pin").addEventListener("keypress", function(event) {
        if (event.key === "Enter") attemptLogin();
    });
});

// ... REST OF YOUR CODE (const ws = ...)
const ws = new WebSocket("ws://127.0.0.1:9090");
let isSimulating = false;
let ledgerStore = ["Block_Index,Timestamp,Machine_ID,Event_Type,Hash"];

// ✅ PANIC LOCK: Once Red, STAY Red until AI fixes it.
let panicMode = false;

function updateUI() {
    document.getElementById("lbl-rpm").innerText = document.getElementById("sim-rpm").value;
    document.getElementById("lbl-temp").innerText = document.getElementById("sim-temp").value;
}

let lastSpoken = 0;
function speakAlert(text) {
    const now = Date.now();
    if (now - lastSpoken < 5000) return; 
    const utterance = new SpeechSynthesisUtterance(text);
    speechSynthesis.speak(utterance);
    lastSpoken = now;
}

function downloadReport() {
    if (ledgerStore.length === 1) { alert("No blocks mined."); return; }
    const csvContent = "data:text/csv;charset=utf-8," + ledgerStore.join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    const dateStr = new Date().toISOString().split('T')[0];
    link.setAttribute("download", `USI_OS_Ledger_${dateStr}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function sendSim() {
    isSimulating = true;
    const rpm = document.getElementById("sim-rpm").value;
    const temp = document.getElementById("sim-temp").value;
    
    document.getElementById("twin-state").innerText = "SIMULATION MODE";
    document.getElementById("twin-state").style.color = "#d29922";

    ws.send(JSON.stringify({
        type: "SIMULATION",
        payload: { speed_rpm: parseInt(rpm), temperature: parseInt(temp), vibration: 2.0, machine_id: "SIM-01" }
    }));
    logToTerminal(`USER: Manual Override ${rpm} RPM | ${temp}°C`, "WARN");
}

function resetSim() {
    isSimulating = false;
    panicMode = false; // Reset lock
    document.getElementById("twin-state").innerText = "LIVE STREAM";
    document.getElementById("twin-state").style.color = "#58a6ff";
    logToTerminal("SYSTEM: Reconnected to Sensor Feed", "INFO");
}

function logToTerminal(msg, type="INFO") {
    const term = document.getElementById("terminal-log");
    if (!term) return;
    const div = document.createElement("div");
    div.className = "log-line";
    const time = new Date().toLocaleTimeString().split(" ")[0];
    
    let color = "#00ff00"; 
    if(type === "WARN") color = "#d29922";
    if(type === "CRITICAL") color = "#f85149";
    if(type === "BLOCK") color = "#58a6ff";
    if(type === "AI_ACTION") color = "#ff00ff";
    
    div.innerHTML = `<span style="color:#666">[${time}]</span> <span style="color:${color}">${msg}</span>`;
    term.insertBefore(div, term.firstChild);
    if (term.children.length > 50) term.removeChild(term.lastChild);
}

const ctx = document.getElementById("tempChart").getContext("2d");
const chart = new Chart(ctx, {
    type: 'line',
    data: { 
        labels: [], 
        datasets: [
            { label: 'Temp', borderColor: '#58a6ff', backgroundColor: 'rgba(88, 166, 255, 0.1)', borderWidth: 2, fill: true, pointRadius: 0, tension: 0.4, data: [] },
            { label: 'Limit', borderColor: 'rgba(248, 81, 73, 0.6)', borderWidth: 1, borderDash: [5, 5], pointRadius: 0, fill: false, data: [] }
        ]
    },
    options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { x: { display: false }, y: { grid: { color: '#222' }, suggestedMin: 50, suggestedMax: 120 } }, plugins: { legend: { display: false } } }
});

ws.onmessage = (event) => {
    try {
        const msg = JSON.parse(event.data);
        const data = msg.payload;
        const topic = msg.topic || "";

        if (topic.includes("digital_twin")) {
            const isAI = (data.machine_id === "AI-AUTOGUARD");
            const costElement = document.getElementById("val-cost");

            // --- 🔒 PANIC LOCK LOGIC ---
            // 1. If Temp is Critical, Lock Interface RED immediately
            if (data.temp > 100) {
                panicMode = true;
            }

            // 2. If Locked, ignore EVERYTHING except the AI Cure
            if (panicMode && !isAI) {
                // Force Red Visuals even if data glitches
                document.getElementById("visual-twin").style.color = "#f85149";
                document.getElementById("twin-state").innerText = "CRITICAL ALERT";
                document.getElementById("twin-state").style.color = "#f85149";
                costElement.classList.add("cost-danger");
                // Don't process anything else until AI arrives
                return; 
            }

            // 3. AI Arrives -> Unlock
            if (isAI) {
                panicMode = false;
                if(document.getElementById("sim-rpm").value != 0) {
                     document.getElementById("sim-rpm").value = 0;
                     document.getElementById("sim-temp").value = 60;
                     updateUI();
                }
            }
            // -----------------------------

            document.getElementById("val-eff").innerText = data.efficiency;
            document.getElementById("val-rul").innerText = data.rul;
            document.getElementById("disp-rpm").innerText = data.rpm;
            document.getElementById("disp-temp").innerText = data.temp;

            // Financial Logic
            let displayCost = "0.00";
            costElement.classList.remove("cost-danger", "cost-saved");

            if (isAI) {
                displayCost = "0.00"; 
                costElement.classList.add("cost-saved"); 
                costElement.style.color = "#ff00ff";
            } 
            else if (data.temp > 100) {
                let riskFactor = (data.temp - 100) * 500; 
                let panicCost = 1000 + riskFactor; 
                displayCost = panicCost.toFixed(2);
                costElement.classList.add("cost-danger"); 
                costElement.style.color = "#f85149";
            } 
            else {
                let baseCost = (data.rpm * 0.003);
                if (data.temp > 90) baseCost *= 1.5; 
                displayCost = baseCost.toFixed(2);
                costElement.style.color = "#fff"; 
            }
            costElement.innerText = displayCost;

            if(!isSimulating || isAI) document.getElementById("twin-state").innerText = data.simulation_state;

            const turbine = document.getElementById("visual-twin");
            const rpm = data.rpm;
            const dur = rpm > 50 ? 60 / (rpm / 20) : 0;
            let animation = dur > 0 ? `spin ${Math.max(0.05, dur)}s linear infinite` : "none";

            const temp = data.temp;
            let color = "#2ea043"; 
            if (temp > 85) color = "#d29922";
            if (temp > 100) color = "#f85149";
            
            if (isAI) { color = "#ff00ff"; animation = "none"; }
            
            turbine.style.animation = animation;
            turbine.style.color = color;
            if(!isSimulating || isAI) document.getElementById("twin-state").style.color = color;
        }

        if (topic.includes("agent_msg")) {
            const box = document.getElementById("ai-text");
            box.innerText = data.nlp_message;
            box.style.color = "#58a6ff";
            
            if(data.nlp_message.includes("INTERVENTION")) {
                box.style.color = "#ff00ff";
                logToTerminal(`⚡ AI EXECUTION: Emergency Stop Triggered`, "AI_ACTION");
                speakAlert("Critical Alert. Machine Stopped.");
            }
            else if(data.nlp_message.includes("DANGER")) {
                box.style.color = "#f85149";
                if(!panicMode) speakAlert("Warning. System Overheating.");
                logToTerminal("AI WARNING: High Temp Detected", "WARN");
            }
        }

        if (topic.includes("blockchain")) {
            document.getElementById("block-counter").innerText = `BLOCKS: ${data.index}`;
            logToTerminal(`BLOCK #${data.index} MINED: [${data.data.event}]`, "BLOCK");
            const row = `${data.index},${new Date().toISOString()},${data.data.machine},${data.data.event},${data.hash}`;
            ledgerStore.push(row);
        }

        if (topic.includes("sensor_data") && !isSimulating) {
            chart.data.labels.push("");
            chart.data.datasets[0].data.push(data.temperature);
            chart.data.datasets[1].data.push(100);
            if(chart.data.labels.length > 50) { 
                chart.data.labels.shift(); 
                chart.data.datasets[0].data.shift();
                chart.data.datasets[1].data.shift();
            }
            chart.update();
            if (Math.random() > 0.95) logToTerminal(`NET: Rx Packet ${data.temperature}°C`, "INFO");
        }

    } catch (e) { console.error(e); }
};