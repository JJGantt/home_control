
from controllers.nano import NanoController
from controllers.govee import GoveeController
from controllers.tv import TvController
from controllers.srent import SmartRentController

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

    def nano_update(self):
        nano = self.controllers["nano"]
        nano.get_current_state()
        print(nano.state)
        self.update_state('Hexagons', {
            #'effect': nano.state["effect"], 
            'brightness': nano.state["brightness"], 
            'timer': str(nano.timer_task)
        })

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







        


