# Auto joiner (/join)

import asyncio
import logging
import re
import time
import os
import sys
import cloudscraper
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
from dbconnect import *

async def main():
	# Connect to client
	client = TelegramClient('session/' + phone_number, api_id, api_hash)
	await client.start(phone_number)
	me = await client.get_me()
	scraper = cloudscraper.create_scraper()

	print(f'Current account: {me.first_name} {me.last_name} (@{me.username})\n')

	print_msg_time('Sending /join command')

	# Start command /join
	try:
		await client.send_message(dogeclick_channel, '/join')
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
		# Join the channel
		@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
		async def join_start(event):
			message = event.raw_text
			if 'Press the "Go to channel" button' in message or 'Go to group' in message:
				# find channel name
				try:
					r = scraper.get(event.message.reply_markup.rows[0].buttons[0].url, allow_redirects = False, headers = {
						'Referer': event.message.reply_markup.rows[0].buttons[0].url,
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
						channel_name = r.headers["Location"].replace('https://telegram.me/', '')
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
						# Join the channel
						try:
							# check if channel is already in db - then its dupe an we skip it
							print_msg_time(f'Joining @{channel_name} ...')
							channelexists = mysql_query_select_fetchone("SELECT * FROM cbb_channels where channelname = '" + channel_name + "';")
							if channelexists is None:
								print_msg_time(f'Verifying...')
								await client(JoinChannelRequest(channel_name))
								# Clicks the joined button
								await client(GetBotCallbackAnswerRequest(
									peer = dogeclick_channel,
									msg_id = event.message.id,
									data = event.message.reply_markup.rows[0].buttons[1].data
								))
								# insert into DB
								mysql_query("INSERT INTO `cbb_channels` (`channelname`, `hourstolast`) VALUES (%s, %s);", (channel_name, '0'))
							else:
								print(channelexists)
								print_msg_time(f'Channel exists in DB, skipping ...')
								time.sleep(2)
								await client(GetBotCallbackAnswerRequest(
									peer = dogeclick_channel,
									msg_id = event.message.id,
									data = event.message.reply_markup.rows[1].buttons[1].data
								))
						except FloodWaitError as e:
							print_msg_time("Flood control... :(")
							timetowait = int(re.search(r'A wait of (\d+) seconds', str(e)).group(1)) + 10

							print_msg_time("should be waiting " + str(timetowait) + " seconds")
							print_msg_time("module is exiting...")
							exit(1)
						except UsernameInvalidError as e:
							print_msg_time("Channel does not exist, skip")
							time.sleep(2)
							await client(GetBotCallbackAnswerRequest(
								peer = dogeclick_channel,
								msg_id = event.message.id,
								data = event.message.reply_markup.rows[1].buttons[1].data
							))
						except Exception as e:
							print_msg_time("unexpected error: " + str(e) + ", skipping ...")
							print_msg_time("skipping")
							time.sleep(2)
							await client(GetBotCallbackAnswerRequest(
								peer = dogeclick_channel,
								msg_id = event.message.id,
								data = event.message.reply_markup.rows[1].buttons[1].data
							))

		# Print waiting hours
		@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
		async def wait_hours(event):
			message = event.raw_text
			if 'You must stay' in message:
				waiting_hours = re.search(r'at least (.*?) to earn', message).group(1)
				# stay 1 hour more than needed - otherwise we would leave the channel too early
				waiting_hours_int = int(re.search(r'at least (\d+) hour', message).group(1)) + 1
				print_msg_time(Fore.GREEN + f'Success! Please wait {waiting_hours} to earn reward\n' + Fore.RESET)
				# update DB row
				mysql_query("UPDATE `cbb_channels` SET hourstolast = " + str(waiting_hours_int) + " WHERE ID = (SELECT ID FROM cbb_channels ORDER BY ID DESC LIMIT 1);");
				time.sleep(30)

		# join not successful
		@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
		async def skip_notfound(event):
			message = event.raw_text
			if 'We cannot find you in' in message:
				print_msg_time(Fore.RED + f'Join not successful, skipping...\n' + Fore.RESET)
				try:
					await client.send_message(dogeclick_channel, '/join')
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

		# no longer valid
		@client.on(events.NewMessage(chats = dogeclick_channel, incoming = True))
		async def skip_nolongervalid(event):
			message = event.raw_text
			if 'no longer valid' in message:
				print_msg_time(Fore.RED + f'Link is no longer valid, skipping...\n' + Fore.RESET)
				try:
					await client.send_message(dogeclick_channel, '/join')
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
