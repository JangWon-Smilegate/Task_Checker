# -*- coding: utf-8 -*-
"""
LAM 업무 스냅샷 수집기
매일 실행하여 부서별 업무 현황을 SQLite에 저장하고,
리포트 seq 매핑 테이블을 점검합니다.
"""
import json
import re
import ssl
import sqlite3
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

# Windows cp949 환경에서 UTF-8 출력
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://lam-web.sgr.com:8081/WORKDASHBOARDAPI"
DB_PATH = "snapshots.db"
CLAUDE_MD_PATH = Path(__file__).parent.parent / "CLAUDE.md"  # D:\Git\CLAUDE.md

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def _get(path: str) -> dict:
    req = urllib.request.Request(f"{BASE}{path}")
    with urllib.request.urlopen(req, context=ctx) as r:
        return json.loads(r.read())


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 일일 부서별 요약 스냅샷
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date TEXT NOT NULL,
            department TEXT NOT NULL,
            total INTEGER DEFAULT 0,
            in_progress INTEGER DEFAULT 0,
            incomplete INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            delayed INTEGER DEFAULT 0,
            d_day INTEGER DEFAULT 0,
            on_hold INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(snapshot_date, department)
        )
    """)

    # 담당자별 과부하 스냅샷
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_member (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date TEXT NOT NULL,
            department TEXT NOT NULL,
            assignee TEXT NOT NULL,
            total INTEGER DEFAULT 0,
            in_progress INTEGER DEFAULT 0,
            incomplete INTEGER DEFAULT 0,
            delayed INTEGER DEFAULT 0,
            d_day INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(snapshot_date, department, assignee)
        )
    """)

    # 지연 업무 상세 기록
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_delayed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date TEXT NOT NULL,
            task_id TEXT NOT NULL,
            title TEXT,
            assignee TEXT,
            department TEXT,
            status TEXT,
            start_date TEXT,
            end_date TEXT,
            delay_days INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(snapshot_date, task_id)
        )
    """)

    # 태스크 단위 일일 스냅샷 (전체 태스크 상태 기록)
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date TEXT NOT NULL,
            task_id TEXT NOT NULL,
            title TEXT,
            assignee TEXT,
            department TEXT,
            status TEXT,
            start_date TEXT,
            end_date TEXT,
            duration TEXT,
            task_type TEXT,
            priority TEXT,
            work_step TEXT,
            flow_json TEXT,
            contents_category TEXT,
            parent_key TEXT,
            delay_days INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(snapshot_date, task_id)
        )
    """)

    # 태스크 변경 감지 로그
    c.execute("""
        CREATE TABLE IF NOT EXISTS task_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_date TEXT NOT NULL,
            task_id TEXT NOT NULL,
            title TEXT,
            change_type TEXT,
            field_name TEXT,
            old_value TEXT,
            new_value TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 리포트 스냅샷 (seq 매핑 변경 추적)
    c.execute("""
        CREATE TABLE IF NOT EXISTS report_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date TEXT NOT NULL,
            seq INTEGER NOT NULL,
            name TEXT,
            desc TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(snapshot_date, seq)
        )
    """)

    # 완료 전환 기록 (당일 새로 완료된 태스크)
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_completed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_date TEXT NOT NULL,
            task_id TEXT NOT NULL,
            title TEXT,
            assignee TEXT,
            department TEXT,
            prev_status TEXT,
            start_date TEXT,
            end_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(detected_date, task_id)
        )
    """)

    conn.commit()
    return conn


# ─────────────────────────────────────────────
# 리포트 수집 & CLAUDE.md seq 매핑 갱신
# ─────────────────────────────────────────────

# CLAUDE.md에 표시할 리포트 키워드 (우선순위 순)
REPORT_KEYWORDS = ["M29", "M28", "M27", "지연", "업무 현황", "타겟", "목표 작업 리스트", "주간 리포트"]
MAX_REPORT_ROWS = 20


def collect_reports(conn: sqlite3.Connection, group_id: int = 1) -> list:
    """리포트 목록을 수집하고 DB에 저장. 변경 시 CLAUDE.md 갱신."""
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    data = _get(f"/reports?groupId={group_id}")
    reports = data.get("data", [])

    c = conn.cursor()

    # 오늘 데이터 저장
    for r in reports:
        c.execute("""
            INSERT OR REPLACE INTO report_snapshots (snapshot_date, seq, name, desc)
            VALUES (?, ?, ?, ?)
        """, (today, r["seq"], r["name"], r.get("desc", "")))
    conn.commit()

    # 어제 데이터와 비교
    prev = {
        row[0]: {"name": row[1], "desc": row[2]}
        for row in c.execute(
            "SELECT seq, name, desc FROM report_snapshots WHERE snapshot_date = ?",
            (yesterday,)
        ).fetchall()
    }

    changes = []
    current_seqs = {r["seq"] for r in reports}
    prev_seqs = set(prev.keys())

    for r in reports:
        if r["seq"] not in prev_seqs:
            changes.append(f"  ✨ 신규: [seq:{r['seq']}] {r['name']}")
        elif prev[r["seq"]]["name"] != r["name"]:
            changes.append(f"  ✏️  이름변경: [seq:{r['seq']}] {prev[r['seq']]['name']} → {r['name']}")

    for seq in prev_seqs - current_seqs:
        changes.append(f"  🗑️  삭제: [seq:{seq}] {prev[seq]['name']}")

    if changes:
        print(f"  리포트 변경 감지 ({len(changes)}건):")
        for msg in changes:
            print(msg)
        _update_claude_md_reports(reports)
    else:
        print(f"  리포트 변경 없음 (총 {len(reports)}개)")

    return reports


def _update_claude_md_reports(reports: list):
    """CLAUDE.md의 주요 리포트 seq 매핑 테이블을 갱신."""
    if not CLAUDE_MD_PATH.exists():
        print(f"  ⚠️  CLAUDE.md 없음: {CLAUDE_MD_PATH}")
        return

    # 주요 리포트 선별 & 정렬
    important = [
        r for r in reports
        if any(kw in r.get("name", "") for kw in REPORT_KEYWORDS)
    ]
    important = sorted(important, key=lambda x: x["seq"], reverse=True)[:MAX_REPORT_ROWS]

    # 테이블 생성
    rows = ["| seq | 리포트명 | 설명 |", "|---|---|---|"]
    for r in important:
        name = r["name"].replace("|", "｜")
        desc = (r.get("desc", "") or "").replace("|", "｜").strip()
        rows.append(f"| {r['seq']} | {name} | {desc} |")
    new_table = "\n".join(rows)

    content = CLAUDE_MD_PATH.read_text(encoding="utf-8")

    # 패턴: "**주요 리포트 seq 매핑" 으로 시작하는 헤더 + 이어지는 테이블 행 교체
    # [^\n]* 로 헤더 끝 부분을 유연하게 매칭 (특수문자·이모지 포함 대응)
    pattern = r'(\*\*주요 리포트 seq 매핑[^\n]*\n)((?:\|[^\n]*\n)+)'
    replacement = f'**주요 리포트 seq 매핑 (자주 사용):**\n{new_table}\n'
    new_content, n = re.subn(pattern, replacement, content)

    if n == 0:
        print(f"  ⚠️  CLAUDE.md 패턴 매칭 실패 — 수동 확인 필요")
    elif new_content != content:
        CLAUDE_MD_PATH.write_text(new_content, encoding="utf-8")
        print(f"  ✅ CLAUDE.md seq 매핑 테이블 업데이트 완료 ({len(important)}개 리포트)")
    else:
        print(f"  ✅ CLAUDE.md seq 매핑 테이블 이미 최신 ({len(important)}개 리포트, 변경 없음)")


def collect_snapshot(group_id: int = 1):
    today = date.today()
    today_str = today.isoformat()

    print(f"  [{datetime.now().strftime('%H:%M:%S')}] 수집 시작: {today_str}")

    # API에서 전체 업무 조회
    data = _get(f"/tasks?groupId={group_id}")
    tasks = data.get("data", [])
    print(f"  전체 업무: {len(tasks)}건")

    # 활성 업무만 필터: 제외 상태를 명시 → 새 상태 자동 포함
    # Backlog(저장소), Pending(외부대기), 완료(종결) 제외
    EXCLUDE_STATUSES = {"완료", "Backlog", "Pending"}
    active_tasks = [t for t in tasks if (t.get("status") or "") not in EXCLUDE_STATUSES]

    # 완료 태스크 맵 (전환 감지용)
    all_tasks_map = {str(t.get("id", "")): t for t in tasks}

    # 부서별 집계
    dept_stats = {}
    member_stats = {}

    for t in active_tasks:
        dept = t.get("department", "미정")
        # 부서를 "실" 단위로 축약 (예: "로스트아크모바일스튜디오 기획실 컨텐츠기획팀 시스템파트" → "기획실")
        dept_short = _shorten_dept(dept)
        status = t.get("status", "")
        assignee = t.get("assignee", "미배정")
        end_date = (t.get("end") or "")[:10]

        # 지연/D-day 판정
        is_delayed = False
        is_dday = False
        delay_days = 0
        if end_date and end_date < today_str and status in ("진행중", "진행 중", "미완료"):
            is_delayed = True
            delay_days = (today - date.fromisoformat(end_date)).days
        elif end_date == today_str and status in ("진행중", "진행 중", "미완료"):
            is_dday = True

        # 부서별 집계
        if dept_short not in dept_stats:
            dept_stats[dept_short] = {
                "total": 0, "in_progress": 0, "incomplete": 0,
                "completed": 0, "delayed": 0, "d_day": 0, "on_hold": 0
            }
        s = dept_stats[dept_short]
        s["total"] += 1
        if status in ("진행중", "진행 중"):
            s["in_progress"] += 1
        elif status == "미완료":
            s["incomplete"] += 1
        elif status == "보류":
            s["on_hold"] += 1
        if is_delayed:
            s["delayed"] += 1
        if is_dday:
            s["d_day"] += 1

        # 담당자별 집계 (쉼표로 복수 담당자 처리)
        for person in (assignee or "미배정").split(","):
            person = person.strip()
            if not person:
                continue
            key = (dept_short, person)
            if key not in member_stats:
                member_stats[key] = {
                    "total": 0, "in_progress": 0, "incomplete": 0,
                    "delayed": 0, "d_day": 0
                }
            m = member_stats[key]
            m["total"] += 1
            if status in ("진행중", "진행 중"):
                m["in_progress"] += 1
            elif status == "미완료":
                m["incomplete"] += 1
            if is_delayed:
                m["delayed"] += 1
            if is_dday:
                m["d_day"] += 1

    # DB 저장
    conn = init_db()
    c = conn.cursor()

    # 부서별 요약 저장
    for dept, s in dept_stats.items():
        c.execute("""
            INSERT OR REPLACE INTO daily_summary
            (snapshot_date, department, total, in_progress, incomplete, completed, delayed, d_day, on_hold)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (today_str, dept, s["total"], s["in_progress"], s["incomplete"],
              s["completed"], s["delayed"], s["d_day"], s["on_hold"]))

    # 담당자별 저장
    for (dept, person), m in member_stats.items():
        c.execute("""
            INSERT OR REPLACE INTO daily_member
            (snapshot_date, department, assignee, total, in_progress, incomplete, delayed, d_day)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (today_str, dept, person, m["total"], m["in_progress"],
              m["incomplete"], m["delayed"], m["d_day"]))

    # 지연 업무 상세 저장
    for t in active_tasks:
        end_date = (t.get("end") or "")[:10]
        if end_date and end_date < today_str and t.get("status") in ("진행중", "진행 중", "미완료"):
            delay_days = (today - date.fromisoformat(end_date)).days
            c.execute("""
                INSERT OR REPLACE INTO daily_delayed
                (snapshot_date, task_id, title, assignee, department, status, start_date, end_date, delay_days)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (today_str, str(t.get("id", "")), t.get("title", ""),
                  t.get("assignee", ""), _shorten_dept(t.get("department", "")),
                  t.get("status", ""), (t.get("start") or "")[:10], end_date, delay_days))

    # 태스크 단위 저장 + 변경 감지
    # 어제 스냅샷 로드 (변경 비교용)
    yesterday_tasks = {}
    yesterday_rows = c.execute(
        "SELECT task_id, status, end_date, assignee FROM daily_tasks WHERE snapshot_date = ?",
        ((today - timedelta(days=1)).isoformat(),)
    ).fetchall()
    for row in yesterday_rows:
        yesterday_tasks[row[0]] = {"status": row[1], "end_date": row[2], "assignee": row[3]}

    changes_count = 0
    for t in active_tasks:
        tid = str(t.get("id", ""))
        end_date = (t.get("end") or "")[:10]
        status = t.get("status", "")
        assignee = t.get("assignee") or "미배정"
        delay_days = 0
        if end_date and end_date < today_str and status in ("진행중", "진행 중", "미완료"):
            delay_days = (today - date.fromisoformat(end_date)).days

        # flow를 JSON 문자열로 저장
        flow = t.get("flow")
        flow_json = json.dumps(flow, ensure_ascii=False) if flow else None

        c.execute("""
            INSERT OR REPLACE INTO daily_tasks
            (snapshot_date, task_id, title, assignee, department, status,
             start_date, end_date, duration, task_type, priority,
             work_step, flow_json, contents_category, parent_key, delay_days)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (today_str, tid, t.get("title", ""), assignee,
              _shorten_dept(t.get("department", "")), status,
              (t.get("start") or "")[:10], end_date,
              t.get("duration", ""), t.get("taskType", ""),
              t.get("priority", ""), t.get("workStep"),
              flow_json, t.get("contentsCategory", ""),
              t.get("parentKey"), delay_days))

        # 변경 감지 (어제 대비)
        if tid in yesterday_tasks:
            prev = yesterday_tasks[tid]
            if prev["status"] != status:
                c.execute("""INSERT INTO task_changes
                    (detected_date, task_id, title, change_type, field_name, old_value, new_value)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (today_str, tid, t.get("title", ""), "status_change", "status", prev["status"], status))
                changes_count += 1
            if prev["end_date"] != end_date and prev["end_date"] and end_date:
                c.execute("""INSERT INTO task_changes
                    (detected_date, task_id, title, change_type, field_name, old_value, new_value)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (today_str, tid, t.get("title", ""), "deadline_change", "end_date", prev["end_date"], end_date))
                changes_count += 1
            if prev["assignee"] != assignee:
                c.execute("""INSERT INTO task_changes
                    (detected_date, task_id, title, change_type, field_name, old_value, new_value)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (today_str, tid, t.get("title", ""), "assignee_change", "assignee", prev["assignee"], assignee))
                changes_count += 1

    # ── 완료 전환 감지 ──────────────────────────────────────
    # 어제 활성 태스크 중 오늘 "완료" 상태로 바뀐 것을 기록
    completed_count = 0
    for tid, prev in yesterday_tasks.items():
        current = all_tasks_map.get(tid)
        if current is None:
            continue
        current_status = current.get("status", "")
        if current_status == "완료" and prev["status"] != "완료":
            # task_changes에 완료 전환 기록
            c.execute("""INSERT OR IGNORE INTO task_changes
                (detected_date, task_id, title, change_type, field_name, old_value, new_value)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (today_str, tid, current.get("title", ""), "status_change",
                  "status", prev["status"], "완료"))
            # daily_completed에 저장
            c.execute("""
                INSERT OR IGNORE INTO daily_completed
                (detected_date, task_id, title, assignee, department, prev_status, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (today_str, tid, current.get("title", ""),
                  current.get("assignee", "미배정"),
                  _shorten_dept(current.get("department", "")),
                  prev["status"],
                  (current.get("start") or "")[:10],
                  (current.get("end") or "")[:10]))
            completed_count += 1

    conn.commit()

    # 결과 출력
    total_all = sum(s["total"] for s in dept_stats.values())
    total_delayed = sum(s["delayed"] for s in dept_stats.values())
    total_dday = sum(s["d_day"] for s in dept_stats.values())
    print(f"  활성 업무: {total_all}건 | 지연: {total_delayed}건 | D-day: {total_dday}건")
    print(f"  태스크 저장: {len(active_tasks)}건 | 변경 감지: {changes_count}건 | 신규 완료: {completed_count}건")
    print(f"  부서: {len(dept_stats)}개 | 담당자: {len(member_stats)}명")

    return conn


def _shorten_dept(dept: str) -> str:
    """부서명을 '실/팀' 단위로 축약"""
    if not dept:
        return "미정"
    parts = dept.replace("로스트아크모바일스튜디오", "").strip().split()
    if not parts:
        return "미정"
    # "기획실 컨텐츠기획팀 시스템파트" → "기획실"
    # "개발관리실 QA팀" → "개발관리실"
    for p in parts:
        if p.endswith("실") or p.endswith("팀"):
            return p
    return parts[0]


def main():
    print(f"\n{'='*50}")
    print(f" LAM 스냅샷 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    # 1. 태스크 스냅샷 수집
    print("\n[1/2] 태스크 스냅샷 수집 중...")
    conn = collect_snapshot()

    # 2. 리포트 seq 매핑 점검
    print("\n[2/2] 리포트 seq 매핑 점검 중...")
    collect_reports(conn)

    conn.close()
    print(f"\n✅ 저장 완료: {DB_PATH}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
