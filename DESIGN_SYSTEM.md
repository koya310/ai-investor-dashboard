# AI Investor Dashboard — Design System

> ネイティブStreamlitコンポーネントを軸とした軽量デザインシステム。
> 「壊れない表示 > 見た目の細かさ」を原則とする。

---

## 1. 設計原則

### 3-Tier コンポーネント戦略

| Tier | 方針 | 使用場面 | unsafe_allow_html |
|------|------|---------|-------------------|
| **Tier 1** | Streamlitネイティブのみ | メトリクス、バナー、プログレス、テーブル | なし |
| **Tier 2** | ネイティブ + 最小インラインCSS | セクションヘッダー、ピル、ステップ番号 | あり（局所的） |
| **Tier 3** | カスタムHTML（例外的に残存） | ダイアログ内テーブル | あり |

### 原則
- **ネイティブ優先**: `st.metric()`, `st.progress()`, `st.container(border=True)` を最優先で使う
- **CSS最小化**: グローバルCSS は95行以下。クラスベースのスタイルは極力排除
- **壊れない**: HTML描画失敗時にテキストがそのまま見える状態を回避する
- **レスポンシブ**: `st.columns()` の自動レスポンシブに委ねる

---

## 2. カラーパレット

```python
# components/shared.py で定義
P = "#2563eb"   # Primary Blue  — ヘッダー、チャート主線
W = "#059669"   # Win Emerald   — 正の値、成功状態
L = "#e11d48"   # Loss Rose     — 負の値、エラー状態
```

| 用途 | 色 | コード | Streamlit対応 |
|------|---|--------|--------------|
| 主要アクセント | Blue | `#2563eb` | `:blue[text]` |
| 利益・成功 | Emerald | `#059669` | `:green[text]`, `st.success()` |
| 損失・エラー | Rose | `#e11d48` | `:red[text]`, `st.error()` |
| 警告・注意 | Amber | `#f59e0b` | `st.warning()` |
| 補助テキスト | Slate | `#94a3b8` | `st.caption()` |
| 背景 | White | `#ffffff` | デフォルト |

---

## 3. コンポーネントカタログ

### Tier 1: ネイティブコンポーネント

#### メトリクスカード
```python
st.metric("勝率", "55%", delta="目標 55%", delta_color="off")
```
用途: KPI表示、ポートフォリオ数値、パイプライン統計

#### ステータスバナー
```python
st.success("**GO** — 全5項目を達成。Phase 4へ移行可能です。")
st.warning("**条件付き** — 3/5項目を達成。")
st.error("**未達** — 2/5項目のみ達成。残り20日で改善が必要です。")
```
用途: Go/No-Go判定、システム状態表示

#### プログレスバー
```python
st.progress(min(1.0, max(0.0, value / target)))
```
用途: KPIチェックリスト達成度

#### コンテナ
```python
with st.container(border=True):
    # カード的なグルーピング
```
用途: ポートフォリオ詳細、取引カード、保有銘柄リスト

#### エクスパンダー
```python
with st.expander("過去の取引をすべて表示（残り12件）", expanded=False):
    # プログレッシブ・ディスクロージャー
```
用途: 取引履歴の折りたたみ、ニュース・分析詳細

#### ダイアログ
```python
@st.dialog("パフォーマンス詳細分析", width="large")
def show_analysis_dialog():
    st.subheader("損益の全体像", divider="gray")
    st.metric("決済回数", "5回", "3勝 2敗")
```
用途: 詳細分析の別画面表示

### Tier 2: ネイティブ + 最小CSS

#### セクションヘッダー
```python
section_header("実取引チェックリスト", color="#f59e0b", subtitle="残り20日で判定")
```
実装: 4px幅のアクセントバー + インラインスタイル。CSSクラス不使用。

#### ピルバッジ
```python
st.markdown(f"ソース {render_pill('Alpaca')}", unsafe_allow_html=True)
```
実装: インラインスタイルの `<span>`。背景色はメイン色の8%透明度。

#### ステッパー番号
```python
# pipeline.py のワークフローステップ
st.markdown(
    '<div style="width:28px;height:28px;border-radius:50%;'
    f'background:{W};...">'
    '✓</div>',
    unsafe_allow_html=True,
)
```
実装: 完了=緑丸✓、失敗=赤丸✗、待機=グレー丸+番号。

### Tier 3: カスタムHTML（残存）

#### ダイアログ内テーブル
```css
.dlg-section { ... }
.dlg-row { display: flex; justify-content: space-between; }
.dlg-key { color: #64748b; }
.dlg-val { font-weight: 600; }
.dlg-insight { background: #fff7ed; border-left: 3px solid #f59e0b; }
```
注: ダイアログ内でのみ使用。メインページでは不使用。

---

## 4. フォーマットヘルパー

`components/shared.py` で定義。全ページで統一的に使用。

| 関数 | 用途 | 例 |
|------|------|-----|
| `fmt_currency(val, show_sign)` | 通貨表示 | `$1,234` / `+$1,234` |
| `fmt_pct(val, show_sign, decimals)` | パーセント | `12.3%` / `+12.3%` |
| `fmt_delta(val, is_pct)` | st.metric用delta | `+$1,234` / `+12.3%` |
| `color_for_value(val)` | 正負で色コード | `#059669` / `#e11d48` |
| `color_for_status(status)` | ステータス→色 | completed→緑, failed→赤 |
| `render_pill(label, color)` | バッジHTML | `<span>Alpaca</span>` |

---

## 5. レイアウトパターン

### ファーストビュー（home.py 上部）
```
[メトリクス x3]        ← st.columns(3) + st.metric
[Verdictバナー][ボタン] ← st.columns([5, 1]) + st.success/warning/error
[データ信頼度注記]      ← st.caption (条件付き表示)
```

### KPIチェックリスト（home.py）
```
[ラベル][プログレスバー][達成/未達]  ← st.columns([2, 4, 2])
  説明    現在値 / 目標値           ← st.caption + st.progress
```

### パイプラインステッパー（pipeline.py）
```
[番号丸][ステップ名+説明][件数+時刻]  ← st.columns([1, 5, 2])
─── divider ───
[番号丸][ステップ名+説明][件数+時刻]
```

### 取引カード（home.py）
```
with st.container(border=True):
  [銘柄 株数 価格 日付][損益金額 (%)]  ← st.columns([4, 2])
```

### カレンダー行（pipeline.py）
```
[日付][状態dot][モード名][実績数値]  ← st.columns([2, 0.5, 4, 3])
```

---

## 6. グローバルCSS（styles.py）

95行のみ。以下のカテゴリのみ残存:

| カテゴリ | 行数 | 目的 |
|---------|------|------|
| `.block-container` padding | 3 | 上部余白の調整 |
| `[data-testid="stMetricValue"]` | 3 | メトリクス数値サイズ |
| `[data-testid="stMetricLabel"]` | 5 | メトリクスラベルスタイル |
| コンテナ余白 | 3 | ボーダーコンテナのパディング |
| expander ヘッダー | 4 | フォントサイズ・太さ |
| ダイアログ min-width | 3 | 最小幅700px |
| hr 余白 | 3 | dividerの余白削減 |
| `.dlg-*` (Tier 3) | 25 | ダイアログ内テーブル用 |
| `.c-pos` / `.c-neg` | 2 | 正負カラーユーティリティ |

---

## 7. Streamlitカラーテキスト記法

Streamlitのマークダウン内で `:[color][text]` 記法を積極活用:

```python
# 利益 = 緑, 損失 = 赤
pnl_color = "green" if pnl >= 0 else "red"
st.markdown(f":{pnl_color}[**+$1,234** (+5.2%)]")

# ステータス表示
st.markdown(":green[**BUY**] 確信度8")
st.markdown(":red[**SELL**] 損切り")
st.markdown(":blue[**保有中**]")
```

---

## 8. データ層（dashboard_data.py）

- GCPのSQLiteデータベースからデータを取得
- 全データ関数は `get_*()` or `build_*()` の命名規則
- `components/shared.py` で `@st.cache_data` ラッパーを提供
- TTL: リアルタイムデータ=120秒、日次データ=600秒

---

## 9. ページ構成

| ページ | ファイル | 主要コンポーネント |
|--------|---------|------------------|
| ポートフォリオ | `pages/home.py` | metric, progress, container, dialog, plotly |
| パイプライン | `pages/pipeline.py` | columns, metric, expander, plotly |
| 日付詳細 | `pages/date_detail.py` | metric, tabs, container, dataframe |
| システム仕様 | `pages/reference.py` | container, metric, tabs, markdown table |

---

## 10. 移行実績

| 指標 | Before | After | 変化 |
|------|--------|-------|------|
| CSS行数 | 500+ | 95 | -81% |
| unsafe_allow_html | 90+ | ~12 | -87% |
| HTML表示バグリスク | 高 | 極低 | - |
| CSSクラス数 | ~70 | 5 | -93% |
| モバイル対応 | 手動 | 自動 | - |

---

## 11. 関連仕様書

- 画面内仕様: `pages/reference.py`
- ドキュメント版詳細仕様: `SYSTEM_SPEC.md`
