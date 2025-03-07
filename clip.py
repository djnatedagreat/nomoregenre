import argparse
import inquirer
from models import AssetType, AudioAsset, AudioClip, Creator
from utils import format_seconds, get_seconds


# Create ArgumentParser
parser = argparse.ArgumentParser(description="Manage Audio Clips")

# Add an argument
parser.add_argument("command", help="add, list, replace, rm")
parser.add_argument("--creator", dest="creator", help="Asset Creator", required=False)
parser.add_argument("--name", dest="name", help="Asset Name", required=False)
#parser.add_argument("--name", dest="name", help="Asset Type", required=False)

# Parse the arguments
args = parser.parse_args()


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
        creator_options = []
        for c in Creator.select():
            creator_options.append((c.name, c.id))
        creator_prompt = [
            inquirer.List("creator", message="Please choose the DJ/Creator", choices=creator_options)
        ]
        answer = inquirer.prompt(creator_prompt)
        return Creator.get_by_id(answer["creator"])
    

match args.command:
    case "list":
        clips = AudioClip.select()
        for clip in clips:
            print ("(" + str(clip.id) + ")\t"+clip.asset.name + "\t" + format_seconds(clip.duration))
    case "add":
        asset_name = require_name()
        creator = require_creator()
        matches = (AudioAsset.select().where(AudioAsset.name.contains(asset_name), AudioAsset.creator_id == creator.id).dicts())

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
        
        print(f"Clip saved")
    case "replace":
        asset_name = require_name()
        creator = require_creator()
        matches = AudioClip.select().join(AudioAsset).where(AudioAsset.name.contains(asset_name), AudioAsset.creator_id == creator.id)

        clip_options = []
        for m in matches:
            clip_options.append((m.asset.name + " " + format_seconds(m.duration), m.id))

        questions2 = [
            inquirer.List("clip", message="Clip to Replace?", choices=clip_options),
            inquirer.Text("start", message="New Start time (hh::mm::ss)"),
            inquirer.Text("end", message="New End time (hh::mm::ss)"),
        ]

        answers2 = inquirer.prompt(questions2)

        clip_for_update = AudioClip.get(answers2["clip"])
        clip_for_update.start_time = get_seconds(answers2["start"])
        clip_for_update.end_time = get_seconds(answers2["end"])
        #clip = AudioClip(asset=answers2["mix"],start_time=get_seconds(answers2["start"]),end_time=get_seconds(answers2["end"]))
        clip_for_update.save()
        
        print(f"Clip Updated")
    case "rm" | "remove" | "delete" | "del":
        print("The remove command is not yet implemented.")
    case _:
        parser.print_help()

