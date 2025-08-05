import asyncio
import threading
from app import TwitchMonitorApp

def run_async_loop(loop: asyncio.AbstractEventLoop):
    """Sets the event loop for the current thread and runs it forever."""
    asyncio.set_event_loop(loop)
    loop.run_forever()

if __name__ == "__main__":
    async_loop = asyncio.new_event_loop()

    thread = threading.Thread(target=run_async_loop, args=(async_loop,), daemon=True)
    thread.start()

    app = TwitchMonitorApp(loop=async_loop)
    app.mainloop()