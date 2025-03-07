# converts hh::mm::ss.sss to seconds
def get_seconds(time_str):
    """Get seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

def format_seconds(seconds):
    hours, remainder = divmod(seconds, 3600)  # Get hours
    minutes, seconds = divmod(remainder, 60)  # Get minutes and seconds
    result = ""
    if hours > 0:
        result = result + f"{round(hours)} Hrs "
    if minutes > 0:
        result = result + f"{round(minutes)} Mins "
    result = result + f"{round(seconds)} Secs"
    return result
def load_config():
    from os import path
    from dotenv import dotenv_values
    if path.exists(".env.local"):
        print("LOCAL DEV ENVIRONMENT ACTIVATED")
        return dotenv_values(".env.local")
    else:
        return dotenv_values(".env")  # take environment variables from .env.
    