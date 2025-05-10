import argparse
import inquirer
import json
from models import Show, ShowSegment, AudioClip, ShowSegmentClip
from ..action import Action
from peewee import SqliteDatabase

class AddShowAction(Action):
    
    def __init__(self, args):
        self.air_date = super().require_arg(args,"air_date")
        self.program_def = self.require_program_def(args,"program")
        # TODO: Remove Hardcoding from the following lines
        self.show_name = "No More Genre Show: {}".format(self.air_date)

    def run(self):
        #build_date=datetime.now().strftime("Y-%m-%d")
        duration = self.program_def["duration_min"]
        db = SqliteDatabase(':memory:')
        with db.atomic() as transaction:  # Opens new transaction.
            try:
                show = Show(name=self.show_name,first_air_date=self.air_date, duration=duration)
                show.save()
                for seg in self.program_def["segments"]:
                    print(seg)
                    segment = ShowSegment(name=seg["name"],show=show)
                    
                    if "duration_min" in seg:
                        segment.duration_min = seg["duration_min"]
                    if "duration_max" in seg:
                        segment.duration_max = seg["duration_max"]
                    if "prefill_only" in seg:
                        segment.prefill_only = seg["prefill_only"]
                    else:
                        segment.prefill_only = False
                    
                    segment.save()
                    #print(segment)
                    if seg["clips"] and len(seg["clips"]) > 0:
                        # add clips
                        for sc in seg["clips"]:
                            clip = AudioClip.get_by_id(sc["id"])
                            new_segment_clip = ShowSegmentClip(segment=segment, clip=clip)
                            new_segment_clip.save()
                            print()
            except BaseException as e:
                # Because this block of code is wrapped with "atomic", a
                # new transaction will begin automatically after the call
                # to rollback().
                transaction.rollback()
                raise e
                #print(f"An error occurred: {e}")
                #error_saving = True

    def require_program_def(self, args, arg_name):
        program_def_file = None
        if getattr(args, arg_name, None) is not None:
            program_def_file = getattr(args, arg_name)
        
        if not program_def_file:
            prompt = [
                inquirer.Path("program_def_file", message="Enter a Program Definition File (JSON)")
            ]
            answer = inquirer.prompt(prompt)
            program_def_file = answer["program_def_file"]
        try:
            with open(program_def_file, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            raise Exception(f"Error: File not found at path: {program_def_file}")
        except json.JSONDecodeError:
            raise Exception(f"Error: Invalid JSON format in file: {program_def_file}")

def handle(args, **kwargs):
    parser = argparse.ArgumentParser(description="Add Show")
    parser.add_argument('air_date', type=str, help="Date First Airing")
    parser.add_argument('--program', dest="program", required=True, type=str, help="Path to program definition file")
    parsed_args = parser.parse_args(args)
    action = AddShowAction(parsed_args)
    try:
        action.run()
        print(f"Show created. Use `python nmg.py show fill` to start adding clips")
    except Exception as e:
        print("Error: " + str(e))
        exit(2)