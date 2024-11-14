async function updateState() {
    const response = await fetch('http://172.20.6.231:8080/api/state');
    const states = await response.json();
    const thermostatState = states['thermostat'];
    document.getElementById('thermostat').textContent = 
        `{Mode: [${thermostatState.mode}], Cool: ${thermostatState.cool}, Heat: ${thermostatState.heat}}`;
    const lockState = states['lock'];
        document.getElementById('lock-status').textContent = 
        `${lockState.locked ? "Locked" : "Unlocked"}, Battery: ${lockState.battery}`;
    document.getElementById('json-output').textContent = JSON.stringify(states, null, 2)

}

async function sendPrompt() {
    const prompt = document.getElementById('prompt').value;
    
    if (!prompt.trim()) {
        return; 
    }
    
    try {
        const response = await fetch('/api/gpt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        document.getElementById('response').textContent = JSON.stringify(result, null, 2);
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('response').textContent = `Error: ${error.message}`;
    }
}

function checkEnter(event) {
    if (event.key === 'Enter') {
        sendPrompt();
        event.preventDefault(); 
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateState();
});
