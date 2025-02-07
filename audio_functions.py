import ffmpeg
from dotenv import dotenv_values

config = dotenv_values(".env")  # take environment variables from .env.

def get_duration(file):
    probe = ffmpeg.probe(file)
    duration = float(probe['format']['duration'])  # Extract duration
    return duration

# should really be format_seconds
def convert_seconds(seconds):
    hours, remainder = divmod(seconds, 3600)  # Get hours
    minutes, seconds = divmod(remainder, 60)  # Get minutes and seconds
    return f"{hours}:{minutes}:{seconds}"

# converts hh::mm::ss.sss to seconds
def get_seconds(time_str):
    """Get seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)