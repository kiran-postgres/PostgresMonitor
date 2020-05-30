qry = dict()

qry['database-sizes'] = {
    'heading': 'Database Sizes',
    'caption': 'Following table shows Database sizes on the server',
    'query': """
SELECT
    datname,
    pg_database_size(datname) / 1024 / 1024 DB_SIZE_MB
FROM
    pg_database
ORDER BY
    pg_database_size(datname)
""",
    'table-width': 'half',
    'graph-width': 'half',
    'graph-required': 'Y',
    'graph-type': 'pie-chart'
}

qry['get-indexes'] = {
    'heading': 'Indexes',
    'caption': '',
    'query': """
select
    t.relname as table_name,
    i.relname as index_name,
    string_agg(a.attname, ',') as column_name
from
    pg_class t,
    pg_class i,
    pg_index ix,
    pg_attribute a
where
    t.oid = ix.indrelid
    and i.oid = ix.indexrelid
    and a.attrelid = t.oid
    and a.attnum = ANY(ix.indkey)
    and t.relkind = 'r'
    and t.relname not like 'pg_%'
group by  
    t.relname,
    i.relname
order by
    t.relname,
    i.relname
""",
    'table-width': 'half',
    'graph-width': '',
    'graph-required': 'N',
    'graph-type': ''
}

# qry['running-queries'] = {
#     'heading': 'Shows Currently running Queries',
#     'caption': '',
#     'query': """
# SELECT
#     pid,
#     --age(query_start, clock_timestamp()),
#     usename,
#     query
# FROM
#     pg_stat_activity
# WHERE
#     query != '<IDLE>'
# AND query NOT ilike '%pg_stat_activity%'
# order by query_start desc
# """,
#     'width': 'half',
# }
#
# qry['queries-running-for-morethan-2-mins'] = {
#     'heading': 'Queries running for more than 2 minutes',
#     'caption': '',
#     'query': """
# SELECT
# --    now() - query_start AS "runtime",
#     usename,
#     datname,
#     state,
#     query
# FROM
#     pg_stat_activity
# WHERE now() - query_start > '2 minutes'::interval
# --ORDER BY runtime DESC
# """,
#     'width': 'half',
#     'graph-required': 'N',
#     'graph-type': ''
# }
#
# qry['table-sizes'] = {
#     'heading': 'Table Sizes',
#     'caption': 'Following table shows Table Sizes in this database',
#     'query': """
# SELECT
#     relname,
#     pg_size_pretty
#     ( pg_total_relation_size ( relname::regclass)) as full_size,
#     pg_size_pretty(pg_relation_size(relname::regclass)) as table_size,
#     pg_size_pretty(pg_total_relation_size(relname::regclass) - pg_relation_size(relname::regclass)) as index_size
# from
#     pg_stat_user_tables
# order by pg_total_relation_size(relname::regclass) desc
# limit 10
# """,
#     'width': 'full',
#     'graph-required': 'Y',
#     'graph-type': 'bar-chart'
# }
#

