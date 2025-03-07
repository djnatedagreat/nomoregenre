"""
Moving towards custom database migrations using the playhouse.migrate library.
peewee-moves seems under supported and documentation wasn't very helpful when
it came to doing some necessary things.
"""

import argparse
import sys
import os
from peewee import * 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Show
from utils import load_config
from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.migrate import SqliteMigrator, migrate

# Create ArgumentParser
parser = argparse.ArgumentParser(description="Manage Migration")
parser.add_argument("command", help="up, down")
# Parse the arguments
args = parser.parse_args()

# SQLite example:
config = load_config()  # take environment variables from .env.
db = SqliteExtDatabase(config["SQLITE_DB"])
migrator = SqliteMigrator(db)

#show_fk_field = ForeignKeyField(Show, field=Show.id, default=0, backref='segments')
duration_field = IntegerField(default=0)
filename_field = CharField(null=True)

def up():
    migrate(
        migrator.add_column('show', 'duration', duration_field),
        migrator.add_column('show', 'filename', filename_field),
        migrator.drop_not_null('show', 'build_date')
    )

def down():
    migrate(
        migrator.drop_column('show', 'duration'),
        migrator.drop_column('show', 'filename'),
        migrator.add_not_null('show','build_date')
    )

match args.command:
    case "up":
        up()
    case "down":
        down()