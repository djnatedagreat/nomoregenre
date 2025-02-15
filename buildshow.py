import ffmpeg
#from dotenv import load_dotenv
#load_dotenv()  # take environment variables from .env.
import inquirer
import argparse
from datetime import date, datetime
from utils import format_seconds
from models import AudioClip, AudioAsset, Creator, Show, ShowFormat, ShowSegment
from audio_functions import get_duration
from dotenv import dotenv_values
from colorama import Fore, Back, Style

config = dotenv_values(".env")  # take environment variables from .env.

# Create ArgumentParser
parser = argparse.ArgumentParser(description="Build a new Radio Show")

# Add an argument
parser.add_argument("showdate", help="First air date of the show")

# Parse the arguments
args = parser.parse_args()

#print (args.showdate)

show, show_created = Show.get_or_create(first_air_date=args.showdate, defaults={"build_date": date.today()})
show._filename = config["LIBRARY_DIR"]+"/show/no-more-genre-{}.mp3".format(args.showdate)

#legal_id_file = config["ID_DIR"]+"/legal-id.mp3"
legal_id_clip = (AudioClip.select().join(AudioAsset).where(AudioAsset.key == "legal-id").get())

#group_id_file = config["ID_DIR"]+"/group-show-id.mp3"
#group_id_clip = AudioClip.get(AudioClip.asset.filename == group_id_file)
group_id_clip = (AudioClip.select().join(AudioAsset).where(AudioAsset.key == "original-group-id").get())

show_format = ShowFormat();
show_format.min_duration = 10800
show_format.max_duration = 10980
show_format.add_part("Legal ID 1", legal_id_clip, legal_id_clip.duration, legal_id_clip.duration)
show_format.add_part("Group ID 1", group_id_clip, group_id_clip.duration, group_id_clip.duration)
show_format.add_part("Hour 1", None, 3567, 3807)
show_format.add_part("Legal ID 2", legal_id_clip, legal_id_clip.duration, legal_id_clip.duration)
show_format.add_part("Group ID 2", group_id_clip, group_id_clip.duration, group_id_clip.duration)
show_format.add_part("Hour 2", None, 3567, 3807)
show_format.add_part("Legal ID 3", legal_id_clip, legal_id_clip.duration, legal_id_clip.duration)
show_format.add_part("Group ID 3", group_id_clip, group_id_clip.duration, group_id_clip.duration)
show_format.add_part("Hour 3", None, 3567, 3807)


def choose_segment(min_time, max_time):
    segments = AudioClip.select().join(AudioAsset).join(Creator).where(AudioClip.end_time - AudioClip.start_time < max_time).order_by(AudioAsset.type, AudioAsset.submitted.desc(), AudioAsset.name, (AudioClip.end_time - AudioClip.start_time).desc())
    segs = []
    for seg in segments:
        segs.append((seg.asset.creator.name + " - " + seg.asset.submitted.strftime("%Y-%m-%d") + " - " + seg.asset.name + " (" + seg.format_seconds() + ")", seg.id))
    questions = [
        inquirer.List("segment", message="You are filling: " + format_seconds(part_to_fill.get_min_time_to_fill()) + ' (Max: ' + format_seconds(part_to_fill.get_max_time_to_fill()) +")", choices=segs),
    ]

    answers = inquirer.prompt(questions)
    return AudioClip.get(AudioClip.id==answers["segment"])
    #print(answers["segment"])

def get_is_filled(part):
    if part.incomplete():
        return format_seconds(part.get_min_time_to_fill())
    else:
        return "filled"
    
def print_show_overview():
    print ("\n"+Fore.RED + Style.BRIGHT +"Show Format Overview" + Style.RESET_ALL +"\n")
    for part in show_format.parts:
        print("  "+Fore.CYAN + Style.BRIGHT +part.name + " (" + get_is_filled(part) + Style.RESET_ALL + ")") 
        for clip in part.clips:
            print("    " + clip.asset.name + " (" + format_seconds(clip.duration) + ")")
    

print_show_overview()

while show_format.has_unfilled_part():
    part_to_fill = show_format.get_first_unfilled_part()
    print("\n"+Fore.RED + Style.BRIGHT + "Filling \"" + part_to_fill.name + "\"" + Style.RESET_ALL)
    for c in part_to_fill.clips:
        print("  " + c.asset.name)
    
    print("  " + format_seconds(part_to_fill.get_min_time_to_fill()) + " left to fill")
    print("\n")

    clip = choose_segment(part_to_fill.get_min_time_to_fill(), part_to_fill.get_max_time_to_fill())
    part_to_fill.add_clip(clip)

    # should only do this after a part is filled, and if there's an overage.
    if part_to_fill.filled and part_to_fill.overage > 0:
        show_format.reduce_unfilled(part_to_fill.overage)

print_show_overview()
questions = [
        inquirer.Confirm("confirm_build", message="Do you want to build this show?"),
    ]

answers = inquirer.prompt(questions)

if answers["confirm_build"]:
    show_format.build(show._filename)
    show_model = Show(build_date=datetime.now().strftime("%Y-%m-%d"),first_air_date=args.showdate)
    show_model.save()
    # save segments
    for p in show_format.parts:
        for c in p.clips:
            if c.asset.type.name == "mix":
                show_segment = ShowSegment(show=show_model,segment=c)
                show_segment.save()
    print("Build Complete!")
else:
    print("Bye!")

