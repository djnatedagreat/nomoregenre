import argparse
from models import AudioAsset
from peewee import fn
from ..action import Action
from os import path
import ffmpeg
from pydub import AudioSegment
from pydub.playback import play
import numpy as np
from utils import get_seconds
from library import library

class PreviewAssetAction(Action):

    def __init__(self, id, args):
        self.id = id
        self.clip_len = 7 * 1000
        self.cf = 1*1000 # crossfade

    def run(self):
       
        aa = AudioAsset.get_by_id(self.id)
        #existing_asset = AudioAsset.get_or_none(AudioAsset.key == key)
        if not aa:
            raise Exception("Audio Asset not found.")
        
        
        asset_file = library.asset_path(aa)
        preview_file = asset_file + ".preview"
        
        # if a preview file exists use it
        if path.exists(preview_file):
            segment = AudioSegment.from_file(preview_file, format="mp3")
            play(segment)
        else:
            segment = AudioSegment.from_file(asset_file, format="mp3")
            # get evenly spaced clips
            segment.duration_seconds
            markers = np.linspace(0, segment.duration_seconds, 5)[1:-1]
            print(markers)
            preview = AudioSegment.empty()
            preview += segment[:self.clip_len]
            for m in markers:
                #print('appending preview at' +str(m))
                st = m*1000
                end = st + self.clip_len
                #print("len: " + str(end - st))
                preview = preview.append(segment[st:end], crossfade=self.cf)
            preview = preview.append(segment[0-self.clip_len:], crossfade=self.cf)
            # save a preview file for speed and efficiency next time
            preview.export(preview_file, format="mp3")
            play(preview)

# kwargs "at" for asset_type filter eg. mix, id, etc. assumes asset type name 
def handle(args, **kwargs):

    parser = argparse.ArgumentParser(description="Preview Asset")
    parser.add_argument('id', help="Asset ID or Ref")
    parsed_args = parser.parse_args(args)
    action = PreviewAssetAction(parsed_args.id, parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)