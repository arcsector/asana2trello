# Asana to Trello Tool

This was intended for me to move all my boards from Asana to Trello, and as such, it does just that. Specify your board name, API Key/Secret, and PAT and you'll be on your way!

Note that I have not tested this on List type boards in Asana, only card boards, so YMMV with Lists. Make sure the [requirements](requirements.txt) are installed before running.

## Usage

```bash
> python trello_connect.py -h

usage: trello_connect.py [-h] [--trello-key TRELLO_KEY] [--trello-secret TRELLO_SECRET] [--asana-pat ASANA_PAT] [--board BOARD]

optional arguments:
  -h, --help            show this help message and exit
  --trello-key TRELLO_KEY
                        Trello Oauth API Key
  --trello-secret TRELLO_SECRET
                        Trello Oauth API Token/Secret
  --asana-pat ASANA_PAT
                        Asana API Personal Access Token
  --board BOARD         Board name that you want to move from Asana to Trello
```

## How to Get a Trello API Key

1. Login into your [Trello](https://trello.com/) Account
2. Go to this [link](https://trello.com/app-key) to get the API Key
3. On the same page, click on generate token to generate a token which needs to be used to get authorization for your boards, lists & cards

## How to Get an Asana Personal Access Token

1. Sign into your [Asana Developer Portal](https://app.asana.com/0/developer-console)
2. Click `+ Create New Personal Access Token`
3. Type a description of what you’ll use the Personal Access Token for.
4. Click `Create`
5. Copy your token.

## What Gets Moved

- [x] Columns
- [x] Tasks
  - [x] Task Description/Notes
  - [x] Comments without attachments
- [x] Subtasks
  - [x] Subtask Separators
  - [x] Whether task is done or not
