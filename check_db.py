# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect("snapshots.db")
c = conn.cursor()

# 테이블 목록
tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("=== 테이블 목록 ===")
for t in tables:
    count = c.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
    print(f"  {t[0]}: {count}건")

# 스냅샷 날짜 범위
print("\n=== 스냅샷 날짜 범위 ===")
for table in ["daily_summary", "daily_tasks", "daily_delayed", "task_changes"]:
    try:
        row = c.execute(f"SELECT MIN(snapshot_date), MAX(snapshot_date) FROM {table}").fetchone()
        print(f"  {table}: {row[0]} ~ {row[1]}")
    except:
        pass

# report_snapshots 여부
print("\n=== report_snapshots 존재 여부 ===")
has_report = c.execute("SELECT name FROM sqlite_master WHERE name='report_snapshots'").fetchone()
print(f"  {'있음' if has_report else '없음 (오늘 추가됨, 첫 실행 시 생성)'}")

conn.close()
