import argparse
from models import Show
from ..action import Action
from utils import load_config
from slugify import slugify
from datetime import date
from os import path, close as close_fd
import tempfile
from pydub import AudioSegment
import ffmpeg

class BuildShowAction(Action):
    
    def __init__(self, args):
        self.id = super().require_arg(args, "id")
        self.default_crossfade = 5*1000 # crossfade

    def run(self):
        show = Show.get_by_id(self.id)
        config = load_config()
        if show.has_unfilled_segment():
            raise Exception("Your show is incomplete. Use the 'fill' action to fill up the segments with clips.")
        # TODO: make audio format configurable
        show.filename = "{}.mp3".format(slugify(show.name))
        show.save()

        outputfile = path.normpath(config["SHOW_DIR"]) + "/" +show.filename
        mix_inputs = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for seg in show.segments:
                for sc in seg.clips:
                    # This is an mp3 file. We need to convert it to a wav file
                    # because ffmpeg can't seek through mp3 files like it can through wav files
                    # We will pay with longer wait times during build, but
                    # storing files as mp3s will save a ton of space.
                    segment_file = config["LIBRARY_DIR"] + "/" + sc.clip.asset.type.name + "/" + sc.clip.asset.filename
                    # This is the wav output file.
                    fd, wav_file = tempfile.mkstemp(dir=temp_dir, suffix=".wav")
                    #close_fd(fd)  # Close the file descriptor if you're not using it immediately
                    #print("Unique file path:", path)
                    #wav_file = path.join(temp_dir, sc.clip.asset.filename.replace(".mp3",".wav"))
                    # TODO: why does it keep prompting me if I want to overwrite the file????
                    # This converts the mp3 to a wav
                    ffmpeg.input(segment_file).output(wav_file).run()
                    mix_input = sc.clip.get_input_stream_with_filters(wav_file)
                    mix_inputs.append(mix_input)
            
            ffmpeg.concat(*mix_inputs, v=0, a=1).output(outputfile).run()

        '''
        print(
        ffmpeg
        .concat(*mix_inputs, v=0, a=1)
        #.filter(mix_inputs, 'amix', inputs=len(mix_inputs), duration='longest')
        .output(outputfile)
        .compile()
        #.run()
        ) 
        
        show_stream = AudioSegment.empty()
        for seg in show.segments:
            for sc in seg.clips:
                # TODO: custom crossfades per clip
                cf = self.default_crossfade
                start = sc.clip.start_time * 1000
                end = sc.clip.end_time * 1000
                clip = AudioSegment.from_mp3(config["LIBRARY_DIR"] + "/" + sc.clip.asset.type.name + "/" + sc.clip.asset.filename)
                show_stream += clip[start:end]
                print("Processing: " + sc.clip.asset.name)
                # TODO: add support for fade in / fade out
                print(cf)
                show_stream.append(clip[start:end], crossfade=cf)
        #show.build()
        show_stream.export(outputfile, format="mp3")
        '''

        show.build_date = date.today()
        show.save()
        print("Build Complete!")

def handle(args, **kwargs):
    parser = argparse.ArgumentParser(description="Build Show")
    parser.add_argument('--id', dest="id", help="Show ID")
    parsed_args = parser.parse_args(args)
    action = BuildShowAction(parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)

'''
def build(self, output_dir):
        #from pydub import AudioSegment
        outputfile = path.normpath(output_dir) + "/" +self.filename
        #show = AudioSegment.empty()
            #for m in markers:
                #print('appending preview at' +str(m))
                #st = m*1000
                #end = st + clip_len
                #print("len: " + str(end - st))
                #preview = preview.append(segment[st:end], crossfade=cf)
            #preview = preview.append(segment[0-clip_len:], crossfade=cf)
            # save a preview file for speed and efficiency next time
            #preview.export(preview_file, format="mp3")
        streams = []
        for seg in self.segments:
            for sc in seg.clips:
                # TODO: Should not know about LIBRARY DIR. Should probably call a util
                #show = show.append(segment[st:end], crossfade=cf)
                streams.append(ffmpeg.input(config["LIBRARY_DIR"] + "/" + sc.clip.asset.type.name + "/" + sc.clip.asset.filename, ss=sc.clip.start_time, to=sc.clip.end_time))
        (
        ffmpeg
        .concat(*streams, v=0, a=1)
        .output(outputfile)
        .run()
        ) 

'''

        