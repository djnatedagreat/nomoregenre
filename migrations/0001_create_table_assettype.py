"""
create table assettype
date created: 2025-02-05 02:13:57.624769
"""


def upgrade(migrator):
    with migrator.create_table('assettype') as table:
        table.primary_key('id')
        table.char('name', max_length=255)


def downgrade(migrator):
    migrator.drop_table('assettype')
