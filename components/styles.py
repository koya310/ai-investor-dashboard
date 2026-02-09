"""最小限のCSS — ネイティブコンポーネント移行後の残存スタイル"""

import streamlit as st


def inject_css():
    """ネイティブStreamlitコンポーネントへ移行後の最小CSS"""
    st.markdown(
        """<style>
/* ── グローバル微調整 ── */

/* メインエリアの上部余白を詰める */
.block-container {
    padding-top: 1.5rem;
}

/* メトリクス数値のフォントサイズ調整 */
[data-testid="stMetricValue"] {
    font-size: 1.2rem;
}

/* メトリクスラベルの色 */
[data-testid="stMetricLabel"] {
    color: #64748b;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* コンテナ内の余白調整 */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
    padding: 0;
}

/* expander ヘッダーのフォント */
details summary {
    font-size: 0.85rem;
    font-weight: 600;
}

/* ダイアログ内の横幅を広めに */
[data-testid="stDialog"] {
    min-width: 700px;
}

/* divider の余白を詰める */
hr {
    margin: 0.3rem 0;
}

/* ── ダイアログ内テーブル用（Tier 3: 残存HTML） ── */

.dlg-section {
    font-size: 0.82rem;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.3rem;
    margin: 1rem 0 0.5rem;
}

.dlg-row {
    display: flex;
    justify-content: space-between;
    padding: 0.25rem 0;
    font-size: 0.8rem;
    border-bottom: 1px solid #f8fafc;
}

.dlg-key {
    color: #64748b;
}

.dlg-val {
    font-weight: 600;
    color: #0f172a;
}

.dlg-insight {
    background: #fff7ed;
    border-left: 3px solid #f59e0b;
    border-radius: 4px;
    padding: 0.6rem 0.8rem;
    margin: 0.5rem 0;
    font-size: 0.78rem;
    color: #92400e;
}

/* ── 正負カラーユーティリティ（最小限残存） ── */

.c-pos { color: #059669; }
.c-neg { color: #e11d48; }
</style>""",
        unsafe_allow_html=True,
    )
