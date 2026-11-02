
const gridElement = document.getElementById("letter-grid");
const indicators = document.querySelectorAll(".minute-indicators span");

let letters = [];

// Create the letter grid once.
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

// Update illuminated letters and minute indicators.
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

// Fetch the latest clock state.
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

// Start the clock.
refreshClock();
setInterval(refreshClock, 1000);
