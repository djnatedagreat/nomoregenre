import argparse
import inquirer
import datetime
import ffmpeg
from models import AudioAsset, Creator, AssetType, AudioClip, format_seconds
from dotenv import dotenv_values
from slugify import slugify
import os

print("DEPRECATED: INSTEAD USE audio_asset.py")
exit()

config = dotenv_values(".env")  # take environment variables from .env.

# Create ArgumentParser
parser = argparse.ArgumentParser(description="Register a DJ mix in the database")

# Add an argument
parser.add_argument("file", help="File location of mix")

# Parse the arguments
args = parser.parse_args()

# get mix asset type
mixtype = AssetType.select().where(AssetType.name == 'mix').get()

# get list of creators 
creator_options = []
for c in Creator.select():
  creator_options.append((c.name, c.id))

# Use the argument
questions = [
    inquirer.Text("name", message="Enter a descriptive name for the mix."),
    inquirer.List("creator", message="Please choose the DJ/Creator", choices=creator_options),
    inquirer.Text("submit_date", message="Enter the date this mix was submitted",default=datetime.date.today()),
]

answers = inquirer.prompt(questions)

probe = ffmpeg.probe(args.file)
duration = float(probe['format']['duration'])  # Extract duration in seconds
readable_duration= format_seconds(duration)
print(f"Duration: {readable_duration}")

mix = AudioAsset(key=slugify(answers["name"]), name=answers["name"], filename=os.path.basename(args.file), type=mixtype.id, creator=answers["creator"], submitted=answers["submit_date"])
mix.save() # now stored in the database

# save the full clip
clip = AudioClip(asset=mix.id,start_time=0,end_time=duration)
clip.save()

#print(mix.__dict__)


