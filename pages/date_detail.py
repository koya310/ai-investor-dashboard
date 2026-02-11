"""Date Detail — 日付別詳細ログ"""

import logging
from datetime import date, datetime

import dashboard_data as _dm
import streamlit as st

from components.shared import P, W, WEEKDAY_JP, MODE_LABELS, section_header

logger = logging.getLogger(__name__)

# ── 対象日付を取得 ──
query_date = st.query_params.get("date", date.today().isoformat())
available_dates = _dm.get_available_log_dates(60)
date_options = [date.fromisoformat(d) for d in available_dates] if available_dates else [date.today()]

if available_dates and query_date not in available_dates:
    target_date = available_dates[0]
else:
    target_date = query_date

target_idx = 0
for i, dd in enumerate(date_options):
    if dd.isoformat() == target_date:
        target_idx = i
        break

selected_date = st.selectbox(
    "表示日",
    options=date_options,
    index=target_idx,
    format_func=lambda dd: f"{dd.isoformat()} ({WEEKDAY_JP[dd.weekday()]})",
)

if selected_date.isoformat() != target_date:
    st.query_params["date"] = selected_date.isoformat()
    st.rerun()

target_date = selected_date.isoformat()

try:
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    wd = WEEKDAY_JP[dt.weekday()]
    st.title(f"{target_date} ({wd})")
except Exception:
    st.title(target_date)

st.caption("日次の実行ログをニュース収集から取引まで時系列で確認します。")
with st.expander("このページの見方", expanded=False):
    st.markdown(
        """
        1. 上部メトリクスで当日の処理量を確認  
        2. `システム実行ログ` で失敗ランとエラー文を確認  
        3. `ティッカー別フロー` で銘柄ごとのニュース→分析→シグナル→取引を確認  
        4. 下部タブで生ログ（ニュース本文・AI要約・シグナル・取引）を確認
        """
    )

# ── サマリー ──
summary = _dm.get_log_day_summary(target_date)
runs = _dm.get_log_system_runs(target_date)
completed_runs = len(runs[runs["status"] == "completed"]) if len(runs) > 0 else 0
run_success_rate = (completed_runs / len(runs) * 100) if len(runs) > 0 else 0

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("ニュース", f"{summary['news']}件")
m2.metric("AI分析", f"{summary['analysis']}件")
m3.metric("シグナル", f"{summary['signals']}件")
m4.metric("取引", f"{summary['trades']}件")
m5.metric("実行回数", f"{summary['runs']}回")
m6.metric("完了率", f"{run_success_rate:.0f}%")

# ── システム実行ログ ──
section_header("システム実行ログ", color=P)
if len(runs) > 0:
    for _, r in runs.iterrows():
        status = r["status"]
        mode_label = MODE_LABELS.get(r["run_mode"], r["run_mode"])
        if status == "completed":
            st.success(
                f"**{mode_label}** | {r['started_at']} → {r.get('ended_at', '')} | "
                f"ニュース {r.get('news_collected', 0)} / "
                f"シグナル {r.get('signals_detected', 0)} / "
                f"取引 {r.get('trades_executed', 0)}"
            )
        elif status == "failed":
            st.error(
                f"**{mode_label}** | {r['started_at']} | "
                f"エラー: {r.get('error_message', '')[:100]}"
            )
        else:
            st.warning(f"**{mode_label}** | {r['started_at']} | {status}")
else:
    st.info("この日の実行記録なし")

# ── ティッカー別フロー ──
section_header("ティッカー別フロー", color=W)
st.caption("同日の銘柄別に、ニュース→分析→シグナル→取引の発生有無を表示します。")
ticker_flow = _dm.get_date_ticker_flow(target_date)

if ticker_flow:
    for tf in ticker_flow[:20]:
        with st.container(border=True):
            cols = st.columns([1, 1, 1, 1, 2])

            with cols[0]:
                st.markdown(f"**{tf['ticker']}**")

            with cols[1]:
                if tf["news_count"] > 0:
                    st.caption(f"ニュース {tf['news_count']}件")
                else:
                    st.caption("-")

            with cols[2]:
                if tf["analysis_count"] > 0:
                    direction = tf.get("analysis_direction", "")
                    dir_label = {
                        "bullish": ":green[強気]",
                        "bearish": ":red[弱気]",
                        "neutral": "中立",
                    }.get(direction, "")
                    st.markdown(f"分析 {tf['analysis_count']}件 {dir_label}")
                else:
                    st.caption("-")

            with cols[3]:
                sig = tf.get("signal")
                if sig:
                    sig_color = "green" if sig["type"] == "BUY" else "red"
                    st.markdown(
                        f":{sig_color}[**{sig['type']}**] "
                        f"確信度{sig.get('conviction', 0)}"
                    )
                else:
                    st.caption("-")

            with cols[4]:
                trd = tf.get("trade")
                if trd:
                    action_color = "green" if trd["action"] == "BUY" else "red"
                    pnl = trd.get("pnl")
                    pnl_str = ""
                    if pnl is not None:
                        pnl_color = "green" if pnl >= 0 else "red"
                        pnl_str = f" :{pnl_color}[${pnl:+,.0f}]"
                    st.markdown(
                        f":{action_color}[**{trd['action']}**] "
                        f"{trd['shares']}株 @${trd['price']:.2f}{pnl_str}"
                    )
                else:
                    st.caption("-")
else:
    st.info("この日のデータなし")

# ── 詳細タブ ──
news_df = _dm.get_log_news(target_date)
analysis_df = _dm.get_log_analyses(target_date)
sig_df = _dm.get_log_signals(target_date)
trades_df = _dm.get_log_trades(target_date)

tab_news, tab_analysis, tab_signals, tab_trades = st.tabs(
    [
        f"ニュース ({len(news_df)})",
        f"AI分析 ({len(analysis_df)})",
        f"シグナル ({len(sig_df)})",
        f"取引 ({len(trades_df)})",
    ]
)

with tab_news:
    if len(news_df) > 0:
        if "published_at" in news_df.columns:
            news_df = news_df.sort_values("published_at", ascending=False)
        for _, n in news_df.head(30).iterrows():
            with st.expander(f"{n['source']} | {n['title'][:80]}"):
                st.markdown(n.get("content", "")[:500])
                if n.get("url"):
                    st.caption(n["url"])
    else:
        st.info("ニュースなし")

with tab_analysis:
    if len(analysis_df) > 0:
        if "analyzed_at" in analysis_df.columns:
            analysis_df = analysis_df.sort_values("analyzed_at", ascending=False)
        for _, a in analysis_df.iterrows():
            direction = a.get("direction", "")
            dir_color = ("green" if direction == "bullish"
                         else ("red" if direction == "bearish" else "gray"))
            with st.expander(
                f"{a.get('theme', '')} | {a.get('ticker', '')} | "
                f":{dir_color}[{direction}] {a.get('score', 0):.0f}"
            ):
                st.markdown(a.get("summary", ""))
    else:
        st.info("AI分析なし")

with tab_signals:
    if len(sig_df) > 0:
        if "detected_at" in sig_df.columns:
            sig_df = sig_df.sort_values("detected_at", ascending=False)
        st.dataframe(
            sig_df[
                ["ticker", "signal_type", "conviction", "confidence",
                 "price", "status", "detected_at"]
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("シグナルなし")

with tab_trades:
    if len(trades_df) > 0:
        if "entry_timestamp" in trades_df.columns:
            trades_df = trades_df.sort_values("entry_timestamp", ascending=False)
        st.dataframe(trades_df, use_container_width=True, hide_index=True)
    else:
        st.info("取引なし")
