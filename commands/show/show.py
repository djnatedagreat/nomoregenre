import argparse
from models import ShowSegment, Show, ShowSegmentClip, AudioClip
#from peewee import fn
from ..action import Action
from utils import get_seconds, h1, h2, format_seconds
from colorama import Fore, Back, Style

#config = load_config()

class ShowShowAction(Action):

    def __init__(self, id, args):
        self.id = id

    def run(self):
        s = Show.get_by_id(self.id)

        h1 ("Show Details")
        print(Fore.CYAN+"ID:\t\t"+Fore.WHITE+Style.BRIGHT + str(s.id) + Style.RESET_ALL)
        print(Fore.CYAN+"First Air Date:\t" +Fore.WHITE+Style.BRIGHT + s.first_air_date.strftime("%Y-%m-%d")+ Style.RESET_ALL)
        print(Fore.CYAN+"Duration:\t" +Fore.WHITE+Style.BRIGHT + str(s.duration) + " secs" + Style.RESET_ALL)
        if s.filename:
            print(Fore.CYAN+"Filename:\t" +Fore.WHITE+Style.BRIGHT + s.filename+ Style.RESET_ALL)
        if s.build_date:
            print(Fore.CYAN+"Build Date:\t" +Fore.WHITE+Style.BRIGHT + s.build_date.strftime("%Y-%m-%d")+ Style.RESET_ALL)
        else:
            print(Fore.CYAN+"Build Date:\t" +Fore.WHITE+Style.BRIGHT + "Not Built"+ Style.RESET_ALL)
        
        self.print_show_program(s)
    
    def print_show_program(self, show):
        h1 ("Show Program")
        for seg in show.segments:
            h2 (seg.name)
            if seg.prefill_only:
                print ("  (Prefill Only)")
            #print("  "+Fore.CYAN + Style.BRIGHT +seg.name + Style.RESET_ALL ) 
            if len(seg.clips) > 0:
                for clip in seg.clips:
                    #print(clip.__data__)
                    audioclip = AudioClip.get_by_id(clip.clip)
                    #print (audioclip.asset.name)
                    print("    (" + str(audioclip.asset.id) + ") " + audioclip.asset.name + " (" + format_seconds(audioclip.duration) + ")")
            else:
                print("    Empty")

# kwargs "at" for asset_type filter eg. mix, id, etc. assumes asset type name 
def handle(args, **kwargs):

    parser = argparse.ArgumentParser(description="Show Show")
    parser.add_argument('id', help="Show ID")
    parsed_args = parser.parse_args(args)
    action = ShowShowAction(parsed_args.id, parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)

