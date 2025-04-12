import argparse
from models import AudioAsset, AssetType, Creator, AudioClip, ShowSegmentClip
from peewee import fn, JOIN
from tabulate import tabulate

class ListAssetAction:

    def __init__(self, asset_type, creator_name):
        self.asset_type = asset_type  # instance attribute
        self.creator_name = creator_name
        
    def run(self):
        assets = (AudioAsset.select(
                    AudioAsset,
                    fn.COUNT(ShowSegmentClip.id).alias('clip_use_count')
                 )
                 .join(Creator)
                 .join(AudioClip, JOIN.LEFT_OUTER, on=(AudioAsset.id == AudioClip.asset_id))
                 .join(ShowSegmentClip, JOIN.LEFT_OUTER, on=(AudioClip.id == ShowSegmentClip.clip_id))
                 .group_by(AudioAsset.id)
                 .order_by(Creator.name)
                 )
        if (self.asset_type):
            type = AssetType.get_or_none(AssetType.name == self.asset_type)
            assets = assets.where(AudioAsset.type == type.id)
        if (self.creator_name):
            creator = Creator.get_or_none(fn.LOWER(Creator.name) == fn.LOWER(self.creator_name))
            if not creator:
                raise Exception("Invalid creator specified.")
            assets = assets.where(AudioAsset.creator == creator.id)
        
        headers = ['ID','Type', 'Created By', 'Asset Name', 'Use Count']
        data = []
        for a in assets:
            data.append([a.id, a.type.name, a.creator.name, a.name, a.clip_use_count])
            #print(f"({a.id}) {a.type.name}\t\t{a.creator.name}\t{a.name}\t\t{a.clip_use_count}")
        
        print(tabulate(data, headers=headers, tablefmt="pipe"))
            #print ("("+str(a.id)+") "+a.type.name + "\t" + a.creator.name + "\t" + a.name)

# kwargs "at" for asset_type filter eg. mix, id, etc. assumes asset type name 
def handle(args, **kwargs):

    parser = argparse.ArgumentParser(description="List Assets")
    parser.add_argument('--by', dest="by", type=str, help="Name of Creator")
    parsed_args = parser.parse_args(args)
    action = ListAssetAction(kwargs.get("at"), parsed_args.by)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)