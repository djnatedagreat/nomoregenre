import argparse
import importlib
from models import AssetType

def main():
    parser = argparse.ArgumentParser(prog="nmg", description="Build Your Radio Show")
    entity_parsers = parser.add_subparsers(dest="entity", required=True)
    creator_type_parser = entity_parsers.add_parser("creator", aliases=['c', 'dj'], help="Manage Creators")
    asset_parser = entity_parsers.add_parser("asset_type", aliases=['at'], help="Manage Asset Types")
    show_parser = entity_parsers.add_parser(
        "show", aliases=['s'],
        help="Manage Shows",
        description="Build and manage radio shows.",
        epilog="""\
commands:
  add <air_date> --program <file>    Create a new show from a program JSON
  list                               List all shows
  show <id>                          Display show details and segment contents
  fill <id> [--candidates]           Fill segments interactively; --candidates lists clips
  push <show_id> <clip_id>           Push a clip to the next unfilled segment
  pop <show_id>                      Remove the last clip from a show
  build <id>                         Compile show segments into a final MP3
  clear <id>                         Remove all clips from a show
  pluck <id> [--asset <asset_id>]    Remove one clip from a show
  backup                             Backup show MP3s to S3
  publish <id> [--title] [--public]  Publish a built show to SoundCloud
  pub-list [show_id]                 List publications for a show (or all shows)
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    entity_parsers.add_parser("admin", help="Admin commands")
    
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
        "s": "show",
        "admin": "admin",
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
        "admin": {"at":None},
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
   
    asset_type_parser = entity_parsers.add_parser(
        "asset", aliases=at_aliases,
        help="Manage Audio Assets",
        description="Manage audio assets. Use an asset type name (e.g. 'mix') as an alias for 'asset'.",
        epilog="""\
commands:
  add --file <file> [--by <creator>] [--name <name>] [--when <date>]
                                     Add a new audio asset
  list [--by <creator>]              List assets (optionally filtered by creator)
  show <id>                          Show asset details
  preview <id>                       Preview an asset
  clip <id> <start> <end>            Create a clip (hh:mm:ss.000 format)
  trim <id> [--offset <secs>]        Trim a clip from the start
  fade <id> <in|out> <duration> --clip <clip_id>
                                     Apply a fade to a clip
  tag <id> <tag> [--remove]          Add or remove a tag on an asset
  import [--folder <dir>] [--report-only]
                                     Import assets from a watch folder
  backup                             Backup assets to S3
  rm <id>                            Remove an asset
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
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