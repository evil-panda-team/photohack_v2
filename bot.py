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

from icface.run import create_mp4
from add_video_in_template import make_gif

import pathlib

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = '660004381:AAFtmUJ3JU6orRcJIuxFgtf9sQByFB8H5Xs'
REQUEST_KWARGS = {
    #'proxy_url': 'http://46.8.28.17:8080'  # socks5://{0}:{1}'.format(proxy, port)
    # Optional, if you need authentication:
    # 'urllib3_proxy_kwargs': {
    #     'username': 'PROXY_USER',
    #     'password': 'PROXY_PASS',
    # }
}

result_path = "bot/source/"


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
    keyboard = [[InlineKeyboardButton('baba ', callback_data='first')],
                [InlineKeyboardButton('carrey ', callback_data='second')],
                ]
    return InlineKeyboardMarkup(keyboard)


def work(bot, update, option):
    userid = update.callback_query.message.chat.id
    create_mp4(result_path + str(userid)+ "/source.jpg", option)

    params_transform = {
        'rotate': True,
        'angle_start': 0,
        'angle_step': 0.5,
        'scale_start': 0.5,
        'scale_step': 0.01
    }

    folder = result_path + str(userid) + "/"
    # Paths
    params_paths = {
        'templates_folder': 'templates/',
        'animations_folder': folder,
        'gifs_folder': folder,
        'animation_name': 'source.mp4',
        'gif_name': 'source.gif'
    }

    # Text lines params
    params_text = {
        'thickness_line_1': 2,
        'thickness_line_2': -1,
        'color': (0, 0, 0),
        'headline_text': 'Sensation!!!',
        'sub_headline_text': 'Vlados okazalsya volcharoy'
    }

    # Select one of the scenarios
    scenario = 2
    scale_factor = 3
    show_result = True

    make_gif(params_paths, params_text, params_transform,
             scale_factor=scale_factor, scenario=scenario, show_result=show_result)


    gifpath = result_path + str(userid)+ "/source.gif"
    bot.send_animation(chat_id=update.callback_query.message.chat_id, animation=open(gifpath, 'rb'), timeout=50)


def first_menu(bot, update):
    bot.send_message(chat_id=update.callback_query.message.chat_id, text="baba choosed! Wait a bit please")

    work(bot, update, "icface/csv/baba.csv")


def second_menu(bot, update):
    bot.send_message(chat_id=update.callback_query.message.chat_id, text="carrey choosed! Wait a bit please")

    work(bot, update, "icface/csv/carrey.csv")


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
