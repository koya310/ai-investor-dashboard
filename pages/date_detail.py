"""Date Detail — 日付別詳細ログ"""

from __future__ import annotations

import logging
from datetime import date, datetime

import dashboard_data as _dm
import streamlit as st

from components.shared import (
    L,
    MODE_LABELS,
    P,
    W,
    WEEKDAY_JP,
    fmt_currency,
    nav_back,
    render_pill,
    section_header,
)

logger = logging.getLogger(__name__)


def _as_date(s: str | None, fallback: date) -> date:
    if not s:
        return fallback
    try:
        return date.fromisoformat(s)
    except Exception:
        return fallback


def _hm(ts: str) -> str:
    if not ts or len(ts) < 16:
        return "-"
    return ts[11:16]


def _set_date_query(d: date) -> None:
    st.query_params["date"] = d.isoformat()
    st.rerun()


available_str = _dm.get_available_log_dates(365)
available_dates = sorted([date.fromisoformat(d) for d in available_str]) if available_str else []
fresh = _dm.get_data_latest_dates()

latest_available = available_dates[-1] if available_dates else date.today()
earliest_available = available_dates[0] if available_dates else date.today()

query_date = _as_date(st.query_params.get("date"), latest_available)
if query_date < earliest_available:
    query_date = earliest_available
if query_date > latest_available:
    query_date = latest_available

idx = available_dates.index(query_date) if query_date in available_dates else -1
prev_date = available_dates[idx - 1] if idx > 0 else None
next_date = available_dates[idx + 1] if idx >= 0 and idx < len(available_dates) - 1 else None

nav_back("← パイプライン", "pages/pipeline.py")

st.title("日付詳細")
with st.container(border=True):
    nav1, nav2, nav3, nav4 = st.columns([1.2, 2.5, 1.2, 1.1])
    with nav1:
        if st.button("◀ 前日", use_container_width=True, disabled=prev_date is None):
            _set_date_query(prev_date)
    with nav2:
        picked = st.date_input(
            "表示日",
            value=query_date,
            min_value=earliest_available,
            max_value=max(latest_available, date.today()),
            format="YYYY-MM-DD",
        )
    with nav3:
        if st.button("翌日 ▶", use_container_width=True, disabled=next_date is None):
            _set_date_query(next_date)
    with nav4:
        if st.button("最新へ", use_container_width=True, disabled=query_date == latest_available):
            _set_date_query(latest_available)

    if picked != query_date:
        _set_date_query(picked)

    wd = WEEKDAY_JP[query_date.weekday()]
    st.markdown(f"**{query_date.isoformat()} ({wd})**")
    st.caption(
        f"最新データ日: {fresh.get('latest', '-') or '-'}  "
        f"(runs: {fresh.get('runs', '-') or '-'} / signals: {fresh.get('signals', '-') or '-'})"
    )

target_date = query_date.isoformat()
summary = _dm.get_log_day_summary(target_date)
runs = _dm.get_log_system_runs(target_date)
ticker_flow = _dm.get_date_ticker_flow(target_date)

completed_runs = len(runs[runs["status"] == "completed"]) if len(runs) > 0 else 0
run_success_rate = (completed_runs / len(runs) * 100) if len(runs) > 0 else 0
traded_cnt = sum(1 for tf in ticker_flow if tf.get("trade"))
signal_only_cnt = sum(1 for tf in ticker_flow if tf.get("signal") and not tf.get("trade"))

section_header("当日サマリー", color=P, subtitle=target_date)
with st.container(border=True):
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("ニュース", f"{summary['news']}件")
    m2.metric("AI分析", f"{summary['analysis']}件")
    m3.metric("シグナル", f"{summary['signals']}件")
    m4.metric("約定", f"{summary['trades']}件")
    m5.metric("実行回数", f"{summary['runs']}回")
    m6.metric("実行完了率", f"{run_success_rate:.0f}%")

    if summary["trades"] > 0:
        st.success(f"この日は {summary['trades']} 件の売買が実行されています。")
    elif summary["signals"] > 0:
        st.warning("シグナルは出ていますが、売買実行はありません。")
    else:
        st.info("売買判断・実行はありません。")


section_header("システム実行ログ", color=P)
with st.container(border=True):
    if len(runs) == 0:
        st.info("この日の実行記録はありません。")
    else:
        for _, r in runs.iterrows():
            status = str(r.get("status", ""))
            mode_label = MODE_LABELS.get(r.get("run_mode", ""), r.get("run_mode", ""))
            status_info = {
                "completed": ("正常完了", W, "処理は最後まで完了"),
                "failed": ("失敗", L, "途中で停止"),
                "running": ("実行中", P, "現在実行中"),
                "interrupted": ("中断", "#f59e0b", "途中で中断"),
            }.get(status, (status, "#64748b", "状態不明"))

            status_label, status_color, status_note = status_info
            with st.container(border=True):
                h1, h2, h3, h4 = st.columns([2.2, 1.2, 3.2, 1.4])
                with h1:
                    st.markdown(
                        f"**{mode_label}** {render_pill(status_label, status_color)}",
                        unsafe_allow_html=True,
                    )
                with h2:
                    st.caption(f"{_hm(str(r.get('started_at', '')))} - {_hm(str(r.get('ended_at', '')))}")
                with h3:
                    st.markdown(
                        f"ニュース **{int(r.get('news_collected', 0) or 0)}件** / "
                        f"シグナル **{int(r.get('signals_detected', 0) or 0)}件** / "
                        f"取引 **{int(r.get('trades_executed', 0) or 0)}件**"
                    )
                    st.caption(status_note)
                with h4:
                    err_cnt = int(r.get("errors_count", 0) or 0)
                    st.metric("エラー件数", f"{err_cnt}件")

                err_msg = str(r.get("error_message", "") or "").strip()
                if err_msg:
                    st.caption(f"エラー詳細: {err_msg[:180]}")


section_header("Ticker別フロー", color=W)
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.metric("対象Ticker", f"{len(ticker_flow)}")
    c2.metric("売買実行あり", f"{traded_cnt}")
    c3.metric("シグナルのみ", f"{signal_only_cnt}")

    if not ticker_flow:
        st.info("この日のTicker別データはありません。")
    else:
        for tf in ticker_flow[:30]:
            ticker = tf["ticker"]
            has_news = tf.get("news_count", 0) > 0
            has_analysis = tf.get("analysis_count", 0) > 0
            sig = tf.get("signal")
            trd = tf.get("trade")

            if trd:
                final_label = "売買実行"
                final_color = W if trd.get("action") == "BUY" else L
            elif sig:
                final_label = "シグナルのみ"
                final_color = "#f59e0b"
            elif has_analysis:
                final_label = "分析まで"
                final_color = P
            elif has_news:
                final_label = "ニュースのみ"
                final_color = "#64748b"
            else:
                final_label = "データなし"
                final_color = "#64748b"

            stage_txt = " / ".join(
                [
                    f"ニュース {'✅' if has_news else '—'}",
                    f"分析 {'✅' if has_analysis else '—'}",
                    f"シグナル {'✅' if sig else '—'}",
                    f"売買 {'✅' if trd else '—'}",
                ]
            )

            with st.container(border=True):
                f1, f2, f3 = st.columns([2.0, 3.0, 2.2])
                with f1:
                    st.markdown(
                        f"**{ticker}** {render_pill(final_label, final_color)}",
                        unsafe_allow_html=True,
                    )
                with f2:
                    st.caption(stage_txt)
                with f3:
                    if trd:
                        pnl = trd.get("pnl")
                        pnl_txt = fmt_currency(float(pnl), show_sign=True) if pnl is not None else "-"
                        st.markdown(
                            f"**{trd.get('action', '-') }** {int(trd.get('shares', 0) or 0)}株  "
                            f"@ ${float(trd.get('price', 0) or 0):.2f}  /  {pnl_txt}"
                        )
                    elif sig:
                        st.markdown(
                            f"**{sig.get('type', '-')}**  確信度 {int(sig.get('conviction', 0) or 0)}"
                        )
                    else:
                        st.caption("売買判断なし")


news_df = _dm.get_log_news(target_date)
analysis_df = _dm.get_log_analyses(target_date)
sig_df = _dm.get_log_signals(target_date)
trades_df = _dm.get_log_trades(target_date)

section_header("詳細データ", color=P)
with st.container(border=True):
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
            view = news_df.copy()
            cols = [c for c in ["created_at", "source", "title", "theme", "importance"] if c in view.columns]
            st.dataframe(view[cols], use_container_width=True, hide_index=True)
        else:
            st.info("ニュースなし")

    with tab_analysis:
        if len(analysis_df) > 0:
            view = analysis_df.copy()
            cols = [
                c for c in
                ["analyzed_at", "theme", "ticker", "analysis_type", "direction", "score", "recommendation"]
                if c in view.columns
            ]
            st.dataframe(view[cols], use_container_width=True, hide_index=True)
        else:
            st.info("AI分析なし")

    with tab_signals:
        if len(sig_df) > 0:
            view = sig_df.copy()
            if "detected_at" in view.columns:
                view = view.sort_values("detected_at", ascending=False)
            cols = [
                c for c in
                ["detected_at", "ticker", "signal_type", "conviction", "confidence", "price", "status"]
                if c in view.columns
            ]
            st.dataframe(view[cols], use_container_width=True, hide_index=True)
        else:
            st.info("シグナルなし")

    with tab_trades:
        if len(trades_df) > 0:
            view = trades_df.copy()
            if "entry_timestamp" in view.columns:
                view = view.sort_values("entry_timestamp", ascending=False)
            cols = [
                c for c in
                ["entry_timestamp", "exit_timestamp", "ticker", "action", "shares", "entry_price", "exit_price", "profit_loss", "status"]
                if c in view.columns
            ]
            st.dataframe(view[cols], use_container_width=True, hide_index=True)
        else:
            st.info("取引なし")
