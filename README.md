# What is this?

The project DOGE Click offers you a list of bots to interact with. You can complete several tasks (join chat, chat with bots, visit websites) to get a small amount of crypto money of your choice.

Thos tool automates all tasks and withdrawal process. Otherwise the earnings are way too small.

_Will I get rich???_
→ No.

This won't run on windows, of course!

# Installation

Install Docker and Docker-Compose on your machine.

Git clone this repo and navigate to the destination folder.

```
cp .env-example .env
```

Modify `.env` and fill in the values.
Get your API data from [Telegram](https://my.telegram.org/auth).

Then login to Telegram:

```
./login.sh
```

After that the bot is ready to startup:

```
./update.sh
```

To withdraw, run

```
./withdraw.sh
```

!!! Auto withdraw should only be enabled for LTC bot. Otherwise transaction fees would be too much! Use at your own risk!

# Crontab

You should not run this manually. Instead use the crontab provided in crontab file.

# Maximize earnings

You could referal yourself with multiple accounts.

# Is this legal?

Is does violate the terms of Telegram and DOGE click. Do not use!

This project and the developer are not in touch with DOGE Click or Telegram by any means.

# Donate

If you earn a lot of money and appreciate my work, consider [a donation](https://blog.kill0rz.com/spenden/). Thanks!