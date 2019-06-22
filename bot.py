#!/usr/bin/python3
import logging
import sys
import json
import os
# import urllib.request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import pathlib

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = '660004381:AAFtmUJ3JU6orRcJIuxFgtf9sQByFB8H5Xs'
REQUEST_KWARGS = {
    'proxy_url': 'https://3.120.225.128:3128'  # socks5://{0}:{1}'.format(proxy, port)
    # Optional, if you need authentication:
    # 'urllib3_proxy_kwargs': {
    #     'username': 'PROXY_USER',
    #     'password': 'PROXY_PASS',
    # }
}

result_path = "bot/source/"
target_path = "bot/target/"


def photohandler(bot, update):
    userid = update.message.from_user.id
    out_path = result_path + str(userid)
    pathlib.Path(out_path).mkdir(parents=True, exist_ok=True)
    fileid = update.message.photo[-1]
    photo = bot.get_file(fileid)
    photo.download(out_path + "/source.jpg")

    reply_markup = menu_keyboard()
    bot.send_message(chat_id=update.message.chat_id, text="choose variant", reply_markup=reply_markup)


def debugprint(obj):
    for k, v in obj.__dict__.items():
        print(k, v)


def menu_keyboard():
    keyboard = [[InlineKeyboardButton('Option 1', callback_data='first')],
                [InlineKeyboardButton('Option 2', callback_data='second')],
                ]
    return InlineKeyboardMarkup(keyboard)


def work(bot, update, option):
    # TODO: put work here

    userid = 299477991  # TODO: update.callback_query.message.from_user.id
    gitpath = target_path + str(userid) + "/target.gif"
    bot.send_animation(chat_id=update.callback_query.message.chat_id, animation=open(gitpath, 'rb'), timeout=50)


def first_menu(bot, update):
    bot.send_message(chat_id=update.callback_query.message.chat_id, text="First choosed! Wait a bit please")

    work(bot, update, 1)


def second_menu(bot, update):
    bot.send_message(chat_id=update.callback_query.message.chat_id, text="Second choosed! Wait a bit please")

    work(bot, update, 2)


def run_bot():
    updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS)
    dispatcher = updater.dispatcher

    def start(bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="I'm a super bot, send me an image!")

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    def notunderstand(bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="I'm a super bot, understand only image!")

    echo_handler = MessageHandler(Filters.text, notunderstand)
    dispatcher.add_handler(echo_handler)

    photo_handler = MessageHandler(Filters.photo, photohandler)
    dispatcher.add_handler(photo_handler)

    dispatcher.add_handler(CallbackQueryHandler(first_menu, pattern='first'))
    dispatcher.add_handler(CallbackQueryHandler(second_menu, pattern='second'))

    updater.start_polling()
    updater.idle()
    updater.stop()
    print("telegram bot done")


if __name__ == "__main__":
    run_bot()
