import asyncio
import websockets
import threading

compass_heading = -1.0
async def parseHeading(websocket, path):
    global compass_heading
    heading = await websocket.recv()
    compass_heading = float(heading)
    # print(compass_heading)

def run_event_loop(loop):
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(parseHeading, "192.168.4.1", 1234)
    loop.run_until_complete(start_server)
    loop.run_forever()

loop = asyncio.new_event_loop()
websocket_thread = threading.Thread(target=run_event_loop, args=(loop,))
websocket_thread.start()
# run_event_loop()
def get_heading():
    return compass_heading
if __name__ == '__main__':
    import time
    while True:
        print(compass_heading)
        time.sleep(.1)