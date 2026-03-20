import argparse
import inquirer
from models import Show, ShowSegment, ShowSegmentClip, AudioClip, AudioAsset, Creator
from utils import format_seconds, get_seconds, load_config, h1, h2
from os import path, remove
from colorama import Fore, Back, Style
from datetime import date, datetime
from peewee import *
import json


config = load_config()

# Create ArgumentParser
parser = argparse.ArgumentParser(description="Manage Shows")

# Add an argument
parser.add_argument("command", help="add, list, rm, show, fill, clear, build")
parser.add_argument("--program", dest="program", help="Show Program Definition File (JSON)", required=False)
parser.add_argument("--id", dest="id", help="Specify a show ID for the current action", required=False)
parser.add_argument("--name", dest="name", help="Specify a name for the current action", required=False)
parser.add_argument("--duration", dest="duration", help="Specify the duration in seconds", required=False)
parser.add_argument("--duration-max", dest="duration_max", help="Specify the maximum duration in seconds", required=False)
parser.add_argument("--air-date", dest="air_date", help="Specify a 'first airing date' for the current action as YYY-MM-DD", required=False)
parser.add_argument("--remove-file", dest="remove_file", help="Remove the file?", required=False, action='store_true')

# Parse the arguments
args = parser.parse_args()

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
            inquirer.Text("name", message="Enter a descriptive name")
        ]
        answer = inquirer.prompt(name_prompt)
        return answer["name"]
    
def require_duration():
    if args.duration:
        return args.duration
    else:
        prompt = [
            inquirer.Text("duration", message="Enter duration in seconds")
        ]
        answer = inquirer.prompt(prompt)
        return answer["duration"]
    
def require_duration_max():
    if args.duration_max:
        return args.duration_max
    else:
        prompt = [
            inquirer.Text("duration_max", message="Enter max duration in seconds")
        ]
        answer = inquirer.prompt(prompt)
        return answer["duration_max"]
    
def require_airdate():
    if args.air_date:
        return args.air_date
    else:
        date_prompt = [
            inquirer.Text("air_date", message="Enter the air date for the show YYYY-MM-DD")
        ]
        answer = inquirer.prompt(date_prompt)
        return answer["air_date"]

def require_program_def():
    program_def_file = args.program
    if not program_def_file:
        prompt = [
            inquirer.Path("program_def_file", message="Enter a Program Definition File (JSON)")
        ]
        answer = inquirer.prompt(prompt)
        program_def_file = answer["program_def_file"]
    try:
        with open(program_def_file, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File not found at path: {program_def_file}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file: {program_def_file}")
        return None

def print_show_program(show):
    h1 ("Show Program")
    for seg in show.segments:
        h2 (seg.name)
        #print("  "+Fore.CYAN + Style.BRIGHT +seg.name + Style.RESET_ALL ) 
        if len(seg.clips) > 0:
            for clip in seg.clips:
                #print(clip.__data__)
                audioclip = AudioClip.get_by_id(clip.clip)
                #print (audioclip.asset.name)
                print("    " + audioclip.asset.name + " (" + format_seconds(audioclip.duration) + ")")
        else:
            print("    Empty")
    
def choose_clip(segment):
    clips = AudioClip.select().join(AudioAsset).join(Creator).where(AudioClip.end_time - AudioClip.start_time < segment.get_max_time_to_fill()).order_by(AudioAsset.type, AudioAsset.submitted.desc(), AudioAsset.name, (AudioClip.end_time - AudioClip.start_time).desc())
    choices = []
    for c in clips:
        choices.append((c.asset.creator.name + " - " + c.asset.submitted.strftime("%Y-%m-%d") + " - " + c.asset.name + " (" + c.format_seconds() + ")", c.id))
    questions = [
        inquirer.List("clip", message="You are filling: " + format_seconds(segment.get_min_time_to_fill()) + ' (Max: ' + format_seconds(segment.get_max_time_to_fill()) +")", choices=choices),
    ]

    answers = inquirer.prompt(questions)
    return AudioClip.get(AudioClip.id==answers["clip"])
    #print(answers["segment"])

match args.command:
    case "list":
        print('deprecated. Use: python nmg.py show list')
       
    case "show":
        print('deprecated. Use: python nmg.py show show --id=x')
        exit()
    case "add":
        print('deprecated. Use: python nmg.py show add')
        exit()
    case "fill":  
        print('deprecated. Use: python nmg.py show fill --id=x')
        exit()
    case "build":
        print('deprecated. Use: python nmg.py show build --id=x')
        exit()
    case "clear":
        print('deprecated. Use: python nmg.py show clear --id=x')
        exit()
    case "rm" | "remove" | "delete" | "del":
        id = require_id()
        show = Show.get_by_id(id)
        print(str(show.first_air_date.strftime("%Y-%m-%d")))
        if show:
            questions = [
            inquirer.Confirm("confirm_continue", message="Are you sure you want to delete this show (" + show.first_air_date.strftime("%Y-%m-%d") + ") and the associated file?"),
            ]
            answers = inquirer.prompt(questions)
            if answers["confirm_continue"]:
                print(str(show.id))
                show.delete_instance(recursive=True)
                if args.remove_file:
                    show_filename = config["LIBRARY_DIR"]+"/show/no-more-genre-{}.mp3".format(show.first_air_date.strftime("%Y-%m-%d"))
                    if path.exists(show_filename):
                        remove(show_filename)
                print("show removed")
            else:
                print("canceling")
        else:
            print("Show does not exist")
    case _:
        parser.print_help()

