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
from models import Show, AudioClip, ShowSegment, ShowSegmentClip
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
#name_field = CharField(null=True)
#d_min_field = IntegerField(default=0)
##d_max_field = IntegerField(default=0)
#show_field = ForeignKeyField(Show, field=Show.id, default=0, backref='segments')
#old_segment_field = ForeignKeyField(AudioClip, field=AudioClip.id, default=0, backref='segments')

def up():
    migrate(
        migrator.rename_table('showsegment', 'showsegment_old'),
        #ShowSegment.create_table()
        #migrator.create_table('showsegment', (
        #    ('id', IntegerField(primary_key=True)),
        #    ('show_id', ForeignKeyField(AudioClip, field=AudioClip.id, default=0, backref='segments')),
        #    ('name', CharField(max_length=255, null=True)),
        #    ('duration_min', IntegerField(null=False, default=0)),
        #    ('duration_max', IntegerField(null=False, default=0)),
        #)),
        
        #migrator.add_column('showsegment', 'show_id', show_fk_field),
        #migrator.add_column('showsegment', 'name', name_field),
        #migrator.add_column('showsegment', 'duration_min', d_min_field),
        #migrator.add_column('showsegment', 'duration_max', d_max_field),
        #print("Drop segment_id field manually")
        #migrator.drop_index('showsegment', 'showsegment_segment_id'),
        #migrator.drop_column('showsegment', 'segment_id'),
    )
    db.create_tables([ShowSegment,ShowSegmentClip]),

def down():
    migrate(
        migrator.drop_table('showsegmentclip'),
        migrator.drop_table('showsegment'),
        migrator.rename_table('showsegment_old', 'showsegment')
    )

match args.command:
    case "up":
        up()
    case "down":
        down()