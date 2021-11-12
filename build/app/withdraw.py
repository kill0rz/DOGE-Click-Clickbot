# Auto withdrawer (withdraw)

import asyncio
import logging
import re
import time
import os
import sys
import mysql.connector

from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.errors.rpcerrorlist import UsernameInvalidError
from cloudscraper.exceptions import CloudflareChallengeError
from colorama import Fore, init as color_ama

from common import *

async def main():
	if not os.path.exists("session"):
		os.mkdir("session")

	# Connect to client
	client = TelegramClient('session/' + phone_number, api_id, api_hash)
	await client.start(str(phone_number))
	me = await client.get_me()

	print(f'Current account: {me.first_name} {me.last_name} (@{me.username})\n')
	print_msg_time('Sending Withdraw command')

	# Start command Withdraw
	try:
		await client.send_message(dogeclick_channel, 'Withdraw')
	except FloodWaitError as e:
		print_msg_time("Flood control... :(")
		timetowait = int(re.search(r'A wait of (\d+) seconds', str(e)).group(1)) + 10

		print_msg_time("waiting " + str(timetowait) + " seconds")
		time.sleep(timetowait)
		print_msg_time("module is exiting because this is the initial call...")
		exit(1)
	except Exception as e:
		print_msg_time("Cannot connect to channel!")
		print_msg_time(str(e))
		print_msg_time("module is exiting...")
		exit(1)

	# Start the withdrawal process
	@client.on(events.NewMessage(chats = dogeclick_channel, incoming=True))
	async def send_address(event):
		message = event.raw_text
		if 'To withdraw, enter your' in message:
			print_msg_time("Sending withdraw address")
			await client.send_message(dogeclick_channel, withdraw_address)

	# enter amount
	@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
	async def enter_amount(event):
		message = event.raw_text
		if 'amount to withdraw' in message:
			print_msg_time("selecting max amount")
			await client.send_message(dogeclick_channel, 'Max amount')

	# confirm
	@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
	async def confirm(event):
		message = event.raw_text
		if 'Are you sure you want' in message:
			print_msg_time("Confirm")
			await client.send_message(dogeclick_channel, 'Confirm')

	# withdrawal ok
	@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
	async def withdrawal_ok(event):
		message = event.raw_text
		if 'withdrawal has been' in message:
			print_msg_time(Fore.GREEN + 'SUCCESS\n' + Fore.RESET)
			print_msg_time("module is exiting...")
			exit(1)

	# insufficient amount
	@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
	async def no_ads(event):
		message = event.raw_text
		if 'too small to withdraw' in message:
			print_msg_time(Fore.RED + 'Not enough balance..\n' + Fore.RESET)
			print_msg_time("module is exiting...")
			exit(1)

	await client.run_until_disconnected()

asyncio.get_event_loop().run_until_complete(main())
