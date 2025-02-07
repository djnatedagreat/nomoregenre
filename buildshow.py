import ffmpeg
#from dotenv import load_dotenv
#load_dotenv()  # take environment variables from .env.
import inquirer
import argparse
from datetime import date, datetime
from models import AudioClip, AudioAsset, Creator, Show, ShowFormat, ShowSegment
from audio_functions import get_duration, convert_seconds
from dotenv import dotenv_values

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


def choose_segment(time_to_fill):
    segments = AudioClip.select().where(AudioClip.end_time - AudioClip.start_time < time_to_fill)
    segs = []
    for seg in segments:
        segs.append((seg.asset.creator.name + " - " + seg.asset.name + " (" + seg.get_length_str() + ")", seg.id))
    questions = [
        inquirer.List("segment", message="Please choose another segment", choices=segs),
    ]

    answers = inquirer.prompt(questions)
    return AudioClip.get(AudioClip.id==answers["segment"])
    #print(answers["segment"])

def print_show():
    for part in show_format.parts:
        print(part.name + " (" + convert_seconds(part.clip_total_duration) + ")") 
        for clip in part.clips:
            print(" " + clip.asset.name + " (" + convert_seconds(clip.duration) + ")")
    

#num_hours = 3
#hours_built = 0

while show_format.has_unfilled_part():
    part_to_fill = show_format.get_first_unfilled_part()
    print_show()
    print("Filling part: " + part_to_fill.name + " need between " + convert_seconds(part_to_fill.get_min_time_to_fill()) + ' and ' + convert_seconds(part_to_fill.get_max_time_to_fill()) )
    clip = choose_segment(part_to_fill.get_max_time_to_fill())
    #curr_clip = ffmpeg.input(clip.asset.filename)
    part_to_fill.add_clip(clip)
    print(clip)

show_format.build(show._filename)
show_model = Show(build_date=datetime.now().strftime("%Y-%m-%d"),first_air_date=args.showdate)
show_model.save()


# save segments
for p in show_format.parts:
    for c in p.clips:
        if c.asset.type.name == "mix":
            show_segment = ShowSegment(show=show_model,segment=c)
            show_segment.save()

print('done')



'''
while hours_built < num_hours:
    curr_hour = hours_built + 1
    curr_hour_length = legal_id_len + group_id_len
    to_fill = hour_segment_length_min - curr_hour_length
    to_fill_str = convert_seconds(to_fill)
    show.clips.append(legal_id)
    show.clips.append(group_id)
    print(f"Hour {curr_hour}, Time to fill {to_fill_str} ")
    while curr_hour_length < hour_segment_length_min:
        print(f"Hour {curr_hour}, Time to fill {to_fill_str} ")
        clip = choose_segment(hour_segment_length_max - curr_hour_length)
        show.clip.append(ffmpeg.input(segment.asset.filename))
        curr_hour_length = curr_hour_length - clip.duration()
        to_fill = hour_segment_length_min - curr_hour_length
        to_fill_str = convert_seconds(to_fill)
    hours_built = hours_built + 1

        


#while show_length < show_length_min:
    

(
  ffmpeg
  .concat(legal_id.audio, group_id.audio, v=0, a=1)
  .output("files/shows/" + output_file, acodec="libmp3lame")
  .run()
)
'''
