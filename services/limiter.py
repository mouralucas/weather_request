import time
from collections import deque, defaultdict
import asyncio


class RequestLimiter:
    def __init__(self, max_requests_per_period=60, period=60):
        # Create the basic data for validate the number of requests per period
        # The default is 60 requests per minute
        self.max_requests_per_period = max_requests_per_period
        self.period = period
        self.queue = deque(maxlen=max_requests_per_period)

    async def check_availability(self):
        # This method controls the access to the resource based in the params
        # Checks every 0.5s if the maximum number of requests is already used, if it is suspended and checks again until the period passes
        while len(self.queue) >= self.max_requests_per_period and time.time() - self.queue[0] < self.period:
            await asyncio.sleep(0.5)

        # When the period passes (or not yet full) add a new request to the queue
        self.queue.append(time.time())

    async def fetch_with_rate_limit(self, fn, *args, **kwargs):
        # before execute the function check if the process have a free slot
        # uses await so maintains the loop free to other actions
        await self.check_availability()
        try:
            # With the slot granted execute the function (in this case the request to OpenWeather)
            return await fn(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Error during function execution: {str(e)}")