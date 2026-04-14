const fs = require("fs");
const JSZip = require("jszip");
const xml2js = require("xml2js");

const EMU = 914400; // 1 inch = 914400 EMU

async function analyze(filePath) {
  const data = fs.readFileSync(filePath);
  const zip = await JSZip.loadAsync(data);

  for (const name of Object.keys(zip.files).sort()) {
    if (!name.match(/ppt\/slides\/slide\d+\.xml$/)) continue;
    const xml = await zip.files[name].async("string");
    const result = await xml2js.parseStringPromise(xml);
    const spTree = result["p:sld"]["p:cSld"][0]["p:spTree"][0];

    const shapes = [];

    // Process sp (shapes)
    if (spTree["p:sp"]) {
      for (const sp of spTree["p:sp"]) {
        shapes.push(parseShape(sp, "sp"));
      }
    }

    // Process grpSp (group shapes)
    if (spTree["p:grpSp"]) {
      for (const grp of spTree["p:grpSp"]) {
        const grpInfo = parseGroupShape(grp);
        shapes.push(grpInfo);
      }
    }

    // Process cxnSp (connector shapes / lines)
    if (spTree["p:cxnSp"]) {
      for (const cxn of spTree["p:cxnSp"]) {
        shapes.push(parseConnector(cxn));
      }
    }

    // Sort by Y then X
    shapes.sort((a, b) => (a.y || 0) - (b.y || 0) || (a.x || 0) - (b.x || 0));

    console.log(`\n${"=".repeat(60)}`);
    console.log(`SLIDE: ${name}`);
    console.log(`Total shapes: ${shapes.length}`);
    console.log(`${"=".repeat(60)}`);

    for (const sh of shapes) {
      printShape(sh, 0);
    }
  }
}

function parseShape(sp, type) {
  const info = { type };

  // Name
  const nvSpPr = sp["p:nvSpPr"] || sp["p:nvCxnSpPr"];
  if (nvSpPr && nvSpPr[0] && nvSpPr[0]["p:cNvPr"]) {
    info.name = nvSpPr[0]["p:cNvPr"][0].$.name || "";
  }

  // Position & Size
  const spPr = sp["p:spPr"] && sp["p:spPr"][0];
  if (spPr) {
    if (spPr["a:xfrm"] && spPr["a:xfrm"][0]) {
      const xfrm = spPr["a:xfrm"][0];
      if (xfrm["a:off"] && xfrm["a:off"][0]) {
        info.x = +(+xfrm["a:off"][0].$.x / EMU).toFixed(2);
        info.y = +(+xfrm["a:off"][0].$.y / EMU).toFixed(2);
      }
      if (xfrm["a:ext"] && xfrm["a:ext"][0]) {
        info.w = +(+xfrm["a:ext"][0].$.cx / EMU).toFixed(2);
        info.h = +(+xfrm["a:ext"][0].$.cy / EMU).toFixed(2);
      }
    }

    // Fill color
    if (spPr["a:solidFill"] && spPr["a:solidFill"][0]) {
      const sf = spPr["a:solidFill"][0];
      if (sf["a:srgbClr"]) info.fill = sf["a:srgbClr"][0].$.val;
    }

    // Line color
    if (spPr["a:ln"] && spPr["a:ln"][0]) {
      const ln = spPr["a:ln"][0];
      if (ln["a:solidFill"] && ln["a:solidFill"][0]) {
        const lf = ln["a:solidFill"][0];
        if (lf["a:srgbClr"]) info.lineColor = lf["a:srgbClr"][0].$.val;
      }
      if (ln["a:prstDash"]) info.dash = ln["a:prstDash"][0].$.val;
      if (ln.$ && ln.$.w) info.lineW = +(+ln.$.w / 12700).toFixed(1);
    }
  }

  // Text
  const txBody = sp["p:txBody"] && sp["p:txBody"][0];
  if (txBody && txBody["a:p"]) {
    const texts = [];
    for (const p of txBody["a:p"]) {
      if (p["a:r"]) {
        for (const r of p["a:r"]) {
          if (r["a:t"]) {
            const t = typeof r["a:t"][0] === "string" ? r["a:t"][0] : r["a:t"][0]._ || "";
            if (t.trim()) {
              const rPr = r["a:rPr"] && r["a:rPr"][0];
              let fontSize = null, fontColor = null, bold = false;
              if (rPr) {
                if (rPr.$.sz) fontSize = (+rPr.$.sz / 100);
                if (rPr.$.b === "1") bold = true;
                if (rPr["a:solidFill"] && rPr["a:solidFill"][0] && rPr["a:solidFill"][0]["a:srgbClr"]) {
                  fontColor = rPr["a:solidFill"][0]["a:srgbClr"][0].$.val;
                }
              }
              texts.push({ text: t.trim(), fontSize, fontColor, bold });
            }
          }
        }
      }
    }
    if (texts.length) info.texts = texts;
  }

  return info;
}

function parseGroupShape(grp) {
  const info = { type: "grpSp", children: [] };

  // Group name
  if (grp["p:nvGrpSpPr"] && grp["p:nvGrpSpPr"][0] && grp["p:nvGrpSpPr"][0]["p:cNvPr"]) {
    info.name = grp["p:nvGrpSpPr"][0]["p:cNvPr"][0].$.name || "";
  }

  // Group position
  if (grp["p:grpSpPr"] && grp["p:grpSpPr"][0] && grp["p:grpSpPr"][0]["a:xfrm"] && grp["p:grpSpPr"][0]["a:xfrm"][0]) {
    const xfrm = grp["p:grpSpPr"][0]["a:xfrm"][0];
    if (xfrm["a:off"] && xfrm["a:off"][0]) {
      info.x = +(+xfrm["a:off"][0].$.x / EMU).toFixed(2);
      info.y = +(+xfrm["a:off"][0].$.y / EMU).toFixed(2);
    }
    if (xfrm["a:ext"] && xfrm["a:ext"][0]) {
      info.w = +(+xfrm["a:ext"][0].$.cx / EMU).toFixed(2);
      info.h = +(+xfrm["a:ext"][0].$.cy / EMU).toFixed(2);
    }
  }

  // Child shapes
  if (grp["p:sp"]) {
    for (const sp of grp["p:sp"]) {
      info.children.push(parseShape(sp, "sp"));
    }
  }
  if (grp["p:cxnSp"]) {
    for (const cxn of grp["p:cxnSp"]) {
      info.children.push(parseConnector(cxn));
    }
  }
  if (grp["p:grpSp"]) {
    for (const subGrp of grp["p:grpSp"]) {
      info.children.push(parseGroupShape(subGrp));
    }
  }

  return info;
}

function parseConnector(cxn) {
  const info = { type: "cxnSp" };

  if (cxn["p:nvCxnSpPr"] && cxn["p:nvCxnSpPr"][0] && cxn["p:nvCxnSpPr"][0]["p:cNvPr"]) {
    info.name = cxn["p:nvCxnSpPr"][0]["p:cNvPr"][0].$.name || "";
  }

  const spPr = cxn["p:spPr"] && cxn["p:spPr"][0];
  if (spPr) {
    if (spPr["a:xfrm"] && spPr["a:xfrm"][0]) {
      const xfrm = spPr["a:xfrm"][0];
      if (xfrm["a:off"] && xfrm["a:off"][0]) {
        info.x = +(+xfrm["a:off"][0].$.x / EMU).toFixed(2);
        info.y = +(+xfrm["a:off"][0].$.y / EMU).toFixed(2);
      }
      if (xfrm["a:ext"] && xfrm["a:ext"][0]) {
        info.w = +(+xfrm["a:ext"][0].$.cx / EMU).toFixed(2);
        info.h = +(+xfrm["a:ext"][0].$.cy / EMU).toFixed(2);
      }
      if (xfrm.$ && xfrm.$.flipH) info.flipH = true;
    }

    if (spPr["a:ln"] && spPr["a:ln"][0]) {
      const ln = spPr["a:ln"][0];
      if (ln["a:solidFill"] && ln["a:solidFill"][0] && ln["a:solidFill"][0]["a:srgbClr"]) {
        info.lineColor = ln["a:solidFill"][0]["a:srgbClr"][0].$.val;
      }
      if (ln["a:prstDash"]) info.dash = ln["a:prstDash"][0].$.val;
      if (ln.$ && ln.$.w) info.lineW = +(+ln.$.w / 12700).toFixed(1);
    }
  }

  return info;
}

function printShape(sh, indent) {
  const pad = "  ".repeat(indent);
  const pos = `(${sh.x}, ${sh.y}) ${sh.w}x${sh.h}`;
  let desc = `${pad}[${sh.type}] ${sh.name || ""} @ ${pos}`;
  if (sh.fill) desc += ` fill=#${sh.fill}`;
  if (sh.lineColor) desc += ` line=#${sh.lineColor}`;
  if (sh.lineW) desc += ` lineW=${sh.lineW}pt`;
  if (sh.dash) desc += ` dash=${sh.dash}`;
  if (sh.flipH) desc += ` flipH`;
  console.log(desc);

  if (sh.texts) {
    for (const t of sh.texts) {
      let tDesc = `${pad}  "${t.text}"`;
      if (t.fontSize) tDesc += ` sz=${t.fontSize}pt`;
      if (t.fontColor) tDesc += ` c=#${t.fontColor}`;
      if (t.bold) tDesc += ` bold`;
      console.log(tDesc);
    }
  }

  if (sh.children) {
    for (const c of sh.children) {
      printShape(c, indent + 1);
    }
  }
}

analyze("D:/Git/lam/LLM_플로우_New.pptx").catch(console.error);
