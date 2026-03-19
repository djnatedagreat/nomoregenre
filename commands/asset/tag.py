import argparse
from models import AudioAsset, Tag, AudioAssetTag
from ..action import Action


class TagAssetAction(Action):

    def __init__(self, asset_id, tag_name, remove):
        self.asset_id = asset_id
        self.tag_name = tag_name.lower()
        self.remove = remove

    def run(self):
        asset = AudioAsset.get_by_id(self.asset_id)

        if self.remove:
            tag = Tag.get_or_none(Tag.name == self.tag_name)
            if not tag:
                raise Exception(f"Tag '{self.tag_name}' does not exist.")
            deleted = (AudioAssetTag
                       .delete()
                       .where(AudioAssetTag.asset == asset, AudioAssetTag.tag == tag)
                       .execute())
            if deleted:
                print(f"Removed tag '{self.tag_name}' from '{asset.name}'.")
            else:
                raise Exception(f"Asset '{asset.name}' does not have tag '{self.tag_name}'.")
        else:
            tag, _ = Tag.get_or_create(name=self.tag_name)
            _, created = AudioAssetTag.get_or_create(asset=asset, tag=tag)
            if created:
                print(f"Tagged '{asset.name}' with '{self.tag_name}'.")
            else:
                print(f"'{asset.name}' already has tag '{self.tag_name}'.")


def handle(args, **kwargs):
    parser = argparse.ArgumentParser(description="Tag an audio asset")
    parser.add_argument('asset_id', help="Asset ID")
    parser.add_argument('tag', help="Tag name")
    parser.add_argument('--remove', action='store_true', help="Remove the tag from the asset")
    parsed_args = parser.parse_args(args)
    action = TagAssetAction(parsed_args.asset_id, parsed_args.tag, parsed_args.remove)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)
