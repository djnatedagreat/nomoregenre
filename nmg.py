import argparse
import importlib

def main():
    parser = argparse.ArgumentParser(prog="nmg", description="Build Your Radio Show")
    entity_parsers = parser.add_subparsers(dest="entity", required=True)

    # Define 'asset_type' subcommand
    asset_type_parser = entity_parsers.add_parser("asset_type", aliases=['at'], help="Manage AssetTypes")
    creator_type_parser = entity_parsers.add_parser("creator", aliases=['c', 'dj'], help="Manage Creators")
    asset_parser = entity_parsers.add_parser("asset", aliases=['a'], help="Manage Audio Assets")
    show_parser = entity_parsers.add_parser("show", aliases=['s'], help="Manage Shows")
    args, remaining_args = parser.parse_known_args()

    #print(args)
    command_map = {
        "asset": "asset",
        "a": "asset",
        "asset_type": "asset_type",
        "at": "asset_type",
        "creator": "creator",
        "c": "creator",
        "dj": "creator",
        "show": "show",
    }
    # Dynamically load the module and execute the action
    try:
        module = importlib.import_module(f"commands.{command_map[args.entity]}.command")
        module.handle(remaining_args)
    except ModuleNotFoundError:
        asset_type_parser.print_help()
        #print(f"Error: No entity handler found for '{args.entity}'.")

if __name__ == "__main__":
    main()