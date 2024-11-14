from openai import OpenAI
import json
from controllers import SmartRentController
import asyncio
from dotenv import load_dotenv
import os
from logger import logger

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

'''
controllers = {
    "nano": nano,
    "tv": tv,
    "smart_rent": smart_rent,
    "govee": govee,
    "kasa": kasa
    "state": state
    "pisplay": pisplay
}
'''
 
class FunctionCaller:
    def __init__(self, controllers, state):
        self.controllers = controllers
        self.client = OpenAI()
        self.client.api_key = openai_api_key
        self.state_manager = state

        self.tools = [
            {   
                "type": "function",
                "function": { 
                "name": "set_thermostat_temperature",
                "description": "Sets the thermostat temperature or adjusts it based on a change value. If no values are given it will return the current termperature. Should be set to 78 if user is leaving",
                "parameters": {
                    "type": "object",
                    "properties": {
                    "temperature": {
                        "type": "integer",
                        "description": "The desired temperature to set the thermostat to"
                    },
                    "change": {
                        "type": "integer",
                        "description": "The change in temperature to adjust the thermostat by"
                    }
                    },
                    "required": [
                    ]
                    }
                }
            },
            {   
                "type": "function",
                "function": {
                    "name": "lock",
                    "description": "Handles the lock state of the door. Returns lock state if no arguments provided. Door should be unlocked if user is leaving",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lock": {
                                "type": "integer",
                                "enum": [0, 1],
                                "description": "Set to 1 to lock the door"
                            },
                            "unlock": {
                                "type": "integer",
                                "enum": [0, 1],
                                "description": "Set to 1 to unlock the door"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "tv_volume",
                    "description": "Changes the volume of the tv based on the user's input",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "integer",
                                "description": "The amount to change the volume. Value is negative for turning the tv down.",
                            }
                        },
                        "required": ["amount"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_hexagons",
                    "description": "Sets hexagon lights with various modes and brightness",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "brightness": {
                            "type": "number",
                            "description": "Brightness level for the hexagons. Only use if user specificly mentions brightness. Can be sent as only argument"
                        },
                        "effect": {
                            "type": "string",
                            "enum": [
                                "Cocoa Beach",
                                "Cotton Candy",
                                "Date Night",
                                "Jungle",
                                "Morning Sky",
                                "Prism",
                                "Vintage Modern",
                                "Waterfall"
                            ],
                            "description": "The effect(color scheme) to apply to the hexagons, can be picked at random if not specified"
                        },
                        "mode": {
                            "type": "string",
                            "enum": [
                            "Effect",
                            "Previous",
                            "Hourly_Weather",
                            "Timer"
                            ],
                            "description": "Mode to set the hexagons to"
                        },
                        "time_length": {
                            "type": "number",
                            "description": "Time length to set the timer in minutes(portions of minutes are acceptable), required when mode is 'Timer'"
                        }
                        },
                        "required": [
                        ]
                    }
                }
            },
            {
                "type": "function",
                "function" : {
                    "name": "get_pretitiest_girl_info",
                    "description": "Returns information on who the prettiest girl is",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "control_lights",
                    "description": "Controls various lights based on the specified action and value.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device": {
                                "type": "string",
                                "enum": [
                                    "bedroom_lamp",
                                    "kitchen_leds",
                                    "kitchen_island_light",
                                    "pool_table_light",
                                    "entry_light",
                                    "kitchen_ceiling_light_1",
                                    "kitchen_ceiling_light_2"
                                ],
                                "description": "The identifier for the smart light device."
                            },
                            "action": {
                                "type": "string",
                                "enum": [
                                    "absolute_brightness",
                                    "change_brightness",
                                    "get_brightness",
                                    "set_color",
                                    "set_temperature",
                                    "power_state"
                                ],
                                "description": "The action to perform on the light. Options:\n\n"
                                    "- 'absolute_brightness': Sets brightness to an absolute value (1-100).\n"
                                    "- 'change_brightness': Changes brightness by a relative amount (positive or negative).\n"
                                    "- 'get_brightness': Retrieves the current brightness level.\n"
                                    "- 'set_color': Sets the light to a specific color using an RGB value (0 to 16777215).\n"
                                    "- 'set_temperature': Sets the color temperature (2000K to 9000K).\n"
                                    "- 'power_state': Turns the light on or off (value 1 for on, 0 for off)."
                            },
                            "value": {
                                "type": "integer",
                                "description": "The value for brightness, color, temperature, or power state, depending on the action"
                            }
                        },
                        "required": ["device", "action", "value"],
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "control_display",
                    "description": "Controls the display. Use this when the user asks to show the weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "mode": {
                                "type": "string",
                                "enum": [
                                    "Weather"
                                ],
                                "description": "The mode to change the display to"
                            },
                            "value": {
                                "type": "string",
                                "enum": [
                                    "None"
                                ],
                                "description": ""
                            }
                        },
                        "required": ["mode"],
                    }
                }
            }

        ]

    async def prompt(self, message):
        messages = []
        messages.append({"role": "system", "content": "You use the supplied tools to control various home electronics for the user"})

        logger.info(f"prompt: {message}")
        messages.append({"role": "user", "content": message})
        
        response = self.client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=self.tools,
        )

        message = response.choices[0].message
        tool_calls = message.tool_calls
        
        if tool_calls == None:
            logger.info(f"message - {message.content}")
            return message.content
        
        tasks = [self.handle_tool_call(tool_call) for tool_call in tool_calls]
        results = await asyncio.gather(*tasks)

        logger.info(results)

        return "" 
    
    async def handle_tool_call(self, tool_call):
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if hasattr(self, function_name):
            logger.info(f"function: {function_name}, arguments: {arguments}")

            func = getattr(self, function_name) 
            result = await func(**arguments) 
        return result

    async def control_display(self, mode, value=None):
        pisplay = self.controllers["pisplay"]

        if mode == "Weather":
            pisplay.open_weather()
            return {"response": {"display_mode": "weather"}}

    async def set_thermostat_temperature(self, temperature=None, change=None):
        smart_rent = self.controllers["smart_rent"]

        if temperature:
            try:
                new_temp = await smart_rent.change_temp(temperature)
                if new_temp == temperature:
                    return {"status": "success", 
                            "data": {"temperature": temperature}}
                else:
                    return {"status": "error", 
                            "data": {"temperature": new_temp}, 
                            "error": "temperature has not been changed to correct value"}
            except Exception as e:
                return {"status": "error", 
                        "error": str(e)}
        elif change:
            try:
                new_temp = await smart_rent.directional_temp(change)
                return {"status": "success", 
                        "data": {"temperature": temperature}}
            except Exception as e:
                return {"status": "error", 
                        "error": str(e)}
        else:
            try:
                smart_rent.get_therm_state()
                cool_point = smart_rent.therm_cool_point     #todo: heat logic
                return {"status": "success",
                        "data": {"temperature": cool_point}}  
            except Exception as e:
                return {"status": "error",
                        "error": str(e)}

    async def lock(self, lock=None):
        smart_rent = self.controllers["smart_rent"]  

        if lock != None:
            locked = await smart_rent.set_locked(lock)
            return {"status": "success",
                    "data": {"locked": locked}}
        else:
            locked = await smart_rent.get_locked()
            return {"status": "success",
                    "data": {"locked": locked}}
        
    async def tv_volume(self, amount):
        tv = self.controllers["tv"]
        tv.change_volume(amount)
        return {"status": "success",
                "data": {"volume_change": amount}}
    
    async def set_hexagons(self, mode=None, brightness=None, time_length=None, effect=None):
        nano = self.controllers["nano"]
        nano.cancel_previous_timer()

        try:
            if brightness != None:
                response = nano.set_brightness(brightness)
                return {"status": "success",
                        "data": {"response": response}}
            elif effect != None:
                response = nano.set_effect(effect)
                return {"status": "success",
                        "data": {"response": response}}
            if mode != None:
                if mode == "Previous":
                    nano.set_previous_state()
                    return {"status:" "success"
                            "data": {"mode": mode}}
                elif mode == "Hourly_Weather":
                    nano.set_hourly_forecast()
                    return {"status:" "success"
                            "data": {"mode": mode}}
                elif mode == "Timer":
                    if time_length == 0:
                        return {"status": "success",
                                "data": {"time": 0}}
                    seconds = int(time_length * 60)
                    nano.timer_task = asyncio.create_task(nano.set_timer(seconds))
                    return {"status": "success",
                            "data": {"time": time_length}}
        except Exception as e:
            return {"status": "error",
                    "error": str(e)}
    
    async def control_lights(self, device, action, value):
        govee = self.controllers["govee"]
        kasa = self.controllers["kasa"]
        try:
            if action == "power_state":
                if value == 1:
                    if device in [
                        "entry_light", 
                        "kitchen_ceiling_light_1", 
                        "kitchen_ceiling_light_2",
                    ]:
                        await kasa.power_state("kitchen_ceiling_lights", value)
                    else:
                        await kasa.power_state(device, value)
                    await govee.power_state(device, value)
                else:
                    await kasa.power_state(device, value)    
                    await govee.power_state(device, value)   
            elif action == "absolute_brightness":
                await govee.set_brightness(device, value)
            elif action == "change_brightness":
                await govee.get_state(device)
                current_brightness = govee.state[device]["brightness"]
                await govee.set_brightness(current_brightness + value)
            elif action == "get_brightness":
                await govee.get_state(device)
                current_brightness = govee[device]["brightness"]
                return {"status": "success",
                        "data": {"brightness": current_brightness}}
            elif action == "set_color":
                await govee.set_color(device, value)
            elif action == "set_temperature":
                await govee.set_temperature(device, value)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error",
                    "error": str(e)}

    async def get_pretitiest_girl_info(self): 
        return {"status": "success",
                "data": {"prettiest_girl": "lyz"}}

async def main():
    caller = FunctionCaller()
    await caller.prompt("make it 72 in here")

if __name__ == "__main__":
    asyncio.run(main())





