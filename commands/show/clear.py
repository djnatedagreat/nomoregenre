import argparse
import inquirer
from models import ShowSegment, Show, AudioClip, AudioAsset, Creator
#from peewee import fn
from ..action import Action
from utils import get_seconds, format_seconds, h1
from colorama import Fore, Back, Style

#config = load_config()

class ClearShowAction(Action):

    def __init__(self, id, args):
        self.id = id

    def run(self):
        show = Show.get_by_id(self.id)

        if show.is_built:
            print("Show is Already Built")
            return

        for seg in show.segments:
            if not seg.prefill_only:
                for c in seg.clips:
                    c.delete_instance()
        
        print("Show Cleared! All Clips Removed.")

def handle(args, **kwargs):

    parser = argparse.ArgumentParser(description="Show Asset Details")
    parser.add_argument('id', help="Show ID")
    parsed_args = parser.parse_args(args)
    action = ClearShowAction(parsed_args.id, parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)