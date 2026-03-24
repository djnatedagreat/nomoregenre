import argparse
from models import AudioAsset, Creator, AssetType, AudioClip, ShowSegment, Show, ShowSegmentClip
from peewee import fn
from ..action import Action
from os import path
from utils import get_seconds, h1, h2
from colorama import Fore, Back, Style
from tabulate import tabulate
from library import library

class ShowAssetAction(Action):

    def __init__(self, id, asset_type, args):
        self.asset_type = asset_type
        self.id = id

    def run(self):
       
        aa_q = ( AudioAsset.select()
                .join(Creator)
                .join(AudioClip, on=(AudioAsset.id == AudioClip.asset_id))
                .where(AudioAsset.id == self.id)
            )
        if (self.asset_type):
            type = AssetType.get_or_none(AssetType.name == self.asset_type)
            if type:
                aa_q = aa_q.join(AssetType, on=((AudioAsset.type_id == AssetType.id) & (AssetType.id == type.id)))
        
        aa = aa_q.get_or_none()

        shows = ( Show.select()
                .join(ShowSegment, on=(Show.id == ShowSegment.show_id))
                .join(ShowSegmentClip, on=(ShowSegment.id == ShowSegmentClip.segment_id))
                .join(AudioClip, on=(ShowSegmentClip.clip_id == AudioClip.id))
                .join(AudioAsset, on=(AudioClip.asset_id == AudioAsset.id))
                .where(AudioAsset.id == self.id) )
        
        # show segments
        #shows = show_q.get()

        #existing_asset = AudioAsset.get_or_none(AudioAsset.key == key)
        if not aa:
            raise Exception("Audio Asset not found.")
        
        asset_file = library.asset_path(aa)
        preview_file = asset_file + ".preview"

        h1 ("Details")
        print(Fore.CYAN+"ID:\t\t"+Fore.WHITE+Style.BRIGHT + str(aa.id) + Style.RESET_ALL)
        print(Fore.CYAN+"Type:\t\t" +Fore.WHITE+Style.BRIGHT + aa.type.name.capitalize() + Style.RESET_ALL)
        print(Fore.CYAN+"Name:\t\t" +Fore.WHITE+Style.BRIGHT + aa.name+ Style.RESET_ALL)
        print(Fore.CYAN+"Created By:\t" +Fore.WHITE+Style.BRIGHT + aa.creator.name+ Style.RESET_ALL)
        print(Fore.CYAN+"Submit Date:\t" +Fore.WHITE+Style.BRIGHT + aa.submitted.strftime("%Y-%m-%d")+ Style.RESET_ALL)

        #print(Fore.CYAN+"Duration:\t" +Fore.WHITE+Style.BRIGHT + str(show.duration) + " secs" + Style.RESET_ALL)
        if aa.filename:
            print(Fore.CYAN+"Filename:\t" +Fore.WHITE+Style.BRIGHT + aa.filename+ Style.RESET_ALL)
        
        h1 ("Clips")
        clip_headers = ['ID','Length', 'Start', 'End', 'Fade In', 'Fade Out']
        clip_data = []
        for c in aa.clips:
            clip_data.append([c.id, c.format_seconds(), str(c.start_time), str(c.end_time),str(c.fade_in_length),str(c.fade_out_length)])
            #print(Fore.CYAN+"("+str(c.id)+")\t\t"+Fore.WHITE+Style.BRIGHT +  c.format_seconds()  + "\t\tfrom " + str(c.start_time) +  Style.RESET_ALL)
        print(tabulate(clip_data, headers=clip_headers, tablefmt="pipe"))
        # Add to display: Included in shows, Clips
        h1 ("Appears in Shows")
        for s in shows:
            print(Fore.CYAN+"("+str(s.id)+")\t\t"+Fore.WHITE+Style.BRIGHT +  str(s.first_air_date)  + Style.RESET_ALL)
# kwargs "at" for asset_type filter eg. mix, id, etc. assumes asset type name 
def handle(args, **kwargs):

    parser = argparse.ArgumentParser(description="Show Asset Details")
    parser.add_argument('id', help="Asset ID or Ref")
    parsed_args = parser.parse_args(args)
    action = ShowAssetAction(parsed_args.id, kwargs.get("at"), parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)