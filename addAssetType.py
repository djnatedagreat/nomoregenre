import argparse
from models import AssetType

# Create ArgumentParser
parser = argparse.ArgumentParser(description="Add a new AssetType to the database")

# Add an argument
parser.add_argument("type", help="Asset Type")

# Parse the arguments
args = parser.parse_args()

# Use the argument

assettype = AssetType(name=args.type)
assettype.save()

print(f"Asset type saved -- {args.type}")
