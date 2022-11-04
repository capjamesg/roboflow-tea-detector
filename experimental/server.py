import asyncio
import json
import time

import websockets

last_check = None


async def check(websocket):
    print(websocket)
    if (last_check and last_check < time.time() - 10) or not last_check:
        with open("tea_breaks.json", "r") as f:
            tea_breaks = json.load(f)
            for tea_break in tea_breaks:
                await websocket.send(json.dumps(tea_break))
                print(f"> {tea_break}")
        last_check = time.time()
        print(last_check)


async def main():
    async with websockets.serve(check, "localhost", 8000):
        await asyncio.Future()


asyncio.run(main())
