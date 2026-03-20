import argparse
import importlib
from models import AssetType

def main():
    parser = argparse.ArgumentParser(prog="nmg", description="Build Your Radio Show")
    entity_parsers = parser.add_subparsers(dest="entity", required=True)
    creator_type_parser = entity_parsers.add_parser("creator", aliases=['c', 'dj'], help="Manage Creators")
    asset_parser = entity_parsers.add_parser("asset_type", aliases=['at'], help="Manage Asset Types")
    show_parser = entity_parsers.add_parser("show", aliases=['s'], help="Manage Shows")
    
    # map used to dynamically route aliases and commands
    command_map = {
        "asset": "asset",
        "a": "asset",
        "asset_type": "asset_type",
        "at": "asset_type",
        "creator": "creator",
        "c": "creator",
        "dj": "creator",
        "show": "show",
        "s": "show"
    }
    at_kwarg_map = {
        "asset": {"at":None},
        "a": {"at":None},
        "asset_type": {"at":None},
        "at": {"at":None},
        "creator": {"at":None},
        "c": {"at":None},
        "dj": {"at":None},
        "show": {"at":None},
        "s": {"at":None},
    }
    # dynamic asset commands based on asset_types
    at_aliases = ['a']
    ats = AssetType.select()
    for at in ats:
        # add a command alias
        at_aliases.append(at.name)
        # dynamically append to command map
        command_map[at.name] = "asset"
        # add to at_map to build kwargs
        at_kwarg_map[at.name] = {"at":at.name}
   
    asset_type_parser = entity_parsers.add_parser("asset", aliases=at_aliases, help="Manage Audio Assets")
    args, remaining_args = parser.parse_known_args()

    # Dynamically load the module and execute the action
    try:
        module = importlib.import_module(f"commands.{command_map[args.entity]}.command")
        module.handle(remaining_args, **(at_kwarg_map[args.entity]))
    except ModuleNotFoundError:
        asset_type_parser.print_help()
        #print(f"Error: No entity handler found for '{args.entity}'.")

if __name__ == "__main__":
    main()