import argparse
import inquirer
import datetime
import ffmpeg
from models import AudioAsset, Creator, AssetType, AudioClip
from dotenv import dotenv_values
from slugify import slugify
import os

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
#print(answers.segments)

# Get clip length
def format_seconds(seconds):
    hours, remainder = divmod(seconds, 3600)  # Get hours
    minutes, seconds = divmod(remainder, 60)  # Get minutes and seconds
    return hours, minutes, seconds

probe = ffmpeg.probe(args.file)
duration = float(probe['format']['duration'])  # Extract duration
h, m, s = format_seconds(duration)
print(f"{h} hours, {m} minutes, {s} seconds")
print(f"Duration: {duration:.2f}");

#class AudioAsset(BaseModel):
    #name = CharField()
    #filename = CharField()
    #type = ForeignKeyField(AssetType, backref='assets')
    #creator = ForeignKeyField(Creator, backref='assets')
    #submitted = DateField()
mix = AudioAsset(key=slugify(answers["name"]), name=answers["name"], filename=os.path.basename(args.file), type=mixtype.id, creator=answers["creator"], submitted=answers["submit_date"])
mix.save() # now stored in the database

# save the full clip
clip = AudioClip(asset=mix.id,start_time=0,end_time=duration)
clip.save()

#print(mix.__dict__)


