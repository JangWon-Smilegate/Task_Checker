const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
const s = pres.addSlide();
s.background = { color: "EBEBEF" };

const FONT = "Rix락-Sans Medium";

// ── Colors (Grey tone) ───────────────────────────────────
const NAVY    = "2E2E38";
const ENG_ITEM= "3C3C48";
const ENG_BDR = "505060";
const ENG_TXT = "D2D4DC";
const ENG_SEC = "383842";
const ENG_SEC_B= "484852";
const WHITE   = "FFFFFF";
const GRP_BG  = "FFFFFF";
const GRP_BDR = "C0C0C8";
const HDR_BG  = "E6E6EA";
const ITEM_BG = "F0F0F4";
const ITEM_BDR= "CCCCD2";
const TXT_DRK = "2A2A32";
const TXT_MID = "48484F";
const FRM_BG  = "F4F4F6";
const FRM_BDR = "BBBBC4";
const FRM_HDR = "E4E4EA";
const LLM_BDR = "303038";

const BLUE   = "5B7DB8";
const BLUE2  = "7B7DB8";
const AMBER  = "B08830";
const GREEN  = "4A9070";
const PURPLE = "7030A0";

// ── Layout ────────────────────────────────────────────────
// Frames
const FRM_Y = 0.90, FRM_H = 3.85, FRM_HDR_H = 0.30;
const LF_X = 0.20, LF_W = 1.56;              // Left frame
const RF_X = 7.50, RF_W = 2.30;              // Right frame

// LLM box (outline only, centered between frames)
const LLM_X = 2.53, LLM_W = 4.20;
const LLM_Y = 1.93, LLM_H = 2.10;

// LLM internal grid (3 cols × 2 rows)
const GW = 1.18;                              // Group width
const COL_GAP = 0.19;
const ROW_GAP = 0.10;
const C1X = LLM_X + 0.14;
const C2X = C1X + GW + COL_GAP;
const C3X = C2X + GW + COL_GAP;
const R1Y = LLM_Y + 0.06 + 0.22 + 0.08;      // After label
const R2Y = R1Y + 0.71 + ROW_GAP;             // After row 1 max height

// ── Helpers ───────────────────────────────────────────────
const RC = (x, y, w, h, fill, bdr) =>
  s.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: fill },
    line: bdr ? { color: bdr, width: 0.5 } : { color: fill },
  });

const TX = (text, x, y, w, h, o = {}) =>
  s.addText(text, {
    x, y, w, h,
    fontSize: o.sz || 8, color: o.c || TXT_MID,
    fontFace: FONT, bold: o.b || false,
    align: o.al || "center", valign: o.va || "middle", margin: 0,
  });

function inputCell(x, y, w, h, header, items, accent) {
  const hh = 0.22, pad = 0.035;
  const iH = Math.min(0.17, (h - hh - 0.06) / Math.max(items.length, 1));

  RC(x, y, w, h, GRP_BG, GRP_BDR);
  RC(x, y, 0.04, h, accent, accent);
  RC(x, y, w, hh, HDR_BG, GRP_BDR);
  RC(x, y, 0.04, hh, accent, accent);
  TX(header, x + 0.10, y, w - 0.15, hh, { sz: 8.5, c: TXT_DRK, b: true, al: "left" });

  items.forEach((it, i) => {
    const iy = y + hh + 0.03 + i * iH;
    RC(x + pad + 0.04, iy, w - pad * 2 - 0.04, iH - 0.025, ITEM_BG, ITEM_BDR);
    TX(it, x + pad + 0.04, iy, w - pad * 2 - 0.04, iH - 0.025, { sz: 7.5, c: TXT_MID });
  });
}

function llmGroup(x, y, w, header, items, accent) {
  const hh = 0.18, pad = 0.03;
  const iH = 0.125;
  const totalH = hh + items.length * iH + 0.03;

  RC(x, y, w, totalH, ENG_SEC, ENG_SEC_B);
  RC(x, y, 0.04, totalH, accent, accent);
  TX(header, x + 0.08, y, w - 0.12, hh, { sz: 8, c: WHITE, b: true, al: "left" });

  items.forEach((it, i) => {
    const iy = y + hh + 0.015 + i * iH;
    if (it === "…") {
      RC(x + pad + 0.035, iy, w - pad * 2 - 0.035, iH - 0.02, ENG_ITEM, ENG_BDR);
      TX(it, x + pad + 0.035, iy, w - pad * 2 - 0.035, iH - 0.02, { sz: 6.5, c: ENG_BDR });
    } else {
      RC(x + pad + 0.035, iy, w - pad * 2 - 0.035, iH - 0.02, ENG_ITEM, ENG_BDR);
      TX(it, x + pad + 0.035, iy, w - pad * 2 - 0.035, iH - 0.02, { sz: 6.5, c: ENG_TXT });
    }
  });

  return totalH;
}

// ══════════════════════════════════════════════════════════
// TITLE BAR
// ══════════════════════════════════════════════════════════
RC(0, 0, 10, 0.45, NAVY, NAVY);
TX("LLM 기반 업무 효율화 — 시스템 플로우", 0.15, 0.02, 9.7, 0.43, {
  sz: 16, c: WHITE, b: true, al: "left",
});

// ══════════════════════════════════════════════════════════
// LEFT FRAME (입력 · 트리거)
// ══════════════════════════════════════════════════════════
RC(LF_X, FRM_Y, LF_W, FRM_H, FRM_BG, FRM_BDR);
RC(LF_X, FRM_Y, LF_W, FRM_HDR_H, FRM_HDR, FRM_BDR);
TX("입력 · 트리거", LF_X + 0.08, FRM_Y, LF_W - 0.16, FRM_HDR_H, {
  sz: 9, c: TXT_DRK,
});

// Input cells (centered horizontally, evenly spaced vertically)
{
  const cx = LF_X + (LF_W - 1.20) / 2;
  const contentTop = FRM_Y + FRM_HDR_H;
  const contentH = FRM_H - FRM_HDR_H;
  const totalCellH = 0.77 + 0.60 + 0.76;      // sum of cell heights
  const gap = (contentH - totalCellH) / 4;     // equal spacing top/between/bottom

  inputCell(cx, contentTop + gap, 1.20, 0.77,
    "유저", ["Slack", "Claude", "ChatGPT"], BLUE);
  inputCell(cx, contentTop + gap + 0.77 + gap, 1.20, 0.60,
    "스케줄러", ["주기 · 내용 설정", "일별 · 주별 · 월별"], AMBER);
  inputCell(cx, contentTop + gap + 0.77 + gap + 0.60 + gap, 1.20, 0.76,
    "회의록 녹음", ["파일 업로드", "실시간 스트리밍"], GREEN);
}

// ══════════════════════════════════════════════════════════
// RIGHT FRAME (연동 플랫폼)
// ══════════════════════════════════════════════════════════
RC(RF_X, FRM_Y, RF_W, FRM_H, FRM_BG, FRM_BDR);
RC(RF_X, FRM_Y, RF_W, FRM_HDR_H, FRM_HDR, FRM_BDR);
TX("연동 플랫폼", RF_X + 0.08, FRM_Y, RF_W - 0.16, FRM_HDR_H, {
  sz: 9, c: TXT_DRK,
});

// Platform cells (centered)
{
  const cx = RF_X + (RF_W - 1.20) / 2;
  const contentTop = FRM_Y + FRM_HDR_H;
  const contentH = FRM_H - FRM_HDR_H;
  const cellH = 0.77;
  const platGap = 0.30;
  const totalH = cellH * 2 + platGap;
  const topOffset = (contentH - totalH) / 2;

  inputCell(cx, contentTop + topOffset, 1.20, cellH,
    "Hansoft / Jira", ["Task · 일정 조회", "Task 생성 · 업데이트", "…"], BLUE);
  inputCell(cx, contentTop + topOffset + cellH + platGap, 1.20, cellH,
    "Confluence", ["문서 검색 (RAG)", "변경 내용 추적", "…"], BLUE);
}

// ══════════════════════════════════════════════════════════
// LLM BOX (outline only)
// ══════════════════════════════════════════════════════════
s.addShape(pres.shapes.RECTANGLE, {
  x: LLM_X, y: LLM_Y, w: LLM_W, h: LLM_H,
  line: { color: LLM_BDR, width: 0.5 },
});
TX("LLM", LLM_X + 0.08, LLM_Y + 0.04, 1.0, 0.22, {
  sz: 9, c: TXT_MID, al: "left",
});

// ── Row 1: In / 일정 / 지식 검색 ──────────────────────────
llmGroup(C1X, R1Y, GW, "In",
  ["의도 분석", "Query 생성", "STT", "…"], PURPLE);

llmGroup(C2X, R1Y, GW, "일정",
  ["업무 현황 조회", "지연 조회", "Task 생성", "…"], BLUE);

llmGroup(C3X, R1Y, GW, "지식 검색",
  ["문서 검색", "문서 요약", "…"], BLUE2);

// ── Row 2: Out / 회의록 / 보고서 ──────────────────────────
llmGroup(C1X, R2Y, GW, "Out",
  ["응답 생성", "보고서 생성", "외부 툴 호출", "…"], PURPLE);

llmGroup(C2X, R2Y, GW, "회의록",
  ["회의록 요약", "Task 생성", "참석자 공유", "…"], GREEN);

llmGroup(C3X, R2Y, GW, "보고서",
  ["일간 보고 (개인/조직)", "주간 보고 (개인/조직)", "지연 알림", "일정 마감 알림", "…"], AMBER);

// ── Save ──────────────────────────────────────────────────
pres.writeFile({ fileName: "D:/Git/lam/LLM_플로우.pptx" })
  .then(() => console.log("✅ D:/Git/lam/LLM_플로우.pptx"))
  .catch(e => { console.error("❌", e); process.exit(1); });
