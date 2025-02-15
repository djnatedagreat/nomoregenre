import ffmpeg
from dotenv import dotenv_values

config = dotenv_values(".env")  # take environment variables from .env.

def get_duration(file):
    probe = ffmpeg.probe(file)
    duration = float(probe['format']['duration'])  # Extract duration
    return duration
