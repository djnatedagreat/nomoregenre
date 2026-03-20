#import argparse
from models import AssetType

class ListAction:
    def run(self):
        ats = AssetType.select()
        for at in ats:
            print(f"({at.id}) {at.name}")

def handle(args):
    action = ListAction()
    action.run()