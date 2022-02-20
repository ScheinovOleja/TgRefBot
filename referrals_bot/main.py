import os

from aiogram import Dispatcher
from aiogram.utils import executor

from referrals_bot import dp, loop, logger
from referrals_bot.handlers import register_admin, register_users


async def main(dispatcher: Dispatcher):
    await register_admin(dispatcher)
    await register_users(dispatcher)


async def shutdown(dispatcher: Dispatcher):
    logger.debug(f"Shutdowning...")
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RollerSiteCms.settings')
    executor.start_polling(dp, skip_updates=True, loop=loop, on_shutdown=shutdown, on_startup=main)
