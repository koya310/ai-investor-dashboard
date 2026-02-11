"""Reference — システム仕様リファレンス"""

from datetime import datetime

import dashboard_data as _dm
import streamlit as st

from components.shared import L, P, W, section_header

fresh = _dm.get_data_latest_dates()

st.title("システム仕様")
with st.container(border=True):
    st.caption("判定基準・計算式・実行ルール・障害時の見方をまとめています。")


section_header("運用スコープ", color=P)
with st.container(border=True):
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Phase 3 開始日", _dm.PHASE3_START)
    c2.metric("判定期限", _dm.GONOGO_DEADLINE)
    c3.metric("初期資本", f"${_dm.INITIAL_CAPITAL:,.0f}")
    c4.metric("判定KPI", "4項目")
    c5.metric("最新データ日", fresh.get("latest", "-") or "-")
    st.caption(f"画面更新時刻: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


section_header("Go/No-Go 判定仕様", color="#f59e0b")
with st.container(border=True):
    st.markdown(
        f"""
| KPI | 目標値 | 計算式 | 判定の意味 |
|---|---:|---|---|
| 勝率 | **{_dm.KPI_TARGETS['win_rate']:.0f}%以上** | `wins / closed_trades * 100` | 取引の質 |
| 年率リターン | **{_dm.KPI_TARGETS['annual_return']:.0f}%以上** | `actual_return_pct * (365 / days_running)` | 収益性 |
| 最大DD | **{_dm.KPI_TARGETS['max_drawdown']:.0f}%以下** | ピーク比の最大下落率 | 下振れ耐性 |
| 稼働率 | **{_dm.KPI_TARGETS['uptime']:.0f}%以上** | `completed_runs / total_runs * 100` | 運用品質 |
"""
    )

    st.markdown(
        """
        **総合判定ロジック**

        - `GO`: 4/4 達成
        - `CONDITIONAL_GO`: 3/4 達成
        - `NO_GO`: 0-2/4 達成
        """
    )


section_header("KPIの計算ルール", color=W)
with st.container(border=True):
    st.markdown(
        """
        | 項目 | 詳細ルール |
        |---|---|
        | 勝率 | `status='CLOSED'` の取引のみ対象 |
        | 年率リターン | 累積損益を初期資本で割り、運用日数で年換算 |
        | 最大DD | `portfolio_snapshots` 優先。無い場合はトレード損益から推定 |
        | 稼働率 | 開始7日以内は全期間、8日目以降は直近7日ローリング |
        """
    )


section_header("パイプライン仕様", color=P)
with st.container(border=True):
    st.markdown(
        """
| Step | 入力 | 出力 | ユーザー視点の確認ポイント |
|---|---|---|---|
| 1. 情報収集 | ニュースAPI/RSS | `news` | ニュース件数が0でないか |
| 2. AI分析 | ニュース・銘柄群 | `ai_analysis` | 方向性(強気/弱気)が偏っていないか |
| 3. 売買判断 | テクニカル+AI分析 | `signals` | シグナルの確信度が低すぎないか |
| 4. 注文執行 | シグナル+リスク制約 | `trades` | シグナルに対し実行漏れがないか |
| 5. 資産記録 | 約定・ポジション | `portfolio_snapshots` | 損益・DD表示が更新されているか |
"""
    )


section_header("実行モードと期待結果", color=W)
with st.container(border=True):
    st.markdown(
        """
| モード | 意味 | 最低限更新されるべきデータ |
|---|---|---|
| フル実行 | 収集〜執行まで一括 | `news`, `ai_analysis`, `signals`, `trades`, `system_runs` |
| 中間実行 | 日中の再評価 | `signals`, `system_runs` |
| 軽量実行 | 最小再チェック | `system_runs` |
| ニュース収集 | 収集のみ | `news`, `system_runs` |
| 分析のみ | 分析更新 | `ai_analysis`, `system_runs` |
"""
    )


section_header("リスク管理ルール", color=L)
with st.container(border=True):
    st.markdown(
        """
| 項目 | ルール | 目的 |
|---|---|---|
| ハードストップロス | -8% | 単一銘柄の急落を制限 |
| 最低リスクリワード | 1.5:1以上 | 期待値の維持 |
| 1日最大買付 | 3件 | 過剰売買を抑制 |
| セクター集中制限 | 1件/セクター/日 | 集中リスク抑制 |
| 決算ブラックアウト | 前後7日 | ギャップリスク回避 |
| 最低現金保有 | $5,000 | 運用継続性の確保 |
"""
    )


section_header("データ更新・鮮度", color=P)
with st.container(border=True):
    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("news", fresh.get("news", "-") or "-")
    d2.metric("analysis", fresh.get("analysis", "-") or "-")
    d3.metric("signals", fresh.get("signals", "-") or "-")
    d4.metric("runs", fresh.get("runs", "-") or "-")
    d5.metric("trades", fresh.get("trades", "-") or "-")

    st.markdown(
        """
| 項目 | キャッシュTTL | 備考 |
|---|---:|---|
| Alpacaポートフォリオ/ポジション | 120秒 | 失敗時はトレード履歴推定にフォールバック |
| パイプライン状態 | 120秒 | 当日状況を短周期更新 |
| 日次資産推移/SPY比較 | 600秒 | 中長期表示のため長め |
| 品質集計・タイムライン | 600秒 | 直近7日平均を使用 |
"""
    )


section_header("画面ごとの使い分け", color=W)
with st.container(border=True):
    st.markdown(
        """
| 画面 | 見るべき指標 | 主な判断 |
|---|---|---|
| ポートフォリオ | KPI達成率、累積損益、DD | 実取引移行可否 |
| パイプライン | 当日ステップ完了状況、異常件数 | 運用停止ポイントの把握 |
| 日付詳細 | 実行ログ、Tickerフロー、売買実行有無 | 日次原因分析 |
"""
    )

