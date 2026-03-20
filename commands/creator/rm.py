import argparse
from models import Creator, AudioAsset
from ..action import Action

class RmCreatorAction(Action):
    def run(self, args):
        name = super().require_arg(args, "name")
        # check if exists
        creator = Creator.get_or_none(Creator.name == name)
        if not creator:
            raise Exception("Creator " +name+ " not found")
        # check if there's any associated assets
        assets = AudioAsset.select().join(Creator).where(Creator.id==creator.id)
        if (len(assets) >  0):
            raise Exception("Creator " +creator.name+ " has associated audio assets. Removal is not supported... yet.")
        creator.delete_instance()
        
def handle(args):
    parser = argparse.ArgumentParser(description="Remove Creator")
    parser.add_argument('name', type=str, help="Name of Creator")
    action = RmCreatorAction()
    parsed_args = parser.parse_args(args)
    try:
        action.run(parsed_args)
        print("Creator has been deleted.")
    except Exception as e:
        print("Error: " + str(e))
        exit(2)