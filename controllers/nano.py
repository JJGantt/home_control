import requests
from datetime import datetime
from helpers.openmeteo import openmeteo
from helpers.weather_codes import weather_codes
import pandas as pd
import random
from helpers.new_codes import new_codes
import asyncio
from .govee import GoveeController
from .kswitch import KasaController
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("NANO_API_KEY")

#Controls the hexagon lighting. 
#Includes functionality to display the weather and timers on the hexagons
class NanoController:
    def __init__(self):
        self.auth_token = api_key
        self.ip_address = "172.20.7.17"
        self.port = "16021"
        self.panels = []
        self.state_dict = {i: [(0, 0, 0, 1)] for i in range(len(self.panels))}

        self.timer_task = None
        self.effect = "Cocoa Beach"
        self.state = {
            "brightness" : 0, 
            "effect" : "Cocoa Beach"
        }
        self.get_panels()

    @property
    def base_url(self):
        return f"http://{self.ip_address}:{self.port}/api/v1/{self.auth_token}"

    def get_current_state(self):
        url = self.base_url + "/state"
        response = requests.get(url)
        self.state = response.json()

        self.state["brightness"] = response.json()['brightness']['value']

        url = self.base_url + "/effects"
        response = requests.get(url)
        effect = response.json()['select']
        if effect != '*Dynamic*':
            self.state["effect"] = response.json()['select']

    def set_previous_state(self):
        self.set_brightness(self.state["brightness"])
        
        if "effect" in self.state:
            print(self.state)
            self.set_effect(self.state["effect"])
        else:
            self.set_effect("Cocoa Beach")
    
    def set_brightness(self, brightness):
            url = self.base_url + "/state"
            payload = {'brightness': {'value': brightness, 'duration': 2}}
            response = requests.put(url, json=payload)
            return response
    
    def set_effect(self, effect):
        url = self.base_url + "/effects/select"
        payload = {'select': effect}
        response = requests.put(url, json=payload)
        return response

    def update_token(self):
        url = f"http://{self.ip_address}:{self.port}/api/v1/new"
        response = requests.post(url)
        self.auth_token = response.json()["auth_token"]
        print(self.auth_token)

    def get_panels(self):
        response = requests.get(self.base_url + "/panelLayout/layout")

        if response.status_code == 200:
            layout = response.json()
        else:
            print(f"Failed to retrieve layout. Status code: {response.status_code}")

        panels = []
        for panel in layout["positionData"]:
            panelID = panel["panelId"]
            y = panel["y"]
            if panelID != 0:
                panels.append((panelID, y))

        panels.sort(reverse=True, key = lambda x: x[1])
        panels = [id for id, _ in panels]

        self.panels = panels

    def set_color(self, hue):
        url = self.base_url + "/state"   #todo: this

    def dynamic(self, color_dict):
        url = self.base_url + "/effects"

        for i in color_dict:
            self.state_dict[i] = color_dict[i]

        intervals = self.get_intervals(self.state_dict)
        max_interval = max(intervals)

        animData_string = f"{len(self.panels)}"
        for i, rgbt_array in enumerate(self.state_dict.values()):
            mult = int(max_interval / intervals[i])          #todo: least common denominator
            animData_string += f" {str(self.panels[i])} {len(rgbt_array) * mult}" 
            rgbt_string = ""
            for r, g, b, t in rgbt_array:
                rgbt_string += f" {r} {g} {b} 0 {t}"
            rgbt_string *= mult
            animData_string += rgbt_string

        payload = {"write" : {"command" : "display", "animType" : "custom", "animData" : animData_string, "loop": True, "palette":[]}}
        response = requests.put(url, json=payload)
        return response

    def get_intervals(self, color_dict):
        intervals = []
        for value in color_dict.values():
            total_interval = 0
            for _, _, _, t in value:
                total_interval += t
            intervals.append(total_interval)
        return intervals

    async def set_timer(self, seconds):
        govee = GoveeController()
        kasa = KasaController()
        await kasa.start()
        for device in govee.devices.keys():
            await govee.get_state(device)
            govee.states[device]["original_color"] = govee.states[device]["colorRgb"]

        self.get_current_state()

        panel_count = len(self.panels)
        seconds_per_panel = seconds / panel_count
        t = int(seconds_per_panel * 10)

        sub_ts = int(seconds_per_panel)

        transition_array = []
        r_0, g_0, b_0 = (0, 0, 255)
        r_1, g_1, b_1 = (255, 174, 66)
        r_d, g_d, b_d = (r_1 - r_0, g_1 - g_0, b_1 - b_0)
        for sub_t in range(sub_ts):
            rgbt = (int(r_0 + sub_t * (r_d / sub_ts)),
                    int(g_0 + sub_t * (g_d / sub_ts)),
                    int(b_0 + sub_t * (b_d / sub_ts)),
                    10)
            transition_array.append(rgbt)

        start_color = [(r_0, g_0, b_0, 10)]
        end_color = [(r_1, g_1, b_1, 10)]

        start = {i: start_color for i in range(panel_count)}
        
        self.dynamic(start)

        for i in range(panel_count - 1, -1, -1):
            self.dynamic({i: transition_array})
            await asyncio.sleep(seconds_per_panel)
            self.dynamic({i: end_color})

        await kasa.all_on()
        await asyncio.sleep(0.25)
        await govee.trigger_alarm()
        self.set_brightness(100)
        self.dynamic(self.get_end_animation())
        
        await asyncio.sleep(15)

        self.set_previous_state()
        for device in govee.devices.keys():
            await govee.control(device, "devices.capabilities.color_setting", "colorRgb", govee.states[device]["original_color"])

    def get_end_animation(self):
        anim_dict = {}
        for p in range(len(self.panels)):
            color_array = []
            for i in range(20):
                rgbt = (int(random.random() * 255), int(random.random() * 255), int(random.random() * 255), 5)
                color_array.append(rgbt)
            anim_dict[p] = color_array
        return anim_dict

    def cancel_previous_timer(self):
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()  
            print("Previous timer cancelled")
            self.set_previous_state()

    def get_weather_df(self):
        df, sunrise, sunset = openmeteo()
        current_utc = pd.to_datetime(datetime.now()).tz_localize('UTC')

        df = df[df['date'] >= current_utc]
        return df

    def set_hourly_forecast(self):
        df = self.get_weather_df()
        now = datetime.now()
        current_hour = now.hour if now.minute < 30 else now.hour + 1

        hours = [(current_hour + i) % 24 for i in range(6)]
        is_night = [0 if hour > 6 and hour < 19 else 1 for hour in hours]

        codes = df["weather_code"][:6].to_list()
        codes = [int(code) for code in codes]

        color_dict = {}
        for n in range(6):
            code_array = new_codes[codes[n]][is_night[n]].copy()
            random.shuffle(code_array)
            color_dict[n] = code_array 

        self.dynamic(color_dict)

    def n_hour_precipitation(self, n):
        df = self.get_weather_df()

        n_hour_precip = df.groupby(df.index // n)['precipitation_probability'].mean()[:6]
        color_dict = self.precip_to_color_dict(n_hour_precip)
        self.dynamic(color_dict)

    def precip_to_color_dict(self, precips):
        return { i : [(0,0, 2.55 * precip, 1)] for i, precip in enumerate(precips) }

    def test(self):
        codes = [0, 1, 2, 3, 63, 65]
        #codes = [0, 1, 2, 3, 3, 3]
        is_night = [0] * 6

        color_dict = {}
        for n in range(6):
            code_array = new_codes[codes[n]][is_night[n]].copy()
            random.shuffle(code_array)
            color_dict[n] = code_array

        print(color_dict)
        print(codes)
        print(is_night)

        self.dynamic(color_dict)


async def main():
    nano = NanoController()
    await nano.set_timer(30)

if __name__ == "__main__":
    asyncio.run(main())





