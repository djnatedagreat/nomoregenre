import argparse
import inquirer
from models import ShowSegment, Show, AudioClip, AudioAsset, Creator, AssetType
#from peewee import fn
from ..action import Action
from utils import get_seconds, format_seconds, h1
from colorama import Fore, Back, Style

#config = load_config()

class FillShowAction(Action):

    def __init__(self, id, args):
        self.id = id

    def run(self):
        show = Show.get_by_id(self.id)
        while show.has_unfilled_segment():
            segment_to_fill = show.get_first_unfilled_segment()
            h1("Filling " +segment_to_fill.name) 
            for sc in segment_to_fill.clips:
                print("  " + sc.clip.asset.name)

            print("  " + format_seconds(segment_to_fill.get_min_time_to_fill()) + " left to fill")
            print("\n")
            at_choices = {}
            ats = AssetType.select()
            for at in ats:
                at_choices[at.name] = at.id
            at_q = [inquirer.List("asset_type", message="What do you want to add?", choices=list(at_choices.keys()))]
            answers = inquirer.prompt(at_q)
            new_clip = self.choose_clip(segment_to_fill, at_choices[answers["asset_type"]])
            segment_to_fill.add_clip(new_clip)

            if segment_to_fill.is_filled and segment_to_fill.overage > 0:
                show.reduce_unfilled_segments(segment_to_fill.overage)

            # I'm WORKING HERE
        print('Show is filled! Use build command to make mp3 file.')  

    
    def choose_clip(self,segment,asset_type):
        clips = AudioClip.select().join(AudioAsset).join(Creator).where(AudioAsset.type_id == asset_type).where(AudioClip.end_time - AudioClip.start_time < segment.get_max_time_to_fill()).order_by(AudioAsset.type, AudioAsset.submitted.desc(), AudioAsset.name, (AudioClip.end_time - AudioClip.start_time).desc())
        choices = []
        for c in clips:
            choices.append((c.asset.creator.name + " - " + c.asset.submitted.strftime("%Y-%m-%d") + " - " + c.asset.name + " (" + c.format_seconds() + ")", c.id))
        
        questions = [
            inquirer.List("clip", message="You are filling: " + format_seconds(segment.get_min_time_to_fill()) + ' (Max: ' + format_seconds(segment.get_max_time_to_fill()) +")", choices=choices),
        ]

        answers = inquirer.prompt(questions)
        return AudioClip.get(AudioClip.id==answers["clip"])

def handle(args, **kwargs):

    parser = argparse.ArgumentParser(description="Show Asset Details")
    parser.add_argument('id', help="Show ID")
    parsed_args = parser.parse_args(args)
    action = FillShowAction(parsed_args.id, parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)