import argparse
from models import Show, ShowSegmentClip, ShowSegment
from ..action import Action


class PopClipAction(Action):

    def __init__(self, show_id):
        self.show_id = show_id

    def run(self):
        show = Show.get_by_id(self.show_id)

        if show.is_built:
            raise Exception("Show is already built.")

        last = (ShowSegmentClip
                .select()
                .join(ShowSegment)
                .where(ShowSegment.show == show)
                .order_by(ShowSegmentClip.id.desc())
                .first())

        if not last:
            raise Exception("Show has no clips to remove.")

        name = last.clip.asset.name
        segment_name = last.segment.name
        last.delete_instance()
        print(f"Removed '{name}' from segment '{segment_name}'.")


def handle(args, **kwargs):
    parser = argparse.ArgumentParser(description="Remove the last clip from a show")
    parser.add_argument('show_id', help="Show ID")
    parsed_args = parser.parse_args(args)
    action = PopClipAction(parsed_args.show_id)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)
