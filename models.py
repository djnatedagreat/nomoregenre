from dotenv import dotenv_values
from peewee import * 
from playhouse.sqlite_ext import SqliteExtDatabase
from audio_functions import get_duration
from utils import format_seconds
import ffmpeg

config = dotenv_values(".env")  # take environment variables from .env.

db = SqliteExtDatabase(config["SQLITE_DB"])

class BaseModel(Model):
    class Meta:
        database = db

class Creator(BaseModel):
    name = CharField()

class AssetType(BaseModel):
    name = CharField()

class AudioAsset(BaseModel):
    key=CharField(unique=True)
    name = CharField()
    filename = CharField()
    type = ForeignKeyField(AssetType, backref='assets')
    creator = ForeignKeyField(Creator, backref='assets')
    submitted = DateField()
    def get_path_to_file(self):
        return config["LIBRARY_DIR"] + "/" + self.type.name + "/" + self.filename

class AudioClip(BaseModel):
    asset = ForeignKeyField(AudioAsset, backref='clips')
    start_time = FloatField(default=0)
    end_time = FloatField(default=0)
    fade_in_length = FloatField(default=0)
    fade_out_length = FloatField(default=0)
    @property
    def duration(self):
        return self.end_time - self.start_time
    
    def format_seconds(self):
        hours, remainder = divmod(self.duration, 3600)  # Get hours
        minutes, seconds = divmod(remainder, 60)  # Get minutes and seconds
        result = ""
        if hours > 0:
            result = result + f"{round(hours)} Hrs "
        if minutes > 0:
            result = result + f"{round(minutes)} Mins "
        result = result + f"{round(seconds)} Secs"
        return result

class Show(BaseModel):
    build_date = DateField()
    first_air_date = DateField()
    #filename = CharField(null=True, column_name=None)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._clips = []
        self._filename = None
    @property
    def filename(self):
        return self._filename
    @property
    def clips(self):
        return self._clips 
    @property
    def clip_duration(self):
        tot_duration = 0
        for c in clips:
            tot_duration = tot_duration + c.duration
        return tot_duration
        
class ShowFormat(Model):
    min_duration = float
    max_duration = float
    parts = [] 
    def add_part(self, name, clip, duration_min, duration_max):
        part = ShowFormatPart(name, clip, duration_min, duration_max)
        self.parts.append(part)
    def fill_part(self, name, clip, duration):
        part = {
            "name": name,
            "clip": clip,
            "duration": duration
        }
        self.parts.append(part)

    def has_unfilled_part(self):
        if self.get_first_unfilled_part():
            return True
        else:
            return False
    
    def get_unfilled_parts(self):
        unfilled = []
        for p in self.parts:
            if p.incomplete():
                #print("inc " + p.name)
                unfilled.append(p)
        return unfilled

    def get_first_unfilled_part(self):
        unfilled_parts = self.get_unfilled_parts()
        if len(unfilled_parts) > 0:
            return unfilled_parts[0]
        else:
            return False
    
    # let's change this to reduce_unfilled_parts_by(secs) and
    # do the calculation of time outside of this function.
    # overage could be applied multiple times. See below.
    def reduce_unfilled(self, secs):
        if self.min_duration == 0 and self.max_duration == 0:
            return
        if not self.has_unfilled_part:
            return
        unfilled = self.get_unfilled_parts()
        unfilled_count = len(unfilled)
        if unfilled_count == 0:
            return
        
        # shorten unfilled parts
        time_for_each = secs // unfilled_count
        print ("time for each: " + format_seconds(time_for_each))
        for p in unfilled:
            print("before min: " + p.name + " " +format_seconds(p.duration_min))
            print("before max: " + p.name + " " +format_seconds(p.duration_max))
            p.duration_min = p.duration_min - time_for_each
            p.duration_max = p.duration_max - time_for_each
            print("after min: " + format_seconds(p.duration_min))
            print("after max: " + format_seconds(p.duration_max))
        return
               
    def build(self, output_file):
        streams = []
        for p in self.parts:
            for c in p.clips:
                streams.append(ffmpeg.input(config["LIBRARY_DIR"] + "/" + c.asset.type.name + "/" + c.asset.filename, ss=c.start_time, to=c.end_time))
        (
        ffmpeg
        .concat(*streams, v=0, a=1)
        .output(output_file)
        .run()
        )
        
        
class ShowFormatPart(Model):
    def __init__(self, name: str, clip: AudioClip, duration_min: float, duration_max: float):
        self.name = name
        self.clips = []
        #self.clip_total_duration = 0
        self.duration_min = 0
        self.duration_max = 0
        if clip:
            self.clips.append(clip)
            #self.clip_total_duration = clip.duration
        if duration_min :
            self.duration_min = duration_min
        if duration_max :
            self.duration_max = duration_max

    @property
    def clip_total_duration(self):
        duration = 0
        for c in self.clips:
            duration = duration + c.duration
        return duration
    @property
    def overage(self):
        overage = self.clip_total_duration - self.duration_min
        return max(0,overage)
    @property
    def filled(self):
        if self.get_min_time_to_fill() <= 0:
            return True
        else:
            return False
        
    def incomplete(self):
        return not self.filled

    def get_min_time_to_fill(self):
        return self.duration_min - self.clip_total_duration
    
    def get_max_time_to_fill(self):
        return self.duration_max - self.clip_total_duration
    
    def add_clip(self, clip: AudioClip):
        self.clips.append(clip)
    
class ShowSegment(BaseModel):
    show = ForeignKeyField(Show)
    segment = ForeignKeyField(AudioClip)

