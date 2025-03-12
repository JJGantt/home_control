
from controllers.nano import NanoController
from controllers.govee import GoveeController
from controllers.tv import TvController
from controllers.srent import SmartRentController
from dataclasses import dataclass, asdict

@dataclass
class NanoState:
    brightness: int
    color: str

nano_state = NanoState(brightness=255, color="blue")
nano_dict = asdict(nano_state)
print(nano_dict)  # {'brightness': 255, 'color': 'blue'}


'''
controllers = {
    "nano": nano,
    "tv": tv,
    "smart_rent": smart_rent,
    "govee": govee,
    "kasa": kasa,
    "pisplay": pisplay,
}
'''
class StateManager:
    def __init__(self, controllers):
        self.controllers = controllers
        self.states = {
        }

    def get_states(self):
        return self.states

    def update_state(self, device, new_state):
        if device not in self.states: 
            self.states[device] = {}
        self.states[device].update(new_state)

    async def full_update(self):
        self.nano_update()
        await self.govee_update()
        await self.therm_update()
        await self.lock_update()
        await self.nano_update()

    async def nano_update(self):
        nano: NanoController = self.controllers["nano"]

        await nano.set_state()
        state = await nano.get_state()
        
        self.update_state('Hexagons', asdict(state))

    async def govee_update(self):
        govee = self.controllers["govee"]
        await govee.get_all_states()
        for device in govee.devices.keys():
            self.update_state(device, govee.states[device])

    async def therm_update(self):
        smart_rent = self.controllers["smart_rent"]
        therm_state = smart_rent.get_therm_state()
        self.update_state('thermostat', {
            'mode': therm_state[0], 
            'cool': therm_state[1], 
            'heat': therm_state[2]})

    async def lock_update(self):
        smart_rent = self.controllers["smart_rent"]
        locked = smart_rent.lock.get_locked()
        battery = smart_rent.lock.get_battery_level()
        self.update_state('lock', {'locked': locked, 'battery': battery})







        


