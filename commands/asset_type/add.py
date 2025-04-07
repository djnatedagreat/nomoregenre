import argparse
from models import AssetType
from ..action import Action

class AddAssetTypeAction(Action):
    
    def run(self, args):
        name = super().require_arg(args,"name")
        # check if already exists
        at = AssetType.get_or_none(AssetType.name == name)
        if at:
            raise Exception("Asset Type " +at.name+ " already exists with ID " + str(at.id))
        # create
        at = AssetType(name=name)
        at.save()

def handle(args):
    parser = argparse.ArgumentParser(description="Add Asset Type")
    parser.add_argument('name', type=str, help="Name of Asset Type")
    action = AddAssetTypeAction()
    parsed_args = parser.parse_args(args)
    try:
        action.run(parsed_args)
        print(f"Asset Type saved!")
    except Exception as e:
        print("Error: " + str(e))
        exit(2)