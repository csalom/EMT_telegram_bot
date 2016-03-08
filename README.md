# EMT_telegram_bot
A telegram bot which gives bus stop information in Palma

There are two ways to use this bot:

bot.py --> class EMTBot

EMTBot is a reactive telegram bot that expects a specific message "/aturada" with
a bus stop number. Example: "/aturada 455". This look for information of this
bus stop and send some messages to the chat where was requested. If bus stop
number is not provided, it will send a information message outpointing this fact.

notification_bot.py --> class NotificationBot

NotificationBot is a simplest bot that will give information from a default
bus stop at an exact time. The CHAT_ID used in this bot have been taken from
the updater telegram class.

This bots are coded using python-telegram-bot 
(https://github.com/python-telegram-bot/python-telegram-bot), as you can see at the requeriments.

