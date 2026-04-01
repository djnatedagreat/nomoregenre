"""
Create showpublication table for tracking where shows have been published.
"""

import argparse
import sys
import os
from peewee import *
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_config
from playhouse.sqlite_ext import SqliteExtDatabase

parser = argparse.ArgumentParser(description="Manage Migration")
parser.add_argument("command", help="up, down")
args = parser.parse_args()

config = load_config()
db = SqliteExtDatabase(config["SQLITE_DB"])

def up():
    db.execute_sql("""
        CREATE TABLE IF NOT EXISTS showpublication (
            id INTEGER NOT NULL PRIMARY KEY,
            show_id INTEGER NOT NULL REFERENCES show(id),
            provider VARCHAR(255) NOT NULL,
            account VARCHAR(255),
            external_id VARCHAR(255) NOT NULL,
            url VARCHAR(255) NOT NULL,
            published_at DATETIME NOT NULL
        )
    """)

def down():
    db.execute_sql("DROP TABLE IF EXISTS showpublication")

match args.command:
    case "up":
        up()
    case "down":
        down()
