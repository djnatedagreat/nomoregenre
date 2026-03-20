import argparse
from models import Creator
from ..action import Action

class AddCreatorAction(Action):
    
    def run(self, args):
        name = super().require_arg(args,"name")
        # check if already exists
        creator = Creator.get_or_none(Creator.name == name)
        if creator:
            raise Exception("Creator " +creator.name+ " already exists with ID " + str(creator.id))
        # create
        new_creator = Creator(name=name)
        new_creator.save()

def handle(args):
    parser = argparse.ArgumentParser(description="Add Creator")
    parser.add_argument('name', type=str, help="Name of Creator")
    action = AddCreatorAction()
    parsed_args = parser.parse_args(args)
    try:
        action.run(parsed_args)
        print(f"Creator saved!")
    except Exception as e:
        print("Error: " + str(e))
        exit(2)