const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "LLM을 활용한 업무 효율화 방안";

// ── Color Palette ──────────────────────────────────────────
const C = {
  navy:    "1E2761",
  blue:    "2D4B9E",
  iceBlue: "CADCFC",
  sky:     "7DA7E0",
  white:   "FFFFFF",
  offWhite:"F4F7FE",
  gray:    "64748B",
  darkGray:"334155",
  accent:  "3B82F6",
  green:   "22C55E",
};

const makeShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.12 });

// ══════════════════════════════════════════════════════════════
// SLIDE 1 — Title
// ══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // Left accent bar
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.35, h: 5.625, fill: { color: C.accent } });

  // Decorative circle (top-right)
  s.addShape(pres.shapes.OVAL, { x: 7.8, y: -0.8, w: 3.5, h: 3.5, fill: { color: C.blue, transparency: 60 }, line: { color: C.blue, transparency: 60 } });
  s.addShape(pres.shapes.OVAL, { x: 8.5, y: 3.2, w: 2.2, h: 2.2, fill: { color: C.accent, transparency: 70 }, line: { color: C.accent, transparency: 70 } });

  // Tag
  s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 1.0, w: 2.2, h: 0.38, fill: { color: C.accent }, line: { color: C.accent } });
  s.addText("AI 업무 혁신", { x: 0.7, y: 1.0, w: 2.2, h: 0.38, fontSize: 12, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });

  // Title
  s.addText("LLM을 활용한", { x: 0.7, y: 1.6, w: 8.5, h: 0.75, fontSize: 40, color: C.iceBlue, bold: true, fontFace: "Calibri", margin: 0 });
  s.addText("업무 효율화 방안", { x: 0.7, y: 2.35, w: 8.5, h: 0.75, fontSize: 40, color: C.white, bold: true, fontFace: "Calibri", margin: 0 });

  // Subtitle
  s.addText("Slack · Claude · ChatGPT  →  Hansoft · Jira · Confluence", {
    x: 0.7, y: 3.3, w: 8.5, h: 0.45,
    fontSize: 16, color: C.iceBlue, fontFace: "Calibri", margin: 0,
  });

  // Bottom line
  s.addShape(pres.shapes.LINE, { x: 0.7, y: 4.85, w: 8.6, h: 0, line: { color: C.sky, width: 1, transparency: 50 } });
  s.addText("2026", { x: 0.7, y: 5.0, w: 2, h: 0.3, fontSize: 11, color: C.sky, margin: 0 });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 2 — 현황 및 문제점
// ══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };

  // Top header bar
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("현황 및 문제점", { x: 0.5, y: 0, w: 9, h: 0.75, fontSize: 22, color: C.white, bold: true, fontFace: "Calibri", valign: "middle", margin: 0 });

  const problems = [
    { icon: "🔍", title: "정보 파편화", desc: "업무 정보가 Hansoft·Jira·Confluence에 분산\n필요한 정보를 찾는 데 과도한 시간 소모" },
    { icon: "🔄", title: "반복적 컨텍스트 전환", desc: "여러 도구를 오가며 진행 상황 확인\n업무 흐름이 끊기고 집중력 저하" },
    { icon: "⏱️", title: "보고 및 공유 비효율", desc: "현황 취합·정리에 많은 시간 투입\n최신 정보 반영이 늦어 의사결정 지연" },
    { icon: "🤝", title: "협업 도구 미활용", desc: "Slack 등 채팅 도구가 단순 메시지 전달에 그침\n업무 시스템과의 연계 부재" },
  ];

  const cols = [0.4, 5.2];
  problems.forEach((p, i) => {
    const col = cols[i % 2];
    const row = i < 2 ? 1.0 : 3.0;
    const bw = 4.4, bh = 1.7;

    s.addShape(pres.shapes.RECTANGLE, { x: col, y: row, w: bw, h: bh, fill: { color: C.white }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
    // Accent left border
    s.addShape(pres.shapes.RECTANGLE, { x: col, y: row, w: 0.06, h: bh, fill: { color: C.accent }, line: { color: C.accent } });

    s.addText(p.icon + "  " + p.title, { x: col + 0.15, y: row + 0.18, w: bw - 0.25, h: 0.4, fontSize: 16, color: C.navy, bold: true, fontFace: "Calibri", margin: 0 });
    s.addText(p.desc, { x: col + 0.15, y: row + 0.65, w: bw - 0.3, h: 0.9, fontSize: 13, color: C.darkGray, fontFace: "Calibri", margin: 0 });
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 3 — 솔루션 개요
// ══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("솔루션 개요", { x: 0.5, y: 0, w: 9, h: 0.75, fontSize: 22, color: C.white, bold: true, fontFace: "Calibri", valign: "middle", margin: 0 });

  // Central concept box
  s.addShape(pres.shapes.RECTANGLE, { x: 3.0, y: 1.05, w: 4.0, h: 1.1, fill: { color: C.navy }, line: { color: C.navy }, shadow: makeShadow() });
  s.addText("LLM 기반 업무 통합 허브", { x: 3.0, y: 1.05, w: 4.0, h: 1.1, fontSize: 17, color: C.white, bold: true, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

  // Left column — 입력 채널
  s.addShape(pres.shapes.RECTANGLE, { x: 0.35, y: 0.95, w: 2.3, h: 0.45, fill: { color: C.blue }, line: { color: C.blue } });
  s.addText("입력 채널", { x: 0.35, y: 0.95, w: 2.3, h: 0.45, fontSize: 14, color: C.white, bold: true, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

  const inputs = [
    { name: "Slack", color: "4A154B", desc: "채팅 / BOT" },
    { name: "Claude", color: "D97706", desc: "AI 어시스턴트" },
    { name: "ChatGPT", color: "10A37F", desc: "AI 어시스턴트" },
  ];
  inputs.forEach((item, i) => {
    const y = 1.55 + i * 1.1;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.35, y, w: 2.3, h: 0.85, fill: { color: C.white }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.35, y, w: 0.06, h: 0.85, fill: { color: item.color }, line: { color: item.color } });
    s.addText(item.name, { x: 0.5, y: y + 0.05, w: 2.1, h: 0.38, fontSize: 15, color: C.navy, bold: true, fontFace: "Calibri", margin: 0 });
    s.addText(item.desc, { x: 0.5, y: y + 0.45, w: 2.1, h: 0.3, fontSize: 11, color: C.gray, fontFace: "Calibri", margin: 0 });
  });

  // Right column — 연동 시스템
  s.addShape(pres.shapes.RECTANGLE, { x: 7.35, y: 0.95, w: 2.3, h: 0.45, fill: { color: C.blue }, line: { color: C.blue } });
  s.addText("연동 시스템", { x: 7.35, y: 0.95, w: 2.3, h: 0.45, fontSize: 14, color: C.white, bold: true, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

  const outputs = [
    { name: "Hansoft", color: "E11D48", desc: "프로젝트 관리" },
    { name: "Jira", color: "0052CC", desc: "이슈 트래킹" },
    { name: "Confluence", color: "0065FF", desc: "문서 관리" },
  ];
  outputs.forEach((item, i) => {
    const y = 1.55 + i * 1.1;
    s.addShape(pres.shapes.RECTANGLE, { x: 7.35, y, w: 2.3, h: 0.85, fill: { color: C.white }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 7.35, y, w: 0.06, h: 0.85, fill: { color: item.color }, line: { color: item.color } });
    s.addText(item.name, { x: 7.5, y: y + 0.05, w: 2.1, h: 0.38, fontSize: 15, color: C.navy, bold: true, fontFace: "Calibri", margin: 0 });
    s.addText(item.desc, { x: 7.5, y: y + 0.45, w: 2.1, h: 0.3, fontSize: 11, color: C.gray, fontFace: "Calibri", margin: 0 });
  });

  // Arrows  left → center
  s.addShape(pres.shapes.LINE, { x: 2.65, y: 2.0, w: 0.35, h: 0, line: { color: C.accent, width: 2 } });
  s.addShape(pres.shapes.LINE, { x: 2.65, y: 3.1, w: 0.35, h: 0, line: { color: C.accent, width: 2 } });
  s.addShape(pres.shapes.LINE, { x: 2.65, y: 4.2, w: 0.35, h: 0, line: { color: C.accent, width: 2 } });
  // center → right
  s.addShape(pres.shapes.LINE, { x: 7.0, y: 2.0, w: 0.35, h: 0, line: { color: C.accent, width: 2 } });
  s.addShape(pres.shapes.LINE, { x: 7.0, y: 3.1, w: 0.35, h: 0, line: { color: C.accent, width: 2 } });
  s.addShape(pres.shapes.LINE, { x: 7.0, y: 4.2, w: 0.35, h: 0, line: { color: C.accent, width: 2 } });

  // Bottom tagline
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.2, w: 10, h: 0.425, fill: { color: C.iceBlue }, line: { color: C.iceBlue } });
  s.addText("자연어 질의 한 줄로 업무 현황·문서를 즉시 검색하고 결과를 채팅 채널에 출력", {
    x: 0.5, y: 5.2, w: 9, h: 0.425,
    fontSize: 13, color: C.navy, bold: true, fontFace: "Calibri", align: "center", valign: "middle", margin: 0,
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 4 — 시스템 플로우 다이어그램
// ══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: "162050" }, line: { color: "162050" } });
  s.addText("시스템 플로우", { x: 0.5, y: 0, w: 9, h: 0.75, fontSize: 22, color: C.white, bold: true, fontFace: "Calibri", valign: "middle", margin: 0 });

  // Flow steps
  const steps = [
    { num: "1", label: "사용자 요청", sub: "Slack / Claude\nChatGPT 채팅", color: "4A154B" },
    { num: "2", label: "LLM 처리", sub: "의도 분석\n쿼리 생성", color: C.accent },
    { num: "3", label: "API 연동", sub: "Hansoft / Jira\nConfluence API", color: "0052CC" },
    { num: "4", label: "결과 출력", sub: "채팅 채널에\n요약·링크 반환", color: C.green },
  ];

  const boxW = 1.8, boxH = 2.0;
  const startX = 0.55;
  const gapX = 0.55; // space between boxes for arrow
  const y = 1.5;

  steps.forEach((step, i) => {
    const x = startX + i * (boxW + gapX + 0.5);

    // Card
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: boxW, h: boxH,
      fill: { color: "253882" }, line: { color: "3B52A0", width: 1 },
      shadow: makeShadow(),
    });

    // Number badge
    s.addShape(pres.shapes.OVAL, { x: x + 0.65, y: y + 0.12, w: 0.5, h: 0.5, fill: { color: step.color }, line: { color: step.color } });
    s.addText(step.num, { x: x + 0.65, y: y + 0.12, w: 0.5, h: 0.5, fontSize: 14, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });

    // Label
    s.addText(step.label, { x: x + 0.1, y: y + 0.75, w: boxW - 0.2, h: 0.5, fontSize: 15, color: C.white, bold: true, fontFace: "Calibri", align: "center", margin: 0 });

    // Sub description
    s.addText(step.sub, { x: x + 0.1, y: y + 1.3, w: boxW - 0.2, h: 0.6, fontSize: 12, color: C.iceBlue, fontFace: "Calibri", align: "center", margin: 0 });

    // Arrow (not after last)
    if (i < steps.length - 1) {
      const ax = x + boxW + 0.1;
      s.addShape(pres.shapes.LINE, { x: ax, y: y + boxH / 2, w: gapX + 0.3, h: 0, line: { color: C.sky, width: 2 } });
      s.addText("▶", { x: ax + gapX + 0.1, y: y + boxH / 2 - 0.18, w: 0.3, h: 0.35, fontSize: 14, color: C.sky, margin: 0 });
    }
  });

  // Bottom note
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.8, w: 9.0, h: 0.55, fill: { color: "253882" }, line: { color: "3B52A0", width: 1 } });
  s.addText("사용자는 채팅 창에서 자연어로 질문 → LLM이 적절한 API를 선택·호출 → 결과를 요약하여 채널에 게시", {
    x: 0.5, y: 4.8, w: 9.0, h: 0.55,
    fontSize: 13, color: C.iceBlue, fontFace: "Calibri", align: "center", valign: "middle", margin: 0,
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 5 — 주요 기능
// ══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("주요 기능", { x: 0.5, y: 0, w: 9, h: 0.75, fontSize: 22, color: C.white, bold: true, fontFace: "Calibri", valign: "middle", margin: 0 });

  const features = [
    {
      icon: "💬", title: "업무 현황 조회",
      items: ["\"이번 스프린트 미완료 이슈 보여줘\"", "\"오늘 마감 태스크 목록\"", "Jira·Hansoft 실시간 쿼리"],
    },
    {
      icon: "📄", title: "문서 검색 & 요약",
      items: ["\"API 인증 가이드 찾아줘\"", "\"QA 체크리스트 요약해줘\"", "Confluence 전문 검색 + AI 요약"],
    },
    {
      icon: "🔔", title: "알림 & 리포트 자동화",
      items: ["매일 오전 스프린트 요약 자동 게시", "PR·이슈 상태 변경 시 채널 알림", "주간 진행률 리포트 자동 생성"],
    },
    {
      icon: "🤖", title: "대화형 업무 지원",
      items: ["자연어로 이슈 생성·업데이트", "\"버그 이슈 만들어줘\" 즉시 처리", "담당자 지정·우선순위 설정 지원"],
    },
  ];

  const cols = [0.4, 5.2];
  features.forEach((f, i) => {
    const col = cols[i % 2];
    const row = i < 2 ? 0.95 : 3.15;
    const bw = 4.4, bh = 2.0;

    s.addShape(pres.shapes.RECTANGLE, { x: col, y: row, w: bw, h: bh, fill: { color: C.white }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: col, y: row, w: bw, h: 0.5, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText(f.icon + "  " + f.title, { x: col + 0.12, y: row, w: bw - 0.2, h: 0.5, fontSize: 15, color: C.white, bold: true, fontFace: "Calibri", valign: "middle", margin: 0 });

    f.items.forEach((item, j) => {
      s.addText([{ text: item, options: { bullet: true } }], {
        x: col + 0.2, y: row + 0.58 + j * 0.45, w: bw - 0.35, h: 0.42,
        fontSize: 13, color: C.darkGray, fontFace: "Calibri", margin: 0,
      });
    });
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 6 — 연동 시스템 상세
// ══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("연동 시스템 상세", { x: 0.5, y: 0, w: 9, h: 0.75, fontSize: 22, color: C.white, bold: true, fontFace: "Calibri", valign: "middle", margin: 0 });

  const systems = [
    {
      name: "Hansoft", color: "E11D48",
      apis: ["태스크 목록 조회 API", "진행 상태 업데이트", "담당자·마감일 조회"],
      usecase: "\"내 태스크 중 In Progress인 것들 보여줘\"",
    },
    {
      name: "Jira", color: "0052CC",
      apis: ["이슈 검색 (JQL)", "스프린트 현황 조회", "이슈 생성·업데이트"],
      usecase: "\"이번 스프린트 버그 이슈 현황은?\"",
    },
    {
      name: "Confluence", color: "0065FF",
      apis: ["페이지 전문 검색 API", "콘텐츠 조회·요약", "댓글·첨부파일 조회"],
      usecase: "\"온보딩 가이드 문서 찾아서 요약해줘\"",
    },
  ];

  systems.forEach((sys, i) => {
    const x = 0.4 + i * 3.1;
    const y = 0.95;
    const bw = 2.9, bh = 4.35;

    s.addShape(pres.shapes.RECTANGLE, { x, y, w: bw, h: bh, fill: { color: C.white }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: bw, h: 0.55, fill: { color: sys.color }, line: { color: sys.color } });
    s.addText(sys.name, { x: x + 0.15, y, w: bw - 0.2, h: 0.55, fontSize: 18, color: C.white, bold: true, fontFace: "Calibri", valign: "middle", margin: 0 });

    s.addText("제공 API", { x: x + 0.15, y: y + 0.65, w: bw - 0.2, h: 0.35, fontSize: 13, color: C.accent, bold: true, fontFace: "Calibri", margin: 0 });
    sys.apis.forEach((api, j) => {
      s.addText([{ text: api, options: { bullet: true } }], {
        x: x + 0.15, y: y + 1.05 + j * 0.4, w: bw - 0.25, h: 0.38,
        fontSize: 12, color: C.darkGray, fontFace: "Calibri", margin: 0,
      });
    });

    // Use-case box
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.1, y: y + 2.85, w: bw - 0.2, h: 1.3, fill: { color: C.offWhite }, line: { color: "DBEAFE", width: 1 } });
    s.addText("활용 예시", { x: x + 0.2, y: y + 2.95, w: bw - 0.35, h: 0.3, fontSize: 11, color: C.accent, bold: true, fontFace: "Calibri", margin: 0 });
    s.addText(sys.usecase, { x: x + 0.2, y: y + 3.28, w: bw - 0.35, h: 0.75, fontSize: 11, color: C.darkGray, fontFace: "Calibri", italic: true, margin: 0 });
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 7 — 기대 효과
// ══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("기대 효과", { x: 0.5, y: 0, w: 9, h: 0.75, fontSize: 22, color: C.white, bold: true, fontFace: "Calibri", valign: "middle", margin: 0 });

  // Big stat callouts
  const stats = [
    { val: "70%↓", label: "정보 검색 시간 단축", color: C.accent },
    { val: "3x", label: "업무 현황 공유 속도", color: "22C55E" },
    { val: "단일", label: "채팅 창에서 모든 업무 조회", color: "F59E0B" },
  ];

  stats.forEach((st, i) => {
    const x = 0.5 + i * 3.1;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 0.95, w: 2.8, h: 1.55, fill: { color: C.white }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y: 0.95, w: 2.8, h: 0.07, fill: { color: st.color }, line: { color: st.color } });
    s.addText(st.val, { x, y: 1.1, w: 2.8, h: 0.75, fontSize: 36, color: st.color, bold: true, fontFace: "Calibri", align: "center", margin: 0 });
    s.addText(st.label, { x, y: 1.88, w: 2.8, h: 0.5, fontSize: 13, color: C.darkGray, fontFace: "Calibri", align: "center", margin: 0 });
  });

  // Detail benefits
  const benefits = [
    { icon: "✅", title: "생산성 향상", desc: "반복적인 정보 수집 업무 자동화로 개발·기획에 집중하는 시간 확보" },
    { icon: "✅", title: "의사결정 가속화", desc: "실시간 현황 파악으로 병목 구간 즉시 확인, 빠른 의사결정 지원" },
    { icon: "✅", title: "협업 문화 개선", desc: "채팅 채널에서 누구나 업무 현황 조회 → 투명한 정보 공유 문화 정착" },
    { icon: "✅", title: "온보딩 가속화", desc: "신규 입사자가 채팅으로 문서 검색 → 도구 학습 시간 단축" },
  ];

  benefits.forEach((b, i) => {
    const x = i % 2 === 0 ? 0.4 : 5.2;
    const y = i < 2 ? 2.75 : 4.05;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.4, h: 0.95, fill: { color: C.white }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
    s.addText(b.icon + "  " + b.title, { x: x + 0.15, y: y + 0.08, w: 4.1, h: 0.35, fontSize: 14, color: C.navy, bold: true, fontFace: "Calibri", margin: 0 });
    s.addText(b.desc, { x: x + 0.15, y: y + 0.47, w: 4.1, h: 0.38, fontSize: 12, color: C.darkGray, fontFace: "Calibri", margin: 0 });
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 8 — 구현 로드맵
// ══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("구현 로드맵", { x: 0.5, y: 0, w: 9, h: 0.75, fontSize: 22, color: C.white, bold: true, fontFace: "Calibri", valign: "middle", margin: 0 });

  // Timeline base line
  s.addShape(pres.shapes.LINE, { x: 0.5, y: 2.1, w: 9.0, h: 0, line: { color: C.sky, width: 3 } });

  const phases = [
    {
      phase: "Phase 1", period: "1~2개월",
      color: C.accent,
      items: ["Jira API 연동", "Slack BOT 기본 구축", "업무 현황 조회 기능"],
    },
    {
      phase: "Phase 2", period: "3~4개월",
      color: "F59E0B",
      items: ["Confluence 검색 연동", "AI 요약 기능 추가", "Claude / ChatGPT 지원"],
    },
    {
      phase: "Phase 3", period: "5~6개월",
      color: C.green,
      items: ["Hansoft 전체 연동", "자동 리포트 생성", "이슈 생성·업데이트 지원"],
    },
  ];

  phases.forEach((p, i) => {
    const x = 0.7 + i * 3.05;

    // Dot on timeline
    s.addShape(pres.shapes.OVAL, { x: x + 0.9, y: 1.85, w: 0.5, h: 0.5, fill: { color: p.color }, line: { color: p.color } });

    // Card above timeline
    s.addShape(pres.shapes.RECTANGLE, { x, y: 0.9, w: 2.7, h: 0.9, fill: { color: p.color }, line: { color: p.color }, shadow: makeShadow() });
    s.addText(p.phase, { x, y: 0.9, w: 2.7, h: 0.45, fontSize: 15, color: C.white, bold: true, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });
    s.addText(p.period, { x, y: 1.35, w: 2.7, h: 0.45, fontSize: 13, color: C.white, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

    // Card below timeline
    s.addShape(pres.shapes.RECTANGLE, { x, y: 2.45, w: 2.7, h: 2.6, fill: { color: C.white }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y: 2.45, w: 0.06, h: 2.6, fill: { color: p.color }, line: { color: p.color } });
    p.items.forEach((item, j) => {
      s.addText([{ text: item, options: { bullet: true } }], {
        x: x + 0.15, y: 2.6 + j * 0.72, w: 2.45, h: 0.62,
        fontSize: 13, color: C.darkGray, fontFace: "Calibri", margin: 0,
      });
    });
  });
}

// ══════════════════════════════════════════════════════════════
// SLIDE 9 — 결론
// ══════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.35, h: 5.625, fill: { color: C.accent }, line: { color: C.accent } });
  s.addShape(pres.shapes.OVAL, { x: 7.5, y: -0.5, w: 3.5, h: 3.5, fill: { color: C.blue, transparency: 60 }, line: { color: C.blue, transparency: 60 } });
  s.addShape(pres.shapes.OVAL, { x: 8.2, y: 3.5, w: 2.0, h: 2.0, fill: { color: C.accent, transparency: 70 }, line: { color: C.accent, transparency: 70 } });

  s.addText("결론 및 제안", { x: 0.7, y: 0.7, w: 8, h: 0.6, fontSize: 28, color: C.iceBlue, bold: true, fontFace: "Calibri", margin: 0 });

  const points = [
    "Slack·Claude·ChatGPT를 채팅 인터페이스로 활용해 Hansoft·Jira·Confluence와 자연어로 연동",
    "별도 도구 전환 없이 채팅 창 하나로 모든 업무 현황 조회 및 문서 검색 가능",
    "단계적 구현(Phase 1→3)으로 리스크를 최소화하며 점진적 가치 제공",
    "장기적으로 이슈 자동 생성·업데이트까지 확장하여 완전한 AI 업무 어시스턴트 구현",
  ];

  points.forEach((pt, i) => {
    s.addShape(pres.shapes.OVAL, { x: 0.65, y: 1.55 + i * 0.85, w: 0.35, h: 0.35, fill: { color: C.accent }, line: { color: C.accent } });
    s.addText(String(i + 1), { x: 0.65, y: 1.55 + i * 0.85, w: 0.35, h: 0.35, fontSize: 13, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(pt, { x: 1.15, y: 1.55 + i * 0.85, w: 7.8, h: 0.7, fontSize: 14, color: C.iceBlue, fontFace: "Calibri", valign: "middle", margin: 0 });
  });

  s.addShape(pres.shapes.LINE, { x: 0.7, y: 5.1, w: 8.6, h: 0, line: { color: C.sky, width: 1, transparency: 50 } });
  s.addText("LLM 통합 업무 허브 구축으로 팀의 생산성과 협업 수준을 한 단계 높입니다.", {
    x: 0.7, y: 5.18, w: 8.6, h: 0.35,
    fontSize: 13, color: C.sky, fontFace: "Calibri", italic: true, margin: 0,
  });
}

// ── Save ──────────────────────────────────────────────────────
pres.writeFile({ fileName: "D:/Git/lam/LLM_업무효율화.pptx" })
  .then(() => console.log("✅ 저장 완료: D:/Git/lam/LLM_업무효율화.pptx"))
  .catch(e => { console.error("❌ 오류:", e); process.exit(1); });
