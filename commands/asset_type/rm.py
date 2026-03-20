import argparse
from models import AssetType, AudioAsset
from ..action import Action

class RmAssetTypeAction(Action):
    def run(self, args):
        name = super().require_arg(args, "name")
        # check if exists
        at = AssetType.get_or_none(AssetType.name == name)
        if not at:
            raise Exception("Asset Type " +name+ " not found")
        # check if there's any associated assets
        assets = AudioAsset.select().join(AssetType).where(AssetType.id==at.id)
        if (len(assets) >  0):
            raise Exception("Asset Type " +name+ " has associated audio assets. Removal is not supported... yet.")
        at.delete_instance()
        
def handle(args):
    parser = argparse.ArgumentParser(description="Remove Asset Type")
    parser.add_argument('name', type=str, help="Name of Asset Type")
    action = RmAssetTypeAction()
    parsed_args = parser.parse_args(args)
    try:
        action.run(parsed_args)
        print("Asset Type has been deleted.")
    except Exception as e:
        print("Error: " + str(e))
        exit(2)