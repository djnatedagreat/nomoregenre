"""
create table show
date created: 2025-02-05 02:13:57.626805
"""


def upgrade(migrator):
    with migrator.create_table('show') as table:
        table.primary_key('id')
        table.date('build_date')
        table.date('first_air_date')


def downgrade(migrator):
    migrator.drop_table('show')
