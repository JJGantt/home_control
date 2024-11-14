import uuid
import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOVEE_API_KEY")

class GoveeController():
    def __init__(self):
        self.data = {}
        self.base_url = "https://openapi.api.govee.com/router/api/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Govee-API-Key": api_key 
        }
        self.devices = {
            "bedroom_lamp": {
                "sku": "H6072",
                "address": "D1:0C:D2:32:37:38:35:9A"
            },
            "kitchen_leds": {
                "sku": "H6110",
                "address": "70:88:A4:C1:38:F0:11:4B"
            },
            "kitchen_island_light": {
                "sku": "H6008",
                "address": "E6:9A:D0:C9:07:80:5A:3E"
            },
            "entry_light": {
                "sku": "H6008",
                "address": "28:D7:D0:C9:07:86:6A:F4"
            },
            "kitchen_ceiling_light_1": {
                "sku": "H6008",
                "address": "77:F3:D0:C9:07:78:C9:A0"
            },
            "kitchen_ceiling_light_2": {
                "sku": "H6008",
                "address": "B2:C5:D0:C9:07:78:40:A4"
            }
        }
        self.states = {}

    async def get_devices(self):
        url = self.base_url + "/user/devices"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            return response.json()
    
    async def get_scenes(self):
        url = self.base_url + "/device/scenes"
        request_id = str(uuid.uuid4())

        payload = {
            "requestId": request_id,
            "payload": {
                "sku": self.kitchen_led_sku,
                "device": self.kitchen_led_adress
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
        return response.json()
    
    '''Example:
    online True
    powerSwitch 1
    gradientToggle 
    brightness 21
    segmentedBrightness 
    segmentedColorRgb 
    colorRgb 16777215
    colorTemperatureK 2000
    lightScene 
    musicMode 
    diyScene 
    snapshot 
    dreamViewToggle 
    '''
    async def get_state(self, device):
        url = self.base_url + "/device/state"
        request_id = str(uuid.uuid4())

        payload = {
            "requestId": request_id,
            "payload": {
                "sku": self.devices[device]["sku"],
                "device": self.devices[device]["address"]
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)

        self.states[device] = {}

        for capability in response.json()["payload"]["capabilities"]:
            self.states[device][capability["instance"]] = capability["state"]["value"]

        return self.states[device]
    
    async def get_all_states(self):
        for device in self.devices.keys():
            await self.get_state(device)
        return self.states
        
    async def control(self, device, type, instance, value):
        url = self.base_url + "/device/control"
        request_id = str(uuid.uuid4())

        payload = {
            "requestId": request_id,
            "payload": {
                "sku": self.devices[device]["sku"],
                "device": self.devices[device]["address"],
                "capability": {
                    "type": type,
                    "instance": instance,
                    "value": value
                }
            }
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)        
        return response.json()
    
    #value between 1-100
    async def set_brightness(self,device, value):
        if value:
            response = await self.control(device, "devices.capabilities.range", "brightness", value)
        return response

    async def power_state(self, device, value):
        if device in self.devices.keys():
            response = await self.control(device, "devices.capabilities.on_off", "powerSwitch", value)
            return response

    async def set_color(self, device, value):
        await self.control(device, "devices.capabilities.color_setting", "colorRgb", value)

    #value between 2000-9000
    async def set_temperature(self, device, value):
        await self.control(device, "devices.capabilities.color_setting", "colorTemperatureK", value)

    async def set_scene(self, device, value):
        await self.control(device, "devices.capabilities.dynamic_scene", "lightScene", value)

    async def trigger_alarm(self):   
        for device in self.devices.keys():
            await self.set_scene(device, 81)
        return 


async def main():
    govee = GoveeController()
    response = await govee.power_state("kitchen_island_light", 0)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())