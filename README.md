# home_control

This server runs on a raspberry pi 5 and sends commands over wifi and cec(and eventually bluetooth) to control various home electronics(Lighting, air conditioning, telivision, etc.).

It recieves commands as strings at the /api/gpt endpoint and utilizes openai'a structured outputs to faciliate the various smart device controllers. The functionality of these devices has been extended to include weather forecasts and timers displayed through dynamic lighting throughout the home.

Commands originate from a EMP32 microcontroller with a IS2 microphone transmitting audio via WebSocket to a Quart server for wake word identification and voice-to-text processing before being sent to the main server. Originally commands came from a Siri shortcut that forwards spoken text to the main server. This is still functional, but the unreliability of Siri and extra steps throughout an external network(typically adding at least 5 seconds to the process) warranted the creation of a fully internal and customizable audio processing system. The firmware for the EMP32 and the audio processing server are [here](https://github.com/JJGantt/ESP32-AudioRelay) and [here](https://github.com/JJGantt/voice_control).
