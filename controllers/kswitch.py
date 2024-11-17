#command - kasa discover

import asyncio
from kasa import Discover
from logger import logger
from dotenv import load_dotenv
import os

load_dotenv()
username = os.getenv("KASA_USERNAME")
password = os.getenv("KASA_PASSWORD")

class KasaController:
    def __init__(self):
        #todo: make devices environmental
        self.devices = {
            "pool_table_light": "172.20.1.101",
            "kitchen_island_light": "172.20.1.102",
            "kitchen_ceiling_lights": "172.20.5.53"
        }

    #todo: make authentication variables environmental
    async def start(self):
        for device, IP in self.devices.items():
            self.devices[device] = await Discover.discover_single(
                IP, username=username, 
                password=password
            )
        await self.devices[device].set_alias(device)

    async def power_state(self, device, value):
        if device in self.devices.keys():
            if value == 1:
                await self.devices[device].turn_on() 
            elif value == 0:
                await self.devices[device].turn_off()

    async def all_on(self):
        for device in self.devices.keys():
            await self.devices[device].turn_on()


async def main():
    kasa = KasaController()
    await kasa.start()
    #print(kasa.devices.items())
    await kasa.power_state("kitchen_ceiling_lights", 1)
    #print(kasa.devices)

if __name__ == "__main__":
    asyncio.run(main())