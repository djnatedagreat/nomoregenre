import argparse
import importlib

def handle(cli_args, **kwargs):
    parser = argparse.ArgumentParser(description="Admin actions")
    action_parsers = parser.add_subparsers(dest="action")
    action_parsers.add_parser("db-backup", help="Backup the database to S3")
    args, remaining_args = parser.parse_known_args(cli_args)
    action_module_map = {"db-backup": "db_backup"}
    try:
        module_action = action_module_map.get(args.action, args.action)
        module_name = f"commands.admin.{module_action}"
        module = importlib.import_module(module_name)
        module.handle(remaining_args, **kwargs)
    except ModuleNotFoundError:
        print(f"Error: Not a valid action '{args.action}'.")
