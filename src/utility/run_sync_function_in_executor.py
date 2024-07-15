import asyncio
from typing import Callable, Any

async def run_sync_function_in_executor(sync_func: Callable[..., Any], *args, **kwargs) -> Any:
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, sync_func, *args, **kwargs)
    return result
