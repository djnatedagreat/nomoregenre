import argparse
import inquirer
import os
import ffmpeg
from slugify import slugify
from models import Creator, AudioAsset, AssetType, AudioClip
from peewee import fn
from utils import get_seconds, load_config

config = load_config()

parser = argparse.ArgumentParser(description="Manage audio assets such as mixes and IDs")

# Add an argument
parser.add_argument("command", help="add, list, rm, preview")
parser.add_argument("--id", dest="id", help="Asset ID", required=False)
parser.add_argument("--name", dest="name", help="Asset Name", required=False)
parser.add_argument("--type", dest="type", help="Asset Type", required=False)
parser.add_argument("--creator", dest="creator", help="Asset Creator", required=False)
parser.add_argument("--file", dest="file", help="File location of asset", required=False)
parser.add_argument("--date", dest="date", help="Date Submited", required=False)
# Parse the arguments
args = parser.parse_args()

# get list of creators 
creator_options = []
for c in Creator.select():
  creator_options.append((c.name, c.id))

# get list of creators 
type_options = []
for at in AssetType.select():
  type_options.append((at.name, at.id))

def require_id():
    if args.id:
        return args.id
    else:
        prompt = [
            inquirer.Text("id", message="Enter an ID")
        ]
        answer = inquirer.prompt(prompt)
        return answer["id"]
    
def require_name():
    if args.name:
        return args.name
    else:
        name_prompt = [
            inquirer.Text("name", message="Enter a descriptive name for the mix.")
        ]
        answer = inquirer.prompt(name_prompt)
        return answer["name"]

def require_creator():
    creator_name = None
    if args.creator:
        return Creator.get_or_none(Creator.name == args.creator)
    else:
        creator_prompt = [
            inquirer.List("creator", message="Please choose the DJ/Creator", choices=creator_options)
        ]
        answer = inquirer.prompt(creator_prompt)
        return Creator.get_by_id(answer["creator"])

def require_type():
    asset_type = None
    if args.type:
        return AssetType.get_or_none(AssetType.name == args.type)
    else:
        at_prompt = [
            inquirer.List("asset_type", message="Please choose the Asset Type", choices=type_options)
        ]
        answer = inquirer.prompt(at_prompt)
        return AssetType.get_by_id(answer["asset_type"])

def require_file():
    if args.file:
        return args.file
    else:
        file_prompt = [
            inquirer.Path("file", message="Enter the file", exists=True, path_type=inquirer.Path.FILE),
        ]
        answer = inquirer.prompt(file_prompt)
        return answer["file"]  

def require_date():
    if args.date:
        return args.date
    else:
        date_prompt = [
            inquirer.Text("date", message="Enter the Date Submited"),
        ]
        answer = inquirer.prompt(date_prompt)
        return answer["date"]      

match args.command:
    case "list":
        assets = AudioAsset.select()
        if (args.type):
            type = AssetType.get(AssetType.name == args.type)
            assets = assets.where(AudioAsset.type == type.id)
        if (args.creator):
            creator = Creator.get(fn.LOWER(Creator.name) == fn.LOWER(args.creator))
            assets = assets.where(AudioAsset.creator == creator.id)
        for a in assets:
            print ("("+str(a.id)+") "+a.type.name + "\t" + a.creator.name + "\t" + a.name)
    case "add":
        asset_name = require_name()
        key=slugify(asset_name)
        # check if already exists
        asset = AudioAsset.get_or_none(AudioAsset.key == key)
        if asset:
            print("Audio Asset " +asset_name+ " exists with ID " + str(asset.id) + "Asset names must be unique... Exiting")
            exit()
        # validate type
        asset_type = require_type()
        if not asset_type:
            print("Can not find asset type... Exiting")
            exit()
        # validate creator
        asset_creator = require_creator()
        if not asset_creator:
            print("Can not find creator... Exiting")
            exit()
        # validate file
        asset_file =  require_file()
        basename=os.path.basename(asset_file)
        probe = ffmpeg.probe(asset_file)
        duration = float(probe['format']['duration'])  # Extract duration in seconds
        if not duration > 0:
            print("Audio file has no length... Exiting")
            exit()
        # validate submit date 2025-01-01 format
        submit_date = require_date()

        print(asset_name + " " +asset_type.name + " " + asset_creator.name + " " + basename + " " + submit_date)
        asset = AudioAsset(key=key, name=asset_name, filename=basename, type=asset_type.id, creator=asset_creator.id, submitted=submit_date)
        asset.save() # now stored in the database

        # save the full clip
        clip = AudioClip(asset=asset.id,start_time=0,end_time=duration)
        clip.save()

        print(f"Audio Asset saved -- {asset.name}")
    case "rm" | "remove" | "delete" | "del":
        # check if exists
        #creator = Creator.get_or_none(Creator.name == args.name)
        #if not creator:
        #    print("Creator " +args.name+ " does not exist... Exiting")
        #    exit()
        # check if there's any associated assets
        #assets = AudioAsset.select().join(Creator).where(Creator.id==creator.id)
        #if (len(assets) >  0):
        #    print("Creator " +creator.name+ " has associated audio assets. Removal is not supported... yet.")
        #    exit()
        #creator.delete_instance()
        print("Not Implemented ") #+creator.name+ " has been deleted.")
    case "preview":
        from pydub import AudioSegment
        from pydub.playback import play
        import numpy as np
        clip_len = 7 * 1000
        cf = 1*1000
        id = require_id()
        aa = AudioAsset.get_by_id(id)
        directory = config["LIBRARY_DIR"]+"/"+aa.type.name+"/"
        asset_file = directory + aa.filename
        segment = AudioSegment.from_file(asset_file, format="mp3")
        # get evenly spaced clips
        segment.duration_seconds
        markers = np.linspace(0, segment.duration_seconds, 5)[1:-1]
        print(markers)
        preview = AudioSegment.empty()
        preview += segment[:clip_len]
        for m in markers:
            #print('appending preview at' +str(m))
            st = m*1000
            end = st + clip_len
            #print("len: " + str(end - st))
            preview = preview.append(segment[st:end], crossfade=cf)
        preview = preview.append(segment[0-clip_len:], crossfade=cf)
        # could build a preview file and save it with something like .preview.mp3
        # and look for it first. Maybe that would save some time.
        play(preview)
    case _:
        parser.print_help()
