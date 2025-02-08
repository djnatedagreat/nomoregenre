import argparse
import inquirer
import datetime
import ffmpeg
from models import AudioAsset, Creator, AssetType, AudioClip
from dotenv import dotenv_values
from slugify import slugify
import os
from audio_functions import get_seconds

config = dotenv_values(".env")  # take environment variables from .env.

# get list of creators 
creator_options = []
for c in Creator.select():
  creator_options.append((c.name, c.id))

# Use the argument
questions = [
    inquirer.Text("name", message="Search Mix Name"),
    inquirer.List("creator", message="Search for DJ/Creator", choices=creator_options),
]

answers = inquirer.prompt(questions)

matches = (AudioAsset.select().where(AudioAsset.name.contains(answers["name"]), AudioAsset.creator_id == answers["creator"]).dicts())
mix_options = []
for m in matches:
    mix_options.append((m['name'], m['id']))

questions2 = [
   inquirer.List("mix", message="What mix?", choices=mix_options),
   inquirer.Text("start", message="Start time (hh::mm::ss)"),
   inquirer.Text("end", message="End time (hh::mm::ss)"),
]

answers2 = inquirer.prompt(questions2)

clip = AudioClip(asset=answers2["mix"],start_time=get_seconds(answers2["start"]),end_time=get_seconds(answers2["end"]))
clip.save()