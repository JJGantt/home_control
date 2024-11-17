# home_control

This server runs on a Raspberry Pi 5 and sends commands over Wi-Fi and CEC (and eventually Bluetooth) to control various home electronics (lighting, air conditioning, television, etc.).

It receives commands as strings at the /api/gpt endpoint and utilizes OpenAI's structured outputs to facilitate the various smart device controllers. The functionality of these devices has been extended to include weather forecasts and timers displayed through dynamic lighting throughout the home.

Commands originate from an EMP32 microcontroller with an IS2 microphone transmitting audio via WebSocket to a Quart server for wake word identification and voice-to-text processing before being sent to the main server. Originally, commands came from a Siri shortcut that forwards spoken text to the main server. This approach is still functional, but the unreliability of Siri and extra steps throughout an external network (typically adding at least 5 seconds to the process) warranted the creation of a fully local and customizable audio processing system. The firmware for the EMP32 and the audio processing server are [here](https://github.com/JJGantt/ESP32-AudioRelay) and [here](https://github.com/JJGantt/voice_control).

Demonstrations:

[Timer](https://drive.google.com/file/d/1lNFXadyBaEw3cxatC6kpN1qZ_msOE1W1/view?usp=sharing)

[Lighting](https://drive.google.com/file/d/1AI8I-KzgFazXOlBAxKcvLerGa7lcSwBB/view?usp=share_link)
