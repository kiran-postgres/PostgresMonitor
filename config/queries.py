qry = dict()

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
"""
}

qry['running-queries'] = {
    'heading': 'Shows Currently running Queries',
    'caption': '',
    'query': """
SELECT
    pid,
    age(query_start, clock_timestamp()),
    usename,
    query
FROM
    pg_stat_activity
WHERE
    query != '<IDLE>'
AND query NOT ilike '%pg_stat_activity%' 
order by query_start desc
"""
}
