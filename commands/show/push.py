import argparse
from models import Show, AudioClip
from ..action import Action


class PushClipAction(Action):

    def __init__(self, show_id, clip_id):
        self.show_id = show_id
        self.clip_id = clip_id

    def run(self):
        show = Show.get_by_id(self.show_id)
        clip = AudioClip.get_by_id(self.clip_id)

        # Check if show is already built
        if show.is_built:
            print("Show is Already Built")
            raise Exception("Show is already built")
        
        segment = show.get_first_unfilled_segment()
        if not segment:
            raise Exception("Show has no unfilled segments.")

        if clip.duration > segment.get_max_time_to_fill():
            raise Exception(
                f"Clip '{clip.asset.name}' ({clip.format_seconds()}) is too long for segment "
                f"'{segment.name}' (max {segment.get_max_time_to_fill():.0f}s remaining)."
            )

        segment.add_clip(clip)
        print(f"Added '{clip.asset.name}' to segment '{segment.name}'.")

        if segment.is_filled and segment.overage > 0:
            show.reduce_unfilled_segments(segment.overage)


def handle(args, **kwargs):
    parser = argparse.ArgumentParser(description="Push a clip to the next unfilled show segment")
    parser.add_argument('show_id', help="Show ID")
    parser.add_argument('clip_id', help="Clip ID")
    parsed_args = parser.parse_args(args)
    action = PushClipAction(parsed_args.show_id, parsed_args.clip_id)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)
