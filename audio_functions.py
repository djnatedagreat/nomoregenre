import ffmpeg

def get_duration(file):
    probe = ffmpeg.probe(file)
    duration = float(probe['format']['duration'])  # Extract duration
    return duration
