import argparse
import inquirer
import datetime
import ffmpeg
from models import AudioAsset, Creator, AssetType, AudioClip
from slugify import slugify
from dotenv import dotenv_values
from utils import format_seconds
import os

print("DEPRECATED: INSTEAD USE audio_asset.py")
exit()

config = dotenv_values(".env")  # take environment variables from .env.

# Create ArgumentParser
parser = argparse.ArgumentParser(description="DEPRECATED: INSTEAD USE audio_asset.py")

# Add an argument
parser.add_argument("file", help="File location of ID")

# Parse the arguments
args = parser.parse_args()

# get mix asset type
mixtype = AssetType.select().where(AssetType.name == 'id').get()

# get list of creators 
creator_options = []
for c in Creator.select():
  creator_options.append((c.name, c.id))

# Use the argument
questions = [
    inquirer.Text("name", message="Enter a descriptive name for the mix."),
    inquirer.List("creator", message="Please choose the DJ/Creator", choices=creator_options),
    inquirer.Text("submit_date", message="Enter the date this ID was submitted",default=datetime.date.today()),
]

answers = inquirer.prompt(questions)
#print(answers.segments)

# Get clip length
def format_seconds(seconds):
    hours, remainder = divmod(seconds, 3600)  # Get hours
    minutes, seconds = divmod(remainder, 60)  # Get minutes and seconds
    return hours, minutes, seconds

probe = ffmpeg.probe(args.file)
duration = float(probe['format']['duration'])  # Extract duration
readable_duration= format_seconds(duration)
print(f"Duration: {readable_duration}")

id = AudioAsset(key=slugify(answers["name"]),name=answers["name"], filename=os.path.basename(args.file), type=mixtype.id, creator=answers["creator"], submitted=answers["submit_date"])
id.save() # now stored in the database

# save the full clip
clip = AudioClip(asset=id.id,start_time=0,end_time=duration)
clip.save()

#print(mix.__dict__)