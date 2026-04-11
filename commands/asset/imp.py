import argparse
import os
import shutil
from datetime import datetime
from models import AssetType, AudioAsset, Creator
from ..action import Action
from slugify import slugify
from utils import load_config
from mastering.provider import PROVIDERS as MASTERING_PROVIDERS
from library import library

config = load_config()


def _mutagen(path):
    from mutagen.id3 import ID3, ID3NoHeaderError
    try:
        return ID3(path)
    except ID3NoHeaderError:
        return None


def _read_tags(filepath):
    tags = _mutagen(filepath)
    if tags is None:
        raise Exception(f"No ID3 tags found in '{os.path.basename(filepath)}'.")

    title = str(tags["TIT2"]) if "TIT2" in tags else None
    artist = str(tags["TPE1"]) if "TPE1" in tags else None

    missing = [k for k, v in [("TIT2 (title)", title), ("TPE1 (artist)", artist)] if not v]
    if missing:
        raise Exception(f"Missing required ID3 tags in '{os.path.basename(filepath)}': {', '.join(missing)}")

    mtime = os.path.getmtime(filepath)
    submit_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

    # Optional: TXXX frame with description "tags", comma-separated (e.g. "early, jazz")
    nmg_tags = []
    txxx = tags.get("TXXX:tags") or tags.get("TXXX:Tags")
    if txxx:
        nmg_tags = [t.strip() for t in str(txxx.text[0]).split(",") if t.strip()]

    return {"name": title.strip(), "creator": artist.strip(), "date": submit_date, "tags": nmg_tags}



class ImportAssetAction(Action):

    def __init__(self, asset_type, args):
        self.asset_type = asset_type
        self.folder = args.folder or config.get("WATCH_DIR")
        # self.master = args.master      # disabled: no mastering provider available
        # self.provider = args.provider
        # self.reference = args.reference
        self.master = False
        self.provider = None
        self.reference = None
        self.report_only = args.report_only

    def run(self):
        if not self.folder:
            raise Exception("No folder specified and WATCH_DIR is not set in .env")
        if not os.path.isdir(self.folder):
            raise Exception(f"Folder not found: {self.folder}")

        at = AssetType.get_or_none(AssetType.name == self.asset_type)
        if not at:
            raise Exception(f"Asset type '{self.asset_type}' not found.")

        processed_dir = library.processed_dir()

        if not self.report_only:
            os.makedirs(processed_dir, exist_ok=True)

        mp3_files = [f for f in os.listdir(self.folder) if f.lower().endswith(".mp3")]
        if not mp3_files:
            print("No MP3 files found in watch folder.")
            return

        if self.report_only:
            print(f"Report only — no files will be moved or added to the database.\n")

        print(f"Found {len(mp3_files)} file(s).\n")

        for filename in mp3_files:
            source_path = os.path.join(self.folder, filename)
            print(f"Processing: {filename}")
            try:
                self._import_file(source_path, at, processed_dir)
            except Exception as e:
                print(f"  Error: {e}\n  Skipping.\n")
                continue

    def _import_file(self, source_path, at, processed_dir):
        tags = _read_tags(source_path)
        name = tags["name"]
        creator_name = tags["creator"]
        submit_date = tags["date"]
        nmg_tags = tags["tags"]

        creator = Creator.get_or_none(Creator.name == creator_name)
        if not creator:
            raise Exception(
                f"Creator '{creator_name}' not found in database. "
                f"Add them first with: python nmg.py c add \"{creator_name}\""
            )

        key = slugify(name)
        existing = AudioAsset.get_or_none(AudioAsset.key == key)
        if existing:
            raise Exception(f"Asset '{name}' already exists with ID {existing.id}.")

        output_filename = library.build_asset_filename(submit_date, creator_name, name)
        dest_path = library.asset_path(output_filename, self.asset_type)

        if self.report_only:
            print(f"  Output filename : {output_filename}")
            print(f"  Destination     : {dest_path}")
            cmd = (
                f"python nmg.py {at.name} add"
                f" --file \"{dest_path}\""
                f" --name \"{name}\""
                f" --by \"{creator_name}\""
                f" --when {submit_date}"
            )
            print(f"  mix add command : {cmd}")
            if nmg_tags:
                for t in nmg_tags:
                    print(f"  tag command     : python nmg.py {at.name} tag <asset_id> {t}")
            print()
            return

        if os.path.exists(dest_path):
            raise Exception(f"Destination file already exists: {dest_path}")

        working_path = source_path

        if self.master:
            import importlib
            master_mod = importlib.import_module("commands.asset.master")
            mastered_path = master_mod.run(working_path, self.provider, self.reference)
            working_path = mastered_path

        shutil.copy2(working_path, dest_path)
        print(f"  Copied to library: {output_filename}")

        if self.master and working_path != source_path:
            os.remove(working_path)

        import importlib
        add = importlib.import_module("commands.asset.add")
        add.handle(
            [f"--file={dest_path}", f"--name={name}", f"--by={creator_name}", f"--when={submit_date}"],
            at=at.name,
        )

        if nmg_tags:
            asset = AudioAsset.get_or_none(AudioAsset.key == slugify(name))
            if asset:
                tag_mod = importlib.import_module("commands.asset.tag")
                for t in nmg_tags:
                    tag_mod.handle([str(asset.id), t], at=at.name)

        shutil.move(source_path, os.path.join(processed_dir, os.path.basename(source_path)))
        print(f"  Source moved to: processed/{os.path.basename(source_path)}\n")


def handle(args, **kwargs):
    parser = argparse.ArgumentParser(description="Import audio assets from a watch folder")
    parser.add_argument("--folder", type=str, help="Folder to scan (overrides WATCH_DIR in .env)")
    # parser.add_argument("--master", action="store_true", help="Master each file before importing")  # disabled: no mastering provider available
    # parser.add_argument("--provider", type=str, default=config.get("MASTERING_PROVIDER", "landr"),
    #                     choices=list(MASTERING_PROVIDERS.keys()), help="Mastering provider (default: landr)")
    # parser.add_argument("--reference", type=str, help="Reference track for mastering")
    parser.add_argument("--report-only", action="store_true",
                        help="Preview what would happen without making any changes")
    parsed_args = parser.parse_args(args)
    action = ImportAssetAction(kwargs.get("at"), parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)
