"""Transactional, repeatable upsert into a user-provisioned PostgreSQL database.
DATABASE_URL must identify a dedicated revenue_operations database.
"""
import os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.analytics import read_csv_rows,ROOT

def load():
    import psycopg
    from psycopg import sql
    with psycopg.connect(os.environ['DATABASE_URL']) as connection:
        if connection.info.dbname!='revenue_operations':raise ValueError('Use a dedicated revenue_operations database')
        connection.execute((ROOT/'sql/postgres_schema.sql').read_text())
        def upsert(table,rows,key):
            if not rows:return
            columns=list(rows[0]);updates=[c for c in columns if c!=key]
            suffix=sql.SQL('DO UPDATE SET ')+sql.SQL(',').join(sql.SQL('{}=EXCLUDED.{}').format(sql.Identifier(c),sql.Identifier(c)) for c in updates) if updates else sql.SQL('DO NOTHING')
            statement=sql.SQL('INSERT INTO {} ({}) VALUES ({}) ON CONFLICT ({}) ').format(sql.Identifier(table),sql.SQL(',').join(map(sql.Identifier,columns)),sql.SQL(',').join(sql.Placeholder() for _ in columns),sql.Identifier(key))+suffix
            with connection.cursor() as cursor:cursor.executemany(statement,[tuple(row[c] for c in columns) for row in rows])
        rows=read_csv_rows('opportunities')
        upsert('accounts',read_csv_rows('accounts'),'account_id');upsert('sales_reps',read_csv_rows('sales_reps'),'rep_id');upsert('contacts',read_csv_rows('contacts'),'contact_id')
        upsert('products',[{'product':p} for p in sorted({r['product'] for r in rows})],'product')
        upsert('opportunities',rows,'opportunity_id')
        count=connection.execute('SELECT COUNT(*) FROM opportunities').fetchone()[0]
        total=connection.execute('SELECT SUM(revenue) FROM sales').fetchone()[0]
        if count!=len(rows):raise ValueError('Unexpected database coverage; review existing records before proceeding')
        print({'loaded_opportunities':count,'won_value':str(total),'mode':'transactional upsert'})
if __name__=='__main__':load()
