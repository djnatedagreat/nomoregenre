import argparse
from models import AudioAsset, AudioClip, AssetType
from peewee import fn
from ..action import Action
from utils import get_seconds, load_config
from os import path
import ffmpeg

config = load_config()

# If an audio file was manually trimmed with, for example, audacity. That will change the length of the file
# and affect time marks for any clips. This is a utility that will rebuild the clips.
# If you manually trimmed the start of the file, then pass the length trimmed in seconds.
# If trimmed from the end, it can figure that out automatically because it can detect the change in length.
class TrimAssetAction(Action):

    def __init__(self, asset_type, args):
        self.asset_type = asset_type
        self.id = super().require_arg(args, "id")
        self.offset = args.offset

    def run(self):
        aa_q = AudioAsset.select()
        aa_q = aa_q.where(AudioAsset.id == self.id)
        if (self.asset_type):
            type = AssetType.get_or_none(AssetType.name == self.asset_type)
            aa_q = aa_q.where(AudioAsset.type == type.id)
        
        aa = aa_q.get_or_none()
        
        if not aa:
            raise Exception("Audio Asset not found.")
        
        directory = path.normpath(config["LIBRARY_DIR"])+"/"+aa.type.name+"/"
        asset_file = directory + aa.filename
        probe = ffmpeg.probe(asset_file)
        new_duration = float(probe['format']['duration'])  # Extract duration in seconds
        if not new_duration > 0:
            raise Exception ("Audio file is misformated or empty.")
        
        for c in aa.clips:
            current_duration = c.duration
            curr_start = c.start_time
            curr_end = c.end_time
            # should I check if the new duration is different from the old duration??
            if self.offset > 0: # adjust based on --offset
                c.start_time = max(c.start_time - self.offset,0)
                # shift the end time
                c.end_time = max(c.end_time - self.offset,0)

                # now adjust for end time, if needed.
                # if the end time is now greater than the new start time + new duration
                c.end_time = min(c.start_time + new_duration, c.end_time)
            # I think I might be missing an else that should handle if the end was trimmed????
            c.save()
            
        print("Clips have been adjusted for " + aa.name)

# kwargs "at" for asset_type filter eg. mix, id, etc. assumes asset type name 
def handle(args, **kwargs):

    parser = argparse.ArgumentParser(description="Resize Clips")
    parser.add_argument('--offset', type=float) # start offset (change from start) in seconds
    parser.add_argument('--id', required=True, dest="id", help="Asset ID")
    parsed_args = parser.parse_args(args)
    action = TrimAssetAction(kwargs.get("at"), parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)