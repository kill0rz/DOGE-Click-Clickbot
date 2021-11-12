# login helper

import asyncio
import logging
import re
import time
import os
import sys

from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.errors.rpcerrorlist import UsernameInvalidError
from colorama import Fore, init as color_ama

from common import *

async def main():
	if not os.path.exists("session"):
		os.mkdir("session")

	# Connect to client
	client = TelegramClient('session/' + phone_number, api_id, api_hash)
	await client.start(phone_number)
	me = await client.get_me()

	print(f'Current account: {me.first_name} {me.last_name} (@{me.username})\n')

asyncio.get_event_loop().run_until_complete(main())
