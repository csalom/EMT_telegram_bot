#!/usr/bin/env
# -*- encoding: utf-8 -*-

import time
import schedule
import logging
from datetime import datetime

from telegram import Bot
from bot_conf import BOT_TOKEN, CHAT_ID
from bot import EMTBot

# create logger
logger = logging.getLogger('scheduled')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class EMTNotificationBot(object):
    def __init__(self):
        logger.debug('[INIT] Starting')
        self.bot = Bot(token=BOT_TOKEN)

    def _is_not_weekend(self):
        return datetime.now().isoweekday() in range(1, 6)

    def scheduled_bus(self):
        if self._is_not_weekend():
            logger.debug('[Scheduled_bus]')
            emt_bot = EMTBot()
            emt_bot.get_stop_info(self.bot, CHAT_ID)

    def run(self):
        schedule.every().day.at("17:40").do(self.scheduled_bus)
        schedule.every().day.at("17:45").do(self.scheduled_bus)
        while True:
            schedule.run_pending()
            time.sleep(30)


if __name__ == '__main__':
    bot = EMTNotificationBot()
    bot.run()
