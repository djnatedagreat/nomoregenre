"""
Create tag and audioassettag tables for tagging audio assets.
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
        CREATE TABLE IF NOT EXISTS tag (
            id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE
        )
    """)
    db.execute_sql("""
        CREATE TABLE IF NOT EXISTS audioassettag (
            id INTEGER NOT NULL PRIMARY KEY,
            asset_id INTEGER NOT NULL REFERENCES audioasset(id),
            tag_id INTEGER NOT NULL REFERENCES tag(id),
            UNIQUE (asset_id, tag_id)
        )
    """)

def down():
    db.execute_sql("DROP TABLE IF EXISTS audioassettag")
    db.execute_sql("DROP TABLE IF EXISTS tag")

match args.command:
    case "up":
        up()
    case "down":
        down()
