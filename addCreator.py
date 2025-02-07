import argparse
from models import Creator

# Create ArgumentParser
parser = argparse.ArgumentParser(description="Add a new DJ/Creator to the database")

# Add an argument
parser.add_argument("name", help="Creator Name")

# Parse the arguments
args = parser.parse_args()

# Use the argument

creator = Creator(name=args.name)
creator.save()

print(f"Creator saved -- {args.name}")
