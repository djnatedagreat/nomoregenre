import argparse
import importlib

# kwargs ... at (for asset_type)
# 'at' will be passed to actions as an asset type filter
#  eg. at=mix 
def handle(cli_args, **kwargs):
    at_filter = kwargs.get("at", None)
    #print(at_filter)
    parser = argparse.ArgumentParser(description="Asset actions")
    action_parsers = parser.add_subparsers(dest="action", help="Available Actions: add, list, rm")
    action_parsers.add_parser("add", help="Add Asset")
    action_parsers.add_parser("list", help="List Assets")
    action_parsers.add_parser("rm", help="Remove Asset")
    action_parsers.add_parser("preview", help="Preview Asset")
    action_parsers.add_parser("show", help="Show Asset Details")
    action_parsers.add_parser("clip", help="Create Asset Clip")
    action_parsers.add_parser("trim", help="Trim Asset Clip") # remove from beginning or end but no other changes
    action_parsers.add_parser("fade", help="Fade Asset Clip")
    action_parsers.add_parser("tag", help="Tag an Asset")
    action_parsers.add_parser("backup", help="Backup assets to S3")
    args, remaining_args = parser.parse_known_args(cli_args)
    try:
        module_action = action_module_map.get(args.action, args.action)
        module_name = f"commands.asset.{module_action}"
        module = importlib.import_module(module_name)
        module.handle(remaining_args, **kwargs)
    except ModuleNotFoundError:
        print(f"Error: Not a valid action '{args.action}'.")