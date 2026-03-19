import argparse
import inquirer
from models import ShowSegment, Show, ShowSegmentClip, AudioClip, AudioAsset, AudioAssetTag, Tag, Creator, AssetType
from peewee import fn
#from peewee import fn
from ..action import Action
from utils import get_seconds, format_seconds, h1
from colorama import Fore, Back, Style
from tabulate import tabulate

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
            if new_clip == None:
                continue
            
            segment_to_fill.add_clip(new_clip)

            if segment_to_fill.is_filled and segment_to_fill.overage > 0:
                show.reduce_unfilled_segments(segment_to_fill.overage)

            # I'm WORKING HERE
        print('Show is filled! Use build command to make mp3 file.')  

    
    def choose_clip(self,segment,asset_type):
        clips = AudioClip.select().join(AudioAsset).join(Creator).where(AudioAsset.type_id == asset_type).where(AudioClip.end_time - AudioClip.start_time < segment.get_max_time_to_fill()).order_by(AudioAsset.type, AudioAsset.submitted.desc(), AudioAsset.name, (AudioClip.end_time - AudioClip.start_time).desc())
        choices = []
        back_option = "← Go Back"
        choices.append(back_option)
        for c in clips:
            choices.append((c.asset.creator.name + " - " + c.asset.submitted.strftime("%Y-%m-%d") + " - " + c.asset.name + " (" + c.format_seconds() + ")", c.id))
        
        questions = [
            inquirer.List("clip", message="You are filling: " + format_seconds(segment.get_min_time_to_fill()) + ' (Max: ' + format_seconds(segment.get_max_time_to_fill()) +")", choices=choices),
        ]

        answers = inquirer.prompt(questions)
        if answers["clip"] == back_option:
            return None
        
        return AudioClip.get(AudioClip.id==answers["clip"])

def print_candidates(show):
    segment = show.get_first_unfilled_segment()
    if not segment:
        raise Exception("Show has no unfilled segments.")

    max_duration = segment.get_max_time_to_fill()
    min_duration = segment.get_min_time_to_fill()

    h1(f"Segment: {segment.name}")
    print(f"  Min to fill: {format_seconds(min_duration)}")
    print(f"  Max to fill: {format_seconds(max_duration)}\n")

    used_mix_asset_ids = (AudioAsset
                          .select(AudioAsset.id)
                          .join(AudioClip)
                          .join(ShowSegmentClip)
                          .join(ShowSegment)
                          .where(ShowSegment.show == show)
                          .where(AudioAsset.type == AssetType.get(AssetType.name == 'mix').id)
                          .tuples())
    used_mix_asset_ids = {row[0] for row in used_mix_asset_ids}

    clips = (AudioClip
             .select()
             .join(AudioAsset)
             .join(Creator)
             .where((AudioClip.end_time - AudioClip.start_time) <= max_duration)
             .where((AudioAsset.type != AssetType.get(AssetType.name == 'mix').id) |
                    (AudioAsset.id.not_in(used_mix_asset_ids)))
             .order_by(AudioAsset.type, AudioAsset.submitted.desc(), AudioAsset.name,
                       (AudioClip.end_time - AudioClip.start_time).desc()))

    usage_stats = (ShowSegmentClip
                   .select(ShowSegmentClip.clip,
                           fn.MAX(Show.first_air_date).alias('last_air_date'),
                           fn.COUNT(ShowSegmentClip.id).alias('use_count'))
                   .join(ShowSegment)
                   .join(Show)
                   .group_by(ShowSegmentClip.clip)
                   .tuples())
    usage_map = {row[0]: (row[1], row[2]) for row in usage_stats}

    headers = ['Clip ID', 'Type', 'Creator', 'Asset Name', 'Submitted', 'Duration', 'Last Used', 'Use Count', 'Tags']
    data = []
    for c in clips:
        tags = ', '.join(at.tag.name for at in AudioAssetTag.select().join(Tag).where(AudioAssetTag.asset == c.asset.id))
        last_used, use_count = usage_map.get(c.id, ('', ''))
        data.append([c.id, c.asset.type.name, c.asset.creator.name, c.asset.name, c.asset.submitted, c.format_seconds(), last_used, use_count, tags])

    if not data:
        print("No clips found that fit this segment.")
        return

    print(tabulate(data, headers=headers, tablefmt="pipe"))


def handle(args, **kwargs):

    parser = argparse.ArgumentParser(description="Fill Show Segments")
    parser.add_argument('id', help="Show ID")
    parser.add_argument('--candidates', action='store_true', help="List clips that fit the next unfilled segment")
    parsed_args = parser.parse_args(args)

    try:
        if parsed_args.candidates:
            show = Show.get_by_id(parsed_args.id)
            print_candidates(show)
        else:
            action = FillShowAction(parsed_args.id, parsed_args)
            action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)