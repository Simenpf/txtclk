const settingIds = [
    "background",
    "inactive_color",
    "active_color",
    "indicator_color",
    "glow_intensity",
    "clock_width_vw",
    "letter_size_vw",
    "grid_gap_px",
    "offset_x_px",
    "offset_y_px",
    "indicator_size_px",
    "indicator_offset_px",
];

const statusElement = document.getElementById("status");

let currentConfig = {};
let updateTimeout = null;

function showStatus(message) {
    statusElement.textContent = message;
}

function getFormConfig() {
    const config = {};

    for (const id of settingIds) {
        const input = document.getElementById(id);

        config[id] = input.type === "range"
            ? Number(input.value)
            : input.value;
    }

    return config;
}

function updateOutputs() {
    for (const id of settingIds) {
        const input = document.getElementById(id);
        const output = input.parentElement.querySelector("output");

        if (output) {
            output.textContent = input.value;

            if (input.type === "range") {
                output.textContent += id.endsWith("_vw")
                    ? " vw"
                    : " px";
            }
        }
    }
}

function populateForm(config) {
    currentConfig = config;

    for (const id of settingIds) {
        document.getElementById(id).value = config[id];
    }

    updateOutputs();
}

async function sendConfig() {
    try {
        showStatus("Applying changes...");

        const response = await fetch("/api/config", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(getFormConfig()),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Could not apply settings.");
        }

        currentConfig = await response.json();
        showStatus("Changes applied");
    } catch (error) {
        showStatus(`Error: ${error.message}`);
    }
}

function scheduleUpdate() {
    updateOutputs();
    showStatus("Applying changes...");

    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(sendConfig, 50);
}

async function loadConfig() {
    try {
        const response = await fetch("/api/config");

        if (!response.ok) {
            throw new Error("Could not load settings.");
        }

        populateForm(await response.json());
        showStatus("Connected");
    } catch (error) {
        showStatus(`Error: ${error.message}`);
    }
}

for (const id of settingIds) {
    document.getElementById(id)
        .addEventListener("input", scheduleUpdate);

    document.getElementById(id)
        .addEventListener("change", scheduleUpdate);
}

loadConfig();


const resetButton = document.getElementById("reset-config");

if (resetButton) {
const defaultButtonText = "Reset to factory defaults";
const confirmButtonText = "Tap again to confirm";

let resetConfirmTimeout = null;
let resetPending = false;

function cancelResetConfirmation() {
    resetPending = false;

    clearTimeout(resetConfirmTimeout);
    resetConfirmTimeout = null;

    resetButton.textContent = defaultButtonText;
    resetButton.classList.remove("confirm-reset");
}

resetButton.addEventListener("click", async () => {
    // First tap: ask for confirmation.
    if (!resetPending) {
        resetPending = true;

        resetButton.textContent = confirmButtonText;
        resetButton.classList.add("confirm-reset");

        showStatus("Tap again to reset. Cancelled automatically in 5 seconds.");

        resetConfirmTimeout = setTimeout(() => {
            cancelResetConfirmation();
            showStatus("Reset cancelled");
        }, 5000);

        return;
    }

    // Second tap: perform the reset.
    cancelResetConfirmation();

    clearTimeout(updateTimeout);

    resetButton.disabled = true;
    showStatus("Resetting configuration...");

    try {
        const response = await fetch("/api/config", {
            method: "DELETE",
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(
                error.detail || "Could not reset configuration."
            );
        }

        const config = await response.json();

        populateForm(config);
        showStatus("Factory defaults restored");

    } catch (error) {
        console.error("Reset failed:", error);
        showStatus(`Error: ${error.message}`);

    } finally {
        resetButton.disabled = false;
    }
});

}