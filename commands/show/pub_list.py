import argparse
from models import Show, ShowPublication
from ..action import Action
from tabulate import tabulate


class PubListAction(Action):

    def __init__(self, args):
        self.show_id = args.show_id

    def run(self):
        if self.show_id:
            show = Show.get_by_id(self.show_id)
            pubs = ShowPublication.select().where(ShowPublication.show == show)
        else:
            pubs = ShowPublication.select()

        if not pubs.count():
            print("No publications found.")
            return

        rows = []
        for pub in pubs:
            rows.append([
                pub.id,
                pub.show.name,
                pub.provider,
                pub.account or "",
                pub.external_id,
                pub.url,
                pub.published_at,
            ])

        print(tabulate(rows, headers=["ID", "Show", "Provider", "Account", "External ID", "URL", "Published At"]))


def handle(args, **kwargs):
    parser = argparse.ArgumentParser(description="List publications for a show")
    parser.add_argument("show_id", nargs="?", help="Show ID (omit to list all)")
    parsed_args = parser.parse_args(args)
    action = PubListAction(parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)
