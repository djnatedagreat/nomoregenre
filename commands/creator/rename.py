import argparse
from models import Creator
from ..action import Action

class RenameCreatorAction(Action):
    
    def run(self, args):
        from_name = super().require_arg(args,"from_name")
        to_name = super().require_arg(args,"to_name")
        creator = Creator.get_or_none(Creator.name == from_name)
        if not creator:
            raise Exception("Creator " + from_name + " does not exist.")
        # check if name already in use
        creator_ck = Creator.get_or_none(Creator.name == to_name)
        if creator_ck:
            raise Exception("Creator " +creator_ck.name+ " already exists with ID " + str(creator_ck.id))
        # create
        creator.name = from_name
        creator.save()

def handle(args):
    parser = argparse.ArgumentParser(description="Rename Creator")
    parser.add_argument('from_name', type=str, help="Name of Creator to rename")
    parser.add_argument('to_name', type=str, help="New Name for Creator")
    action = RenameCreatorAction()
    parsed_args = parser.parse_args(args)
    try:
        action.run(parsed_args)
        print(f"Creator renamed!")
    except Exception as e:
        print("Error: " + str(e))
        exit(2)