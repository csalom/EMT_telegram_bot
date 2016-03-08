#!/usr/bin/env
# -*- coding: utf-8 -*-

import requests
from telegram import Updater
import logging

from bot_conf import BOT_TOKEN, BASE_URL

updater = Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher


# create logger
logger = logging.getLogger('emt_bot')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class EMTBot(object):
    def __init__(self):
        logger.info('[INIT] Starting')

    def get_info_bus(self, bus_info, clave, bot, chat_id):
        # Parsing to telegram messages bus information
        if "seconds" in bus_info[clave] and "destino" in bus_info[clave]:
            if bus_info[clave]['enParada']:
                bot.sendMessage(chat_id=chat_id, text="Bus a la aturada")
            elif bus_info[clave]['llegando']:
                bot.sendMessage(chat_id=chat_id,
                                text="Bus arribant a la aturada")
            else:
                res = "Temps estimat a l'aturada: {} minuts".format(
                        bus_info[clave]['seconds']/60)
                if bus_info[clave]['seconds'] % 60 != 0:
                    res += " i {} segons".format(
                            bus_info[clave]['seconds'] % 60)
                bot.sendMessage(chat_id=chat_id, text=res)

    def get_stop(self, bot, update):
        logger.info(update.message.chat_id)
        logger.info(update.message.text)
        try:
            bus_stop = update.message.text.split()[1]
        except IndexError:
            bot.sendMessage(chat_id=update.message.chat_id,
                            text="Aturada no introduida")
            return
        self.get_stop_info(bot, update.message.chat_id, bus_stop)

    def get_stop_info(self, bot, chat_id, bus_stop='572'):
        url = "{}?p={}".format(BASE_URL, bus_stop)
        logger.info(url)
        resp = requests.get(url)
        stop_info = resp.json()
        logger.info(resp.json())

        # Example of response
        # {u'error': False,
        #  u'errorMessage': u'',
        #  u'errorType': 0,
        #  u'estimaciones': [{u'color': u'5496AF',
        #                     u'line': u'16',
        #                     u'vh_first': {u'__hashCodeCalc': False,
        #                                   u'destino': u'ESTABLIMENTS',
        #                                   u'enParada': False,
        #                                   u'llegando': False,
        #                                   u'seconds': 1320},
        #                     u'vh_second': {u'__hashCodeCalc': False,
        #                                    u'enParada': False,
        #                                    u'llegando': False}}],
        #  u'nombreParada': u'General Riera, 30',
        #  u'timestamp': 1456959073977}

        if not stop_info['error']:
            text = "Aturada " + bus_stop + ": " + stop_info['nombreParada']
            bot.sendMessage(chat_id=chat_id, text=text)
            if not stop_info['estimaciones']:
                text = "No hi hi informació de l'aturada"
                bot.sendMessage(chat_id=chat_id, text=text)
            else:
                for bus_info in stop_info['estimaciones']:
                    bus_line = "Línia: {}".format(bus_info['line'])
                    bot.sendMessage(chat_id=chat_id, text=bus_line)
                    if "seconds" in bus_info['vh_first'] and "destino" in bus_info['vh_first']:
                        self.get_info_bus(bus_info, "vh_first", bot, chat_id)
                    if "seconds" in bus_info['vh_second'] and "destino" in bus_info['vh_second']:
                        self.get_info_bus(bus_info, "vh_second", bot, chat_id)
        else:
            bot.sendMessage(chat_id=chat_id,
                            text="Error a la petició!")
            logger.debug("Error: {}".format(stop_info['errorMessage']))

    def run(self):
        dispatcher.addTelegramCommandHandler('aturada', self.get_stop)
        updater.start_polling()
        updater.idle()

if __name__ == '__main__':
    bot = EMTBot()
    bot.run()
