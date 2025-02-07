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

# Create ArgumentParser
#parser = argparse.ArgumentParser(description="Register a DJ mix in the database")

# Add an argument
#parser.add_argument("file", help="File location of mix")

# Parse the arguments
#args = parser.parse_args()

# get mix asset type
#mixtype = AssetType.select().where(AssetType.name == 'mix').get()

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
    #print(m['name'], m['submitted'])
#print(matches)
#print(answers.segments)

questions2 = [
   inquirer.List("mix", message="What mix?", choices=mix_options),
   inquirer.Text("start", message="Start time (hh::mm::ss)"),
   inquirer.Text("end", message="End time (hh::mm::ss)"),
]

# Need to prompt for start time and end time
# convert to seconds
# save clip

answers2 = inquirer.prompt(questions2)

clip = AudioClip(asset=answers2["mix"],start_time=get_seconds(answers2["start"]),end_time=get_seconds(answers2["end"]))
clip.save()

# Get clip length
##def convert_seconds(seconds):
#    hours, remainder = divmod(seconds, 3600)  # Get hours
#    minutes, seconds = divmod(remainder, 60)  # Get minutes and seconds
#    return hours, minutes, seconds

#probe = ffmpeg.probe(args.file)
#duration = float(probe['format']['duration'])  # Extract duration
#h, m, s = convert_seconds(duration)
#print(f"{h} hours, {m} minutes, {s} seconds")
#print(f"Duration: {duration:.2f}");

#class AudioAsset(BaseModel):
    #name = CharField()
    #filename = CharField()
    #type = ForeignKeyField(AssetType, backref='assets')
    #creator = ForeignKeyField(Creator, backref='assets')
    #submitted = DateField()
#mix = AudioAsset(key=slugify(answers["name"]), name=answers["name"], filename=os.path.basename(args.file), type=mixtype.id, creator=answers["creator"], submitted=answers["submit_date"])
#mix.save() # now stored in the database

# save the full clip
#clip = AudioClip(asset=mix.id,start_time=0,end_time=duration)
#clip.save()

#print(mix.__dict__)


