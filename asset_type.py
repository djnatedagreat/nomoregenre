import argparse
from models import AssetType, AudioAsset


# Create ArgumentParser
parser = argparse.ArgumentParser(description="Manage Asset Types")

# Add an argument
parser.add_argument("command", help="add, list, rm")
parser.add_argument("--name", dest="name", help="Asset Type", required=False)

# Parse the arguments
args = parser.parse_args()

match args.command:
    case "list":
        ats = AssetType.select()
        for at in ats:
            print (at.name)
    case "add":
        # check if already exists
        at = AssetType.get_or_none(AssetType.name == args.name)
        if at:
            print("Asset Type " +at.name+ " exists with ID " + str(at.id) + "... Exiting")
            exit()
        # create
        at = AssetType(name=args.name)
        at.save()
        print(f"Asset Type saved -- {at.name}")
    case "rm" | "remove" | "delete" | "del":
        # check if exists
        at = AssetType.get_or_none(AssetType.name == args.name)
        if not at:
            print("Asset Type " +args.name+ " does not exist... Exiting")
            exit()
        # check if there's any associated assets
        assets = AudioAsset.select().join(AssetType).where(AssetType.id==at.id)
        if (len(assets) >  0):
            print("Asset Type " +at.name+ " has associated audio assets. Removal is not supported... yet.")
            exit()
        at.delete_instance()
        print("Asset Type " +at.name+ " has been deleted.")
    case _:
        parser.print_help()
