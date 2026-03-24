from os import path
from utils import load_config

config = load_config()

class Library:
    def __init__(self):
        self.root = path.normpath(config["LIBRARY_DIR"])

    def asset_path(self, asset_or_filename, asset_type_name=None):
        """
        Returns the full path to an asset's audio file.
        Accepts either an AudioAsset model object, or a filename string
        paired with an asset_type_name string.
        """
        if isinstance(asset_or_filename, str):
            return f"{self.root}/{asset_type_name}/{asset_or_filename}"
        return f"{self.root}/{asset_or_filename.type.name}/{asset_or_filename.filename}"

    def asset_dir(self, asset_type_name):
        """
        Returns the directory path for a given asset type name.
        For example, asset_dir('mix') returns LIBRARY_DIR/mix/
        """
        return f"{self.root}/{asset_type_name}/"

    def processed_dir(self):
        """
        Returns the directory where imported source files are moved after processing.
        Configured via PROCESSED_DIR in .env. Defaults to LIBRARY_DIR/processed.
        """
        return path.normpath(config.get("PROCESSED_DIR", path.join(self.root, "processed")))

    def build_asset_filename(self, submit_date, creator_name, asset_name):
        """
        Generates the canonical filename for an audio asset.
        Format: YYYY_MM_DD_Creator_Title.mp3
        Example: 2026_03_21_Nate_Outer_Limits_Vol_5.mp3
        """
        date_part = submit_date.replace("-", "_")
        creator_part = creator_name.replace(" ", "_")
        title_part = "_".join(w.capitalize() for w in asset_name.split())
        return f"{date_part}_{creator_part}_{title_part}.mp3"

library = Library()
