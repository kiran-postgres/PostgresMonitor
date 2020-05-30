qry = dict()

qry['Connections'] = {
    'heading': 'Connections',
    'caption': 'Connections',
    'query': """ select client_addr, usename, datname, count(*) from pg_stat_activity group by 1,2,3 order by 4 desc 
""",
    'table-width': 'half',
    'graph-width': 'half',
    'graph-required': 'N',
    'graph-type': '',
    'category': 'performance'
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
    'graph-width': 'half',
    'graph-required': 'N',
    'graph-type': ''
}

qry['running-queries'] = {
    'heading': 'Shows Currently running Queries',
    'caption': '',
    'query': """
SELECT
    pid,
    --age(query_start, clock_timestamp()),
    usename,
    query
FROM
    pg_stat_activity
WHERE
    query != '<IDLE>'
AND query NOT ilike '%pg_stat_activity%' 
order by query_start desc
""",
    'table-width': 'full',
    'graph-width': 'half',
    'graph-required': 'N',
    'graph-type': ''
}

qry['queries-running-for-morethan-2-mins'] = {
    'heading': 'Queries running for more than 2 minutes',
    'caption': '',
    'query': """
SELECT
--    now() - query_start AS "runtime",
    usename,
    datname,
    state,
    query
FROM
    pg_stat_activity
WHERE now() - query_start > '2 minutes'::interval 
--ORDER BY runtime DESC
""",
    'table-width': 'full',
    'graph-width': 'half',
    'graph-required': 'N',
    'graph-type': ''
}


qry['table-sizes'] = {
    'heading': 'Table Sizes',
    'caption': 'Following table shows Table Sizes in this database',
    'query': """
SELECT
    relname,
    pg_total_relation_size ( relname::regclass) / 1024 as full_size_kb, 
    pg_relation_size(relname::regclass) / 1024 as table_size_kb, 
    pg_total_relation_size(relname::regclass) - pg_relation_size(relname::regclass) / 1024 as index_size_kb 
from 
    pg_stat_user_tables 
order by pg_total_relation_size(relname::regclass) desc 
limit 10
""",
    'table-width': 'half',
    'graph-width': 'half',
    'graph-required': 'Y',
    'graph-type': 'bar-graph'
}

qry['database-sizes'] = {
    'heading': 'Database Sizes',
    'caption': 'Following table Database sizes',
    'query': """
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname))
FROM
    pg_database
ORDER BY
    pg_database_size(datname)
""",
    'table-width': 'half',
    'graph-width': 'half',
    'graph-required': 'Y',
    'graph-type': 'bar-chart'
}


qry['Index Bloating'] = {
    'heading': 'Index Bloating',
    'caption': 'Index Bloating',
    'query': """
SELECT
  nspname,
  relname,
  round(100 * pg_relation_size(indexrelid) / pg_relation_size(indrelid)) / 100 AS index_ratio,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
  pg_size_pretty(pg_relation_size(indrelid)) AS table_size
FROM pg_index I
LEFT JOIN pg_class C ON (C.oid = I.indexrelid)
LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
WHERE nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast') AND
  C.relkind='i' AND
  pg_relation_size(indrelid) > 0
""",
    'table-width': 'half',
    'graph-width': 'half',
    'graph-required': 'N',
    'graph-type': ''
}


qry['Monitor AutoVaccum'] = {
    'heading': 'AutoVaccum',
    'caption': 'AutoVaccum',
    'query': """
SELECT schemaname,relname,last_autovacuum,last_autoanalyze FROM pg_stat_all_tables
""",
    'table-width': 'half',
    'graph-width': 'half',
    'graph-required': 'N',
    'graph-type': ''
}

qry['Candidates For AutoVaccum'] = {
    'heading': 'AutoVaccum',
    'caption': 'AutoVaccum',
    'query': """
SELECT *,
  n_dead_tup > av_threshold AS "av_needed",
  CASE WHEN reltuples > 0
       THEN round(100.0 * n_dead_tup / (reltuples))
       ELSE 0
  END AS pct_dead
FROM (SELECT
      N.nspname,
      C.relname,
      pg_stat_get_tuples_inserted(C.oid) AS n_tup_ins,
      pg_stat_get_tuples_updated(C.oid) AS n_tup_upd,
      pg_stat_get_tuples_deleted(C.oid) AS n_tup_del,
      pg_stat_get_live_tuples(C.oid) AS n_live_tup,
      pg_stat_get_dead_tuples(C.oid) AS n_dead_tup,
      C.reltuples AS reltuples,
      round(current_setting('autovacuum_vacuum_threshold')::integer
        + current_setting('autovacuum_vacuum_scale_factor')::numeric * C.reltuples) AS av_threshold,
      date_trunc('minute', greatest(pg_stat_get_last_vacuum_time(C.oid),
                                    pg_stat_get_last_autovacuum_time(C.oid))) AS last_vacuum,
      date_trunc('minute', greatest(pg_stat_get_last_analyze_time(C.oid), pg_stat_get_last_analyze_time(C.oid))) AS last_analyze
FROM pg_class C
LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
WHERE C.relkind IN ('r', 't')
AND N.nspname NOT IN ('pg_catalog', 'information_schema') AND
    N.nspname !~ '^pg_toast'
    ) AS av
ORDER BY av_needed DESC,n_dead_tup DESC
""",
    'table-width': 'half',
    'graph-width': 'half',
    'graph-required': 'N',
    'graph-type': ''
}

qry['Killing Active Sessions'] = {
    'heading': 'AutoVaccum',
    'caption': 'AutoVaccum',
    'query': """
SELECT pg_cancel_backend(procpid);
""",
    'table-width': 'half',
    'graph-width': 'half',
    'graph-required': 'N',
    'graph-type': ''
}
qry['Time consuming Queries'] = {
    'heading': 'Time consuming Queries',
    'caption': 'Time consuming Queries',
    'query': """
SELECT substring(query, 1, 100) AS short_query, round(total_time::numeric, 2) AS total_time, calls, rows, round(total_time::numeric / calls, 2) AS avg_time, round((100 * total_time / sum(total_time::numeric) OVER ())::numeric, 2) AS percentage_cpu FROM pg_stat_statements ORDER BY avg_time DESC LIMIT 20
""",
    'table-width': 'half',
    'graph-width': 'half',
    'graph-required': 'N',
    'graph-type': ''
}

qry['CPU Intensive'] = {
    'heading': 'CPU',
    'caption': 'CPU',
    'query': """
SELECT substring(query, 1, 50) AS short_query, round(total_time::numeric, 2) AS total_time, calls, rows, round(total_time::numeric / calls, 2) AS avg_time, round((100 * total_time / sum(total_time::numeric) OVER ())::numeric, 2) AS percentage_cpu FROM pg_stat_statements ORDER BY total_time DESC LIMIT 20
""",
    'table-width': 'half',
    'graph-width': 'half',
    'graph-required': 'N',
    'graph-type': ''
}

qry['Connections'] = {
    'heading': 'Connections',
    'caption': 'Connections',
    'query': """
select client_addr, usename, datname, count(*) from pg_stat_activity group by 1,2,3 order by 4 desc
""",
    'table-width': 'half',
    'graph-width': 'half',
    'graph-required': 'N',
    'graph-type': ''
}