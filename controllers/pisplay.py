import subprocess

class DisplayController:
    def __init__(self, tv):
        self.tv = tv
        self.chromium_process = None

    def navigate_to_url(self, url):
        if self.chromium_process:
            self.chromium_process.terminate()
            self.chromium_process.wait()

        self.chromium_process = subprocess.Popen([
            "chromium-browser",
            "--start-fullscreen",
            "--new-window",
            "--disable-gpu",
            "--disable-notifications",
            "--disable-infobars",
            "--disable-translate",
            "--disable-features=AutofillServerCommunication",
            "--disable-blink-features=AutomationControlled",
            url
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    def open_weather(self):
        self.tv.set_active()
        self.navigate_to_url("https://www.windy.com/28.542/-81.379?radar,2024110921,28.014,-81.381,8,m:esBadTx")
