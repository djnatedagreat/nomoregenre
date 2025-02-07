"""
create table audioasset
date created: 2025-02-05 02:13:57.625781
"""


def upgrade(migrator):
    with migrator.create_table('audioasset') as table:
        table.primary_key('id')
        table.char('key', max_length=255, unique=True)
        table.char('name', max_length=255)
        table.char('filename', max_length=255)
        table.foreign_key('AUTO', 'type_id', on_delete=None, on_update=None, references='assettype.id')
        table.foreign_key('AUTO', 'creator_id', on_delete=None, on_update=None, references='creator.id')
        table.date('submitted')


def downgrade(migrator):
    migrator.drop_table('audioasset')
