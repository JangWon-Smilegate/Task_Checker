const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";

const s = pres.addSlide();
s.background = { color: "ECEEF2" };

// ── Colors ─────────────────────────────────────────────────
const NAVY     = "1A1E35";
const ENG_BG   = "22263A";
const ENG_ITEM = "2E3455";
const ENG_BDR  = "3D4470";
const GRP_BG   = "FFFFFF";
const GRP_BDR  = "C8CAD0";
const HDR_BG   = "E2E5EC";
const ITEM_BG  = "F0F1F5";
const ITEM_BDR = "C8CAD0";
const WHITE    = "FFFFFF";
const TXT_DRK  = "252535";
const TXT_MID  = "444455";
const TXT_LIT  = "888899";
const ENG_TXT  = "C8D4F0";
const SUB_TXT  = "9AAACB";
const COL_LBL  = "666677";

// ── Column positions ────────────────────────────────────────
const C1X = 0.08, C1W = 1.78;
const C2X = 1.92, C2W = 1.82;
const C3X = 3.80, C3W = 2.38;
const C4X = 6.24, C4W = 3.68;

// ── Row dimensions ──────────────────────────────────────────
const IH  = 0.21;   // item height
const HH  = 0.25;   // group header height
const GAP = 0.05;   // gap between groups

// ── Y positions ─────────────────────────────────────────────
const TH  = 0.55;              // title bar height
const CLY = TH  + 0.02;       // column label Y
const CLH = 0.22;              // column label height
const CY  = CLY + CLH + 0.04; // content start Y ≈ 0.83
const LY  = 5.28;              // legend Y
const LH  = 0.25;              // legend height

// ── Helpers ─────────────────────────────────────────────────
const R = (x, y, w, h, fill, bdr) =>
  s.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: fill },
    line: bdr ? { color: bdr, width: 0.5 } : { color: fill },
  });

const T = (text, x, y, w, h, o = {}) =>
  s.addText(text, {
    x, y, w, h,
    fontSize: o.sz || 8.5,
    color:    o.c  || TXT_MID,
    fontFace: "Calibri",
    bold:     o.b  || false,
    italic:   o.i  || false,
    align:    o.al || "center",
    valign:   o.va || "middle",
    margin:   0,
  });

function btn(x, y, w, h, text, o = {}) {
  R(x, y, w, h, o.bg || ITEM_BG, o.bdr || ITEM_BDR);
  T(text, x, y, w, h, { sz: o.sz || 8.5, c: o.c || TXT_MID, b: o.b });
}

function grp(x, y, w, header, items, o = {}) {
  const ih = o.ih || IH, hh = o.hh || HH;
  const total = hh + items.length * ih;
  R(x, y, w, total, o.gbg || GRP_BG, o.gbdr || GRP_BDR);
  R(x, y, w, hh,    o.hbg || HDR_BG, o.gbdr || GRP_BDR);
  T(header, x, y, w, hh, { sz: 9, c: TXT_DRK, b: true });
  items.forEach((item, i) => {
    const p = 0.04;
    btn(x + p, y + hh + i * ih + p / 2, w - p * 2, ih - p, item,
      { bg: o.ibg, bdr: o.ibdr, sz: 8.5, c: o.ic });
  });
  return total;
}

// ── Title Bar ───────────────────────────────────────────────
R(0, 0, 10, TH, NAVY, NAVY);
T("LLM 기반 통합 검색·수정 시스템 아키텍처",
  0.15, 0.04, 9.7, 0.3, { sz: 17, c: WHITE, b: true, al: "left" });
T("Hansoft · Jira · Confluence 연동  —  Query / RAG / 스케줄링 / 회의록 자동화",
  0.15, 0.35, 9.7, 0.18, { sz: 9, c: SUB_TXT, al: "left" });

// ── Column Labels ───────────────────────────────────────────
[
  [C1X, C1W, "입력 · 트리거"],
  [C2X, C2W, "처리 엔진"],
  [C3X, C3W, "출력 · 결과"],
  [C4X, C4W, "연동 플랫폼"],
].forEach(([x, w, lbl]) =>
  T(lbl, x, CLY, w, CLH, { sz: 9, c: COL_LBL, al: "left" }));

// ══════════════════════════════════════════════════════════════
// COL 1 — 입력·트리거
// ══════════════════════════════════════════════════════════════
let y1 = CY;
y1 += grp(C1X, y1, C1W, "유저",
  ["Slack", "Claude", "ChatGPT"]) + GAP;
y1 += grp(C1X, y1, C1W, "스케줄러",
  ["Cron·주기 설정", "일별·주별·월별"]) + GAP;
grp(C1X, y1, C1W, "회의록 녹음",
  ["파일 업로드", "실시간 스트리밍"]);

// ══════════════════════════════════════════════════════════════
// COL 2 — 처리 엔진 (dark)
// ══════════════════════════════════════════════════════════════
const ENG_ITEMS = [
  "의도 분석", "쿼리 변환", "STT 처리", "액션 추출",
  "응답 생성", "보고서 포맷팅", "Tool Calling", "회의록 요약",
];
const EHH = 0.35, EIH = 0.30, EPAD = 0.09;
const ENG_H = EHH + ENG_ITEMS.length * EIH + EPAD * 2;

R(C2X, CY, C2W, ENG_H, ENG_BG, ENG_BG);
R(C2X, CY, C2W, EHH, NAVY, NAVY);
T("LLM 통합 엔진", C2X, CY, C2W, EHH, { sz: 11, c: WHITE, b: true });

ENG_ITEMS.forEach((item, i) => {
  const iy = CY + EHH + EPAD + i * EIH;
  const p  = 0.07;
  R(C2X + p, iy, C2W - p * 2, EIH - 0.04, ENG_ITEM, ENG_BDR);
  T(item, C2X + p, iy, C2W - p * 2, EIH - 0.04, { sz: 9, c: ENG_TXT });
});

// ══════════════════════════════════════════════════════════════
// COL 3 — 출력·결과
// ══════════════════════════════════════════════════════════════
let y3 = CY;
y3 += grp(C3X, y3, C3W, "유저 니즈",
  ["이슈 검색", "상태 변경", "문서 검색 (RAG)", "진행 보고", "일정 조회", "문서 수정"]) + GAP;
y3 += grp(C3X, y3, C3W, "보고서 생성",
  ["주간 스프린트 보고서", "리소스 현황 보고서", "마감 임박 알림",
   "품질 지표 보고서", "릴리즈 노트", "문서 변경 요약"]) + GAP;
grp(C3X, y3, C3W, "회의록 자동화",
  ["회의록 문서 생성", "액션 아이템 추출", "Task 자동 생성", "참석자 공유"]);

// ══════════════════════════════════════════════════════════════
// COL 4 — 연동 플랫폼
// ══════════════════════════════════════════════════════════════
let y4 = CY;
const PW = 1.2, AW = 0.22, BW = 0.7;

function secLabel(y, text) {
  T(text, C4X, y, C4W, 0.20, { sz: 8.5, c: "555566", al: "left" });
  s.addShape(pres.shapes.LINE, {
    x: C4X, y: y + 0.20, w: C4W, h: 0,
    line: { color: "BBBBCC", width: 0.5 },
  });
  return 0.25;
}

function platRow(y, platName, pc, badgeText, bc, desc) {
  const rh = 0.36, p = 0.04;
  // Platform box
  R(C4X, y + p, PW, rh - p * 2, pc, pc);
  T(platName, C4X, y + p, PW, rh - p * 2, { sz: 9, c: WHITE, b: true });

  let nx = C4X + PW;
  if (badgeText) {
    T("→", nx, y + p, AW, rh - p * 2, { sz: 10, c: "999AAA" });
    nx += AW;
    R(nx, y + p, BW, rh - p * 2, bc, bc);
    T(badgeText, nx, y + p, BW, rh - p * 2, { sz: 8, c: WHITE, b: true });
    nx += BW;
  }
  const descX = nx + 0.07;
  const descW = C4X + C4W - descX - 0.04;
  T(desc, descX, y + p, descW, rh - p * 2, { sz: 8.5, c: TXT_LIT, al: "left" });
  return rh;
}

// Section 1 — 일반 조회·수정
y4 += secLabel(y4, "일반 조회 · 수정");
y4 += platRow(y4, "Hansoft",    "C5374A", "Query", "1D4ED8", "태스크 · 일정");
y4 += platRow(y4, "Jira",       "0047AB", "Query", "1D4ED8", "이슈 · JQL");
y4 += platRow(y4, "Confluence", "0055CC", "RAG",   "6D28D9", "문서 · 벡터");
y4 += 0.1;

// Section 2 — 회의록 연동
y4 += secLabel(y4, "회의록 연동");
y4 += platRow(y4, "Confluence",    "0055CC", "자동 저장", "047857", "페이지 생성");
y4 += platRow(y4, "Jira / Hansoft","444466", "이슈 생성", "B45309", "담당자 · 기한");
y4 += 0.1;

// Section 3 — 보고서 데이터 수집
y4 += secLabel(y4, "보고서 데이터 수집");
y4 += platRow(y4, "Hansoft",    "C5374A", null, null, "리소스 · 일정 데이터");
y4 += platRow(y4, "Jira",       "0047AB", null, null, "이슈 · 스프린트 데이터");
      platRow(y4, "Confluence", "0055CC", null, null, "문서 변경 내역");

// ── Legend ──────────────────────────────────────────────────
R(0, LY, 10, LH, "DDE0E8", "DDE0E8");

s.addShape(pres.shapes.LINE, {
  x: 0.15, y: LY + LH / 2, w: 0.3, h: 0,
  line: { color: "333355", width: 1.5 },
});
T("유저 요청 흐름", 0.5, LY, 1.6, LH, { sz: 8, c: "444455", al: "left" });

s.addShape(pres.shapes.LINE, {
  x: 2.3, y: LY + LH / 2, w: 0.3, h: 0,
  line: { color: "333355", width: 1.5, dashType: "dash" },
});
T("스케줄 / 회의록 흐름", 2.65, LY, 1.8, LH, { sz: 8, c: "444455", al: "left" });

s.addShape(pres.shapes.LINE, {
  x: 4.55, y: LY + LH / 2, w: 0.3, h: 0,
  line: { color: "333355", width: 1.5, dashType: "dashDot" },
});
T("통제된 AI 흐름", 4.9, LY, 1.5, LH, { sz: 8, c: "444455", al: "left" });

T("LLM Integration Architecture  ·  1 / 1", 0, LY, 9.85, LH, {
  sz: 8, c: "999999", al: "right",
});

// ── Save ────────────────────────────────────────────────────
pres.writeFile({ fileName: "D:/Git/lam/LLM_아키텍처.pptx" })
  .then(() => console.log("✅ D:/Git/lam/LLM_아키텍처.pptx"))
  .catch(e => { console.error("❌", e); process.exit(1); });
