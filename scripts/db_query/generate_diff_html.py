import json
import ssl
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_URL = "https://vault-in.hdel.co.kr:8070/api/executeQuery"
API_KEY = "subae"

def fetch_data(sql):
    query_string = urlencode({"key": API_KEY, "sql": sql})
    url = f"{API_URL}?{query_string}"
    req = Request(url, method="GET", headers={"Accept": "application/json"})
    context = ssl._create_unverified_context()
    with urlopen(req, timeout=60, context=context) as resp:
        raw = resp.read()
        try:
            text = raw.decode("utf-8")
        except:
            text = raw.decode("cp949", errors="replace")
        return json.loads(text)

v44_houid = 1292445
v45_houid = 1304784

v44_sql = f"SELECT '44' AS VERSION, D.* FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = {v44_houid} ORDER BY TO_NUMBER(D.NO)"
v45_sql = f"SELECT '45' AS VERSION, D.* FROM HDEL_DEFAULT.VARIANT_D D WHERE D.HOUID = {v45_houid} ORDER BY TO_NUMBER(D.NO)"

v44_rows = fetch_data(v44_sql)
v45_rows = fetch_data(v45_sql)

v44_by_no = {int(r["NO"]): r for r in v44_rows}
v45_by_no = {int(r["NO"]): r for r in v45_rows}

all_nos = sorted(list(set(v44_by_no.keys()) | set(v45_by_no.keys())))

def extract_pairs(r, prefix_a, prefix_b, count):
    if not r: return []
    res = []
    for i in range(1, count + 1):
        a = r.get(f"{prefix_a}{i}")
        b = r.get(f"{prefix_b}{i}")
        a_str = str(a).strip() if a is not None else ""
        b_str = str(b).strip() if b is not None else ""
        if a_str != "" or b_str != "":
            res.append({"index": i, "key": a_str, "val": b_str})
    return res

full_diff_list = []
ignore_fields = {"VERSION", "REG_DATE", "USERID", "REG_USER_NAME", "HOUID", "PID", "DOUID"}

stats = {"total": len(all_nos), "modified": 0, "added": 0, "deleted": 0, "unchanged": 0}

for no in all_nos:
    r44 = v44_by_no.get(no)
    r45 = v45_by_no.get(no)
    
    specs44 = extract_pairs(r44, "SPEC", "CON", 30)
    specs45 = extract_pairs(r45, "SPEC", "CON", 30)
    keys44 = extract_pairs(r44, "KEY", "VAL", 20)
    keys45 = extract_pairs(r45, "KEY", "VAL", 20)
    
    if r44 is None:
        stats["added"] += 1
        full_diff_list.append({
            "no": no,
            "status": "ADDED",
            "v44": None,
            "v45": {
                "addr": r45.get("ADDR") or "",
                "goto": r45.get("GOTO") or "",
                "remarks": r45.get("REMARKS") or "",
                "specs": specs45,
                "keys": keys45
            },
            "changed_fields": []
        })
    elif r45 is None:
        stats["deleted"] += 1
        full_diff_list.append({
            "no": no,
            "status": "DELETED",
            "v44": {
                "addr": r44.get("ADDR") or "",
                "goto": r44.get("GOTO") or "",
                "remarks": r44.get("REMARKS") or "",
                "specs": specs44,
                "keys": keys44
            },
            "v45": None,
            "changed_fields": []
        })
    else:
        field_diffs = []
        for k in r44.keys():
            if k in ignore_fields: continue
            val44 = str(r44.get(k) or "").strip()
            val45 = str(r45.get(k) or "").strip()
            if val44 != val45:
                field_diffs.append(k)
        
        if field_diffs:
            stats["modified"] += 1
            full_diff_list.append({
                "no": no,
                "status": "MODIFIED",
                "v44": {
                    "addr": r44.get("ADDR") or "",
                    "goto": r44.get("GOTO") or "",
                    "remarks": r44.get("REMARKS") or "",
                    "specs": specs44,
                    "keys": keys44
                },
                "v45": {
                    "addr": r45.get("ADDR") or "",
                    "goto": r45.get("GOTO") or "",
                    "remarks": r45.get("REMARKS") or "",
                    "specs": specs45,
                    "keys": keys45
                },
                "changed_fields": field_diffs
            })
        else:
            stats["unchanged"] += 1
            full_diff_list.append({
                "no": no,
                "status": "UNCHANGED",
                "v44": {
                    "addr": r44.get("ADDR") or "",
                    "goto": r44.get("GOTO") or "",
                    "remarks": r44.get("REMARKS") or "",
                    "specs": specs44,
                    "keys": keys44
                },
                "v45": {
                    "addr": r45.get("ADDR") or "",
                    "goto": r45.get("GOTO") or "",
                    "remarks": r45.get("REMARKS") or "",
                    "specs": specs45,
                    "keys": keys45
                },
                "changed_fields": []
            })

os.makedirs("output_html", exist_ok=True)

html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EL_PA103A03 v44 vs v45 로직 변경 분석 보고서</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-primary: #0f172a;
      --bg-secondary: #1e293b;
      --bg-card: #182234;
      --border-color: #334155;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      
      --accent-blue: #38bdf8;
      --accent-indigo: #818cf8;
      
      --status-mod-bg: rgba(245, 158, 11, 0.15);
      --status-mod-border: #f59e0b;
      --status-mod-text: #fbbf24;
      
      --status-add-bg: rgba(16, 185, 129, 0.15);
      --status-add-border: #10b981;
      --status-add-text: #34d399;
      
      --status-del-bg: rgba(239, 68, 68, 0.15);
      --status-del-border: #ef4444;
      --status-del-text: #f87171;

      --status-same-bg: rgba(100, 116, 139, 0.1);
      --status-same-border: #475569;
      --text-same: #cbd5e1;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Noto Sans KR', 'Inter', sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-main);
      line-height: 1.5;
      padding: 20px;
    }}

    .container {{
      max-width: 1440px;
      margin: 0 auto;
    }}

    /* Header */
    header {{
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 28px 32px;
      margin-bottom: 24px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}

    .header-title h1 {{
      font-size: 26px;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .header-title h1 .pid-badge {{
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      padding: 4px 14px;
      border-radius: 20px;
      font-size: 15px;
      font-weight: 600;
      color: #fff;
    }}

    .header-title p {{
      color: var(--text-muted);
      font-size: 14px;
      margin-top: 6px;
    }}

    .version-meta {{
      display: flex;
      gap: 12px;
    }}

    .v-box {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 10px 16px;
      border-radius: 10px;
      font-size: 13px;
    }}

    .v-box strong {{
      display: block;
      color: var(--accent-blue);
      font-size: 14px;
      margin-bottom: 2px;
    }}

    /* Stats Dashboard */
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}

    .stat-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 18px 20px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .stat-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }}

    .stat-card.active {{
      border-width: 2px;
    }}

    .stat-card .label {{
      font-size: 13px;
      color: var(--text-muted);
      font-weight: 500;
    }}

    .stat-card .val {{
      font-size: 28px;
      font-weight: 700;
      margin-top: 8px;
    }}

    .stat-card.all {{ border-left: 4px solid var(--accent-blue); }}
    .stat-card.all .val {{ color: var(--accent-blue); }}

    .stat-card.mod {{ border-left: 4px solid var(--status-mod-border); }}
    .stat-card.mod .val {{ color: var(--status-mod-text); }}

    .stat-card.add {{ border-left: 4px solid var(--status-add-border); }}
    .stat-card.add .val {{ color: var(--status-add-text); }}

    .stat-card.del {{ border-left: 4px solid var(--status-del-border); }}
    .stat-card.del .val {{ color: var(--status-del-text); }}

    .stat-card.same {{ border-left: 4px solid var(--status-same-border); }}
    .stat-card.same .val {{ color: var(--text-same); }}

    /* Controls */
    .controls {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }}

    .filter-buttons {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .btn-filter {{
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .btn-filter:hover {{
      color: var(--text-main);
      border-color: #475569;
    }}

    .btn-filter.active {{
      background: var(--accent-blue);
      color: #0f172a;
      border-color: var(--accent-blue);
      font-weight: 700;
    }}

    .search-box {{
      position: relative;
      flex: 1;
      max-width: 360px;
    }}

    .search-box input {{
      width: 100%;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 13px;
      outline: none;
    }}

    .search-box input:focus {{
      border-color: var(--accent-blue);
    }}

    /* Main Diff List */
    .diff-list {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .diff-card {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow: hidden;
      transition: border-color 0.2s;
    }}

    .diff-card.status-MODIFIED {{
      border-left: 5px solid var(--status-mod-border);
    }}
    .diff-card.status-ADDED {{
      border-left: 5px solid var(--status-add-border);
    }}
    .diff-card.status-DELETED {{
      border-left: 5px solid var(--status-del-border);
    }}
    .diff-card.status-UNCHANGED {{
      border-left: 5px solid var(--status-same-border);
      opacity: 0.7;
    }}

    .card-header {{
      background: rgba(15, 23, 42, 0.6);
      padding: 12px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border-color);
    }}

    .row-no {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 16px;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .badge-status {{
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }}

    .badge-MODIFIED {{ background: var(--status-mod-bg); color: var(--status-mod-text); border: 1px solid var(--status-mod-border); }}
    .badge-ADDED {{ background: var(--status-add-bg); color: var(--status-add-text); border: 1px solid var(--status-add-border); }}
    .badge-DELETED {{ background: var(--status-del-bg); color: var(--status-del-text); border: 1px solid var(--status-del-border); }}
    .badge-UNCHANGED {{ background: var(--status-same-bg); color: var(--text-same); border: 1px solid var(--status-same-border); }}

    .changed-fields-tags {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}

    .field-tag {{
      background: rgba(245, 158, 11, 0.2);
      color: #fcd34d;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-family: 'JetBrains Mono', monospace;
    }}

    .card-body {{
      padding: 16px 20px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }}

    @media (max-width: 900px) {{
      .card-body {{
        grid-template-columns: 1fr;
      }}
    }}

    .version-column {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 14px;
    }}

    .version-column.v44-col {{
      border-top: 3px solid #64748b;
    }}

    .version-column.v45-col {{
      border-top: 3px solid var(--accent-blue);
    }}

    .col-title {{
      font-size: 12px;
      font-weight: 700;
      color: var(--text-muted);
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
    }}

    .meta-line {{
      display: flex;
      gap: 12px;
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 10px;
      background: rgba(0,0,0,0.2);
      padding: 6px 10px;
      border-radius: 6px;
    }}

    .meta-line span strong {{
      color: var(--text-main);
    }}

    .spec-keys-container {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .section-title {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--accent-blue);
      font-weight: 700;
      margin-top: 4px;
    }}

    .pair-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 6px;
    }}

    .pair-item {{
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 12px;
      font-family: 'JetBrains Mono', monospace;
      display: flex;
      justify-content: space-between;
    }}

    .pair-item.highlight-diff {{
      background: rgba(245, 158, 11, 0.25);
      border-color: #f59e0b;
      color: #fff;
    }}

    .pair-item .k {{
      color: var(--text-muted);
    }}

    .pair-item .v {{
      color: var(--text-main);
      font-weight: 600;
    }}

    .empty-state {{
      color: var(--text-muted);
      font-size: 13px;
      font-style: italic;
      padding: 10px;
      text-align: center;
    }}

    /* Highlights for text */
    .diff-highlight {{
      background: rgba(245, 158, 11, 0.3);
      color: #fef08a;
      padding: 1px 4px;
      border-radius: 3px;
    }}

    footer {{
      margin-top: 40px;
      text-align: center;
      color: var(--text-muted);
      font-size: 13px;
      padding: 20px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="header-title">
        <h1>
          EL_PA103A03
          <span class="pid-badge">v44 vs v45 비교 분석</span>
        </h1>
        <p>PLM 로직 데이터 버전간 구문, 사양(SPEC/CON), 자재(KEY/VAL) 및 분기 흐름 시각화 리포트</p>
      </div>
      <div class="version-meta">
        <div class="v-box">
          <strong>v44 (기존)</strong>
          HOUID: 1292445 | 2026-05-13
        </div>
        <div class="v-box">
          <strong>v45 (최신)</strong>
          HOUID: 1304784 | 2026-09-14
        </div>
      </div>
    </header>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card all active" onclick="filterStatus('ALL')">
        <span class="label">전체 비교 행</span>
        <span class="val">{stats['total']}</span>
      </div>
      <div class="stat-card mod" onclick="filterStatus('MODIFIED')">
        <span class="label">수정된 행 (MODIFIED)</span>
        <span class="val">{stats['modified']}</span>
      </div>
      <div class="stat-card add" onclick="filterStatus('ADDED')">
        <span class="label">신규 추가 (ADDED)</span>
        <span class="val">{stats['added']}</span>
      </div>
      <div class="stat-card del" onclick="filterStatus('DELETED')">
        <span class="label">삭제된 행 (DELETED)</span>
        <span class="val">{stats['deleted']}</span>
      </div>
      <div class="stat-card same" onclick="filterStatus('UNCHANGED')">
        <span class="label">변경 없음 (UNCHANGED)</span>
        <span class="val">{stats['unchanged']}</span>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="controls">
      <div class="filter-buttons">
        <button class="btn-filter active" id="btn-ALL" onclick="filterStatus('ALL')">전체 보기 ({stats['total']})</button>
        <button class="btn-filter" id="btn-MODIFIED" onclick="filterStatus('MODIFIED')">수정만 보기 ({stats['modified']})</button>
        <button class="btn-filter" id="btn-ADDED" onclick="filterStatus('ADDED')">추가만 보기 ({stats['added']})</button>
        <button class="btn-filter" id="btn-DELETED" onclick="filterStatus('DELETED')">삭제만 보기 ({stats['deleted']})</button>
        <button class="btn-filter" id="btn-UNCHANGED" onclick="filterStatus('UNCHANGED')">변경 없음 ({stats['unchanged']})</button>
      </div>
      <div class="search-box">
        <input type="text" id="searchInput" placeholder="NO, 자재번호, SPEC, REMARKS 검색..." oninput="handleSearch()">
      </div>
    </div>

    <!-- Diff List Container -->
    <div class="diff-list" id="diffContainer"></div>

    <footer>
      <p>HDEL PLM Logic Agent &copy; 2026 | Automated DB Verification & Analysis System</p>
    </footer>
  </div>

  <script>
    const diffData = {json.dumps(full_diff_list, ensure_ascii=False)};
    let currentFilter = 'ALL';
    let searchQuery = '';

    function filterStatus(status) {{
      currentFilter = status;
      document.querySelectorAll('.btn-filter').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.getElementById(`btn-${{status}}`);
      if (activeBtn) activeBtn.classList.add('active');

      document.querySelectorAll('.stat-card').forEach(card => card.classList.remove('active'));
      render();
    }}

    function handleSearch() {{
      searchQuery = document.getElementById('searchInput').value.trim().toLowerCase();
      render();
    }}

    function renderPairs(pairs, otherPairs, isModified) {{
      if (!pairs || pairs.length === 0) return '<div class="empty-state">없음</div>';
      
      const otherMap = new Map();
      if (otherPairs) {{
        otherPairs.forEach(p => otherMap.set(p.index, `${{p.key}}:${{p.val}}`));
      }}

      return '<div class="pair-grid">' + pairs.map(p => {{
        const currStr = `${{p.key}}:${{p.val}}`;
        const otherStr = otherMap.get(p.index);
        const isDiff = isModified && (otherStr !== currStr);
        const diffClass = isDiff ? 'highlight-diff' : '';
        return `<div class="pair-item ${{diffClass}}">
          <span class="k">${{p.key}}</span>
          <span class="v">${{p.val}}</span>
        </div>`;
      }}).join('') + '</div>';
    }}

    function render() {{
      const container = document.getElementById('diffContainer');
      container.innerHTML = '';

      const filtered = diffData.filter(item => {{
        if (currentFilter !== 'ALL' && item.status !== currentFilter) return false;
        if (!searchQuery) return true;

        const noStr = item.no.toString();
        const v44Str = item.v44 ? JSON.stringify(item.v44).toLowerCase() : '';
        const v45Str = item.v45 ? JSON.stringify(item.v45).toLowerCase() : '';
        return noStr.includes(searchQuery) || v44Str.includes(searchQuery) || v45Str.includes(searchQuery);
      }});

      if (filtered.length === 0) {{
        container.innerHTML = '<div style="text-align:center; padding: 60px; color: var(--text-muted);">검색 결과가 없습니다.</div>';
        return;
      }}

      filtered.forEach(item => {{
        const card = document.createElement('div');
        card.className = `diff-card status-${{item.status}}`;

        const isMod = item.status === 'MODIFIED';
        const changedTags = item.changed_fields.map(f => `<span class="field-tag">${{f}}</span>`).join('');

        let v44Html = '<div class="empty-state">v44 데이터 없음 (신규 추가행)</div>';
        if (item.v44) {{
          const isAddrDiff = isMod && item.changed_fields.includes('ADDR');
          const isGotoDiff = isMod && item.changed_fields.includes('GOTO');
          const isRemDiff = isMod && item.changed_fields.includes('REMARKS');

          v44Html = `
            <div class="col-title">v44 (기존)</div>
            <div class="meta-line">
              <span>ADDR: <strong class="${{isAddrDiff ? 'diff-highlight' : ''}}">${{item.v44.addr || '-'}}</strong></span>
              <span>GOTO: <strong class="${{isGotoDiff ? 'diff-highlight' : ''}}">${{item.v44.goto || '-'}}</strong></span>
              <span>REMARKS: <strong class="${{isRemDiff ? 'diff-highlight' : ''}}">${{item.v44.remarks || '-'}}</strong></span>
            </div>
            <div class="spec-keys-container">
              <div class="section-title">SPEC / CON 조건 (쌍)</div>
              ${{renderPairs(item.v44.specs, item.v45 ? item.v45.specs : null, isMod)}}
              <div class="section-title">KEY / VAL 산출 자재 (쌍)</div>
              ${{renderPairs(item.v44.keys, item.v45 ? item.v45.keys : null, isMod)}}
            </div>
          `;
        }}

        let v45Html = '<div class="empty-state">v45 데이터 없음 (삭제된 행)</div>';
        if (item.v45) {{
          const isAddrDiff = isMod && item.changed_fields.includes('ADDR');
          const isGotoDiff = isMod && item.changed_fields.includes('GOTO');
          const isRemDiff = isMod && item.changed_fields.includes('REMARKS');

          v45Html = `
            <div class="col-title">v45 (최신)</div>
            <div class="meta-line">
              <span>ADDR: <strong class="${{isAddrDiff ? 'diff-highlight' : ''}}">${{item.v45.addr || '-'}}</strong></span>
              <span>GOTO: <strong class="${{isGotoDiff ? 'diff-highlight' : ''}}">${{item.v45.goto || '-'}}</strong></span>
              <span>REMARKS: <strong class="${{isRemDiff ? 'diff-highlight' : ''}}">${{item.v45.remarks || '-'}}</strong></span>
            </div>
            <div class="spec-keys-container">
              <div class="section-title">SPEC / CON 조건 (쌍)</div>
              ${{renderPairs(item.v45.specs, item.v44 ? item.v44.specs : null, isMod)}}
              <div class="section-title">KEY / VAL 산출 자재 (쌍)</div>
              ${{renderPairs(item.v45.keys, item.v44 ? item.v44.keys : null, isMod)}}
            </div>
          `;
        }}

        card.innerHTML = `
          <div class="card-header">
            <div class="row-no">
              NO. ${{item.no}}
              <span class="badge-status badge-${{item.status}}">${{item.status}}</span>
            </div>
            <div class="changed-fields-tags">
              ${{changedTags}}
            </div>
          </div>
          <div class="card-body">
            <div class="version-column v44-col">${{v44Html}}</div>
            <div class="version-column v45-col">${{v45Html}}</div>
          </div>
        `;

        container.appendChild(card);
      }});
    }}

    render();
  </script>
</body>
</html>
"""

html_path = "output_html/EL_PA103A03_v44_v45_diff.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Interactive HTML visual diff successfully generated at: {html_path}")
