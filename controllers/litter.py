#https://github.com/natekspencer/pylitterbot

import asyncio
from pylitterbot import Account
from dotenv import load_dotenv
import os

load_dotenv()
username = os.getenv("LITTER_USER_NAME")
password = os.getenv("LITTER_PASSWORD")

async def main():
    account = Account()
    try:
        await account.connect(username=username, password=password, load_robots=True)

        print("Robots:")
        for robot in account.robots:
            print(robot)
            history = await robot.get_activity_history()
            insight = await robot.get_insight()
            print(history)
            print(insight)
    finally:
        await account.disconnect()

if __name__ == "__main__":
    asyncio.run(main())