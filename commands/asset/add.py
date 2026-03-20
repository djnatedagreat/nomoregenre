import argparse
from models import AudioAsset, AssetType, Creator, AudioClip
from peewee import fn
from ..action import Action
from slugify import slugify
from os import path
import ffmpeg
from datetime import datetime

class AddAssetAction(Action):

    def __init__(self, asset_type, args):
        self.asset_type = asset_type
        self.creator = super().require_creator(args, "by")
        self.name = super().require_arg(args, "name")
        self.file = super().require_arg(args, "file")
        # validate submit date 2025-01-01 format
        if args.when:
            self.submit_date = args.when
        else:
            self.submit_date = datetime.now().strftime("%Y-%m-%d")
        
    def run(self):
        
        if not self.creator:
            raise Exception("No creator specified.")
        
        at = AssetType.get_or_none(AssetType.name == self.asset_type)
        if not at:
            raise Exception("Can not find asset type, " + self.asset_type)

        # validate name
        key=slugify(self.name)
        existing_asset = AudioAsset.get_or_none(AudioAsset.key == key)
        if existing_asset:
            raise Exception("Audio Asset " +self.name+ " exists with ID " + str(existing_asset.id) + "Asset names must be unique.")
        
        # validate audio file exists and is not empty
        asset_file =  self.file
        basename=path.basename(asset_file)
        probe = ffmpeg.probe(asset_file)
        duration = float(probe['format']['duration'])  # Extract duration in seconds
        if not duration > 0:
            raise Exception ("Audio file is misformated or empty.")

        #print(self.name + " " +at.name + " " + self.creator.name + " " + basename + " " + self.submit_date)
        asset = AudioAsset(key=key, name=self.name, filename=basename, type=at.id, creator=self.creator.id, submitted=self.submit_date)
        asset.save() # now stored in the database

        # save the full clip
        clip = AudioClip(asset=asset.id,start_time=0,end_time=duration)
        clip.save()

        print(f"Audio Asset saved -- {asset.name}")

# kwargs "at" for asset_type filter eg. mix, id, etc. assumes asset type name 
def handle(args, **kwargs):

    parser = argparse.ArgumentParser(description="Add Asset")
    parser.add_argument('--by', dest="by", type=str, help="Name of Creator")
    parser.add_argument('--name', dest="name", type=str, help="Name of Audio Asset")
    parser.add_argument('--file', dest="file", required=True, type=str, help="Path to audio file")
    parser.add_argument('--when', dest="when", type=str, help="Date Submitted (YYYY-MM-DD)")
    parsed_args = parser.parse_args(args)
    action = AddAssetAction(kwargs.get("at"), parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)