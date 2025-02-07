from playhouse.sqlite_ext import SqliteExtDatabase
from peewee_moves import DatabaseManager
from dotenv import dotenv_values
config = dotenv_values(".env")  # take environment variables from .env.

print(config["SQLITE_DB"])
manager = DatabaseManager(SqliteExtDatabase(config["SQLITE_DB"]))
#manager = DatabaseManager({'engine': 'peewee.SqliteDatabase', 'name': 'nomoregenre.db'})
#manager = DatabaseManager('sqlite:///nomoregenre.db')

manager.create('models')
