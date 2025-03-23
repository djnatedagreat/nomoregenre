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
        shows = Show.select()
        for s in shows:
            print ("(" +Fore.WHITE+Style.BRIGHT+ str(s.id) + Style.RESET_ALL+ ")\t" + s.first_air_date.strftime("%Y-%m-%d"))
    case "show":
        id = require_id()
        show = Show.get_by_id(id)
        if (show):
            h1 ("Show Details")
            print(Fore.CYAN+"ID:\t\t"+Fore.WHITE+Style.BRIGHT + str(show.id) + Style.RESET_ALL)
            print(Fore.CYAN+"First Air Date:\t" +Fore.WHITE+Style.BRIGHT + show.first_air_date.strftime("%Y-%m-%d")+ Style.RESET_ALL)
            print(Fore.CYAN+"Duration:\t" +Fore.WHITE+Style.BRIGHT + str(show.duration) + " secs" + Style.RESET_ALL)
            if show.filename:
                print(Fore.CYAN+"Filename:\t" +Fore.WHITE+Style.BRIGHT + show.filename+ Style.RESET_ALL)
            if show.build_date:
                print(Fore.CYAN+"Build Date:\t" +Fore.WHITE+Style.BRIGHT + show.build_date.strftime("%Y-%m-%d")+ Style.RESET_ALL)
            else:
                print(Fore.CYAN+"Build Date:\t" +Fore.WHITE+Style.BRIGHT + "Not Built"+ Style.RESET_ALL)
            print_show_program(show)
        else:
            print("Not Found")
    case "add":
        show_date = require_airdate()
        #existing_show = Show.get_or_none(first_air_date=show_date)
        #if existing_show:
        ##    print("A show for that date already exists.")
        #    exit()

        # Build Program from definition file
        program_def = require_program_def()
        #print(program_def["duration_min"])
        
        # TODO: Remove Hardcoding from the following lines
        show_name = "No More Genre Show: {}".format(show_date)
        #build_date=datetime.now().strftime("Y-%m-%d")
        duration = program_def["duration_min"]
        db = SqliteDatabase(':memory:')
        with db.atomic() as transaction:  # Opens new transaction.
            try:
                show = Show(name=show_name,first_air_date=show_date, duration=duration)
                show.save()
                for seg in program_def["segments"]:
                    print(seg)
                    segment = ShowSegment(name=seg["name"],show=show)
                    
                    if "duration_min" in seg:
                        segment.duration_min = seg["duration_min"]
                    if "duration_max" in seg:
                        segment.duration_max = seg["duration_max"]
                    
                    segment.save()
                    print(segment)
                    if seg["clips"] and len(seg["clips"]) > 0:
                        # add clips
                        for sc in seg["clips"]:
                            clip = AudioClip.get_by_id(sc["id"])
                            new_segment_clip = ShowSegmentClip(segment=segment, clip=clip)
                            new_segment_clip.save()
                            print()
            except BaseException as e:
                # Because this block of code is wrapped with "atomic", a
                # new transaction will begin automatically after the call
                # to rollback().
                transaction.rollback()
                print(f"An error occurred: {e}")
                error_saving = True

    case "fill":  
        id = require_id()
        show = Show.get_by_id(id)
        while show.has_unfilled_segment():
            segment_to_fill = show.get_first_unfilled_segment()
            print(Fore.CYAN + Style.BRIGHT + "Filling " +segment_to_fill.name + Style.RESET_ALL ) 
            for sc in segment_to_fill.clips:
                print("  " + sc.clip.asset.name)

            print("  " + format_seconds(segment_to_fill.get_min_time_to_fill()) + " left to fill")
            print("\n")
            new_clip = choose_clip(segment_to_fill)
            segment_to_fill.add_clip(new_clip)

            if segment_to_fill.is_filled and segment_to_fill.overage > 0:
                show.reduce_unfilled_segments(segment_to_fill.overage)

            # I'm WORKING HERE
        print('Show is filled! Use build command to make mp3 file.')  
    case "build":
        id = require_id()
        show = Show.get_by_id(id)
        print('Let\'s Build!')
        #print (args.showdate)
        # TODO: Remove Hardocding
        show_filename = config["LIBRARY_DIR"]+"/show/no-more-genre-{}.mp3".format(show.first_air_date)
        show.filename = "no-more-genre-{}.mp3".format(show.first_air_date)
        show.build_date = date.today()
        show.save()
        directory = config["LIBRARY_DIR"]+"/show/"
        show.build(directory)
        print("Build Complete!")
    case "clear":
        id = require_id()
        show = Show.get_by_id(id)
        for seg in show.segments:
            prompt = [
                inquirer.Confirm("delete_seg", message="Delete Segment " + seg.name + "?")
            ]
            answer = inquirer.prompt(prompt)
            if answer["delete_seg"]:
                print("Deleting Segment " + seg.name)
                for c in seg.clips:
                    c.delete_instance()
            else:
                print("Leaving Segment " + seg.name)
        #    
        #print("All Segments have been cleared")
        #Need to rethink this... because I don't want to clear pre-programmed segments
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

