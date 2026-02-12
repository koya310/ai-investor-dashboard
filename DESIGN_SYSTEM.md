# AI Investor Dashboard — Design System v2.0

> Dark-theme financial dashboard inspired by Bloomberg Terminal, TradingView, shadcn/ui.
> Built for Streamlit 1.42+ on Streamlit Cloud.
> Research: 20+ professional dashboards analyzed (2026-02-12).

---

## 1. Design Philosophy

| Principle | Why | How |
|-----------|-----|-----|
| **Dark-first** | Trading dashboards are dark. Reduces eye strain, data pops on dark bg. | Zinc-950 page bg, Zinc-900 cards |
| **Card = 1 purpose** | Each card answers ONE question for the user | `st.container(border=True)` per logical unit |
| **Numbers first** | Users scan KPIs in <2 seconds | Hero value top-left, 36px bold |
| **Minimal color** | Too many colors = visual noise | Gray base + green/red semantic + 1 accent |
| **Generous whitespace** | Breathing room makes data readable | 16px gaps, 20-24px card padding |
| **Tabular numbers** | Financial data must column-align | `font-variant-numeric: tabular-nums` everywhere |

---

## 2. Color Tokens

### 2A. Background & Surface (Zinc scale from Tailwind)

| Token | Hex | Usage |
|-------|-----|-------|
| `BG_PAGE` | `#09090b` | Page background (Zinc-950) |
| `BG_CARD` | `#18181b` | Card / widget surface (Zinc-900) |
| `BG_ELEVATED` | `#27272a` | Nested elements, hover bg (Zinc-800) |
| `BG_HOVER` | `#3f3f46` | Pressed states (Zinc-700) |

### 2B. Text

| Token | Hex | Usage |
|-------|-----|-------|
| `TEXT_PRIMARY` | `#fafafa` | Headlines, KPI values (Zinc-50) |
| `TEXT_SECONDARY` | `#a1a1aa` | Labels, descriptions (Zinc-400) |
| `TEXT_MUTED` | `#71717a` | Timestamps, captions (Zinc-500) |

### 2C. Border

| Token | Hex | Usage |
|-------|-----|-------|
| `BORDER` | `#27272a` | Card borders (Zinc-800) |
| `BORDER_HOVER` | `#3f3f46` | Hover borders (Zinc-700) |

### 2D. Semantic Colors

| Token | Hex | Tint BG | Usage |
|-------|-----|---------|-------|
| `PROFIT` | `#22c55e` | `#052e16` | Positive P&L, success (Green-500) |
| `LOSS` | `#ef4444` | `#450a0a` | Negative P&L, error (Red-500) |
| `WARNING` | `#f59e0b` | `#451a03` | Caution states (Amber-500) |
| `ACCENT` | `#6366f1` | `#1e1b4b` | Interactive, links, active (Indigo-500) |
| `INFO` | `#3b82f6` | `#172554` | Informational (Blue-500) |

### 2E. Chart Palette (colorblind-safe)

```python
CHART_COLORS = [
    "#6366f1",  # Indigo (primary)
    "#22c55e",  # Green
    "#f59e0b",  # Amber
    "#ef4444",  # Red
    "#8b5cf6",  # Violet
    "#06b6d4",  # Cyan
    "#ec4899",  # Pink
    "#a1a1aa",  # Gray (baseline)
]
```

---

## 3. Typography

### 3A. Font Stack

```
Primary:  Inter, -apple-system, BlinkMacSystemFont, sans-serif
Japanese: Hiragino Kaku Gothic ProN, Yu Gothic, Meiryo
Mono:     JetBrains Mono, SF Mono, Consolas, monospace
```

Loading method: `<link>` tag (NOT `@import` — prevents CSS block failure).

### 3B. Type Scale

| Role | Size | Weight | Letter-spacing | Usage |
|------|------|--------|----------------|-------|
| Hero value | 2.25rem (36px) | 800 | -0.03em | Portfolio total |
| Page title | 1.5rem (24px) | 700 | -0.02em | st.title() |
| KPI value | 1.75rem (28px) | 700 | -0.01em | Metric values |
| Card title | 0.875rem (14px) | 700 | 0 | Card headers |
| Body | 0.875rem (14px) | 400 | 0 | Default text |
| Label | 0.75rem (12px) | 600 | 0.05em | UPPERCASE labels |
| Caption | 0.75rem (12px) | 400 | 0.01em | Timestamps |

### 3C. Numeric Rules

- ALL financial figures: `font-variant-numeric: tabular-nums`
- Positive values: `#22c55e` (PROFIT)
- Negative values: `#ef4444` (LOSS)
- Delta format: `+$1,234 (+1.6%)` or `-$1,234 (-1.6%)`

---

## 4. Card System

### 4A. Base Card CSS

```css
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #18181b !important;
    border: 1px solid #27272a !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

/* Inner content — must also be styled */
div[data-testid="stVerticalBlockBorderWrapper"] > div:first-child {
    background-color: #18181b !important;
    border-radius: 12px !important;
}
```

### 4B. Card Hover

```css
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #3f3f46 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
}
```

### 4C. Card Title Pattern

```
[● dot 8px] [Title 14px bold] [subtitle pill]
```

### 4D. Metric Card

```css
div[data-testid="metric-container"] {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 12px;
    padding: 16px 20px;
}
/* Label: 12px, 600, UPPERCASE, #a1a1aa, 0.05em spacing */
/* Value: 28px, 700, #fafafa, tabular-nums */
```

---

## 5. Layout Grid

### 5A. Page Structure

```
SIDEBAR (240px, #0f0f12)  |  MAIN (fluid, max-width off)
                          |
                          |  Page Title + caption
                          |
                          |  ROW 1: Hero KPI (full-width card)
                          |
                          |  ROW 2: [Card 2/3] | [Card 1/3]
                          |         or [Card] | [Card] 50/50
                          |
                          |  ROW 3: Chart or data card
                          |
                          |  ROW 4: Table / detail / expander
```

### 5B. Spacing

| Token | Value | Usage |
|-------|-------|-------|
| Gap between cards | 16px | `st.columns(gap="medium")` |
| Card padding | 20px 24px | Internal content |
| Page padding | 1.5rem top, 2rem sides | Block container |
| Section break | 24px | Between card groups |

### 5C. Column Patterns

```python
st.columns(4)             # KPI row
st.columns([2, 1])        # Main + sidebar
st.columns(2)             # Equal halves
st.columns([1.2, 2.5, 1.2, 1.1])  # Date nav
```

---

## 6. Status Indicators

### 6A. Status Dot (8px circle)

| Status | Color | Glow |
|--------|-------|------|
| OK | `#22c55e` | `rgba(34,197,94,0.3)` |
| Warning | `#f59e0b` | `rgba(245,158,11,0.3)` |
| Error | `#ef4444` | `rgba(239,68,68,0.3)` |
| Offline | `#71717a` | none |
| Active | `#6366f1` | `rgba(99,102,241,0.3)` |

### 6B. Status Badge (pill)

```html
<span style="...background:#052e16;color:#4ade80;border-radius:9999px;
  padding:3px 10px;font-size:12px;font-weight:500">
  <span style="...8px dot..."></span> 正常稼働
</span>
```

---

## 7. Chart Theme (Plotly)

```python
CHART_LAYOUT = dict(
    height=320,
    margin=dict(l=0, r=0, t=24, b=0),
    plot_bgcolor="#18181b",
    paper_bgcolor="#18181b",
    font=dict(family="Inter, sans-serif", color="#a1a1aa", size=12),
    xaxis=dict(
        gridcolor="#27272a", linecolor="#3f3f46",
        tickfont=dict(size=11, color="#71717a"), showgrid=True,
    ),
    yaxis=dict(
        gridcolor="#27272a", linecolor="#3f3f46",
        tickfont=dict(size=11, color="#71717a"), showgrid=True,
        tickprefix="$", tickformat=",.0f",
    ),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="#27272a", bordercolor="#3f3f46",
        font=dict(color="#fafafa", size=12),
    ),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="right", x=1, font=dict(size=11, color="#a1a1aa"),
    ),
)
```

CRITICAL: `st.plotly_chart(fig, use_container_width=True, theme=None)`

---

## 8. config.toml

```toml
[theme]
base = "dark"
primaryColor = "#6366f1"
backgroundColor = "#09090b"
secondaryBackgroundColor = "#18181b"
textColor = "#fafafa"
font = "sans serif"
```

---

## 9. CSS Selector Reference

| Target | Selector |
|--------|----------|
| Metric | `div[data-testid="metric-container"]` |
| Metric label | `label[data-testid="stMetricLabel"] > div` |
| Metric value | `div[data-testid="stMetricValue"]` |
| Card wrapper | `div[data-testid="stVerticalBlockBorderWrapper"]` |
| Card inner | `div[data-testid="stVerticalBlockBorderWrapper"] > div:first-child` |
| Sidebar | `section[data-testid="stSidebar"]` |
| Main content | `section.stMain .block-container` |
| Tab list | `.stTabs [data-baseweb="tab-list"]` |
| Tab active | `.stTabs [aria-selected="true"]` |
| Expander | `div[data-testid="stExpander"]` |
| Header | `header[data-testid="stHeader"]` |
| Columns | `div[data-testid="stHorizontalBlock"]` |

---

## 10. Implementation Rules

1. Font loading via `<link>` tag, NEVER `@import`
2. Plotly charts: always `theme=None`
3. Card bg: style BOTH wrapper AND `> div:first-child`
4. All CSS overrides need `!important`
5. Sidebar: explicit `background-color` on `stSidebar`
6. Scrollbar: thin 6px, Zinc-700 thumb, Zinc-950 track
7. Hide Streamlit branding: `#MainMenu`, `footer` → hidden

---

## 11. Page Layouts

### Home

```
[Hero: $98,441 + P&L + SPY]     full-width
[Go/No-Go]  |  [保有銘柄]        2-col
[資産推移 Plotly chart]           full-width
[KPI 4列: 勝率/年率/DD/稼働率]    full-width
[取引履歴 (collapsible)]          full-width
```

### Pipeline

```
[本日サマリー 4 metrics]          full-width
[5-step process]                  full-width
[運用品質]  |  [日付選択]          2-col
[日次カレンダー 14d]               full-width
```

### Date Detail

```
[◀ 日付ナビ ▶]                    compact
[サマリー 6 metrics]               full-width
[実行ログ]  |  [Ticker別フロー]     2-col
[詳細データ tabs]                   full-width
```
