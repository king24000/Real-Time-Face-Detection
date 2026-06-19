/**
 * ==========================================================================
 * REAL-TIME FACE DETECTION HUD SYSTEM - FRONTEND ORCHESTRATOR
 * ==========================================================================
 */

// UI Color Theme Configurations
const THEMES = {
    cyberpunk: {
        name: "CYBERPUNK CYAN",
        primary: "#00ffd5",
        secondary: "#ff00c8",
        glow: "#4da6ff"
    },
    matrix: {
        name: "MATRIX NEON",
        primary: "#00ff00",
        secondary: "#008000",
        glow: "#8cff8c"
    },
    stealth: {
        name: "STEALTH RED",
        primary: "#ff1a1a",
        secondary: "#ff6666",
        glow: "#ff4d4d"
    },
    sunset: {
        name: "SUNSET GOLD",
        primary: "#ff9d00",
        secondary: "#ff4800",
        glow: "#ffdf9e"
    }
};

// Global Application State variables
let activeThemeKey = "cyberpunk";
let showHud = true;
let showBoxes = true;
let showGlasses = true;
let faces = [];

// Performance Telemetry variables
let frameCount = 0;
let lastFpsUpdateTime = 0;
let currentFps = 0;
let latencyMs = 0;
let lastSendTime = 0;
let isWaitingForServer = false;

// WebSocket connection handler
let ws = null;
let reconnectTimer = null;

// HTML Elements
const videoEl = document.getElementById("webcam-video");
const canvasEl = document.getElementById("output-canvas");
const ctx = canvasEl.getContext("2d");
const cameraPrompt = document.getElementById("camera-prompt");
const connectionDot = document.getElementById("connection-dot");
const connectionStatus = document.getElementById("connection-status");
const latencyValue = document.getElementById("tel-latency");

// Form Control Elements
const switchHud = document.getElementById("toggle-hud");
const switchBoxes = document.getElementById("toggle-boxes");
const switchGlasses = document.getElementById("toggle-glasses");
const btnSnapshot = document.getElementById("btn-snapshot");

// Offscreen Canvas for downscaling image to 640x360 to save bandwidth
const offscreenCanvas = document.createElement("canvas");
offscreenCanvas.width = 640;
offscreenCanvas.height = 360;
const offscreenCtx = offscreenCanvas.getContext("2d");

// Alert Toast manager
let alertTimeout = null;
const alertTextEl = document.getElementById("alert-text");

function triggerAlert(message, duration = 2500) {
    if (alertTimeout) clearTimeout(alertTimeout);
    alertTextEl.innerText = message.toUpperCase();
    
    // Reset alert message after duration
    alertTimeout = setTimeout(() => {
        alertTextEl.innerText = "SYSTEM ACTIVE: STANDBY";
    }, duration);
}

// ==========================================================================
// 🔌 WEBSOCKET INTERACTION SECTION
// ==========================================================================

function connectWebSocket() {
    if (ws) {
        ws.close();
    }

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    ws.binaryType = "arraybuffer"; // Performance: send binary data instead of base64 strings

    ws.onopen = () => {
        connectionDot.className = "pulse-dot online";
        connectionStatus.innerText = "ONLINE";
        connectionStatus.style.color = "#22c55e";
        triggerAlert("WS CHANNEL STABILIZED");
        if (reconnectTimer) {
            clearInterval(reconnectTimer);
            reconnectTimer = null;
        }
        isWaitingForServer = false;
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.success) {
                faces = data.faces;
                
                // Calculate latency based on performance ticks
                latencyMs = Math.round(performance.now() - lastSendTime);
                latencyValue.innerText = `${latencyMs} ms`;
            }
        } catch (e) {
            console.error("Error parsing WebSocket JSON:", e);
        }
        isWaitingForServer = false; // Pacing: server replied, ready to send next frame
    };

    ws.onclose = () => {
        connectionDot.className = "pulse-dot";
        connectionStatus.innerText = "OFFLINE";
        connectionStatus.style.color = "#ef4444";
        latencyValue.innerText = "-- ms";
        isWaitingForServer = false;
        
        // Auto-reconnect loop
        if (!reconnectTimer) {
            triggerAlert("CONNECTION LOST: RECONNECTING...");
            reconnectTimer = setInterval(connectWebSocket, 3000);
        }
    };

    ws.onerror = (err) => {
        console.error("WebSocket encountered an error:", err);
    };
}

// Send local frame to FastAPI WebSocket server
function sendFrame() {
    if (!ws || ws.readyState !== WebSocket.OPEN || isWaitingForServer) {
        // Pacing Timeout Safeguard: Reset wait flag if server response is delayed past 1000ms
        if (isWaitingForServer && performance.now() - lastSendTime > 1000) {
            isWaitingForServer = false;
        }
        return;
    }

    // Downscale and mirror camera input to offscreen canvas
    offscreenCtx.save();
    offscreenCtx.translate(offscreenCanvas.width, 0);
    offscreenCtx.scale(-1, 1); // Flip horizontally for natural view
    offscreenCtx.drawImage(videoEl, 0, 0, offscreenCanvas.width, offscreenCanvas.height);
    offscreenCtx.restore();

    // Convert offscreen canvas frame to binary JPEG blob and transmit
    offscreenCanvas.toBlob((blob) => {
        if (blob && ws && ws.readyState === WebSocket.OPEN) {
            ws.send(blob);
            lastSendTime = performance.now();
            isWaitingForServer = true; // Block next frames until response received
        }
    }, "image/jpeg", 0.7);
}

// ==========================================================================
// 🎥 CAMERA STREAM INITIALIZATION
// ==========================================================================

async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: "user"
            },
            audio: false
        });
        
        // 1. Register listener FIRST to avoid race conditions
        videoEl.onloadedmetadata = () => {
            // Adjust local canvas to match video sizes
            canvasEl.width = videoEl.videoWidth;
            canvasEl.height = videoEl.videoHeight;
            
            // Hide camera access loader prompt
            cameraPrompt.style.opacity = 0;
            setTimeout(() => cameraPrompt.style.display = "none", 500);
            
            // Start main loop
            requestAnimationFrame(renderLoop);
        };

        // 2. Assign stream and trigger play
        videoEl.srcObject = stream;
        
        try {
            await videoEl.play();
        } catch (playErr) {
            console.warn("videoEl.play() failed initially, relying on autoplay attribute:", playErr);
        }
    } catch (err) {
        console.error("Camera access failed:", err);
        cameraPrompt.innerHTML = `
            <div style="color:#ef4444; font-size:24px; font-weight:bold;">⚠️ CAMERA ACCESS BLOCKED</div>
            <p style="margin-top:10px; max-width:400px; text-align:center;">Could not start webcam. Please grant camera access permissions in your browser bar and reload.</p>
        `;
    }
}

// ==========================================================================
// 🎨 HUD & OVERLAY GRAPHICS RENDER LOOP
// ==========================================================================

function renderLoop() {
    // 1. Draw raw mirrored camera frame onto the screen Canvas
    ctx.save();
    ctx.translate(canvasEl.width, 0);
    ctx.scale(-1, 1); // Mirror for natural webcam user interface
    ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
    ctx.restore();

    // 2. Perform FPS calculations
    const now = performance.now();
    frameCount++;
    if (now - lastFpsUpdateTime >= 1000) {
        currentFps = Math.round((frameCount * 1000) / (now - lastFpsUpdateTime));
        frameCount = 0;
        lastFpsUpdateTime = now;
    }

    const theme = THEMES[activeThemeKey];

    // 3. Draw Bounding Boxes, Landmarks & Sci-Fi Glasses overlays
    if (showBoxes && faces.length > 0) {
        // Scale factor: server processes 640x360, canvas may be 1280x720
        const scaleX = canvasEl.width / 640;
        const scaleY = canvasEl.height / 360;

        faces.forEach((face, idx) => {
            // Bounding box dimensions
            let [x, y, w, h] = face.bbox;
            x = x * scaleX;
            y = y * scaleY;
            w = w * scaleX;
            h = h * scaleY;

            // Draw bounding box border
            ctx.strokeStyle = theme.primary;
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, w, h);

            // Draw thick styled sci-fi corner ticks
            const cornerLen = Math.min(25, w / 2, h / 2);
            ctx.strokeStyle = theme.secondary;
            ctx.lineWidth = 4;
            
            // Top-Left Corner
            ctx.beginPath();
            ctx.moveTo(x, y + cornerLen); ctx.lineTo(x, y); ctx.lineTo(x + cornerLen, y);
            ctx.stroke();

            // Top-Right Corner
            ctx.beginPath();
            ctx.moveTo(x + w, y + cornerLen); ctx.lineTo(x + w, y); ctx.lineTo(x + w - cornerLen, y);
            ctx.stroke();

            // Bottom-Left Corner
            ctx.beginPath();
            ctx.moveTo(x, y + h - cornerLen); ctx.lineTo(x, y + h); ctx.lineTo(x + cornerLen, y + h);
            ctx.stroke();

            // Bottom-Right Corner
            ctx.beginPath();
            ctx.moveTo(x + w, y + h - cornerLen); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w - cornerLen, y + h);
            ctx.stroke();

            // Draw Distance & Confidence tags above box
            const distVal = face.distance;
            const distStr = distVal < 100 ? `${Math.round(distVal)}cm` : `${(distVal / 100).toFixed(2)}m`;
            const labelText = `FACE ${String(idx + 1).padStart(2, "0")} | CONF: ${Math.round(face.confidence * 100)}% | DIST: ${distStr}`;
            
            ctx.font = "600 11px 'Share Tech Mono', monospace";
            const labelWidth = ctx.measureText(labelText).width;
            const labelH = 18;
            const labelY = (y - 8 - labelH > 0) ? (y - 8) : (y + labelH + 8);
            const labelX = x;

            // Draw tag card background
            ctx.fillStyle = "rgba(10, 10, 12, 0.8)";
            ctx.fillRect(labelX, labelY - labelH, labelWidth + 12, labelH + 4);
            ctx.fillStyle = theme.secondary;
            ctx.fillRect(labelX, labelY - labelH, 2, labelH + 4);

            // Draw text
            ctx.fillStyle = "#ffffff";
            ctx.fillText(labelText, labelX + 7, labelY - 5);

            // Draw dynamic Glasses overlay or traditional crosshairs
            if (face.landmarks && face.landmarks.length >= 6) {
                // Scale landmark coordinates
                const lms = face.landmarks.map(lm => [lm[0] * scaleX, lm[1] * scaleY]);

                if (showGlasses) {
                    drawCyberGlasses(lms, theme);
                } else {
                    // Draw basic crosshair targets
                    lms.forEach(lm => {
                        ctx.fillStyle = theme.glow;
                        ctx.beginPath();
                        ctx.arc(lm[0], lm[1], 3, 0, Math.PI * 2);
                        ctx.fill();

                        ctx.strokeStyle = theme.glow;
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(lm[0] - 5, lm[1]); ctx.lineTo(lm[0] + 5, lm[1]);
                        ctx.moveTo(lm[0], lm[1] - 5); ctx.lineTo(lm[0], lm[1] + 5);
                        ctx.stroke();
                    });
                }
            }
        });
    }

    // 4. Render Top Dashboard elements if HUD enabled
    if (showHud) {
        drawHudOverlay(theme);
    }

    // 5. Send current frame to WebSocket (Pacing manages transmission)
    sendFrame();

    // Loop
    requestAnimationFrame(renderLoop);
}

// Draws futuristic hexagonal glasses using eye and ear landmarks
function drawCyberGlasses(lms, theme) {
    const eyeLeft = lms[0];   // Viewer's left eye (person's right)
    const eyeRight = lms[1];  // Viewer's right eye (person's left)
    const nose = lms[2];
    const mouth = lms[3];
    const earLeft = lms[4];
    const earRight = lms[5];

    const dx = eyeRight[0] - eyeLeft[0];
    const dy = eyeRight[1] - eyeLeft[1];
    const eyeDist = Math.sqrt(dx * dx + dy * dy);

    if (eyeDist > 0) {
        const r = eyeDist * 0.32;

        // Draw nose bridge
        ctx.strokeStyle = theme.primary;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(eyeLeft[0], eyeLeft[1]);
        ctx.lineTo(eyeRight[0], eyeRight[1]);
        ctx.stroke();

        // Draw side temple arms to the ears
        ctx.strokeStyle = theme.secondary;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(eyeLeft[0], eyeLeft[1]); ctx.lineTo(earLeft[0], earLeft[1]);
        ctx.moveTo(eyeRight[0], eyeRight[1]); ctx.lineTo(earRight[0], earRight[1]);
        ctx.stroke();

        // Draw hexagon rings around both eyes
        [eyeLeft, eyeRight].forEach(center => {
            // Draw outer thick hexagon
            ctx.strokeStyle = theme.primary;
            ctx.lineWidth = 2;
            drawHexagon(center[0], center[1], r);

            // Draw inner glowing thin hexagon
            ctx.strokeStyle = theme.glow;
            ctx.lineWidth = 1;
            drawHexagon(center[0], center[1], r * 0.75);

            // Draw center dot
            ctx.fillStyle = theme.glow;
            ctx.beginPath();
            ctx.arc(center[0], center[1], 2, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    // Draw nose and mouth crosshair points
    [nose, mouth].forEach(pt => {
        ctx.fillStyle = theme.glow;
        ctx.beginPath();
        ctx.arc(pt[0], pt[1], 2, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = theme.glow;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(pt[0] - 4, pt[1]); ctx.lineTo(pt[0] + 4, pt[1]);
        ctx.moveTo(pt[0], pt[1] - 4); ctx.lineTo(pt[0], pt[1] + 4);
        ctx.stroke();
    });
}

// Utility to draw a rotated regular hexagon
function drawHexagon(cx, cy, radius) {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
        const angle = (i * Math.PI) / 3 + Math.PI / 6; // Flat top rotation
        const x = cx + radius * Math.cos(angle);
        const y = cy + radius * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
}

// Draws the top visual dashboard panels directly on the Canvas
function drawHudOverlay(theme) {
    const w = canvasEl.width;

    // Top panel border lines
    ctx.strokeStyle = theme.primary;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, 50);
    ctx.lineTo(w, 50);
    ctx.stroke();

    // Top cybernetic corner ticks
    ctx.strokeStyle = theme.secondary;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(10, 50); ctx.lineTo(35, 50);
    ctx.moveTo(w - 35, 50); ctx.lineTo(w - 10, 50);
    ctx.stroke();

    // Render Stats overlay text inside canvas
    ctx.font = "700 13px 'Orbitron', sans-serif";
    ctx.fillStyle = "#ffffff";
    ctx.fillText("CAMERA TARGETS ACQUIRED", 24, 32);

    ctx.font = "600 12px 'Share Tech Mono', monospace";
    const infoText = `HUD_ACTIVE  |  TARGET_COUNT: ${String(faces.length).padStart(2, "0")}  |  FEED_FPS: ${currentFps}`;
    ctx.fillStyle = theme.primary;
    ctx.fillText(infoText, w - 380, 31);
}

// ==========================================================================
// 📸 BACKEND SCREENSHOT CAPTURE PROCESS
// ==========================================================================

async function captureCleanSnapshot() {
    // 1. Draw raw flipped image onto our offscreen canvas
    offscreenCtx.save();
    offscreenCtx.translate(offscreenCanvas.width, 0);
    offscreenCtx.scale(-1, 1);
    offscreenCtx.drawImage(videoEl, 0, 0, offscreenCanvas.width, offscreenCanvas.height);
    offscreenCtx.restore();

    // 2. Generate Base64 Data URL
    const dataUrl = offscreenCanvas.toDataURL("image/png");

    triggerAlert("SAVING SNAPSHOT TO BACKEND...");
    
    // 3. POST upload to server
    try {
        const response = await fetch("/api/screenshot", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ image_base64: dataUrl })
        });
        
        const result = await response.json();
        if (result.success) {
            triggerAlert(`SNAP SAVED: ${result.filename}`);
            console.log(`[HUD API] Clean screenshot saved on server at: ${result.filepath}`);
        } else {
            triggerAlert("SAVE FAILED!");
            console.error("Failed to upload screenshot:", result.error);
        }
    } catch (err) {
        triggerAlert("API NET ERROR!");
        console.error("POST API connection error:", err);
    }
}

// ==========================================================================
// ⌨️ USER CONTROLS & EVENT LISTENERS
// ==========================================================================

function switchTheme(themeKey) {
    if (!THEMES[themeKey]) return;
    
    // Update theme configuration state
    activeThemeKey = themeKey;
    
    // Replace theme styling classes on document body
    document.body.className = `cyber-theme-${themeKey}`;
    
    // Highlight button in sidebar
    document.querySelectorAll(".theme-btn").forEach(btn => {
        btn.classList.remove("active");
    });
    
    const activeBtn = document.getElementById(`btn-theme-${themeKey}`);
    if (activeBtn) activeBtn.classList.add("active");
    
    triggerAlert(`THEME SWITCHED: ${THEMES[themeKey].name}`);
}

// Key bindings configuration
function setupEventListeners() {
    // Checkbox toggles
    switchHud.addEventListener("change", (e) => {
        showHud = e.target.checked;
        triggerAlert(`HUD PANEL: ${showHud ? "SHOW" : "HIDE"}`);
    });

    switchBoxes.addEventListener("change", (e) => {
        showBoxes = e.target.checked;
        triggerAlert(`BOX TRACKING: ${showBoxes ? "SHOW" : "HIDE"}`);
    });

    switchGlasses.addEventListener("change", (e) => {
        showGlasses = e.target.checked;
        triggerAlert(`CYBER GLASSES: ${showGlasses ? "ON" : "OFF"}`);
    });

    // Theme selector click triggers
    Object.keys(THEMES).forEach(themeKey => {
        const btn = document.getElementById(`btn-theme-${themeKey}`);
        if (btn) {
            btn.addEventListener("click", () => switchTheme(themeKey));
        }
    });

    // Snapshot button
    btnSnapshot.addEventListener("click", captureCleanSnapshot);

    // Keyboard Hotkey triggers
    window.addEventListener("keydown", (e) => {
        const key = e.key.toLowerCase();
        
        if (key === "q") {
            // Close tab / clean exit
            triggerAlert("SHUTTING DOWN FEED...");
            if (ws) ws.close();
            videoEl.srcObject.getTracks().forEach(track => track.stop());
            setTimeout(() => window.close(), 1000);
        }
        else if (key === "s") {
            captureCleanSnapshot();
        }
        else if (key === "h") {
            showHud = !showHud;
            switchHud.checked = showHud;
            triggerAlert(`HUD PANEL: ${showHud ? "SHOW" : "HIDE"}`);
        }
        else if (key === "b") {
            showBoxes = !showBoxes;
            switchBoxes.checked = showBoxes;
            triggerAlert(`BOX TRACKING: ${showBoxes ? "SHOW" : "HIDE"}`);
        }
        else if (key === "c") {
            // Cycle active theme
            const keys = Object.keys(THEMES);
            const currentIdx = keys.indexOf(activeThemeKey);
            const nextKey = keys[(currentIdx + 1) % keys.length];
            switchTheme(nextKey);
        }
    });
}

// Main Launcher initialization
window.addEventListener("DOMContentLoaded", () => {
    setupEventListeners();
    connectWebSocket();
    startCamera();
});
