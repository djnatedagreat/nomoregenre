"""
create table audioclip
date created: 2025-02-05 02:13:57.626101
"""


def upgrade(migrator):
    with migrator.create_table('audioclip') as table:
        table.primary_key('id')
        table.foreign_key('AUTO', 'asset_id', on_delete=None, on_update=None, references='audioasset.id')
        table.float('start_time')
        table.float('end_time')
        table.float('fade_in_length')
        table.float('fade_out_length')


def downgrade(migrator):
    migrator.drop_table('audioclip')
