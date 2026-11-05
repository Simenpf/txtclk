
const gridElement = document.getElementById("letter-grid");
const indicators = document.querySelectorAll(".minute-indicators span");

let letters = [];

function initializeGrid(grid) {
    gridElement.innerHTML = "";
    letters = [];

    for (const row of grid) {
        for (const character of row) {
            const letter = document.createElement("span");
            letter.className = "letter";
            letter.textContent = character;

            gridElement.appendChild(letter);
            letters.push(letter);
        }
    }
}

function updateDisplay(state) {
    const activeCells = new Set(
        state.active_cells.map(([row, col]) => row * 11 + col)
    );

    letters.forEach((letter, index) => {
        letter.classList.toggle("active", activeCells.has(index));
    });

    indicators.forEach((indicator, index) => {
        indicator.classList.toggle(
            "active",
            index < state.minute_indicators
        );
    });
}

function applyClockConfig(config) {
    const root = document.documentElement;

    root.style.setProperty("--background", config.background);
    root.style.setProperty("--inactive-color", config.inactive_color);
    root.style.setProperty("--active-color", config.active_color);
    root.style.setProperty("--indicator-color", config.indicator_color);

    root.style.setProperty("--glow-intensity", `${config.glow_intensity}px`);
    root.style.setProperty("--clock-width", `${config.clock_width_vw}vw`);
    root.style.setProperty("--letter-size", `${config.letter_size_vw}vw`);
    root.style.setProperty("--grid-gap", `${config.grid_gap_px}px`);

    root.style.setProperty("--clock-offset-x", `${config.offset_x_px}px`);
    root.style.setProperty("--clock-offset-y", `${config.offset_y_px}px`);

    root.style.setProperty("--indicator-size", `${config.indicator_size_px}px`);
    root.style.setProperty("--indicator-offset", `${config.indicator_offset_px}px`);
}

window.applyClockConfig = applyClockConfig;

async function refreshClock() {
    try {
        const response = await fetch("/api/clock");

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const state = await response.json();

        if (letters.length === 0) {
            initializeGrid(state.grid);
        }

        updateDisplay(state);
    } catch (error) {
        console.error("Failed to update clock:", error);
    }
}

function connectConfigSocket() {
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(
        `${protocol}//${location.host}/ws/config`
    );

    socket.addEventListener("message", (event) => {
        try {
            const config = JSON.parse(event.data);
            applyClockConfig(config);
        } catch (error) {
            console.error("Invalid configuration received:", error);
        }
    });

    socket.addEventListener("close", () => {
        console.warn("Configuration WebSocket disconnected. Reconnecting...");
        setTimeout(connectConfigSocket, 1000);
    });

    socket.addEventListener("error", (error) => {
        console.error("Configuration WebSocket error:", error);
        socket.close();
    });

    // Keep the connection alive.
    socket.addEventListener("open", () => {
        const heartbeat = setInterval(() => {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send("ping");
            } else {
                clearInterval(heartbeat);
            }
        }, 30000);
    });
}

refreshClock();
setInterval(refreshClock, 1000);

if (!document.body.classList.contains("config-page")) {
    connectConfigSocket();
}
