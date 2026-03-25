import argparse
from models import AudioAsset, AssetType
from ..action import Action
from library import library
from storage import storage

class BackupAssetAction(Action):

    def __init__(self, asset_type, args):
        self.asset_type = asset_type

    def run(self):
        at = AssetType.get_or_none(AssetType.name == self.asset_type)
        if not at:
            raise Exception(f"Asset type '{self.asset_type}' not found.")

        assets = AudioAsset.select().where(AudioAsset.type == at.id)
        if not assets:
            print(f"No {self.asset_type} assets found.")
            return

        print(f"Backing up {assets.count()} {self.asset_type} file(s)...\n")
        for asset in assets:
            local_path = library.asset_path(asset)
            s3_key = f"files/{self.asset_type}/{asset.filename}"
            storage.upload_file(local_path, s3_key)

        print(f"\nDone.")

def handle(args, **kwargs):
    parser = argparse.ArgumentParser(description="Backup assets to S3")
    parsed_args = parser.parse_args(args)
    action = BackupAssetAction(kwargs.get("at"), parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)
