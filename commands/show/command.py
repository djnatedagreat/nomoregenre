import argparse
import importlib

# kwargs ... at (for asset_type)
# 'at' will be passed to actions as an asset type filter
#  eg. at=mix 
def handle(cli_args, **kwargs):
    at_filter = kwargs.get("at", None)
    parser = argparse.ArgumentParser(description="Show actions")
    action_parsers = parser.add_subparsers(dest="action", help="Available Actions: add, list, rm, show, fill, build, publish, pub-list")
    action_parsers.add_parser("add", help="Add Show")
    action_parsers.add_parser("list", help="List Shows")
    action_parsers.add_parser("rm", help="Remove Show")
    action_parsers.add_parser("show", help="Show Show Details")
    action_parsers.add_parser("fill", help="Fill Show Segments")
    action_parsers.add_parser("build", help="Build Show")
    action_parsers.add_parser("clear", help="Remove all clips from Show")
    action_parsers.add_parser("pluck", help="Remove one clip from Show")
    action_parsers.add_parser("push", help="Push a clip to the next unfilled segment")
    action_parsers.add_parser("pop", help="Remove the last clip from a show")
    action_parsers.add_parser("backup", help="Backup show files to S3")
    action_parsers.add_parser("publish", help="Publish a built show to SoundCloud")
    action_parsers.add_parser("pub-list", help="List publications for a show")
    args, remaining_args = parser.parse_known_args(cli_args)
    action_module_map = {"pub-list": "pub_list"}
    try:
        module_action = action_module_map.get(args.action, args.action)
        module_name = f"commands.show.{module_action}"
        module = importlib.import_module(module_name)
        module.handle(remaining_args, **kwargs)
    except ModuleNotFoundError:
        print(f"Error: Not a valid action '{args.action}'.")