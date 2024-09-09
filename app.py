import logging
from loader import dp, bot
from handlers import dp
import asyncio



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(create_db_pool(dp))
    # loop.create_task(clear_expired_basket_items(dp["db_pool"]))
    logging.basicConfig(level=logging.INFO, filename="logs.txt")
    try:
        loop.run_until_complete(dp.start_polling(bot))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()