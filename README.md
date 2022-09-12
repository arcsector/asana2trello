# Asana to Trello Tool

This was intended for me to move all my boards from Asana to Trello, and as such, it does just that. Specify your board name, API Key/Secret, and PAT and you'll be on your way!

Note that I have not tested this on List type boards in Asana, only card boards, so YMMV with Lists.

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

## What Gets Moved

- [x] Columns
- [x] Tasks
  - [x] Task Description/Notes
  - [x] Comments without attachments
- [x] Subtasks
  - [x] Subtask Separators
  - [x] Whether task is done or not
