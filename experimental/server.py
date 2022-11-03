import asyncio
import json
import time

import websockets

last_check = None


async def check(websocket):
    print(websocket)
    if (last_check and last_check < time.time() - 10) or not last_check:
        with open("coffee_breaks.json", "r") as f:
            coffee_breaks = json.load(f)
            for coffee_break in coffee_breaks:
                await websocket.send(json.dumps(coffee_break))
                print(f"> {coffee_break}")
        last_check = time.time()
        print(last_check)


async def main():
    async with websockets.serve(check, "localhost", 8000):
        await asyncio.Future()


asyncio.run(main())
