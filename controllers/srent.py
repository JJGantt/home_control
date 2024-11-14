import asyncio
from smartrent import async_login
from dotenv import load_dotenv
import os

load_dotenv()
username = os.getenv("EMAIL")
password = os.getenv("SMARTRENT_PASSWORD")

class SmartRentController:
    def __init__(self):
        self.username = username
        self.password = password
        self.api = None
        self.lock = None
        self.thermostat = None
        self.therm_mode = None
        self.therm_cool_point = None
        self.therm_heat_point = None

    async def login(self):
        self.api = await async_login(self.username, self.password)
        self.lock = self.api.get_locks()[0]
        self.thermostat = self.api.get_thermostats()[0]

    async def relogin(self):
        while True:
            await self.login()
            await asyncio.sleep(3600)

    async def start(self):
        asyncio.create_task(self.relogin())

    async def set_locked(self, locked):
        locked = True if 1 else False
        locked = await self.lock.async_set_locked(locked)
        
        status = self.lock.get_locked() 
        return status

    async def get_locked(self):
        return await self.lock.get_locked() 

    async def display_locks(self):
        for index, lock in enumerate(self.locks):
            status = "locked" if await lock.get_locked() else "unlocked"
            print(f"Lock {index}: {status}")

    def get_therm_state(self):
        self.therm_mode = self.thermostat.get_mode()
        self.therm_cool_point = self.thermostat.get_cooling_setpoint()
        self.therm_heat_point = self.thermostat.get_heating_setpoint()
        
        return (self.therm_mode, self.therm_cool_point, self.therm_heat_point)

    async def directional_temp(self, increment):
        self.get_therm_state()
        if self.therm_mode == 'cool':
            new_temp = int(self.therm_cool_point) + increment
            await self.thermostat.async_set_cooling_setpoint(new_temp)
        else:
            new_temp = int(self.therm_heat_point) + increment
            await self.thermostat.async_set_heating_setpoint(new_temp)

        return new_temp #todo: verification

    async def change_temp(self, temp):
        self.get_therm_state()
        if self.therm_mode == 'cool':
            await self.thermostat.async_set_cooling_setpoint(temp)
        else:
            await self.thermostat.async_set_heating_setpoint(temp)
        return temp #todo: verifcation
    
    async def get_temp_setting(self):
        self.get_therm_state()
        if self.therm_mode == 'cool':
            return self.therm_cool_point
        else:
            return self.therm_heat_point

