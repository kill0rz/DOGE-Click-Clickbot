# Auto bot joiner (/bots)

import asyncio
import logging
import re
import time
import os
import sys
import cloudscraper
import mysql.connector

from telethon import TelegramClient, events
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.errors.rpcerrorlist import ChannelPublicGroupNaError
from telethon.errors.rpcerrorlist import ChannelPrivateError
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.errors.rpcerrorlist import UsernameNotOccupiedError
from cloudscraper.exceptions import CloudflareChallengeError
from datetime import datetime
from colorama import Fore, init as color_ama

from common import *
from dbconnect import *

async def main():
	# Connect to client
	client = TelegramClient('session/' + phone_number, api_id, api_hash)
	await client.start(phone_number)
	me = await client.get_me()
	scraper = cloudscraper.create_scraper()

	print(f'Current account: {me.first_name} {me.last_name} (@{me.username})\n')

	# Start command /bots
	try:
		print_msg_time('Sending /bots command')
		await client.send_message(dogeclick_channel, '/bots')
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
	else:
		# Message the bot
		@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
		async def join_start(event):
			message = event.raw_text
			if 'Forward a message to me' in message:
				# find channel name
				try:
					r = scraper.get(event.original_update.message.reply_markup.rows[0].buttons[0].url, allow_redirects = False, headers = {
						'Referer': event.original_update.message.reply_markup.rows[0].buttons[0].url,
						"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win32; x86) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
					})
					if r.status_code == 403:
						print_msg_time("Forbidden, exiting ...")
						exit(1)
				except CloudflareChallengeError as e:
					print_msg_time("Cloudflare, skipping")
					print_msg_time(str(e))
					time.sleep(2)
					await client(GetBotCallbackAnswerRequest(
						peer = dogeclick_channel,
						msg_id = event.message.id,
						data = event.message.reply_markup.rows[1].buttons[1].data
					))
				else:
					try:
						print("r.status_code: ")
						print(r.status_code)
						channel_name = r.headers["Location"].replace('https://telegram.me/', '')
						channel_name = re.sub(r'\?.*', '', channel_name)
					except Exception as e:
						print_msg_time("unexpected error, skip")
						print_msg_time(str(e))
						time.sleep(2)
						await client(GetBotCallbackAnswerRequest(
							peer = dogeclick_channel,
							msg_id = event.message.id,
							data = event.message.reply_markup.rows[1].buttons[1].data
						))
					else:
						try:
							print_msg_time(f'Messaging @{channel_name} ...')
							await client.send_message(channel_name, '/start')
						except FloodWaitError as e:
							print_msg_time("Flood control... :(")
							timetowait = int(re.search(r'A wait of (\d+) seconds', str(e)).group(1)) + 10

							print_msg_time("should be waiting " + str(timetowait) + " seconds")
							print_msg_time("module is exiting...")
							exit(1)
						except UsernameInvalidError as e:
							print_msg_time("Channel does not exist, skipping ...")
							time.sleep(2)
							await client(GetBotCallbackAnswerRequest(
								peer = dogeclick_channel,
								msg_id = event.message.id,
								data = event.message.reply_markup.rows[1].buttons[1].data
							))
						except Exception as e:
							print_msg_time("unexpected error: " + str(e) + ", skipping ...")
							time.sleep(2)

							await client(GetBotCallbackAnswerRequest(
								peer = dogeclick_channel,
								msg_id = event.message.id,
								data = event.message.reply_markup.rows[1].buttons[1].data
							))
						else:
							# insert into DB
							mysql_query("INSERT INTO `cbb_channels` (`channelname`, `hourstolast`) VALUES (%s, %s);", (channel_name, '0'))
							try:
								# Forward the bot message
								@client.on(events.NewMessage(chats = channel_name, incoming = True))
								async def forward_message(event):
									try:
										msg_id = event.message.id,
										await client.forward_messages(dogeclick_channel, msg_id, channel_name)
									except Exception as e:
										print_msg_time("Error forwarding bot-message. " + str(e) + " - Continue anyway ...")
							except Exception as e:
								print_msg_time("Error forwarding bot-message. " + str(e) + " - Continue anyway ...")

							time.sleep(3)

							## todo: Hier muss darauf gelauscht werden, dass manchmal auch keine Antwort kommt. Momentan hängt sich der Bot hier auf.

		# Print earned amount
		@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
		async def earned_amount(event):
			message = event.raw_text
			if 'You earned' in message:
				print_msg_time(Fore.GREEN + event.raw_text + '\n' + Fore.RESET)
				time.sleep(30)

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
