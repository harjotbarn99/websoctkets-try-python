import asyncio
import json
import logging
import websockets

logging.basicConfig()

STATE = {"value": 0}

USERS = set()


def state_event():
    toSend = json.dumps({"type": "state", **STATE})
    print(f"\nstate event -> {toSend}\n")
    return toSend


def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})


async def notify_state():
    print("\nnotify state\n")
    if USERS:  # asyncio.wait doesn't accept an empty list
            message = state_event()
            print("\nnotify state if\n")
            await asyncio.wait([user.send(message) for user in USERS])


async def notify_users():
    print("\nnotify users\n")
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        print("\nnotify users if\n")
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.add(websocket)
    print("\nregistered\n")
    await notify_users()


async def unregister(websocket):
    USERS.remove(websocket)
    print("\nunregistered\n")
    await notify_users()


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    print("\nserver started\n")
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            print(f"\n{data}\n")
            if data["action"] == "minus":
                STATE["value"] -= 1
                await notify_state()
            elif data["action"] == "plus":
                STATE["value"] += 1
                await notify_state()
            else:
                logging.error("unsupported event: {}", data)
    finally:
        print("\nfinally\n")
        await unregister(websocket)


start_server = websockets.serve(counter, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()