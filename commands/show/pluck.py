import argparse
import inquirer
from models import ShowSegment, Show, AudioClip, AudioAsset, Creator
#from peewee import fn
from ..action import Action
from utils import get_seconds, format_seconds, h1

#config = load_config()

class PluckShowAction(Action):

    def __init__(self, args):
        self.show_id = super().require_arg(args, "show_id")
        self.asset_id = super().require_arg(args, "asset_id")

    def run(self):
        show = Show.get_by_id(self.show_id)

        if show.is_built:
            print("Show is Already Built")
            return

        for seg in show.segments:
            if not seg.prefill_only:
                for c in seg.clips:
                    if int(c.clip.asset.id) == int(self.asset_id):
                        c.delete_instance()
        
        print("Asset Removed.")

def handle(args, **kwargs):

    parser = argparse.ArgumentParser(description="Show Asset Details")
    parser.add_argument('--id', dest="show_id", help="Show ID")
    parser.add_argument('--asset', dest="asset_id", help="Asset ID to be plucked")
    parsed_args = parser.parse_args(args)
    action = PluckShowAction(parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)