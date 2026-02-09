"""Reference — システム仕様リファレンス"""

import streamlit as st

from components.shared import section_header, P, W, L

st.title("システム仕様")
st.caption("AI Investor Phase 3 ペーパートレードの仕様概要")

# ── 投資プロセス ──
section_header("投資プロセス概要", color=P)

with st.container(border=True):
    st.markdown("""
    **5ステップの自動投資パイプライン**

    1. **情報収集** — Finnhub・Google News RSS・Yahoo Finance等から市場ニュースを自動収集
    2. **AI分析** — Gemini ProがシニアアナリストとしてCoT推論・テーマ評価・センチメント分析を実施
    3. **売買判断** — 3戦略（押し目買い・トレンド追従・VIX逆張り）のテクニカル＋AIニュース分析を統合
    4. **注文執行** — 7段階のリスクチェック通過後、Alpaca APIで自動発注
    5. **資産記録** — ポジション・残高をDBに記録、日次パフォーマンス算出
    """)

# ── KPI目標 ──
section_header("Go/No-Go KPI目標", color="#f59e0b")

k1, k2, k3, k4 = st.columns(4)
k1.metric("勝率", "≥ 55%")
k2.metric("年率リターン", "≥ 12%")
k3.metric("最大DD", "≤ 15%")
k4.metric("稼働率", "≥ 99%")

# ── リスク管理 ──
section_header("リスク管理", color=L)

with st.container(border=True):
    st.markdown("""
    | パラメータ | 値 | 説明 |
    |-----------|-----|------|
    | ハードストップロス | -8% | 含み損が-8%に達したら強制売却 |
    | ポートフォリオ上限 | 90% | 株式エクスポージャーの上限 |
    | 最低現金保有 | $5,000 | 常に確保する最低現金 |
    | 1日最大買付 | 3件 | 1日あたりの最大新規買い数 |
    | セクター上限 | 1件/セクター | 同一セクター最大1件/日 |
    | 決算ブラックアウト | 7日 | 決算発表前後7日は新規買い不可 |
    | リスクリワード比 | ≥ 1.5:1 | 最低リスクリワード比 |
    """)

# ── シグナル生成 ──
section_header("シグナル生成戦略", color=W)

tab1, tab2, tab3 = st.tabs(["押し目買い", "トレンド追従", "VIX逆張り"])

with tab1:
    st.markdown("""
    **Mean Reversion（押し目買い）**
    - RSI < 35 かつ MA200より上
    - ボリンジャーバンド下限付近
    - 出来高が平均の1.3倍以上
    """)

with tab2:
    st.markdown("""
    **Trend Following（トレンド追従）**
    - MA50がMA200を上抜け（ゴールデンクロス）
    - MACD がシグナルラインを上回る
    - セクターETFのモメンタムが正
    """)

with tab3:
    st.markdown("""
    **VIX Contrarian（VIX逆張り）**
    - VIX ≥ 25（恐怖指数が高い = 市場パニック）
    - 優良銘柄の急落を買い向かう
    - 確信度閾値が動的に上がる（VIX > 25 → 閾値9）
    """)

# ── 運用環境 ──
section_header("運用環境", color=P)

with st.container(border=True):
    e1, e2 = st.columns(2)
    with e1:
        st.markdown("""
        **GCP (本番)**
        - VM: e2-micro (1GB + 1GB swap)
        - OS: Debian 12
        - systemd サービス (24h稼働)
        - SQLite + WAL モード
        """)
    with e2:
        st.markdown("""
        **スケジュール (ET)**
        - 09:30 フル実行
        - 11:00 中間チェック
        - 13:00 シグナル確認
        - 15:30 最終チェック
        - 16:30 デイリーサマリー
        """)
