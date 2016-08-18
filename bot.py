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

NEW_LINE = "\n"


class EMTBot(object):
    def __init__(self):
        logger.debug('[INIT] Starting')

    @staticmethod
    def get_info_bus(bus_info, clave, bot, chat_id):
        # Parsing to telegram messages bus information
        text = ""
        if "seconds" in bus_info[clave] and "destino" in bus_info[clave]:
            if bus_info[clave]['enParada']:
                text += "Bus a la aturada"
            elif bus_info[clave]['llegando']:
                text += "Bus arribant a la aturada"
            else:
                text += "Temps estimat a l'aturada: {} minuts".format(
                        int(bus_info[clave]['seconds']/60))
                if bus_info[clave]['seconds'] % 60 != 0:
                    text += " i {} segons".format(
                            bus_info[clave]['seconds'] % 60)
        return text + NEW_LINE

    def get_stop_info(self, bot, chat_id, bus_stop='572'):
        url = "{}?p={}".format(BASE_URL, bus_stop)
        # logger.debug(url)
        resp = requests.get(url)
        stop_info = resp.json()
        # logger.debug(resp.json())

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
                    bus_line = "Línia: {}{}".format(bus_info['line'],
                                                    NEW_LINE)
                    # bot.sendMessage(chat_id=chat_id, text=bus_line)
                    if "seconds" in bus_info['vh_first'] and "destino" in bus_info['vh_first']:
                        bus_line += self.get_info_bus(bus_info, "vh_first",
                                                      bot, chat_id)
                    if "seconds" in bus_info['vh_second'] and "destino" in bus_info['vh_second']:
                        bus_line += self.get_info_bus(bus_info, "vh_second",
                                                      bot, chat_id)
                    bot.sendMessage(chat_id=chat_id, text=bus_line)
        else:
            bot.sendMessage(chat_id=chat_id,
                            text="Error a la petició!")
            logger.debug("Error: {}".format(stop_info['errorMessage']))

    def get_stop(self, bot, update):
        # logger.debug(update.message.chat_id)
        # logger.debug(update.message.text)
        try:
            bus_stop = update.message.text.split()[1]
        except IndexError:
            bot.sendMessage(chat_id=update.message.chat_id,
                            text="Aturada no introduida")
            return
        self.get_stop_info(bot, update.message.chat_id, bus_stop)

    def run(self):
        dispatcher.addTelegramCommandHandler('aturada', self.get_stop)
        updater.start_polling()
        updater.idle()

if __name__ == '__main__':
    bot = EMTBot()
    bot.run()
