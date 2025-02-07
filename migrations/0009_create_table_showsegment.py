"""
create table showsegment
date created: 2025-02-05 02:13:57.628018
"""


def upgrade(migrator):
    with migrator.create_table('showsegment') as table:
        table.primary_key('id')
        table.foreign_key('AUTO', 'show_id', on_delete=None, on_update=None, references='show.id')
        table.foreign_key('AUTO', 'segment_id', on_delete=None, on_update=None, references='audioclip.id')


def downgrade(migrator):
    migrator.drop_table('showsegment')
