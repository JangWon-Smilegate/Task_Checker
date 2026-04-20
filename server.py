# -*- coding: utf-8 -*-
"""
LAM Work Dashboard MCP Server
https://lam-web.sgr.com:8081/WORKDASHBOARDAPI
"""
import json
import sqlite3
import ssl
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

BASE = "https://lam-web.sgr.com:8081/WORKDASHBOARDAPI"
SNAPSHOT_DB = Path(r"D:\Git\Task_Checker\snapshots.db")

_WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]


def _fmt_date(date_str: str) -> str:
    """'YYYY-MM-DD' → 'MM-DD(요일)'"""
    if not date_str or len(date_str) < 10:
        return date_str or ""
    try:
        d = date.fromisoformat(date_str[:10])
        return f"{date_str[5:10]}({_WEEKDAY_KO[d.weekday()]})"
    except Exception:
        return date_str[5:10]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

mcp = FastMCP("LAM Work Dashboard")


def _get(path: str) -> dict:
    req = urllib.request.Request(f"{BASE}{path}")
    with urllib.request.urlopen(req, context=ctx) as r:
        return json.loads(r.read())


# ─────────────────────────────────────────────
# Tool 1: 그룹 목록 조회
# ─────────────────────────────────────────────
@mcp.tool()
def get_groups() -> str:
    """LAM Work Dashboard의 그룹(프로젝트) 목록을 반환합니다."""
    data = _get("/groups")
    groups = data.get("data", [])
    lines = []
    for g in groups:
        jira = ", ".join(j["name"] for j in g.get("jiraConfigs", []))
        hansoft = ", ".join(h["name"] for h in g.get("hansoftConfigs", []))
        lines.append(
            f"[id:{g['id']}] {g['name']}\n"
            f"  설명: {g.get('description','')}\n"
            f"  Jira: {jira or '없음'} / Hansoft: {hansoft or '없음'}"
        )
    return "\n\n".join(lines)


# ─────────────────────────────────────────────
# Tool 2: 업무 현황 조회
# ─────────────────────────────────────────────
@mcp.tool()
def get_tasks(
    group_id: int = 1,
    status: Optional[str] = None,
    assignee: Optional[str] = None,
    department: Optional[str] = None,
    task_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 50,
) -> str:
    """
    LAM Work Dashboard 업무 목록을 조회합니다.

    Args:
        group_id: 그룹 ID (기본값 1 = 로스트아크 모바일)
        status: 상태 필터 - '진행 중', '미완료', '완료', '보류', '검토 중', '할 일' 중 하나
        assignee: 담당자 이름 (부분 일치)
        department: 부서명 (부분 일치)
        task_type: 'HANSOFT' 또는 'JIRA'
        date_from: 시작일 필터 (YYYY-MM-DD, 이 날짜 이후 종료 업무)
        date_to: 종료일 필터 (YYYY-MM-DD, 이 날짜 이전 종료 업무)
        limit: 최대 반환 개수 (기본 50, 최대 200)
    """
    data = _get(f"/tasks?groupId={group_id}")
    tasks = data.get("data", [])

    # 필터링
    if status:
        tasks = [t for t in tasks if status in (t.get("status") or "")]
    if assignee:
        tasks = [t for t in tasks if assignee in (t.get("assignee") or "")]
    if department:
        tasks = [t for t in tasks if department in (t.get("department") or "")]
    if task_type:
        tasks = [t for t in tasks if (t.get("taskType") or "").upper() == task_type.upper()]
    if date_from:
        tasks = [t for t in tasks if (t.get("end") or "9999") >= date_from]
    if date_to:
        tasks = [t for t in tasks if (t.get("start") or "0000") <= date_to]

    # 상태별 집계
    status_count: dict[str, int] = {}
    for t in tasks:
        s = t.get("status") or "미정"
        status_count[s] = status_count.get(s, 0) + 1

    total = len(tasks)
    tasks = tasks[:min(limit, 200)]

    summary = f"총 {total}개 업무 (표시: {len(tasks)}개)\n"
    summary += "[ 상태별 ] " + " / ".join(f"{s}:{c}" for s, c in sorted(status_count.items(), key=lambda x: -x[1]))
    summary += "\n\n"

    lines = []
    for t in tasks:
        line = (
            f"[{t.get('taskType','')}] {t.get('title','')}\n"
            f"  담당: {t.get('assignee') or '미배정'}  |  부서: {t.get('department','')}\n"
            f"  상태: {t.get('status','')}  |  기간: {_fmt_date(t.get('start',''))} ~ {_fmt_date(t.get('end',''))}  ({t.get('duration','')})\n"
            f"  우선순위: {t.get('priority','')}  |  ID: {t.get('id','')}"
        )
        if t.get("subTitle"):
            line += f"\n  설명: {t['subTitle']}"
        lines.append(line)

    return summary + "\n\n".join(lines)


# ─────────────────────────────────────────────
# Tool 3: 오늘/이번 주 업무 조회
# ─────────────────────────────────────────────
@mcp.tool()
def get_tasks_today(group_id: int = 1) -> str:
    """오늘 진행 중이거나 마감인 업무를 조회합니다."""
    today = date.today().isoformat()
    data = _get(f"/tasks?groupId={group_id}")
    tasks = data.get("data", [])

    today_tasks = [
        t for t in tasks
        if (t.get("start") or "") <= today <= (t.get("end") or "")
        and (t.get("status") or "") not in ("완료", "삭제됨")
    ]

    if not today_tasks:
        return f"오늘({today}) 진행 중인 업무가 없습니다."

    status_count: dict[str, int] = {}
    for t in today_tasks:
        s = t.get("status") or "미정"
        status_count[s] = status_count.get(s, 0) + 1

    summary = f"오늘({today}) 활성 업무: {len(today_tasks)}개\n"
    summary += "[ 상태별 ] " + " / ".join(f"{s}:{c}" for s, c in sorted(status_count.items(), key=lambda x: -x[1]))
    summary += "\n\n"

    lines = []
    for t in today_tasks:
        lines.append(
            f"[{t.get('taskType','')}] {t.get('title','')}\n"
            f"  담당: {t.get('assignee') or '미배정'}  |  상태: {t.get('status','')}  |  마감: {_fmt_date(t.get('end',''))}"
        )
    return summary + "\n\n".join(lines)


# ─────────────────────────────────────────────
# Tool 4: 이번 주 업무 조회
# ─────────────────────────────────────────────
@mcp.tool()
def get_tasks_this_week(group_id: int = 1) -> str:
    """이번 주(월~일) 활성 업무를 조회합니다."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    mon_str = monday.isoformat()
    sun_str = sunday.isoformat()

    data = _get(f"/tasks?groupId={group_id}")
    tasks = data.get("data", [])

    week_tasks = [
        t for t in tasks
        if (t.get("end") or "") >= mon_str
        and (t.get("start") or "") <= sun_str
        and (t.get("status") or "") not in ("완료", "삭제됨")
    ]

    status_count: dict[str, int] = {}
    dept_count: dict[str, int] = {}
    for t in week_tasks:
        s = t.get("status") or "미정"
        status_count[s] = status_count.get(s, 0) + 1
        dept = (t.get("department") or "").split(" ")[-1] or "미정"
        dept_count[dept] = dept_count.get(dept, 0) + 1

    summary = f"이번 주({mon_str} ~ {sun_str}) 활성 업무: {len(week_tasks)}개\n"
    summary += "[ 상태별 ] " + " / ".join(f"{s}:{c}" for s, c in sorted(status_count.items(), key=lambda x: -x[1]))
    summary += "\n\n"

    lines = []
    for t in week_tasks[:100]:
        lines.append(
            f"[{t.get('taskType','')}] {t.get('title','')}\n"
            f"  담당: {t.get('assignee') or '미배정'}  |  상태: {t.get('status','')}  |  {_fmt_date(t.get('start',''))} ~ {_fmt_date(t.get('end',''))}"
        )
    return summary + "\n\n".join(lines)


# ─────────────────────────────────────────────
# Tool 5: 담당자별 업무 현황
# ─────────────────────────────────────────────
@mcp.tool()
def get_tasks_by_person(assignee: str, group_id: int = 1) -> str:
    """
    특정 담당자의 업무 현황을 조회합니다.

    Args:
        assignee: 담당자 이름 (부분 일치, 예: '이제하', '박도영')
        group_id: 그룹 ID (기본값 1)
    """
    data = _get(f"/tasks?groupId={group_id}")
    tasks = [t for t in data.get("data", []) if assignee in (t.get("assignee") or "")]

    if not tasks:
        return f"'{assignee}' 담당자의 업무를 찾을 수 없습니다."

    active = [t for t in tasks if (t.get("status") or "") not in ("완료", "삭제됨")]
    done = [t for t in tasks if (t.get("status") or "") == "완료"]

    lines = [f"'{assignee}' 업무 현황 - 전체 {len(tasks)}개 (활성: {len(active)}, 완료: {len(done)})\n"]

    status_count: dict[str, int] = {}
    for t in tasks:
        s = t.get("status") or "미정"
        status_count[s] = status_count.get(s, 0) + 1
    lines.append("[ 상태별 ] " + " / ".join(f"{s}:{c}" for s, c in sorted(status_count.items(), key=lambda x: -x[1])))
    lines.append("")

    for t in active[:50]:
        lines.append(
            f"[{t.get('status','')}] {t.get('title','')}\n"
            f"  기간: {_fmt_date(t.get('start',''))} ~ {_fmt_date(t.get('end',''))}  ({t.get('duration','')})  |  ID: {t.get('id','')}"
        )
    return "\n".join(lines)


# ─────────────────────────────────────────────
# Tool 6: 부서별 업무 현황
# ─────────────────────────────────────────────
@mcp.tool()
def get_tasks_by_department(department: str, group_id: int = 1) -> str:
    """
    특정 부서의 업무 현황을 조회합니다.

    Args:
        department: 부서명 (부분 일치, 예: 'BM콘텐츠', '기획실', '모바일사업')
        group_id: 그룹 ID (기본값 1)
    """
    data = _get(f"/tasks?groupId={group_id}")
    tasks = [t for t in data.get("data", []) if department in (t.get("department") or "")]

    if not tasks:
        return f"'{department}' 부서의 업무를 찾을 수 없습니다."

    active = [t for t in tasks if (t.get("status") or "") not in ("완료", "삭제됨")]

    def task_link(t: dict) -> str:
        tid = t.get("id", "")
        if (t.get("taskType") or "").upper() == "JIRA":
            return f"https://jira.sgr.com/browse/{tid}"
        return f"http://lam.sgr.com/{tid}"

    # 서브팀별 그룹핑 (department 필드 마지막 단어 기준)
    from collections import defaultdict
    sub_teams: dict = defaultdict(list)
    for t in active:
        dept_full = (t.get("department") or "").strip()
        # 기획실 제거 후 나머지를 서브팀으로
        sub = dept_full.replace(department, "").strip()
        sub = sub.lstrip(" ").rstrip(" ") or "(기타)"
        sub_teams[sub].append(t)

    status_count: dict[str, int] = {}
    for t in active:
        s = t.get("status") or "미정"
        status_count[s] = status_count.get(s, 0) + 1

    lines = [f"'{department}' 부서 업무 현황 - 활성 {len(active)}개 / 전체 {len(tasks)}개"]
    lines.append("[ 상태별 ] " + " / ".join(f"{s}:{c}" for s, c in sorted(status_count.items(), key=lambda x: -x[1])))
    lines.append("")

    for sub, sub_tasks in sorted(sub_teams.items()):
        lines.append(f"▶ {sub} ({len(sub_tasks)}개)")
        # 진행중 먼저, 그 다음 미완료, 보류
        order = {"진행중": 0, "진행 중": 0, "미완료": 1, "보류": 2}
        sub_tasks_sorted = sorted(sub_tasks, key=lambda t: (order.get(t.get("status", ""), 9), t.get("end") or "9999"))
        for t in sub_tasks_sorted[:30]:
            title = t.get("title", "")
            link = task_link(t)
            assignee = t.get("assignee") or "미배정"
            status = t.get("status", "")
            end = _fmt_date(t.get("end") or "")
            start = _fmt_date(t.get("start") or "")
            lines.append(f"  [{status}] [{title}]({link})  ({assignee}, {start}~{end})")
        if len(sub_tasks) > 30:
            lines.append(f"  ... 외 {len(sub_tasks)-30}개")
        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# Tool 7: 리포트 목록 / 검색
# ─────────────────────────────────────────────
@mcp.tool()
def get_reports(group_id: int = 1, search: Optional[str] = None) -> str:
    """
    LAM Work Dashboard의 리포트(대시보드) 목록을 반환합니다.
    search 파라미터로 이름/설명 검색 가능.

    Args:
        group_id: 그룹 ID (기본값 1)
        search: 검색어 (이름 또는 설명 부분 일치, 예: 'M28_4월', '지연', '기획실')
    """
    data = _get(f"/reports?groupId={group_id}")
    reports = data.get("data", [])

    if search:
        matched = [
            r for r in reports
            if search in r.get("name", "") or search in r.get("desc", "")
        ]
        if not matched:
            return f"'{search}' 검색 결과 없음\n\n전체 {len(reports)}개 리포트 중 일치하는 항목이 없습니다."
        lines = [f"'{search}' 검색 결과: {len(matched)}개\n"]
        for r in matched:
            lines.append(f"[seq:{r['seq']}] {r['name']}\n  {r.get('desc', '')}")
        return "\n\n".join(lines)

    lines = [f"총 {len(reports)}개 리포트\n"]
    for r in reports:
        lines.append(f"[seq:{r['seq']}] {r['name']}\n  {r.get('desc', '')}")
    return "\n\n".join(lines)


# ─────────────────────────────────────────────
# Tool 9: 리포트 기반 태스크 조회
# ─────────────────────────────────────────────
@mcp.tool()
def get_tasks_by_report(
    report_seq: Optional[int] = None,
    report_name: Optional[str] = None,
    group_id: int = 1,
    status: Optional[str] = None,
    limit: int = 200,
) -> str:
    """
    리포트(저장된 필터)를 기준으로 업무 목록을 조회합니다.
    report_seq 또는 report_name 중 하나를 지정하세요.

    ※ 현재 API 제약으로 인해 Hansoft 타겟 필드 직접 필터링이 불가하여,
       리포트 이름에서 월(月) 정보를 파싱하여 마감일 기준으로 근사 필터링합니다.

    Args:
        report_seq: 리포트 seq 번호 (예: 106)
        report_name: 리포트 이름 부분 일치 (예: 'M28_4월', '지연일감')
        group_id: 그룹 ID (기본값 1)
        status: 상태 필터 ('진행중', '미완료', '완료' 등)
        limit: 최대 반환 개수 (기본 200)
    """
    import re, calendar

    # 1. 리포트 찾기
    reports_data = _get(f"/reports?groupId={group_id}")
    reports = reports_data.get("data", [])

    target_report = None
    if report_seq is not None:
        target_report = next((r for r in reports if r["seq"] == report_seq), None)
    elif report_name:
        # 정확히 포함된 것 우선, 없으면 부분 일치
        target_report = next(
            (r for r in reports if report_name in r.get("name", "")), None
        )

    if not target_report:
        # 비슷한 리포트 제안
        keyword = report_name or str(report_seq) or ""
        similar = [
            r for r in reports
            if keyword.lower() in r.get("name", "").lower()
            or keyword.lower() in r.get("desc", "").lower()
        ]
        suggest_lines = "\n".join(
            f"  [seq:{r['seq']}] {r['name']} — {r.get('desc','')}"
            for r in similar[:8]
        )
        msg = f"리포트 '{keyword}'를 찾을 수 없습니다."
        if similar:
            msg += f"\n\n비슷한 리포트 ({len(similar)}개):\n{suggest_lines}"
        return msg

    rname = target_report["name"]
    rdesc = target_report.get("desc", "")

    # 2. 리포트 이름에서 날짜 범위 파싱
    date_from = None
    date_to = None
    filter_note = ""

    month_match = re.search(r'(\d{1,2})월', rname)
    year_match = re.search(r'(202\d)', rname)
    year = int(year_match.group(1)) if year_match else date.today().year

    if month_match:
        month = int(month_match.group(1))
        last_day = calendar.monthrange(year, month)[1]
        date_from = f"{year}-{month:02d}-01"
        date_to = f"{year}-{month:02d}-{last_day}"
        filter_note = f"※ 마감일 기준 필터: {date_from} ~ {date_to} (Hansoft 타겟 필드 근사치)"

    # 3. 태스크 조회 및 필터링
    tasks_data = _get(f"/tasks?groupId={group_id}")
    tasks = tasks_data.get("data", [])

    # 미배정 제외
    tasks = [t for t in tasks if (t.get("assignee") or "미배정") != "미배정"]

    if status:
        tasks = [t for t in tasks if status in (t.get("status") or "")]
    if date_from:
        tasks = [t for t in tasks if (t.get("end") or "9999") >= date_from]
    if date_to:
        tasks = [t for t in tasks if (t.get("end") or "0000") <= date_to]

    # 마감일 기준 정렬
    tasks = sorted(tasks, key=lambda t: t.get("end") or "9999")

    # 상태별 집계
    status_count: dict[str, int] = {}
    for t in tasks:
        s = t.get("status") or "미정"
        status_count[s] = status_count.get(s, 0) + 1

    total = len(tasks)
    display_tasks = tasks[:min(limit, 200)]

    header = (
        f"📋 리포트: {rname} [seq:{target_report['seq']}]\n"
        f"   설명: {rdesc}\n"
        f"   총 {total}개 업무 (표시: {len(display_tasks)}개)\n"
    )
    if filter_note:
        header += f"   {filter_note}\n"

    summary = "[ 상태별 ] " + " / ".join(
        f"{s}:{c}" for s, c in sorted(status_count.items(), key=lambda x: -x[1])
    )

    lines = [header, summary, ""]

    def task_link(t: dict) -> str:
        tid = t.get("id", "")
        if (t.get("taskType") or "").upper() == "JIRA":
            return f"https://jira.sgr.com/browse/{tid}"
        return f"http://lam.sgr.com/{tid}"

    for t in display_tasks:
        line = (
            f"[{t.get('taskType','')}] {t.get('title','')}\n"
            f"  담당: {t.get('assignee') or '미배정'}  |  부서: {t.get('department','')}\n"
            f"  상태: {t.get('status','')}  |  마감: {_fmt_date(t.get('end',''))}  "
            f"|  ID: {t.get('id','')}  |  링크: {task_link(t)}"
        )
        if t.get("subTitle"):
            line += f"\n  설명: {str(t['subTitle'])[:100]}"
        lines.append(line)

    return "\n\n".join(lines)


# ─────────────────────────────────────────────
# Tool 8: 부서 및 멤버 조회
# ─────────────────────────────────────────────
@mcp.tool()
def get_departments(search: Optional[str] = None) -> str:
    """
    부서 및 멤버 정보를 조회합니다.

    Args:
        search: 부서명 또는 멤버 이름으로 검색 (없으면 전체 부서 목록)
    """
    data = _get("/const/dept")
    depts = data.get("data", {})

    if search:
        results = []
        for dept_name, dept_info in depts.items():
            if search in dept_name:
                members = dept_info.get("members", [])
                member_list = ", ".join(f"{m['name']}({m.get('title','')})" for m in members)
                results.append(f"[{dept_name}]\n  멤버: {member_list}")
            else:
                for m in dept_info.get("members", []):
                    if search in m.get("name", ""):
                        results.append(
                            f"[{dept_name}]\n  {m['name']} / {m.get('title','')} / {m.get('uid','')}"
                        )
        return "\n\n".join(results) if results else f"'{search}' 검색 결과 없음"

    # 전체 부서 목록만
    lines = [f"총 {len(depts)}개 부서\n"]
    for dept_name, dept_info in depts.items():
        members = dept_info.get("members", [])
        lines.append(f"• {dept_name} ({len(members)}명)")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# Tool 10: 지연 패턴 분석 (스냅샷 DB 기반)
# ─────────────────────────────────────────────
@mcp.tool()
def get_delay_analytics(days: int = 30, min_delay_count: int = 1) -> str:
    """
    담당자별 지연 패턴을 분석합니다. (snapshots.db 기반)

    Args:
        days: 분석 기간 (기본 30일)
        min_delay_count: 최소 지연 건수 필터 (기본 1건 이상)

    반환 지표:
    - 담당자별 누적 지연 건수 / 지연율 / 평균 지연일
    - 만성 지연자 (기간 내 3건 이상)
    - 마감일 변경 빈도 (deadline drift)
    - 팀별 지연율 요약
    """
    if not SNAPSHOT_DB.exists():
        return f"스냅샷 DB가 없습니다: {SNAPSHOT_DB}\n먼저 snapshot_collector.py를 실행해 주세요."

    conn = sqlite3.connect(SNAPSHOT_DB)
    since = (date.today() - timedelta(days=days)).isoformat()
    today_str = date.today().isoformat()

    # ── 담당자별 지연 통계
    rows = conn.execute("""
        SELECT
            assignee,
            department,
            COUNT(DISTINCT task_id)   AS delay_count,
            ROUND(AVG(delay_days), 1) AS avg_delay_days,
            MAX(delay_days)           AS max_delay_days
        FROM daily_delayed
        WHERE snapshot_date >= ? AND snapshot_date <= ?
          AND assignee != '미배정' AND assignee != ''
        GROUP BY assignee, department
        HAVING delay_count >= ?
        ORDER BY delay_count DESC, avg_delay_days DESC
    """, (since, today_str, min_delay_count)).fetchall()

    # ── 담당자별 전체 담당 건수 (지연율 계산용)
    total_rows = conn.execute("""
        SELECT assignee, COUNT(DISTINCT task_id) AS total
        FROM daily_tasks
        WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM daily_tasks)
          AND assignee != '미배정' AND assignee != ''
        GROUP BY assignee
    """).fetchall()
    total_map = {r[0]: r[1] for r in total_rows}

    # ── 마감일 변경 빈도 (deadline drift)
    drift_rows = conn.execute("""
        SELECT
            t.assignee,
            COUNT(*) AS drift_count,
            GROUP_CONCAT(DISTINCT t.title) AS tasks
        FROM task_changes c
        JOIN daily_tasks t ON c.task_id = t.task_id
            AND t.snapshot_date = (SELECT MAX(snapshot_date) FROM daily_tasks)
        WHERE c.change_type = 'deadline_change'
          AND c.detected_date >= ?
          AND t.assignee != '미배정'
        GROUP BY t.assignee
        ORDER BY drift_count DESC
        LIMIT 10
    """, (since,)).fetchall()

    # ── 팀별 지연율
    team_rows = conn.execute("""
        SELECT
            department,
            COUNT(DISTINCT task_id) AS delay_count
        FROM daily_delayed
        WHERE snapshot_date >= ? AND snapshot_date <= ?
        GROUP BY department
        ORDER BY delay_count DESC
    """, (since, today_str)).fetchall()

    conn.close()

    lines = [f"📊 지연 패턴 분석 (최근 {days}일: {since} ~ {today_str})\n"]

    # 담당자별 지연 테이블
    lines.append("### 담당자별 지연 현황")
    lines.append(f"{'담당자':<12} {'팀':<10} {'지연건수':>6} {'지연율':>7} {'평균지연일':>8} {'최대지연일':>8} {'비고'}")
    lines.append("-" * 75)

    chronic = []
    for assignee, dept, delay_count, avg_days, max_days in rows:
        total = total_map.get(assignee, 0)
        rate = f"{delay_count/total*100:.0f}%" if total > 0 else "N/A"
        note = "🔴 만성" if delay_count >= 3 else ("🟡" if delay_count >= 2 else "")
        if delay_count >= 3:
            chronic.append(assignee)
        lines.append(
            f"{assignee:<12} {dept:<10} {delay_count:>6}건  {rate:>6}  {avg_days:>7.1f}일  {max_days:>7}일  {note}"
        )

    if not rows:
        lines.append("  (지연 이력 없음 — 스냅샷 데이터 부족할 수 있음)")

    # 만성 지연자 요약
    if chronic:
        lines.append(f"\n🔴 만성 지연자 ({len(chronic)}명): {', '.join(chronic)}")
        lines.append("   → 업무 배분 재검토 또는 1:1 면담 권장")

    # 마감일 드리프트
    if drift_rows:
        lines.append(f"\n### 마감일 변경 빈도 (Deadline Drift) — 최근 {days}일")
        lines.append(f"{'담당자':<12} {'마감변경횟수':>8}  변경된 태스크")
        lines.append("-" * 60)
        for assignee, cnt, tasks in drift_rows:
            task_preview = (tasks or "")[:50] + ("..." if tasks and len(tasks) > 50 else "")
            lines.append(f"{assignee:<12} {cnt:>8}회  {task_preview}")
        lines.append("   ※ 마감을 자주 바꾸는 담당자 = 초기 일정 산정 재검토 필요")

    # 팀별 지연 요약
    if team_rows:
        lines.append(f"\n### 팀별 누적 지연 건수 (최근 {days}일)")
        for dept, cnt in team_rows[:8]:
            bar = "█" * min(cnt, 20)
            lines.append(f"  {dept:<12} {bar} {cnt}건")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# Tool 11: 주별 추이 분석 (스냅샷 DB 기반)
# ─────────────────────────────────────────────
@mcp.tool()
def get_trend_report(weeks: int = 4) -> str:
    """
    주별 업무 현황 추이를 분석합니다. (snapshots.db 기반)

    Args:
        weeks: 분석할 주 수 (기본 4주)

    반환 지표:
    - 주별 진행중 / 지연 / D-day 건수 변화
    - 주별 완료 속도 (상태가 완료로 바뀐 건수)
    - 팀별 주간 지연 추이
    """
    if not SNAPSHOT_DB.exists():
        return f"스냅샷 DB가 없습니다: {SNAPSHOT_DB}\n먼저 snapshot_collector.py를 실행해 주세요."

    conn = sqlite3.connect(SNAPSHOT_DB)
    since = (date.today() - timedelta(weeks=weeks, days=date.today().weekday())).isoformat()

    # ── 주별 상태 집계 (매주 금요일 기준 또는 가장 최근 스냅샷)
    rows = conn.execute("""
        SELECT
            snapshot_date,
            SUM(in_progress)   AS in_prog,
            SUM(incomplete)    AS incomplete,
            SUM(delayed)       AS delayed,
            SUM(d_day)         AS dday,
            SUM(on_hold)       AS on_hold,
            SUM(total)         AS total
        FROM daily_summary
        WHERE snapshot_date >= ?
        GROUP BY snapshot_date
        ORDER BY snapshot_date
    """, (since,)).fetchall()

    # ── 주별 완료 전환 건수
    completed_rows = conn.execute("""
        SELECT
            detected_date,
            COUNT(*) AS completed_count
        FROM task_changes
        WHERE change_type = 'status_change'
          AND new_value IN ('완료', 'Done', 'Closed', 'Resolved')
          AND detected_date >= ?
        GROUP BY detected_date
        ORDER BY detected_date
    """, (since,)).fetchall()
    completed_map = {r[0]: r[1] for r in completed_rows}

    conn.close()

    if not rows:
        return f"스냅샷 데이터가 부족합니다. (since: {since})\n최소 1일 이상 데이터가 쌓인 후 사용 가능합니다."

    lines = [f"📈 주별 업무 추이 (최근 {weeks}주)\n"]
    lines.append(f"{'날짜':<12} {'진행중':>6} {'미완료':>6} {'지연':>6} {'D-day':>6} {'완료전환':>8} {'보류':>6} {'전체':>6}")
    lines.append("-" * 70)

    prev_delayed = None
    for snap_date, in_prog, incomplete, delayed, dday, on_hold, total in rows:
        completed = completed_map.get(snap_date, 0)
        delta = ""
        if prev_delayed is not None:
            diff = delayed - prev_delayed
            delta = f" (▲{diff})" if diff > 0 else (f" (▼{abs(diff)})" if diff < 0 else " (━)")
        lines.append(
            f"{snap_date:<12} {in_prog:>6} {incomplete:>6} {delayed:>6}{delta:<8} {dday:>6} {completed:>8} {on_hold:>6} {total:>6}"
        )
        prev_delayed = delayed

    # 추이 해석
    if len(rows) >= 2:
        first_delayed = rows[0][3]
        last_delayed = rows[-1][3]
        trend = "증가 추세 🔴" if last_delayed > first_delayed else ("감소 추세 🟢" if last_delayed < first_delayed else "유지 🟡")
        lines.append(f"\n지연 추이: {first_delayed}건 → {last_delayed}건 ({trend})")

        total_completed = sum(completed_map.get(r[0], 0) for r in rows)
        lines.append(f"기간 내 완료 전환 합계: {total_completed}건")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# Tool 12: 관리 대시보드 (종합)
# ─────────────────────────────────────────────
@mcp.tool()
def get_management_dashboard(scope: str = "전체") -> str:
    """
    관리자용 종합 대시보드를 출력합니다.
    지연 패턴, 부하 분산, 속도, 리스크를 한 화면에 요약합니다.

    Args:
        scope: '전체' | '기획실' | '개발실' | '개발관리실' 등 (기본: 전체)
    """
    if not SNAPSHOT_DB.exists():
        return f"스냅샷 DB가 없습니다: {SNAPSHOT_DB}\n먼저 snapshot_collector.py를 실행해 주세요."

    conn = sqlite3.connect(SNAPSHOT_DB)
    today_str = date.today().isoformat()
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    month_ago = (date.today() - timedelta(days=30)).isoformat()

    # 최신 스냅샷 날짜
    latest = conn.execute("SELECT MAX(snapshot_date) FROM daily_summary").fetchone()[0]
    if not latest:
        conn.close()
        return "스냅샷 데이터가 없습니다."

    scope_filter = f"AND department LIKE '%{scope}%'" if scope != "전체" else ""

    # ── 1. 오늘 현황 요약
    summary = conn.execute(f"""
        SELECT
            SUM(total) AS total,
            SUM(in_progress) AS in_prog,
            SUM(incomplete) AS incomplete,
            SUM(delayed) AS delayed,
            SUM(d_day) AS dday,
            SUM(on_hold) AS on_hold
        FROM daily_summary
        WHERE snapshot_date = ? {scope_filter}
    """, (latest,)).fetchone()

    # ── 2. 지연 위험 TOP 5 담당자 (30일)
    risk_rows = conn.execute(f"""
        SELECT
            d.assignee,
            d.department,
            COUNT(DISTINCT d.task_id) AS delay_count,
            ROUND(AVG(d.delay_days), 1) AS avg_days
        FROM daily_delayed d
        WHERE d.snapshot_date >= ? {scope_filter.replace('department', 'd.department')}
          AND d.assignee != '미배정'
        GROUP BY d.assignee
        ORDER BY delay_count DESC, avg_days DESC
        LIMIT 5
    """, (month_ago,)).fetchall()

    # ── 3. 부하 집중도 (현재 담당 건수 TOP 5)
    load_rows = conn.execute(f"""
        SELECT assignee, department, total, in_progress, incomplete
        FROM daily_member
        WHERE snapshot_date = ? {scope_filter}
          AND assignee != '미배정'
        ORDER BY total DESC
        LIMIT 5
    """, (latest,)).fetchall()

    # ── 4. 이번 주 완료 건수 (velocity)
    velocity = conn.execute("""
        SELECT COUNT(*) FROM task_changes
        WHERE change_type = 'status_change'
          AND new_value IN ('완료', 'Done', 'Closed')
          AND detected_date >= ?
    """, (week_ago,)).fetchone()[0]

    # ── 5. 마감 드리프트 TOP 3
    drift = conn.execute(f"""
        SELECT t.assignee, COUNT(*) AS cnt
        FROM task_changes c
        JOIN daily_tasks t ON c.task_id = t.task_id
            AND t.snapshot_date = (SELECT MAX(snapshot_date) FROM daily_tasks)
        WHERE c.change_type = 'deadline_change'
          AND c.detected_date >= ?
          AND t.assignee != '미배정'
        GROUP BY t.assignee
        ORDER BY cnt DESC
        LIMIT 3
    """, (month_ago,)).fetchall()

    conn.close()

    total, in_prog, incomplete, delayed, dday, on_hold = summary or (0,0,0,0,0,0)

    lines = [
        f"📋 관리 대시보드 [{scope}] — {latest} 기준\n",
        "━" * 50,
        f"진행중 {in_prog}건 · 미완료 {incomplete}건 · 지연 {delayed}건 · D-day {dday}건 · 보류 {on_hold}건 / 전체 {total}건",
        f"이번 주 완료 전환: {velocity}건",
        "━" * 50,
    ]

    # 지연 위험 섹션
    lines.append("\n🔴 지연 위험 TOP 5 (최근 30일)")
    if risk_rows:
        for assignee, dept, cnt, avg in risk_rows:
            chronic_mark = " ⚠️만성" if cnt >= 3 else ""
            lines.append(f"  {assignee} ({dept}) — {cnt}건, 평균 {avg}일{chronic_mark}")
    else:
        lines.append("  (데이터 없음)")

    # 부하 집중 섹션
    lines.append("\n⚖️ 업무 집중 TOP 5 (현재)")
    if load_rows:
        for assignee, dept, total_t, in_prog_t, incomplete_t in load_rows:
            lines.append(f"  {assignee} ({dept}) — 전체 {total_t}건 (진행중 {in_prog_t} / 미완료 {incomplete_t})")
    else:
        lines.append("  (데이터 없음)")

    # 마감 드리프트 섹션
    if drift:
        lines.append("\n📅 마감 자주 변경 (최근 30일)")
        for assignee, cnt in drift:
            lines.append(f"  {assignee} — {cnt}회 변경")

    # 팀별 리스크 레벨
    lines.append("\n🏢 팀별 리스크 레벨")
    risk_level = {"기획실": "🟡", "개발실": "🔴", "개발관리실": "🟢"}
    for team, level in risk_level.items():
        if scope == "전체" or scope in team:
            lines.append(f"  {level} {team}")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# Tool 13: 완료 태스크 조회 (DB 기반)
# ─────────────────────────────────────────────
@mcp.tool()
def get_completed_tasks(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    department: Optional[str] = None,
    assignee: Optional[str] = None,
) -> str:
    """
    DB 스냅샷 기준으로 특정 기간에 완료 처리된 태스크 목록을 반환합니다.
    주간 보고 시 '이번 주 완료 태스크' 조회에 활용합니다.
    Hansoft와 Jira 완료 태스크 모두 포함됩니다.

    Args:
        date_from: 시작일 (YYYY-MM-DD). 기본: 이번 주 월요일
        date_to:   종료일 (YYYY-MM-DD). 기본: 오늘
        department: 부서 필터 (부분 일치, 예: '기획실')
        assignee:   담당자 필터 (부분 일치)
    """
    if not SNAPSHOT_DB.exists():
        return f"스냅샷 DB가 없습니다: {SNAPSHOT_DB}\n먼저 snapshot_collector.py를 실행해 주세요."

    today = date.today()
    if not date_from:
        monday = today - timedelta(days=today.weekday())
        date_from = monday.isoformat()
    if not date_to:
        date_to = today.isoformat()

    conn = sqlite3.connect(SNAPSHOT_DB)

    # daily_completed 테이블 존재 여부 확인
    has_table = conn.execute(
        "SELECT name FROM sqlite_master WHERE name='daily_completed'"
    ).fetchone()
    if not has_table:
        conn.close()
        return (
            "daily_completed 테이블이 없습니다.\n"
            "snapshot_collector.py 최신 버전으로 실행하면 자동 생성됩니다."
        )

    filters = ["detected_date >= ?", "detected_date <= ?", "assignee != '미배정'"]
    params: list = [date_from, date_to]

    if department:
        filters.append("department LIKE ?")
        params.append(f"%{department}%")
    if assignee:
        filters.append("assignee LIKE ?")
        params.append(f"%{assignee}%")

    where = " AND ".join(filters)

    rows = conn.execute(f"""
        SELECT detected_date, task_id, title, assignee, department, prev_status, end_date
        FROM daily_completed
        WHERE {where}
        ORDER BY detected_date DESC, department, assignee
    """, params).fetchall()

    conn.close()

    if not rows:
        return (
            f"해당 기간({date_from} ~ {date_to}) 완료 전환 기록이 없습니다.\n"
            "※ 스냅샷이 수집된 날짜만 추적 가능합니다. 스냅샷이 없던 날의 완료는 집계되지 않습니다."
        )

    lines = [f"✅ 완료 태스크 ({date_from} ~ {date_to}, {len(rows)}건)\n"]
    lines.append("| 완료감지일 | 조직 | 담당자 | 업무 | 이전상태 | 마감 |")
    lines.append("|---|---|---|---|---|---|")

    for detected_date, task_id, title, assignee, dept, prev_status, end_date in rows:
        if task_id.isdigit():
            task_link = f"[{title}](http://lam.sgr.com/{task_id})"
        else:
            task_link = f"[{title}](https://jira.sgr.com/browse/{task_id})"
        end_fmt = _fmt_date(end_date) if end_date else ""
        det_fmt = _fmt_date(detected_date)
        lines.append(
            f"| {det_fmt} | {dept} | {assignee} | {task_link} | {prev_status} | {end_fmt} |"
        )

    # 담당자별 집계
    from collections import Counter
    person_counts = Counter(r[3] for r in rows)
    top_persons = ", ".join(f"{p} {c}건" for p, c in person_counts.most_common(10))
    lines.append(f"\n**담당자별:** {top_persons}")

    # 부서별 집계
    dept_counts = Counter(r[4] for r in rows)
    top_depts = ", ".join(f"{d} {c}건" for d, c in dept_counts.most_common())
    lines.append(f"**부서별:** {top_depts}")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
