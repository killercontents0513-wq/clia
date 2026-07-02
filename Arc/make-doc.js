const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  LevelFormat, VerticalAlign, PageNumber, Header, Footer,
} = require('docx');
const fs = require('fs');

// ── 색상 팔레트 ──────────────────────────────
const RED     = 'C0392B';   // LG 레드
const DARK    = '1A1A1A';   // 거의 검정
const GRAY    = '555555';   // 본문 회색
const LGRAY   = '888888';   // 서브텍스트
const BG_RED  = 'FADBD8';   // 연한 레드 배경
const BG_GRAY = 'F2F3F4';   // 연한 회색 배경
const BG_BLUE = 'D6EAF8';   // 연한 파랑
const BG_GREEN= 'D5F5E3';   // 연한 초록
const WHITE   = 'FFFFFF';
const LINE    = 'E0E0E0';   // 구분선

const CONTENT_W = 9360; // A4 기준 본문 너비(DXA), 1인치 마진

// ── 셀 border helper ─────────────────────────
function makeBorders(color = LINE) {
  const b = { style: BorderStyle.SINGLE, size: 4, color };
  return { top: b, bottom: b, left: b, right: b };
}
function noBorder() {
  const b = { style: BorderStyle.NONE, size: 0, color: WHITE };
  return { top: b, bottom: b, left: b, right: b };
}

// ── 기본 단락 helper ─────────────────────────
function p(runs, opts = {}) {
  return new Paragraph({
    alignment: opts.align || AlignmentType.LEFT,
    spacing: { before: opts.before ?? 80, after: opts.after ?? 80 },
    ...opts.extra,
    children: Array.isArray(runs) ? runs : [runs],
  });
}

function t(text, opts = {}) {
  return new TextRun({
    text,
    font: 'Arial',
    size: opts.size ?? 22,
    bold: opts.bold ?? false,
    color: opts.color ?? DARK,
    italics: opts.italic ?? false,
    break: opts.break ?? 0,
  });
}

function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 160 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: RED, space: 6 } },
    children: [new TextRun({ text, font: 'Arial', size: 36, bold: true, color: RED })],
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 300, after: 120 },
    children: [new TextRun({ text, font: 'Arial', size: 28, bold: true, color: DARK })],
  });
}

function heading3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 80 },
    children: [new TextRun({ text, font: 'Arial', size: 24, bold: true, color: RED })],
  });
}

function bullet(text, indent = 720) {
  return new Paragraph({
    numbering: { reference: 'bullets', level: 0 },
    spacing: { before: 60, after: 60 },
    indent: { left: indent, hanging: 360 },
    children: [new TextRun({ text, font: 'Arial', size: 21, color: DARK })],
  });
}

function space(lines = 1) {
  return new Paragraph({ spacing: { before: 0, after: lines * 120 }, children: [] });
}

// ── 구분선 ────────────────────────────────────
function divider() {
  return new Paragraph({
    spacing: { before: 160, after: 160 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: LINE, space: 4 } },
    children: [],
  });
}

// ── 강조 박스 ────────────────────────────────
function infoBox(lines, bgColor = BG_GRAY) {
  const children = lines.map(([bold, normal]) =>
    p([
      t(bold, { bold: true, size: 21, color: RED }),
      t(normal, { size: 21, color: DARK }),
    ], { before: 60, after: 60 })
  );
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [CONTENT_W],
    rows: [new TableRow({ children: [
      new TableCell({
        borders: makeBorders(RED),
        width: { size: CONTENT_W, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 160, bottom: 160, left: 240, right: 240 },
        children,
      })
    ]})],
  });
}

// ── 일반 테이블 ──────────────────────────────
function dataTable(headers, rows, colWidths) {
  const hRow = new TableRow({
    children: headers.map((h, i) =>
      new TableCell({
        borders: makeBorders(RED),
        width: { size: colWidths[i], type: WidthType.DXA },
        shading: { fill: RED, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 160, right: 160 },
        verticalAlign: VerticalAlign.CENTER,
        children: [p(t(h, { bold: true, color: WHITE, size: 21 }), { before: 0, after: 0, align: AlignmentType.CENTER })],
      })
    ),
  });
  const dRows = rows.map((row, ri) =>
    new TableRow({
      children: row.map((cell, i) => {
        const isHighlight = typeof cell === 'object' && cell.highlight;
        const cellText = isHighlight ? cell.text : cell;
        const bg = ri % 2 === 0 ? 'F9F9F9' : WHITE;
        return new TableCell({
          borders: makeBorders(LINE),
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: isHighlight ? BG_RED : bg, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 160, right: 160 },
          verticalAlign: VerticalAlign.CENTER,
          children: [p(
            t(cellText, { size: 21, bold: isHighlight, color: isHighlight ? RED : DARK }),
            { before: 0, after: 0, align: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER }
          )],
        });
      }),
    })
  );
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [hRow, ...dRows],
  });
}

// ── Phase 박스 (확장성 섹션용) ───────────────
function phaseBox(phase, title, desc, bg) {
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [1800, CONTENT_W - 1800],
    rows: [new TableRow({ children: [
      new TableCell({
        borders: makeBorders(LINE),
        width: { size: 1800, type: WidthType.DXA },
        shading: { fill: RED, type: ShadingType.CLEAR },
        margins: { top: 120, bottom: 120, left: 160, right: 160 },
        verticalAlign: VerticalAlign.CENTER,
        children: [
          p(t(phase, { bold: true, color: WHITE, size: 22 }), { before: 0, after: 0, align: AlignmentType.CENTER }),
        ],
      }),
      new TableCell({
        borders: makeBorders(LINE),
        width: { size: CONTENT_W - 1800, type: WidthType.DXA },
        shading: { fill: bg, type: ShadingType.CLEAR },
        margins: { top: 120, bottom: 120, left: 200, right: 160 },
        children: [
          p(t(title, { bold: true, size: 22, color: DARK }), { before: 0, after: 40 }),
          p(t(desc, { size: 20, color: GRAY }), { before: 0, after: 0 }),
        ],
      }),
    ]})],
  });
}

// ════════════════════════════════════════════
// 문서 구성
// ════════════════════════════════════════════
const doc = new Document({
  numbering: {
    config: [{
      reference: 'bullets',
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: '•',
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } },
      }],
    }],
  },
  styles: {
    default: {
      document: { run: { font: 'Arial', size: 22, color: DARK } },
    },
    paragraphStyles: [
      {
        id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal',
        run: { font: 'Arial', size: 36, bold: true, color: RED },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 },
      },
      {
        id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal',
        run: { font: 'Arial', size: 28, bold: true, color: DARK },
        paragraph: { spacing: { before: 300, after: 120 }, outlineLevel: 1 },
      },
      {
        id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal',
        run: { font: 'Arial', size: 24, bold: true, color: RED },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 },
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 }, // A4
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: LINE, space: 4 } },
          spacing: { after: 80 },
          children: [new TextRun({ text: 'LG Amazon A+ Content Generator — 서비스 소개서', font: 'Arial', size: 18, color: LGRAY })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: LINE, space: 4 } },
          spacing: { before: 80 },
          children: [
            new TextRun({ text: '© LG Electronics  |  Confidential  |  ', font: 'Arial', size: 18, color: LGRAY }),
            new TextRun({ children: [PageNumber.CURRENT], font: 'Arial', size: 18, color: LGRAY }),
          ],
        })],
      }),
    },
    children: [

      // ──────────────────────────────────────
      // 표지
      // ──────────────────────────────────────
      space(2),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 120 },
        children: [new TextRun({ text: 'LG', font: 'Arial', size: 96, bold: true, color: RED })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 200 },
        children: [new TextRun({ text: 'Amazon A+ Content Generator', font: 'Arial', size: 52, bold: true, color: DARK })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 80 },
        children: [new TextRun({ text: '서비스 소개서', font: 'Arial', size: 34, color: GRAY })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 600 },
        children: [new TextRun({ text: '비개발 담당자용  |  2026', font: 'Arial', size: 24, color: LGRAY })],
      }),

      // 표지 요약 박스
      new Table({
        width: { size: CONTENT_W, type: WidthType.DXA },
        columnWidths: [CONTENT_W / 3, CONTENT_W / 3, CONTENT_W / 3],
        rows: [new TableRow({ children: [
          ['URL 입력 한 번으로', '⏱ 30~60초', BG_RED],
          ['A+ 샘플 자동 생성', '🤖 Claude AI', BG_GRAY],
          ['건당 비용', '💰 약 30~100원', BG_BLUE],
        ].map(([label, val, bg], i) => new TableCell({
          borders: noBorder(),
          width: { size: CONTENT_W / 3, type: WidthType.DXA },
          shading: { fill: bg, type: ShadingType.CLEAR },
          margins: { top: 200, bottom: 200, left: 160, right: 160 },
          verticalAlign: VerticalAlign.CENTER,
          children: [
            p(t(label, { size: 20, color: GRAY }), { before: 0, after: 60, align: AlignmentType.CENTER }),
            p(t(val, { size: 28, bold: true, color: RED }), { before: 0, after: 0, align: AlignmentType.CENTER }),
          ],
        }))})],
      }),
      space(2),

      // ──────────────────────────────────────
      // 1. 서비스 개요
      // ──────────────────────────────────────
      heading1('1. 이 서비스가 뭔가요?'),
      p(t('LG.com 제품 페이지 URL 하나만 넣으면, Amazon에 올릴 수 있는 A+ 콘텐츠 샘플을 자동으로 만들어주는 도구입니다.', { size: 22 }), { before: 80, after: 200 }),

      heading2('기존 방식 vs. 이 Generator'),
      dataTable(
        ['구분', '기존 방식', 'A+ Content Generator'],
        [
          ['소요 시간', '담당자 수집 → 디자이너 작업 → 검토 → 수정 (평균 2~3일)', { text: '30~60초', highlight: true }],
          ['필요 인력', '마케터 + 디자이너', { text: '혼자서 가능', highlight: true }],
          ['결과물', '완성본', '즉시 검토 가능한 고품질 초안'],
          ['비용', '외주 시 건당 수십만 원~', { text: '건당 약 30~100원', highlight: true }],
        ],
        [2000, 4000, 3360]
      ),
      space(),

      // ──────────────────────────────────────
      // 2. 작동 원리
      // ──────────────────────────────────────
      heading1('2. 어떻게 이게 가능한가요?'),
      p(t('세 가지 기술이 순서대로 작동합니다. 개발 지식 없이도 이렇게 이해하시면 됩니다.', { size: 22 }), { before: 80, after: 160 }),

      // 흐름도 박스
      new Table({
        width: { size: CONTENT_W, type: WidthType.DXA },
        columnWidths: [2800, 400, 2800, 400, 2960],
        rows: [new TableRow({ children: [
          ['① LG.com 페이지 자동 읽기\n(크롤링)', BG_RED],
          ['→', WHITE],
          ['② AI가 Amazon 규격으로\n분석·배치', BG_GRAY],
          ['→', WHITE],
          ['③ 화면에서 확인·수정\n후 이미지 저장', BG_BLUE],
        ].map(([text, bg]) => new TableCell({
          borders: text === '→' ? noBorder() : makeBorders(LINE),
          width: { size: text === '→' ? 400 : 2900, type: WidthType.DXA },
          shading: { fill: bg, type: ShadingType.CLEAR },
          margins: { top: 160, bottom: 160, left: 160, right: 160 },
          verticalAlign: VerticalAlign.CENTER,
          children: [p(
            text.split('\n').flatMap((line, i) => i === 0
              ? [new TextRun({ text: line, font: 'Arial', size: 21, bold: text !== '→', color: text === '→' ? LGRAY : DARK })]
              : [new TextRun({ text: line, font: 'Arial', size: 20, color: GRAY, break: 1 })]
            ),
            { before: 0, after: 0, align: AlignmentType.CENTER }
          )],
        }))})],
      }),
      space(),

      heading2('① 자동 크롤링 (Puppeteer)'),
      p(t('사람이 브라우저를 열어 페이지를 보는 것처럼, 프로그램이 대신 LG.com에 접속해서 이미지 URL, 제품명, 기능 설명, Alt 텍스트를 모두 수집합니다. 담당자가 아무것도 복사·붙여넣기 할 필요가 없습니다.', { size: 21, color: GRAY }), { before: 60, after: 120 }),

      heading2('② AI 모듈 배치 (Claude API)'),
      p(t('수집된 정보를 Claude AI가 분석해서, 가로형 이미지는 가로형 모듈에, 세로형 이미지는 세로형 모듈에 자동으로 배치합니다. 텍스트는 Amazon A+ 가이드의 글자 수 제한에 맞게 자동으로 다듬어집니다.', { size: 21, color: GRAY }), { before: 60, after: 120 }),

      heading2('③ 실시간 프리뷰 & 편집'),
      p(t('생성된 결과를 화면에서 바로 확인하고, 마음에 안 드는 텍스트는 클릭해서 직접 수정할 수 있습니다. 완성되면 모듈별로 Amazon 규격에 맞게 크롭된 이미지를 한 번에 다운로드합니다.', { size: 21, color: GRAY }), { before: 60, after: 160 }),

      // ──────────────────────────────────────
      // 3. 비용
      // ──────────────────────────────────────
      heading1('3. 비용은 얼마나 드나요?'),

      heading2('현재 구조 (로컬 운영 기준)'),
      dataTable(
        ['항목', '비용', '비고'],
        [
          ['Claude API (AI 분석)', { text: '건당 약 30~80원', highlight: true }, '1회 생성 = 약 4,000~8,000 토큰'],
          ['서버 운영', '₩0', '담당자 PC에서 실행'],
          ['기타 외부 서비스', '₩0', '모두 오픈소스 활용'],
        ],
        [3000, 2500, 3860]
      ),
      space(),

      heading2('월 사용량별 예상 비용'),
      dataTable(
        ['월 생성 건수', '예상 Claude API 비용', '절감 환산 (외주 대비)'],
        [
          ['50건', '약 2,500~4,000원', '외주비 250만원+ 절감'],
          ['200건', '약 10,000~16,000원', '외주비 1,000만원+ 절감'],
          ['1,000건', { text: '약 50,000~80,000원', highlight: true }, '외주비 5,000만원+ 절감'],
        ],
        [2800, 3000, 3560]
      ),
      space(),

      infoBox([
        ['💡 모델 선택 팁: ', '현재 claude-haiku 모델은 Claude 라인업 중 가장 저렴하고 빠른 모델입니다. 품질을 높이고 싶다면 claude-sonnet으로 전환 가능 (비용 약 5~8배 증가).'],
      ], BG_GRAY),
      space(),

      // ──────────────────────────────────────
      // 4. 운영 효율
      // ──────────────────────────────────────
      heading1('4. 최소 인력으로 어떻게 운영하나요?'),
      p(t('현재 구조는 담당자 1명의 PC에서 모든 것이 작동합니다. 별도 서버 계약, IT 인프라 없이 아래 두 줄만 실행하면 됩니다.', { size: 22 }), { before: 80, after: 160 }),

      // 실행 명령어 박스
      new Table({
        width: { size: CONTENT_W, type: WidthType.DXA },
        columnWidths: [CONTENT_W],
        rows: [new TableRow({ children: [new TableCell({
          borders: makeBorders(DARK),
          width: { size: CONTENT_W, type: WidthType.DXA },
          shading: { fill: '1A1A1A', type: ShadingType.CLEAR },
          margins: { top: 160, bottom: 160, left: 280, right: 280 },
          children: [
            p(t('node server.js      ← AI 엔진 켜기 (한 번만)', { size: 20, color: '7EC8E3', bold: false }), { before: 0, after: 60 }),
            p(t('npx serve .         ← 화면 열기  (한 번만)', { size: 20, color: '7EC8E3', bold: false }), { before: 0, after: 0 }),
          ],
        })]})],
      }),
      space(),

      heading2('운영 역할 분담'),
      dataTable(
        ['역할', '필요 여부', '비고'],
        [
          ['개발자 상시 대기', '❌ 불필요', '초기 설치 후 독립 운영'],
          ['별도 서버 계약', '❌ 불필요 (현재)', 'PC에서 실행'],
          ['디자이너 협업', '⚡ 선택적', '초안 생성 후 필요 시만'],
          ['API Key 관리', '✅ 필요', 'Anthropic 콘솔에서 월 사용량 모니터링'],
        ],
        [3000, 2500, 3860]
      ),
      space(),

      // ──────────────────────────────────────
      // 5. 확장성
      // ──────────────────────────────────────
      heading1('5. 더 크게 확장하면 어떻게 되나요?'),
      p(t('현재는 "개인 작업 도구" 수준이지만, 단계별로 확장이 가능합니다.', { size: 22 }), { before: 80, after: 200 }),

      phaseBox('Phase 1\n(현재)', '로컬 도구', '담당자 PC → 혼자 사용 → 초안 생성\n비용: 거의 없음 / 한계: 동시 사용 불가', BG_GRAY),
      space(0),
      phaseBox('Phase 2', '팀 공유 도구', '서버 1대(AWS/GCP, 월 ~$20)에 올리면 팀 전체가 웹 브라우저로 접속 가능\n추가 개발 기간: 1~2일 / 추가 비용: 월 3~5만원', BG_BLUE),
      space(0),
      phaseBox('Phase 3', '글로벌 멀티 마켓', 'LG.com 국가별 URL 구조가 동일 → 추가 개발 없이 전 세계 적용 가능\nlg.com/us/, /uk/, /de/ 등 이미 테스트 완료', BG_GREEN),
      space(0),
      phaseBox('Phase 4', 'Amazon 직접 업로드 자동화', 'Amazon Vendor Central API 연동 → 생성 → 검토 → 업로드 원클릭\n생성부터 게시까지 완전 자동화', BG_RED),
      space(),

      // 멀티 마켓 예시 박스
      infoBox([
        ['🌍 글로벌 확장 예시: ', ''],
        ['lg.com/us/... → ', 'Amazon US A+ 콘텐츠 자동 생성'],
        ['lg.com/uk/... → ', 'Amazon UK A+ 콘텐츠 자동 생성'],
        ['lg.com/de/... → ', 'Amazon DE A+ 콘텐츠 자동 생성'],
      ], BG_GRAY),
      space(),

      // ──────────────────────────────────────
      // 6. ROI 요약
      // ──────────────────────────────────────
      heading1('6. 한눈에 보는 ROI'),
      dataTable(
        ['구분', '수치'],
        [
          ['기존 A+ 콘텐츠 제작 시간', '건당 평균 16시간 (약 2일)'],
          ['Generator 사용 시 시간', '건당 평균 15분 (검토·수정 포함)'],
          ['시간 절감율', { text: '약 94%', highlight: true }],
          ['월 50건 기준 절감 시간', { text: '750시간 → 12.5시간', highlight: true }],
          ['API 비용 (월 50건)', '약 4,000원'],
        ],
        [5000, 4360]
      ),
      space(),

      infoBox([
        ['📊 Amazon 공식 데이터: ', 'A+ 콘텐츠는 일반 상품 페이지 대비 전환율 3~10% 향상 효과가 검증되어 있습니다. 이 Generator는 그 효과를 훨씬 낮은 비용과 시간으로 실현합니다.'],
      ], BG_RED),
      space(2),

      // ──────────────────────────────────────
      // 마무리
      // ──────────────────────────────────────
      divider(),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 240, after: 80 },
        children: [new TextRun({ text: 'LG Electronics — Retail OBS Contents Generator', font: 'Arial', size: 20, color: LGRAY })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 0 },
        children: [new TextRun({ text: 'Confidential  |  Internal Use Only', font: 'Arial', size: 18, color: LGRAY })],
      }),
    ],
  }],
});

Packer.toBuffer(doc).then(buffer => {
  const outPath = '/Users/kangjaeyeong/Desktop/AI Study/lg-web-project/LG_APlus_Generator_소개서.docx';
  fs.writeFileSync(outPath, buffer);
  console.log('✅ 저장 완료:', outPath);
}).catch(err => {
  console.error('❌ 오류:', err.message);
});
