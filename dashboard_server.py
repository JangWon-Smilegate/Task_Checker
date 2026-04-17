# -*- coding: utf-8 -*-
"""
LAM 업무 추이 대시보드 서버
스냅샷 데이터를 API로 제공하고 시각화 페이지를 서빙합니다.
"""
import json
import sqlite3
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_PATH = "snapshots.db"
PORT = 8090


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class DashboardHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # API 라우팅
        if path == "/api/summary":
            self._json_response(self._get_summary(params))
        elif path == "/api/trend":
            self._json_response(self._get_trend(params))
        elif path == "/api/members":
            self._json_response(self._get_members(params))
        elif path == "/api/delayed":
            self._json_response(self._get_delayed(params))
        elif path == "/api/dates":
            self._json_response(self._get_dates())
        elif path == "/" or path == "/index.html":
            self._serve_file("public/index.html", "text/html")
        else:
            # static files
            super().do_GET()

    def _json_response(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _serve_file(self, filepath, content_type):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        except FileNotFoundError:
            self.send_error(404)

    def _get_summary(self, params):
        """최신 날짜의 부서별 요약"""
        date_val = params.get("date", [None])[0]
        conn = get_db()
        if date_val:
            rows = conn.execute(
                "SELECT * FROM daily_summary WHERE snapshot_date = ? ORDER BY total DESC", (date_val,)
            ).fetchall()
        else:
            latest = conn.execute("SELECT MAX(snapshot_date) FROM daily_summary").fetchone()[0]
            if not latest:
                return {"date": None, "departments": []}
            rows = conn.execute(
                "SELECT * FROM daily_summary WHERE snapshot_date = ? ORDER BY total DESC", (latest,)
            ).fetchall()
            date_val = latest

        departments = []
        for r in rows:
            departments.append({
                "department": r["department"],
                "total": r["total"],
                "in_progress": r["in_progress"],
                "incomplete": r["incomplete"],
                "delayed": r["delayed"],
                "d_day": r["d_day"],
                "on_hold": r["on_hold"],
            })
        conn.close()

        total = sum(d["total"] for d in departments)
        total_delayed = sum(d["delayed"] for d in departments)
        total_dday = sum(d["d_day"] for d in departments)

        return {
            "date": date_val,
            "total": total,
            "delayed": total_delayed,
            "d_day": total_dday,
            "departments": departments
        }

    def _get_trend(self, params):
        """기간별 추이 데이터"""
        days = int(params.get("days", ["14"])[0])
        dept = params.get("department", [None])[0]
        conn = get_db()

        if dept:
            rows = conn.execute("""
                SELECT snapshot_date, SUM(total) as total, SUM(in_progress) as in_progress,
                       SUM(incomplete) as incomplete, SUM(delayed) as delayed, SUM(d_day) as d_day
                FROM daily_summary
                WHERE department = ?
                GROUP BY snapshot_date
                ORDER BY snapshot_date DESC LIMIT ?
            """, (dept, days)).fetchall()
        else:
            rows = conn.execute("""
                SELECT snapshot_date, SUM(total) as total, SUM(in_progress) as in_progress,
                       SUM(incomplete) as incomplete, SUM(delayed) as delayed, SUM(d_day) as d_day
                FROM daily_summary
                GROUP BY snapshot_date
                ORDER BY snapshot_date DESC LIMIT ?
            """, (days,)).fetchall()

        conn.close()

        # 오래된 날짜부터 정렬
        rows = list(reversed(rows))
        return {
            "department": dept or "전체",
            "data": [{
                "date": r["snapshot_date"],
                "total": r["total"],
                "in_progress": r["in_progress"],
                "incomplete": r["incomplete"],
                "delayed": r["delayed"],
                "d_day": r["d_day"],
            } for r in rows]
        }

    def _get_members(self, params):
        """담당자별 과부하 현황"""
        date_val = params.get("date", [None])[0]
        dept = params.get("department", [None])[0]
        conn = get_db()

        if not date_val:
            date_val = conn.execute("SELECT MAX(snapshot_date) FROM daily_member").fetchone()[0]
        if not date_val:
            return {"date": None, "members": []}

        query = "SELECT * FROM daily_member WHERE snapshot_date = ?"
        args = [date_val]
        if dept:
            query += " AND department = ?"
            args.append(dept)
        query += " ORDER BY (delayed + d_day) DESC, total DESC"

        rows = conn.execute(query, args).fetchall()
        conn.close()

        return {
            "date": date_val,
            "members": [{
                "assignee": r["assignee"],
                "department": r["department"],
                "total": r["total"],
                "in_progress": r["in_progress"],
                "incomplete": r["incomplete"],
                "delayed": r["delayed"],
                "d_day": r["d_day"],
                "risk": "HIGH" if (r["delayed"] + r["d_day"]) >= 3 else
                        "MEDIUM" if (r["delayed"] + r["d_day"]) >= 1 else "LOW"
            } for r in rows]
        }

    def _get_delayed(self, params):
        """지연 업무 상세"""
        date_val = params.get("date", [None])[0]
        conn = get_db()

        if not date_val:
            date_val = conn.execute("SELECT MAX(snapshot_date) FROM daily_delayed").fetchone()[0]
        if not date_val:
            return {"date": None, "tasks": []}

        rows = conn.execute(
            "SELECT * FROM daily_delayed WHERE snapshot_date = ? ORDER BY delay_days DESC",
            (date_val,)
        ).fetchall()
        conn.close()

        return {
            "date": date_val,
            "tasks": [{
                "task_id": r["task_id"],
                "title": r["title"],
                "assignee": r["assignee"],
                "department": r["department"],
                "status": r["status"],
                "end_date": r["end_date"],
                "delay_days": r["delay_days"],
            } for r in rows]
        }

    def _get_dates(self):
        """수집된 날짜 목록"""
        conn = get_db()
        rows = conn.execute(
            "SELECT DISTINCT snapshot_date FROM daily_summary ORDER BY snapshot_date DESC"
        ).fetchall()
        conn.close()
        return {"dates": [r["snapshot_date"] for r in rows]}

    def log_message(self, format, *args):
        """간결한 로그"""
        if "/api/" in str(args[0]):
            return  # API 호출은 로그 생략
        super().log_message(format, *args)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"LAM 업무 추이 대시보드: http://localhost:{PORT}")
    httpd = HTTPServer(("0.0.0.0", PORT), DashboardHandler)
    httpd.serve_forever()
