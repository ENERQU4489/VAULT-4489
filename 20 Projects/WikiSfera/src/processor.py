import sqlite3
import gzip
import re
import os
import time

DB_PATH = "20 Projects/WikiSfera/data/wiki_graph.db"
PAGE_SQL = "20 Projects/WikiSfera/data/plwiki-latest-page.sql.gz"
LINKS_SQL = "20 Projects/WikiSfera/data/plwiki-latest-pagelinks.sql.gz"

def create_tables(conn):
    cursor = conn.cursor()
    print("🧹 Cleaning up and creating tables...")
    cursor.execute("DROP TABLE IF EXISTS pages")
    cursor.execute("DROP TABLE IF EXISTS links")
    
    # page_id, namespace, title
    cursor.execute("""
        CREATE TABLE pages (
            id INTEGER PRIMARY KEY,
            namespace INTEGER,
            title TEXT
        )
    """)
    
    # from_id, namespace (target), to_id (target)
    cursor.execute("""
        CREATE TABLE links (
            from_id INTEGER,
            to_id INTEGER
        )
    """)
    conn.commit()

def fast_iter_sql(file_path):
    """Generator wyciągający dane z plików SQL dump."""
    with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if not line.startswith("INSERT INTO"):
                continue
            
            start = line.find("VALUES ") + 7
            content = line[start:].strip()
            
            # Rekordy są oddzielone ),(
            records = content[:-1].split("),(")
            for record in records:
                record = record.strip("()")
                yield record

def process_pages(conn):
    print("📄 Processing pages (mapping IDs to titles)...")
    cursor = conn.cursor()
    count = 0
    batch = []
    
    for record in fast_iter_sql(PAGE_SQL):
        parts = record.split(',')
        try:
            p_id = int(parts[0])
            p_ns = int(parts[1])
            p_title = parts[2].strip("'")
            
            if p_ns == 0: # Tylko główne artykuły
                batch.append((p_id, p_ns, p_title))
                count += 1
                
            if len(batch) >= 10000:
                cursor.executemany("INSERT INTO pages VALUES (?, ?, ?)", batch)
                conn.commit()
                batch = []
                print(f"  > Processed {count} pages...", end="\r")
        except:
            continue
            
    if batch:
        cursor.executemany("INSERT INTO pages VALUES (?, ?, ?)", batch)
        conn.commit()
    print(f"\n✅ Total pages: {count}")

def process_links(conn):
    print("🔗 Processing pagelinks (ID-to-ID mode)...")
    cursor = conn.cursor()
    count = 0
    batch = []
    
    for record in fast_iter_sql(LINKS_SQL):
        # Format: (pl_from, pl_namespace, pl_to)
        parts = record.split(',')
        try:
            from_id = int(parts[0])
            to_ns = int(parts[1])
            to_id = int(parts[2])
            
            if to_ns == 0: # Tylko linki do artykułów
                batch.append((from_id, to_id))
                count += 1
                
            if len(batch) >= 100000:
                cursor.executemany("INSERT INTO links VALUES (?, ?)", batch)
                conn.commit()
                batch = []
                print(f"  > Processed {count} links...", end="\r")
        except:
            continue
            
    if batch:
        cursor.executemany("INSERT INTO links VALUES (?, ?)", batch)
        conn.commit()
    print(f"\n✅ Total links: {count}")

def create_indexes(conn):
    print("⚡ Creating indexes...")
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX idx_links_from ON links(from_id)")
    cursor.execute("CREATE INDEX idx_links_to ON links(to_id)")
    cursor.execute("CREATE INDEX idx_pages_id ON pages(id)")
    conn.commit()
    print("✅ Indexes ready.")

if __name__ == "__main__":
    start_time = time.time()
    conn = sqlite3.connect(DB_PATH)
    
    create_tables(conn)
    process_pages(conn)
    process_links(conn)
    create_indexes(conn)
    
    conn.close()
    end_time = time.time()
    print(f"\n🎉 ALL DONE in {int(end_time - start_time)} seconds!")
