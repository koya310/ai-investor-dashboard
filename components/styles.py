"""共通CSSスタイル定義"""


def get_global_css() -> str:
    return """
<style>
/* ── Page ── */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container { background: #f8fafc; }
[data-testid="stHeader"] { background: #f8fafc; }

/* ── Card ── */
.card {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
    padding: 1.4rem 1.5rem;
    margin-bottom: 0.9rem;
}
.card-sm {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    padding: 0.9rem 1.15rem;
    margin-bottom: 0.55rem;
}

/* ── Section header ── */
.sec-hdr {
    display: flex; align-items: center; gap: 0.6rem;
    margin-top: 1.6rem; margin-bottom: 0.7rem;
}
.sec-hdr .bar {
    width: 4px; height: 1.4rem; border-radius: 2px;
}
.sec-hdr .txt {
    font-size: 0.95rem; font-weight: 700; color: #0f172a;
}
.sec-hdr .sub {
    font-size: 0.73rem; color: #94a3b8; margin-left: 0.3rem; font-weight: 400;
}

/* ── Color utils ── */
.c-pos  { color: #059669; }
.c-neg  { color: #e11d48; }
.c-dim  { color: #94a3b8; }
.c-sub  { color: #64748b; }
.c-pri  { color: #2563eb; }

/* ── Pill ── */
.pill {
    display: inline-block; padding: 0.18rem 0.6rem;
    border-radius: 999px; font-size: 0.72rem; font-weight: 600;
}
.pill-blue  { background: #eff6ff; color: #2563eb; }
.pill-green { background: #ecfdf5; color: #059669; }
.pill-red   { background: #fff1f2; color: #e11d48; }

/* ── Split boxes (equity/cash) ── */
.split-row {
    display: flex; gap: 0.8rem;
    margin-top: 1rem; padding: 0 1.5rem;
}
.split-box {
    flex: 1; border-radius: 12px; padding: 0.7rem 0.8rem;
    text-align: center;
}
.split-val { font-size: 1.15rem; font-weight: 700; line-height: 1.2; }
.split-label { font-size: 0.68rem; margin-top: 0.15rem; }

/* ── Position row (inside hero) ── */
.pos-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.5rem 0.4rem;
    border-bottom: 1px solid #f1f5f9;
}
.pos-row:last-child { border-bottom: none; }

/* ── Checklist gauge ── */
.cl-row {
    display: flex; align-items: center; gap: 1rem;
    padding: 0.7rem 0; border-bottom: 1px solid #f1f5f9;
}
.cl-row:last-child { border-bottom: none; }
.cl-label { width: 6rem; flex-shrink: 0; }
.cl-label-txt { font-size: 0.75rem; font-weight: 600; color: #64748b; }
.cl-label-tip { font-size: 0.62rem; color: #94a3b8; margin-top: 0.1rem; }
.cl-bar-wrap { flex: 1; }
.cl-bar-track {
    background: #f1f5f9; border-radius: 6px; height: 10px;
    position: relative; overflow: hidden;
}
.cl-bar-fill { height: 100%; border-radius: 6px; transition: width 0.3s; }
.cl-nums { display: flex; justify-content: space-between; margin-top: 0.2rem; }
.cl-cur { font-size: 0.82rem; font-weight: 700; }
.cl-tgt { font-size: 0.7rem; color: #94a3b8; }
.cl-gap { text-align: right; width: 7rem; flex-shrink: 0; }
.cl-gap-txt { font-size: 0.78rem; font-weight: 600; }
.cl-gap-sub { font-size: 0.62rem; color: #94a3b8; margin-top: 0.1rem; }

/* ── Verdict ── */
.verdict {
    border-radius: 12px; padding: 0.8rem 1.2rem;
    font-size: 0.84rem; margin-top: 0.6rem; line-height: 1.5;
}
.v-go   { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.v-cond { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
.v-ng   { background: #fff1f2; color: #9f1239; border: 1px solid #fecdd3; }

/* ── Trade card ── */
.tr-card {
    background: #fff; border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    padding: 0.75rem 1.1rem; margin-bottom: 0.45rem;
    border-left: 4px solid #e2e8f0;
    display: flex; justify-content: space-between; align-items: center;
}
.tr-win  { border-left-color: #059669; }
.tr-loss { border-left-color: #e11d48; }
.tr-open { border-left-color: #2563eb; }
.tr-best { background: #ecfdf5; border-left-color: #059669; }
.tr-worst { background: #fff1f2; border-left-color: #e11d48; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #f8fafc; }
.cd-num { font-size: 2.4rem; font-weight: 800; line-height: 1; text-align: center; }
.cd-label { font-size: 0.72rem; color: #94a3b8; text-align: center; margin-top: 0.15rem; }

/* ── Mini stat ── */
.mini-stat { text-align: center; padding: 0.3rem 0; }
.mini-val { font-size: 1.1rem; font-weight: 700; color: #0f172a; }
.mini-label { font-size: 0.65rem; color: #94a3b8; margin-top: 0.1rem; }

/* ── Dialog styling ── */
.dlg-section {
    font-size: 0.78rem; font-weight: 700; color: #0f172a;
    margin-top: 1rem; margin-bottom: 0.4rem;
    padding-bottom: 0.3rem; border-bottom: 2px solid #f1f5f9;
}
.dlg-row {
    display: flex; justify-content: space-between;
    padding: 0.35rem 0; font-size: 0.82rem;
    border-bottom: 1px solid #f8fafc;
}
.dlg-key { color: #64748b; }
.dlg-val { font-weight: 600; color: #0f172a; }
.dlg-insight {
    background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px;
    padding: 0.7rem 1rem; margin-top: 0.7rem;
    font-size: 0.8rem; color: #92400e; line-height: 1.6;
}

/* ── Workflow stepper ── */
.wf-intro {
    background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px;
    padding: 0.8rem 1.2rem; margin-bottom: 0.8rem;
    font-size: 0.78rem; color: #1e40af; line-height: 1.6;
}
.wf-step {
    display: flex; align-items: center; gap: 0.9rem;
    padding: 0.7rem 1rem;
    border-bottom: 1px solid #f1f5f9;
}
.wf-step:last-child { border-bottom: none; }
.wf-num {
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700; flex-shrink: 0;
}
.wf-n-ok   { background: #ecfdf5; color: #059669; border: 2px solid #a7f3d0; }
.wf-n-fail { background: #fff1f2; color: #e11d48; border: 2px solid #fecdd3; }
.wf-n-wait { background: #f8fafc; color: #94a3b8; border: 2px dashed #cbd5e1; }
.wf-body { flex: 1; min-width: 0; }
.wf-name { font-size: 0.88rem; font-weight: 700; color: #0f172a; }
.wf-desc { font-size: 0.72rem; color: #94a3b8; margin-top: 0.1rem; }
.wf-right { text-align: right; flex-shrink: 0; min-width: 65px; }
.wf-val  { font-size: 1.05rem; font-weight: 700; color: #0f172a; }
.wf-ts   { font-size: 0.62rem; color: #94a3b8; margin-top: 0.1rem; }

/* ── Info tooltip ── */
.wf-info {
    display: inline-flex; align-items: center; justify-content: center;
    width: 16px; height: 16px; border-radius: 50%;
    background: #e2e8f0; color: #64748b; font-size: 0.6rem; font-weight: 700;
    cursor: help; margin-left: 0.35rem; position: relative; vertical-align: middle;
    transition: background 0.15s;
}
.wf-info:hover { background: #2563eb; color: #fff; }
.wf-tip {
    visibility: hidden; opacity: 0;
    position: absolute; bottom: calc(100% + 8px); left: 50%;
    transform: translateX(-50%); width: 260px;
    background: #1e293b; color: #f1f5f9; font-size: 0.68rem; font-weight: 400;
    line-height: 1.55; padding: 0.6rem 0.8rem; border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 1000; pointer-events: none;
    transition: opacity 0.15s, visibility 0.15s;
}
.wf-tip::after {
    content: ""; position: absolute; top: 100%; left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent; border-top-color: #1e293b;
}
.wf-info:hover .wf-tip { visibility: visible; opacity: 1; }

/* ── Drill-down <details> ── */
.dd-item {
    padding: 0.45rem 0.7rem; border-bottom: 1px solid #f1f5f9;
}
.dd-item:last-child { border-bottom: none; }
.dd-summary {
    cursor: pointer; font-size: 0.82rem; color: #0f172a;
    padding: 0.15rem 0; list-style: none;
}
.dd-summary::-webkit-details-marker { display: none; }
.dd-summary::before {
    content: "\\25B8"; margin-right: 0.4rem; color: #94a3b8;
    display: inline-block; transition: transform 0.15s;
}
details[open] > .dd-summary::before { transform: rotate(90deg); }
.dd-detail {
    margin-top: 0.4rem; padding: 0.55rem 0.8rem;
    background: #f8fafc; border-radius: 8px;
    font-size: 0.76rem; color: #475569; line-height: 1.65;
}
.dd-kv { display: flex; gap: 0.5rem; padding: 0.15rem 0; }
.dd-k { color: #94a3b8; min-width: 5rem; flex-shrink: 0; }
.dd-v { color: #0f172a; }

/* ── Timeline ── */
.tl-row {
    display: flex; align-items: center; gap: 0.7rem;
    padding: 0.55rem 0.8rem; border-bottom: 1px solid #f1f5f9;
}
.tl-row:last-child { border-bottom: none; }
.tl-date { width: 5.5rem; font-size: 0.78rem; font-weight: 600; color: #64748b; }
.tl-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.tl-ok   { background: #059669; }
.tl-warn { background: #f59e0b; }
.tl-fail { background: #e11d48; }
.tl-empty { background: #e2e8f0; }
.tl-info { flex: 1; font-size: 0.78rem; color: #0f172a; }
.tl-sub  { font-size: 0.68rem; color: #94a3b8; margin-left: 0.3rem; }
.tl-nums { font-size: 0.72rem; color: #64748b; text-align: right; white-space: nowrap; }

/* ── Health metric ── */
.health-val { font-size: 1.5rem; font-weight: 800; color: #0f172a; text-align: center; }
.health-label { font-size: 0.65rem; color: #94a3b8; text-align: center; margin-top: 0.1rem; }

/* ── Spec tab ── */
.spec-section { margin-bottom: 1.2rem; }
.spec-title {
    display: flex; align-items: center; gap: 0.5rem;
    font-size: 0.9rem; font-weight: 700; color: #0f172a;
    padding: 0.7rem 1rem; border-bottom: 2px solid #f1f5f9;
}
.spec-icon { font-size: 1rem; }
.spec-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 0.1rem; padding: 0.2rem 0.5rem;
}
.spec-row {
    display: flex; justify-content: space-between; align-items: baseline;
    padding: 0.4rem 0.5rem; border-bottom: 1px solid #f8fafc;
    font-size: 0.78rem;
}
.spec-row:last-child { border-bottom: none; }
.spec-k { color: #64748b; }
.spec-v { font-weight: 600; color: #0f172a; text-align: right; }
.spec-note {
    font-size: 0.72rem; color: #94a3b8; padding: 0.4rem 1rem 0.6rem;
    line-height: 1.55;
}
.spec-list {
    padding: 0.3rem 1rem 0.5rem; font-size: 0.76rem; color: #475569;
    line-height: 1.7;
}
.spec-list li { margin-bottom: 0.15rem; }
.spec-badge {
    display: inline-block; padding: 0.1rem 0.4rem; border-radius: 4px;
    font-size: 0.65rem; font-weight: 600; margin-right: 0.3rem;
}
.spec-b1 { background: #dbeafe; color: #1d4ed8; }
.spec-b2 { background: #ecfdf5; color: #059669; }
.spec-b3 { background: #f1f5f9; color: #64748b; }
.spec-highlight {
    background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px;
    padding: 0.7rem 1rem; margin: 0.5rem 1rem 0.8rem;
    font-size: 0.76rem; color: #1e40af; line-height: 1.6;
}

/* ── News utilization ── */
.nu-flow {
    display: flex; align-items: center; justify-content: center;
    gap: 0; padding: 0.8rem 0; flex-wrap: wrap;
}
.nu-node {
    text-align: center; padding: 0.5rem 0.7rem;
    border-radius: 10px; min-width: 80px;
}
.nu-active { background: #ecfdf5; border: 1.5px solid #a7f3d0; }
.nu-empty  { background: #f8fafc; border: 1.5px dashed #cbd5e1; }
.nu-icon   { font-size: 1rem; }
.nu-label  { font-size: 0.65rem; font-weight: 600; color: #64748b; margin-top: 0.1rem; }
.nu-val    { font-size: 0.95rem; font-weight: 700; color: #0f172a; }
.nu-arrow  { color: #cbd5e1; font-size: 1rem; margin: 0 0.15rem; }
.nu-src-bar {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.25rem 0; font-size: 0.75rem;
}
.nu-src-name { width: 7rem; color: #64748b; flex-shrink: 0; text-align: right; }
.nu-src-fill { height: 6px; border-radius: 3px; background: #2563eb; }
.nu-src-cnt  { color: #94a3b8; font-size: 0.68rem; min-width: 2.5rem; }
.nu-theme-card {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.3rem 0.6rem; border-radius: 8px;
    background: #fff; border: 1px solid #e2e8f0;
    font-size: 0.72rem; margin: 0.2rem;
}
.nu-score { font-weight: 700; }

/* ── Ticker flow (date detail page) ── */
.tf-card {
    background: #fff; border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    padding: 0.7rem 1rem; margin-bottom: 0.4rem;
    border-left: 4px solid #e2e8f0;
}
.tf-card-signal { border-left-color: #2563eb; }
.tf-card-trade  { border-left-color: #059669; }
.tf-header {
    display: flex; align-items: center; gap: 0.6rem;
    font-size: 0.85rem; font-weight: 700; color: #0f172a;
}
.tf-flow {
    display: flex; align-items: center; gap: 0.3rem;
    margin-top: 0.3rem; font-size: 0.75rem; color: #64748b;
    flex-wrap: wrap;
}
.tf-step {
    display: inline-flex; align-items: center; gap: 0.2rem;
    padding: 0.15rem 0.45rem; border-radius: 6px;
    background: #f8fafc;
}
.tf-arrow { color: #cbd5e1; font-size: 0.7rem; }

/* ── Breadcrumb ── */
.breadcrumb {
    font-size: 0.75rem; color: #94a3b8; margin-bottom: 1rem;
    padding: 0.3rem 0;
}
.breadcrumb a {
    color: #2563eb; text-decoration: none;
}
.breadcrumb a:hover { text-decoration: underline; }
.breadcrumb .sep { margin: 0 0.3rem; color: #cbd5e1; }

/* ── Streamlit overrides ── */
.stMarkdown { margin-bottom: 0; }
div[data-testid="stVerticalBlock"] > div:has(> .stMarkdown) { padding-top: 0; padding-bottom: 0; }
h1, h2, h3, h4 { color: #0f172a; }
div[data-testid="stPlotlyChart"] > div {
    border-radius: 16px; overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
}

/* ── Responsive ── */
@media (max-width: 768px) {
    .spec-grid { grid-template-columns: 1fr; }
    .cl-label { width: auto; min-width: 3.5rem; font-size: 0.7rem; }
    .cl-gap { width: auto; min-width: 4rem; font-size: 0.7rem; }
    .wf-step { flex-direction: column; }
    .wf-right { min-width: auto; text-align: left; margin-top: 0.3rem; }
    .tl-date { width: 4rem; font-size: 0.7rem; }
    .tl-nums { font-size: 0.65rem; }
    .wf-tip { width: 200px; font-size: 0.68rem; left: 0; transform: none; }
    .pos-row { flex-direction: column; gap: 0.2rem; }
    .split-row { flex-direction: column; gap: 0.5rem; }
    .tf-flow { flex-direction: column; align-items: flex-start; }
}
</style>
"""
