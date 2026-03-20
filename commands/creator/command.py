import argparse
import importlib

def handle(args, **kwargs):
    #print(args)
    parser = argparse.ArgumentParser(description="Creator actions")
    action_parsers = parser.add_subparsers(dest="action", help="Available Actions: add, list, rm, rename")
    add_parser = action_parsers.add_parser("add", help="Add Creator")
    list_parser = action_parsers.add_parser("list", help="List Creators")
    rm_parser = action_parsers.add_parser("rm", help="Remove Creator")
    rename_parser = action_parsers.add_parser("rename", help="Rename Creator")
    args, remaining_args = parser.parse_known_args(args)
    try:
        module_name = f"commands.creator.{args.action}"
        module = importlib.import_module(module_name)
        module.handle(remaining_args)
    except ModuleNotFoundError:
        print(f"Error: Not a valid action '{args.action}'.")