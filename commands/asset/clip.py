import argparse
from models import AudioAsset, AudioClip, AssetType
from peewee import fn
from ..action import Action
from utils import get_seconds, load_config

config = load_config()

# Create a clip of the asset
class ClipAssetAction(Action):

    def __init__(self, asset_type, args):
        self.asset_type = asset_type
        self.id = super().require_arg(args, "id")
        self.start = args.start
        self.end = args.end

    def run(self):
        aa_q = AudioAsset.select()
        aa_q = aa_q.where(AudioAsset.id == self.id)
        if (self.asset_type):
            type = AssetType.get_or_none(AssetType.name == self.asset_type)
            aa_q = aa_q.where(AudioAsset.type == type.id)
        
        aa = aa_q.get_or_none()
        
        if not aa:
            raise Exception("Audio Asset not found.")

        # TODO: Should probably make sure that the clip length fits inside the bounds of the asset.
        
        clip = AudioClip(asset=aa.id,start_time=get_seconds(self.start),end_time=get_seconds(self.end))
        clip.save()

        print("New clip created for Asset " + aa.name)

# kwargs "at" for asset_type filter eg. mix, id, etc. assumes asset type name 
def handle(args, **kwargs):

    parser = argparse.ArgumentParser(description="Clip Asset")
    parser.add_argument('start')
    parser.add_argument('end')
    parser.add_argument('--id', required=True, dest="id", help="Asset ID")
    parsed_args = parser.parse_args(args)
    action = ClipAssetAction(kwargs.get("at"), parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)