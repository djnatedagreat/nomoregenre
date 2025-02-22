import argparse
import inquirer
from models import Creator, AudioAsset

parser = argparse.ArgumentParser(description="Manage DJs/Creators")

# Add an argument
parser.add_argument("command", help="add, list, rm, rename")
parser.add_argument("--name", dest="name", help="Creator Name", required=False)

# Parse the arguments
args = parser.parse_args()

def require_creator():
    creator_name = None
    if args.creator:
        return Creator.get_or_none(Creator.name == args.creator)
    else:
        creator_prompt = [
            inquirer.List("creator", message="Please choose the DJ/Creator", choices=creator_options)
        ]
        answer = inquirer.prompt(creator_prompt)
        return Creator.get_by_id(answer["creator"])

match args.command:
    case "list":
        creators = Creator.select()
        for c in creators:
            print (c.name)
    case "add":
        if not args.name:
            print("Creator name is a required argument... Exiting.")
            exit()
        # check if already exists
        creator = Creator.get_or_none(Creator.name == args.name)
        if creator:
            print("Creator " +creator.name+ " exists with ID " + str(creator.id) + "... Exiting")
            exit()
        # create
        creator = Creator(name=args.name)
        creator.save()
        print(f"Creator saved -- {args.name}")
    case "rm" | "remove" | "delete" | "del":
        # check if exists
        creator = Creator.get_or_none(Creator.name == args.name)
        if not creator:
            print("Creator " +args.name+ " does not exist... Exiting")
            exit()
        # check if there's any associated assets
        assets = AudioAsset.select().join(Creator).where(Creator.id==creator.id)
        if (len(assets) >  0):
            print("Creator " +creator.name+ " has associated audio assets. Removal is not supported... yet.")
            exit()
        creator.delete_instance()
        print("Creator " +creator.name+ " has been deleted.")
    case "rename":
        creator = Creator.get_or_none(Creator.name == args.name)
        if not creator:
            print("Creator " +args.name+ " does not exist... Exiting")
            exit()
        questions = [inquirer.Text("new_name", message="Enter a new name for this creator")]
        answers = inquirer.prompt(questions)
        creator.name = answers["new_name"]
        creator.save()
        print("Creator has been renamed to " + creator.name);
    case _:
        parser.print_help()
