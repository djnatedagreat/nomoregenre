"""
create table basemodel
date created: 2025-02-05 02:13:57.626421
"""


def upgrade(migrator):
    with migrator.create_table('basemodel') as table:
        table.primary_key('id')


def downgrade(migrator):
    migrator.drop_table('basemodel')
