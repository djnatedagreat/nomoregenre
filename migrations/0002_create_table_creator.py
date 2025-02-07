"""
create table creator
date created: 2025-02-05 02:13:57.625402
"""


def upgrade(migrator):
    with migrator.create_table('creator') as table:
        table.primary_key('id')
        table.char('name', max_length=255)


def downgrade(migrator):
    migrator.drop_table('creator')
