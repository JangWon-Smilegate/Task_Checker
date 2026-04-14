# LAM Work Dashboard AI Assistant

이 프로젝트는 LAM(로스트아크 모바일) 내부 업무 시스템을 Claude AI로 조회하는 환경입니다.

---

## 사용 가능한 MCP 서버

### 1. lam-dashboard
LAM Work Dashboard API를 통해 업무 현황을 조회합니다.
- API: `https://lam-web.sgr.com:8081/WORKDASHBOARDAPI`
- 서버 경로: `C:\Users\jangwonpark\mcp-lamweb\server.py`

### 2. atlassian
Confluence(위키) 및 Jira 조회/작성 도구입니다.
- Confluence: `https://wiki.sgr.com`
- Jira: `https://jira.sgr.com`

---

## 기능 목록

### [업무 현황 조회] lam-dashboard 도구

#### 담당자별 업무 조회
```
도구: mcp__lam-dashboard__get_tasks
파라미터: assignee="이름", status="진행중", limit=200
```
**사용 예시 (자연어):**
- "홍길동이 진행 중인 업무 알려줘"
- "김상현 업무 현황 알려줘"

**출력 형식:**
| 조직 | 담당자 | 업무 | 상태 | 시작 | 마감 |

---

#### 오늘 마감 업무 조회
```
도구: mcp__lam-dashboard__get_tasks_today
파라미터: group_id=1 (기본값)
```
**사용 예시 (자연어):**
- "오늘 마감인 업무 알려줘"
- "오늘 진행 중인 업무 보여줘"

---

#### 이번 주 업무 조회
```
도구: mcp__lam-dashboard__get_tasks_this_week
파라미터: group_id=1 (기본값)
```
**사용 예시 (자연어):**
- "이번 주 업무 알려줘"

---

#### 부서별 업무 조회
```
도구: mcp__lam-dashboard__get_tasks_by_department
파라미터: department="부서명", group_id=1
```
**사용 예시 (자연어):**
- "기획실 업무 현황 알려줘"
- "컨텐츠기획팀 업무 보여줘"

---

#### 전체 업무 필터 조회
```
도구: mcp__lam-dashboard__get_tasks
파라미터:
  - group_id: 1 (로스트아크 모바일, 기본값)
  - status: "진행중" | "미완료" | "완료" | "보류" | "할 일"
  - assignee: "이름" (부분 일치)
  - department: "부서명" (부분 일치)
  - date_from: "YYYY-MM-DD"
  - date_to: "YYYY-MM-DD"
  - limit: 최대 200
```

---

#### 그룹/부서/리포트 조회
```
도구: mcp__lam-dashboard__get_groups          → 전체 그룹 목록
도구: mcp__lam-dashboard__get_departments     → 부서 및 멤버 조회
도구: mcp__lam-dashboard__get_reports         → 리포트 목록
```

---

### [기획 문서 조회] atlassian Confluence 도구

#### 문서 검색
```
도구: mcp__atlassian__confluence_search
파라미터: query="검색어", limit=5
```
**사용 예시 (자연어):**
- "합동댄스 기획서 링크 있어?"
- "스퀘어홀 관련 문서 찾아줘"
- "마이룸 콘텐츠 기획서 알려줘"

**출력 형식:**
| 제목 | 링크 |

---

### [회의록 조회] atlassian Confluence 도구

#### 회의록 검색
```
도구: mcp__atlassian__confluence_search
파라미터: query='type=page AND title ~ "회의" AND created >= "YYYY-MM-DD" AND created <= "YYYY-MM-DD"', limit=30
```

**사용 예시 (자연어):**
- "지난 주 회의 내용 알려줘"
- "이번 주 진행한 회의 요약해 줘"
- "04-09 최적화 TF 회의 내용 알려줘"

**동작 방식:**
1. `confluence_search`로 기간 내 회의록 목록 조회
2. 각 회의록의 `page_id`로 `confluence_get_page` 호출하여 상세 내용 조회
3. 회의별 요약 정리하여 출력

**검색 CQL 패턴:**
| 요청 | CQL query |
|---|---|
| 지난 주 회의 | `type=page AND title ~ "회의" AND created >= "지난주월요일" AND created <= "지난주금요일"` |
| 특정 날짜 회의 | `title ~ "YYYY-MM-DD" AND title ~ "회의"` |
| 특정 주제 회의 | `title ~ "주제" AND title ~ "회의" AND type=page` |
| 최근 회의 | `type=page AND title ~ "회의" AND created >= "시작일"` |

**출력 형식 (목록):**
| 날짜 | 제목 | 링크 |

**출력 형식 (상세 요약):**
각 회의별로 아래 구조로 요약:
```
## MM-DD (요일) | 회의 제목
**참석:** 참석자 목록
- 주요 논의 내용 (3~5개 bullet point)
- **후속:** 후속 진행 사항
```

**주요 회의 유형 (LAM 스튜디오):**
| 회의명 | 주기 | 스페이스 |
|---|---|---|
| 팀장 주간회의 | 매주 월요일 | LAM |
| 기획실 주간 회의 | 매주 월요일 | LAM |
| 최적화 TF 정기회의 | 매주 목요일 | LAM |
| QA 회의 | 매주 | LAM |
| 개발관리실 정기회의 | 매주 월요일 | LAM |
| AI TF 정기회의 | 매주 | LAM |
| 각종 킥오프/개발 회의 | 수시 | LAM |

---

### [주간 보고서 조회] atlassian Confluence 도구

#### 주간 보고서 검색
```
도구: mcp__atlassian__confluence_search
파라미터: query='title ~ "주간보고" AND title ~ "YYYY-MM" AND type=page', limit=10
```

**사용 예시 (자연어):**
- "지난 주 보고 내용 요약해 줘"
- "이번 주 모바일스튜디오 주간보고 알려줘"
- "4월 첫째 주 보고 요약해 줘"

**동작 방식:**
1. `confluence_search`로 해당 기간 주간보고 페이지 검색
2. `confluence_get_page`로 상세 내용 조회 (문서 크기가 클 수 있음)
3. 부서별 주요 내용 요약하여 출력

**검색 CQL 패턴:**
| 요청 | CQL query |
|---|---|
| 모바일스튜디오 주간보고 | `title ~ "모바일스튜디오 주간보고" AND title ~ "YYYY-MM"` |
| 특정 부서 보고 | `title ~ "주간" AND title ~ "보고" AND created >= "시작일" AND created <= "종료일"` |
| 특정 날짜 보고 | `title ~ "주간보고" AND title ~ "YYYY-MM-DD"` |

**주간보고 주요 문서:**
| 문서명 | 주기 | 스페이스 | 내용 |
|---|---|---|---|
| 모바일스튜디오 주간보고 | 매주 목요일 작성 | LAM | 마일스톤 현황, 부서별 이슈, 인사, 전체 업무 현황 |
| 주간 업무 보고 (QA) | 매주 | QA | QA팀 파트별 업무 현황 |
| 주간업무보고 (서버) | 매주 | SERVER | 서버팀 업무 현황 |

**출력 형식 (주간보고 요약):**
```
# YYYY-MM-DD 모바일스튜디오 주간보고

## 마일스톤 현황
- 기간, 목표, 주요 일정

## 인사 발령
| 구분 | 내용 |

## 부서별 주요 업무
### 기획실
- 주요 업무 bullet point

### 개발실
**완료:** 완료 항목
**진행 중:** 진행 항목

### 개발관리실
- 주요 업무 bullet point
```

**참고 사항:**
- 주간보고는 문서 크기가 매우 클 수 있음 (50,000자 이상) → 부서별 핵심만 요약
- 마일스톤 현황, 인사 발령, 기획실 리뷰 일정 등 주요 항목 위주로 정리
- Hansoft 태스크 링크는 `http://lam.sgr.com/{id}` 형식으로 변환하여 표시

---

## 답변 형식 규칙

업무 현황 관련 답변은 항상 아래 컬럼 순서로 테이블 출력:

| 조직 | 담당자 | 업무 | 상태 | 시작 | 마감 |

- **조직**: 부서명 전체 (예: 기획실 컨텐츠기획팀)
- **업무**: 클릭 가능한 링크로 표시 (Hansoft: `http://lam.sgr.com/{id}`, Jira: `https://jira.sgr.com/browse/{id}`)
- **날짜**: MM-DD(요일) 형식 (예: 04-13(월))

---

## 링크 규칙

| 타입 | URL 형식 |
|---|---|
| Hansoft | `http://lam.sgr.com/{task_id}` |
| Jira | `https://jira.sgr.com/browse/{task_id}` |
| Confluence | `https://wiki.sgr.com/pages/viewpage.action?pageId={id}` |

---

## 참고 사항

- 담당자 검색은 **부분 일치** (예: "김상현" → 김상현A, 김상현C 모두 조회됨)
- 기본 그룹 ID는 `1` (로스트아크 모바일)
- SSL 인증서 검증 비활성화 환경 (사내망)
- 서버 실행: `python C:\Users\jangwonpark\mcp-lamweb\server.py`
