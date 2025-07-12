from quart import Quart, request, jsonify, render_template
import asyncio
from controllers import (
    GoveeController, 
    KasaController, 
    SmartRentController, 
    TvController, 
    DisplayController
)
from controllers.nano.nano import NanoController
from state import StateManager
from open_ai import FunctionCaller
from logger import logger

app = Quart(__name__, static_folder='js')
nano = NanoController()
kasa = KasaController()
tv = TvController()
smart_rent = SmartRentController()
govee = GoveeController()
pisplay = DisplayController(tv)

controllers = {
    "nano": nano,
    "tv": tv,
    "smart_rent": smart_rent,
    "govee": govee,
    "kasa": kasa,
    "pisplay": pisplay,
}

state = StateManager(controllers)
function_caller = FunctionCaller(controllers, state)

#Handle asyncronous start up functions
@app.before_serving
async def startup():
    await smart_rent.start()
    await kasa.start()

#Basic display for debugging and testing
@app.route('/')
async def index():
    await state.full_update()
    return await render_template('index.html')

#Return current state of all devices
@app.route('/api/state', methods=['GET'])
async def current_state():
    return jsonify(state.get_states()) 

#Send commands as strings to be converted and executed as function calls
@app.route('/api/gpt', methods=['POST'])
async def gpt(): 
    data = await request.get_json()  
    prompt = data.get('prompt')
    response = await function_caller.prompt(prompt)

    return jsonify(response)

@app.route('/api/hexupdate', methods=['GET'])
async def hex_update():
    logger.info("hex weather update")
    #await nano.update_weather()

    await nano.set_temperature(hour_interval=2)

    print(nano.state.temp_now_rgb)

    await govee.set_color("island_light", nano.state.temp_now_rgb)
    await govee.set_color("cabinet_leds", nano.state.temp_now_rgb)
    

    return jsonify({"status": "weather updated"})



'''
---   All endpoints below this point are not currently used.    ---
---   The /api/gpt endpoint handles all incomming commands.     ---
'''



@app.route('/api/display_on', methods=['GET'])
def display_on():
    tv.set_active()
    state.update_state('tv', {'status': 'on'})
    return jsonify({"status": "on", "tv_state": state.get_states().get('tv', {})})

@app.route('/api/tv/volume_up', methods=['GET'])
def tv_volume_up():
    volume_increment = request.args.get('v', type=int, default=1)
    if volume_increment is None:
        return jsonify({"error": "Missing volume increment parameter"}), 400
    tv.volume_up(volume_increment)
    tv_state = tv.get_volume()
    state.update_state('tv', {'volume': tv_state})
    return jsonify({'volume_up': volume_increment, 'tv_state': state.get_states().get('tv', {})})

@app.route('/api/tv/volume_down', methods=['GET'])
def tv_volume_down():
    volume_decrement = request.args.get('v', type=int, default=1)
    if volume_decrement is None:
        return jsonify({"error": "Missing volume decrement parameter"}), 400
    tv.volume_down(volume_decrement)
    tv_state = tv.get_volume()
    state.update_state('tv', {'volume': tv_state})
    return jsonify({'volume_down': volume_decrement, 'tv_state': state.get_states().get('tv', {})})

@app.route('/api/tv/change_volume', methods=['GET'])
def tv_change_volume():
    change = request.args.get('c', type=int)
    if change is None:
        return jsonify({"error": "Missing volume change parameter"}), 400
    if change < 0:
        tv.volume_down(change * -1)
    else:
        tv.volume_up(change)
    tv_state = tv.get_volume()
    state.update_state('tv', {'volume': tv_state})
    return jsonify({'volume_change': change, 'tv_state': state.get_states().get('tv', {})})

@app.route('/api/tv/off', methods=['GET'])
def tv_off():
    tv.turn_off()
    state.update_state('tv', {'status': 'off'})
    return jsonify({'tv': 'off', 'tv_state': state.get_states().get('tv', {})})

@app.route('/api/get_cool_temp', methods=['GET'])
async def get_temp():
    controller = SmartRentController()
    try:
        await controller.login()
        controller.get_therm_state()
        cool_point = controller.therm_cool_point
        therm_state = controller.get_therm_state()
        state.update_state('thermostat', {'cool_point': cool_point, 'mode': therm_state[0], 'cool': therm_state[1], 'heat': therm_state[2]})
        return jsonify({'cool_point': cool_point, 'thermostat_state': state.get_states().get('thermostat', {})})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/changetemp', methods=['GET'])
async def change_temp():
    temp = request.args.get('t', type=int)
    increment = request.args.get('i', type=int)
    if temp is None and increment is None:
        return jsonify({"error": "Missing temperature or increment parameter"}), 400
    controller = SmartRentController()
    try:
        await controller.login()
        if temp is not None:
            await controller.change_temp(temp)
        elif increment is not None:
            await controller.directional_temp(increment)

        temp_state = controller.get_therm_state()
        state.update_state('thermostat', {'mode': temp_state[0], 'cool': temp_state[1], 'heat': temp_state[2]})
        return jsonify({'thermostat': state.get_states().get('thermostat', {})})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/govee/test', methods=['GET'])
def test():
    govee = GoveeController()
    govee.test()
    state.update_state('govee', {'test': 'complete'})
    return jsonify({"status": "test complete", "govee_state": state.get_states().get('govee', {})})

@app.route('/api/govee/lamp', methods=['GET'])
def govee_lamp_power():
    turn_on = request.args.get('on', type=int)
    if turn_on is None:
        return jsonify({"error": "Missing power parameter"}), 400
    govee = GoveeController()
    govee.lamp_on(turn_on)
    govee_state = govee.get_kitchen_state()
    state.update_state('Kitchen_LEDs', {'power': govee_state['powerSwitch'], 'color': govee_state['colorRgb']})
    return jsonify({"status": f"power: {turn_on}", "kitchen_leds_state": state.get_states().get('Kitchen_LEDs', {})})

@app.route('/api/hourly_weather', methods=['GET'])
def get_hourly_weather():
    try:
        nano.cancel_previous_timer()
        nano.set_hourly_forecast()
        nano_state = {
            'effect': nano.effect,
            'brightness': nano.state_brightness,
            'timer': nano.timer_task
        }
        state.update_state('Hexagons', nano_state)
        return jsonify({"status": "weather_set", "hexagons_state": state.get_states().get('Hexagons', {})})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/set_timer', methods=['GET'])
async def set_timer():
    minutes = request.args.get('s', type=float)
    if minutes is None:
        return jsonify({"error": "Missing timer seconds parameter"}), 400
    seconds = int(minutes * 60)
    try:
        nano.cancel_previous_timer()
        nano.timer_task = asyncio.ensure_future(nano.set_timer(seconds))
        nano_state = {
            'effect': nano.effect,
            'brightness': nano.state_brightness,
            'timer': nano.timer_task
        }
        state.update_state('Hexagons', nano_state)
        return jsonify({"status": "timer is set", "hexagons_state": state.get_states().get('Hexagons', {})})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    