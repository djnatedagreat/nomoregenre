import argparse
import os
from datetime import datetime
from ..action import Action
from storage import storage
from utils import load_config

config = load_config()

class DbBackupAction(Action):

    def run(self):
        db_path = config.get("SQLITE_DB")
        if not db_path:
            raise Exception("SQLITE_DB is not set in .env")

        filename = os.path.basename(db_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_key = f"db/{timestamp}_{filename}"
        print(f"Backing up database...\n")
        storage.upload_file(db_path, s3_key)
        print(f"\nDone.")

def handle(args, **kwargs):
    parser = argparse.ArgumentParser(description="Backup the database to S3")
    parsed_args = parser.parse_args(args)
    action = DbBackupAction()
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)
