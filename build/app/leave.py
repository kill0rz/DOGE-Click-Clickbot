# Auto leaver (intern)

import asyncio
import logging
import re
import time
import os
import sys
import requests
import mysql.connector

from telethon import TelegramClient, events
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.errors.rpcerrorlist import ChannelPublicGroupNaError
from telethon.errors.rpcerrorlist import ChannelPrivateError
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.errors.rpcerrorlist import UsernameNotOccupiedError
from datetime import datetime
from colorama import Fore, init as color_ama

from common import *
from dbconnect import *

def deleteChannelFromDb(channelname):
	try:
		mysql_delete_channel_from_db(channelname)
	except Exception as e:
		print_msg_time(Fore.RED + f'Error while deleting the channel from DB: ' + str(e) + Fore.RESET)
	else:
		print_msg_time(Fore.GREEN + f'Channel deleted from DB.' + Fore.RESET)

async def leaveDialog(client, dialog):
	try:
		try:
			await client.delete_dialog(dialog)
		except Exception as e:
			await client(LeaveChannelRequest(dialog))
	except ChannelPublicGroupNaError as e:
		print_msg_time(Fore.RED + f'ERROR: Cannot leave channel as it is not available (any more).' + Fore.RESET)
	except ChannelPrivateError as e:
		print_msg_time(Fore.RED + f'ERROR: Cannot leave channel as it is private.' + Fore.RESET)
	except UserNotParticipantError as e:
		print_msg_time(Fore.RED + f'ERROR: Cannot leave channel as we are not a member of it (any more).' + Fore.RESET)
	except UsernameNotOccupiedError as e:
		print_msg_time(Fore.RED + f'ERROR: Cannot leave channel as it is not known (any more).' + Fore.RESET)
	except FloodWaitError as e:
		print_msg_time(Fore.RED + f'ERROR: Cannot leave channel: Flood Control :(' + Fore.RESET)
	except Exception as e:
		print_msg_time(Fore.RED + f'Error while leaving the channel: ' + str(e) + Fore.RESET)
	else:
		print_msg_time(f'... done.')
	time.sleep(2)

async def main():
	# Connect to client
	client = TelegramClient('session/' + phone_number, api_id, api_hash)
	await client.start(phone_number)
	me = await client.get_me()

	print(f'Current account: {me.first_name} {me.last_name} (@{me.username})\n')

	# first, leave all channels the are not in db. These are joined by user or are in error state.
	async for dialog in client.iter_dialogs():
		try:
			if hasattr(dialog, "entity") and hasattr(dialog.entity, "username"):
				channelname = dialog.entity.username
			else:
				# wenn wir den channelname eh nicht lesen können, gleich raus. Können wir nicht gegen die DB abgleichen
				print_msg_time(f'Error reading channel name, leave it')
				await leaveDialog(client, dialog)
		except AttributeError as e:
			print_msg_time(Fore.RED + f'Error selecting or leaving unknown channel: ' + str(e) + Fore.RESET)
			print_msg_time(Fore.RED + f'Channel: ' + str(dialog) + Fore.RESET)
		else:
			if channelname is not None and channelname != 'BitcoinClick_bot' and channelname != 'Litecoin_click_bot' and channelname != 'Dogecoin_click_bot' and channelname != 'BCH_click_bot' and channelname != 'Zcash_click_bot':
				channelstoleave = mysql_query_select_fetchone("SELECT id FROM cbb_channels where LOWER(channelname) = '" + channelname + "';")
				if channelstoleave is None:
					# not in DB, leave
					print_msg_time(f'Leaving channel: '+ channelname)
					await leaveDialog(client, channelname)
					deleteChannelFromDb(channelname)

	# second, select all channels, that should be left
	channelstoleave = mysql_query_select("SELECT * FROM cbb_v_getChannelsToLeave;")
	for channel in channelstoleave:
		print_msg_time(f'Leaving channel: '+ channel[0])
		await leaveDialog(client, channel[0])
		deleteChannelFromDb(channel[0])

	print_msg_time(Fore.GREEN + f'\n...Done leaving old channels and bots' + Fore.RESET)
	exit(1)

	await client.run_until_disconnected()

asyncio.get_event_loop().run_until_complete(main())
