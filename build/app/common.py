import asyncio
import logging
import re
import time
import os
import sys
import cloudscraper
import requests
import mysql.connector

from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.errors.rpcerrorlist import UsernameInvalidError
from cloudscraper.exceptions import CloudflareChallengeError
from datetime import datetime
from colorama import Fore, init as color_ama
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

color_ama(autoreset = True)

logging.basicConfig(level = logging.ERROR)

# Get your own values from my.telegram.org
phone_number = os.getenv('PHONE')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
withdraw_address = os.getenv('WITHDRAW_ADDRESS')

''' DogeClick Bot Channel from dogeclick.com
Options:
1. Dogecoin_click_bot
2. Litecoin_click_bot
3. BCH_click_bot
4. Zcash_click_bot
5. Bitcoinclick_bot
# '''
dogeclick_channel = os.getenv('BOT')

def print_msg_time(message):
	print('[' + Fore.CYAN + f'{datetime.now().strftime("%H:%M:%S")}' + Fore.RESET + f'] {message}')

def get_response(url, method = 'GET'):
	ua = UserAgent()
	scraper = cloudscraper.create_scraper(
		browser={
			'browser': 'chrome',
			'platform': 'linux',
			'desktop': True
		},
		delay=10,
		interpreter='nodejs'
	)
	response = scraper.request(method, url, headers = {"User-Agent":str(ua.chrome)}, timeout=15)
	text_response = response.text
	status_code = response.status_code
	return[status_code, text_response]

if not os.path.exists("session"):
	os.mkdir("session")
