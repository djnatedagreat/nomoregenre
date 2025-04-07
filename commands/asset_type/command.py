import argparse
import importlib

def handle(args):
    #print(args)
    parser = argparse.ArgumentParser(prog="nmg.py asset_type", description="Asset Type actions")
    action_parsers = parser.add_subparsers(dest="action", help="Available Actions: add, list, rm")
    add_parser = action_parsers.add_parser("add", help="Add Asset Type")
    list_parser = action_parsers.add_parser("list", help="List Asset Types")
    rm_parser = action_parsers.add_parser("rm", help="Remove Asset Type")
    args, remaining_args = parser.parse_known_args(args)
    try:
        module_name = f"commands.asset_type.{args.action}"
        module = importlib.import_module(module_name)
        module.handle(remaining_args)
    except ModuleNotFoundError:
        print(f"Error: Not a valid action '{args.action}'.")