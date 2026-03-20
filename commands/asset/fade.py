import argparse
from models import AudioAsset, AudioClip, AssetType
from peewee import fn
from ..action import Action
from utils import get_seconds, load_config

config = load_config()

# Set Fade In or Fade Out on  clips
class FadeAssetAction(Action):

    def __init__(self, id, asset_type, args):
        self.asset_type = asset_type
        self.id = id
        self.clip_id = int(super().require_arg(args, "clip"))
        self.direction = super().require_arg(args, "direction")
        self.duration = args.duration or 5 # default to 5 seconds

    def run(self):
        aa_q = AudioAsset.select()
        aa_q = aa_q.where(AudioAsset.id == self.id)
        if (self.asset_type):
            a_type = AssetType.get_or_none(AssetType.name == self.asset_type)
            aa_q = aa_q.where(AudioAsset.type == a_type.id)
        
        aa = aa_q.get_or_none()
        
        if not aa:
            raise Exception("Audio Asset not found.")
        
        for c in aa.clips:
            #print("c.id:", repr(c.id), type(c.id))
            #print("self.clip_id:", repr(self.clip_id), type(self.clip_id))
            if int(c.id) == int(self.clip_id):
                print("Adding fade to " + str(c.id))
                if self.direction == 'out':
                    c.fade_out_length = self.duration
                if self.direction == 'in':
                    c.fade_in_length = self.duration
            c.save()

        print("Fade added to Asset " + aa.name)

# kwargs "at" for asset_type filter eg. mix, id, etc. assumes asset type name 
def handle(args, **kwargs):

    parser = argparse.ArgumentParser(description="Clip Asset")
    parser.add_argument('id', help="Asset ID")
    parser.add_argument('direction',choices=['in', 'out']) # out or in
    parser.add_argument('duration') # how long in seconds
    parser.add_argument('--clip', required=True, dest="clip", help="Clip ID")
    parsed_args = parser.parse_args(args)
    action = FadeAssetAction(parsed_args.id, kwargs.get("at"), parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)