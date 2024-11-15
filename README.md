This server runs on a raspberry pi 5 and sends commands over wifi and cec(and eventually bluetooth) to control various home electronics(Lighting, air conditioning, telivision, etc.). Commands originate from a EMP32 microcontroller with a IS2 microphone transmitting audio via WebSocket to a Quart server for wake word identification and voice-to-text processing. 

This server recieves commands as strings at the /api/gpt endpoint and utilizes openai'a structured outputs to faciliate various smart device controllers. The fucntionality of these devices has been extended to include weather forecasts and timer functionality displayed through dynamic lighting.


