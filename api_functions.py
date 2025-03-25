import asyncio

async def get_exchange_rate():
    """
    Simulates an API call to get exchange rate.
    In a real application, this would make an actual API request.
    """
    # Simulate API call latency
    await asyncio.sleep(1)
    return 1.2

# Add more API functions here as needed 