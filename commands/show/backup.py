import argparse
import os
from models import Show
from ..action import Action
from storage import storage
from utils import load_config

config = load_config()

class BackupShowAction(Action):

    def run(self):
        show_dir = config.get("SHOW_DIR")
        if not show_dir:
            raise Exception("SHOW_DIR is not set in .env")

        shows = Show.select().where(Show.filename.is_null(False))
        if not shows:
            print("No built shows found.")
            return

        print(f"Backing up {shows.count()} show file(s)...\n")
        for show in shows:
            local_path = os.path.join(show_dir, show.filename)
            s3_key = f"files/show/{show.filename}"
            storage.upload_file(local_path, s3_key)

        print(f"\nDone.")

def handle(args, **kwargs):
    parser = argparse.ArgumentParser(description="Backup show files to S3")
    parsed_args = parser.parse_args(args)
    action = BackupShowAction()
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)
