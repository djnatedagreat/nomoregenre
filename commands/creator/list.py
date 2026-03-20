#import argparse
from models import Creator

class ListAction:
    def run(self):
        creators = Creator.select()
        for c in creators:
            print(f"({c.id}) {c.name}")

def handle(args):
    action = ListAction()
    action.run()