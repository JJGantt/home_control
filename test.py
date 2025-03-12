import httpx
from controllers.nano.nano import NanoController
import asyncio
from controllers import GoveeController

govee = GoveeController()


async def main():
    nano = NanoController()
    await nano.set_temperature(hour_interval=2)

    print("temp")
    print(nano.state.temp_now_rgb)
    await govee.set_color("island_light", nano.state.temp_now_rgb)


if __name__ == "__main__":
    asyncio.run(main())
