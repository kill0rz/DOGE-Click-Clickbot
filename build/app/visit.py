# Auto visiter (/visit)

import asyncio
import logging
import re
import time
import os
import re
import sys
import mysql.connector

from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.errors.rpcerrorlist import UsernameInvalidError
from cloudscraper.exceptions import CloudflareChallengeError
from datetime import datetime
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
	print_msg_time('Sending /visit command')

	# Start command /visit
	try:
		await client.send_message(dogeclick_channel, '/visit')
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

	# Start visiting the ads
	@client.on(events.NewMessage(chats = dogeclick_channel, incoming=True))
	async def visit_ads(event):
		message = event.raw_text
		if 'Visit website' in message:
			url = event.original_update.message.reply_markup.rows[0].buttons[0].url
			if url is not None:
				print_msg_time('Visiting website...')

				# Parse the html of url
				try:
					(status_code, text_response) = get_response(url)
					if status_code == 403:
						print(status_code, text_response)
						print_msg_time("Forbidden, exiting ...")
						exit(1)
					else:
						print_msg_time('website visited')
				except Exception as e:
					print_msg_time("Cannot get URL, skipping ...")
					print_msg_time(str(e))
					# Clicks the skip button
					await client(GetBotCallbackAnswerRequest(
						peer = dogeclick_channel,
						msg_id = event.message.id,
						data = event.message.reply_markup.rows[1].buttons[1].data
					))
				else:
					htmlParsedData = BeautifulSoup(text_response, 'html.parser')
					isCaptcha = htmlParsedData.find('div', {'class':'g-recaptcha'})
					isHeadbar = htmlParsedData.find('div', {'id':'headbar'})
					isDdosProtection = htmlParsedData.find('span', {'class':'ray_id'}) or (len(htmlParsedData(text=re.compile("Cloudflare Ray ID"))) > 1)

					# DDoS protection detected
					if isDdosProtection is not None:
						print_msg_time(Fore.RED + 'DDoS protection detected!'+ Fore.RED +' Skipping ads...\n')
						# Clicks the skip button
						await client(GetBotCallbackAnswerRequest(
							peer = dogeclick_channel,
							msg_id = event.message.id,
							data = event.message.reply_markup.rows[1].buttons[1].data
						))

					# Captcha detected
					if isCaptcha is not None:
						print_msg_time(Fore.RED + 'Captcha detected!'+ Fore.RED +' Skipping ads...\n')
						# Clicks the skip button
						await client(GetBotCallbackAnswerRequest(
							peer = dogeclick_channel,
							msg_id = event.message.id,
							data = event.message.reply_markup.rows[1].buttons[1].data
						))

					# Headbar detected
					if isHeadbar is not None:
						print_msg_time(Fore.RED + 'Headbar detected!'+ Fore.RED +' Skipping ads...\n')
						# Clicks the skip button
						await client(GetBotCallbackAnswerRequest(
							peer = dogeclick_channel,
							msg_id = event.message.id,
							data = event.message.reply_markup.rows[1].buttons[1].data
						))

					print_msg_time('waiting for bot response...')

	# bot acknowledged visit
	@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
	async def bot_acknowledged(event):
		message = event.raw_text
		if 'Please stay on the site' in message:
			print_msg_time(Fore.GREEN + "Bot acknowledged visit\n" + Fore.RESET)

	# Print earned money
	@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
	async def wait_hours(event):
		message = event.raw_text
		if 'You earned' in message:
			print_msg_time(Fore.GREEN + f'{message}\n' + Fore.RESET)

	# No more ads
	@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
	async def no_ads(event):
		message = event.raw_text
		if 'no new ads available' in message:
			print_msg_time(Fore.RED + 'Sorry, there are no new ads available\n' + Fore.RESET)
			print_msg_time("module is exiting...")
			exit(1)

	await client.run_until_disconnected()

asyncio.get_event_loop().run_until_complete(main())
