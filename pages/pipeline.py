"""Pipeline — パイプライン監視（グリッドレイアウト版）

Design: Focused cards — each card = ONE purpose.
ROW 1: Today's summary metrics
ROW 2: 5-step pipeline visualization
ROW 3: [Quality metrics] | [Date drill-down]
ROW 4: Daily calendar
Expander: News/analysis deep dive
"""

import logging
from datetime import date as _date
from datetime import datetime as _datetime

import dashboard_data as _dm
import plotly.graph_objects as go
import streamlit as st

from components.shared import (
    L,
    MODE_LABELS,
    P,
    W,
    WEEKDAY_JP,
    card_title,
    render_pill,
    status_badge,
    status_dot_html,
    load_pipeline_status,
    load_runs_timeline,
    load_health_metrics,
)

logger = logging.getLogger(__name__)

# ── データ読み込み ──
pipeline = load_pipeline_status()
timeline_df = load_runs_timeline()
health = load_health_metrics()

st.title("パイプライン")
st.caption("自動売買プロセスの稼働状況")

runs_today = pipeline["runs_today"]
completed_runs = sum(1 for r in runs_today if r.get("status") == "completed")
run_success_rate = (completed_runs / len(runs_today) * 100) if runs_today else 0.0
today_signals = pipeline["steps"]["signals"]["count"]
today_trades = pipeline["steps"]["trading"]["count"]

steps_config = [
    (
        "news", "情報収集", "市場ニュースを自動取得",
        "Finnhub・Google News RSS・Yahoo Finance等から自動収集。",
    ),
    (
        "analysis", "AI分析", "テーマ・銘柄をAIが評価",
        "Gemini Proが6種類の定性分析を実施。",
    ),
    (
        "signals", "売買判断", "買い・売りのシグナルを生成",
        "3戦略（押し目買い・トレンド追従・VIX逆張り）のテクニカル＋AI統合。",
    ),
    (
        "trading", "注文執行", "条件を満たす注文を自動発注",
        "7段階のリスクチェックを通過した場合のみAlpaca APIで発注。",
    ),
    (
        "portfolio", "資産記録", "取引後の資産を記録・更新",
        "Alpacaからポジション・残高を取得しDBに記録。",
    ),
]


# ============================================================
# ROW 1: 本日のサマリー (full width)
# ============================================================

with st.container(border=True):
    card_title("本日のサマリー", color=P, subtitle=pipeline["date"])

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("実行回数", f"{len(runs_today)}回")
    s2.metric("完了率", f"{run_success_rate:.0f}%")
    s3.metric("シグナル", f"{today_signals}件")
    s4.metric("約定", f"{today_trades}件")

    if pipeline["total_errors"] > 0:
        st.warning(f"本日の異常件数: {pipeline['total_errors']}件")
    elif runs_today:
        st.success("本日は異常なしで稼働中です。")
    else:
        st.info("本日はまだ実行されていません。")


# ============================================================
# ROW 2: 投資プロセス (full width)
# ============================================================

with st.container(border=True):
    card_title("投資プロセス", color=P)

    for i, (key, label, desc, tip) in enumerate(steps_config):
        if i > 0:
            st.divider()

        step = pipeline["steps"][key]
        status = step["status"]
        count = step["count"]
        time_str = step["last_at"]

        col_num, col_body, col_right = st.columns([1, 5, 2])

        with col_num:
            if status == "completed":
                st.markdown(
                    f'<div style="width:28px;height:28px;border-radius:50%;'
                    f'background:{W};color:#fff;display:flex;align-items:center;'
                    f'justify-content:center;font-size:0.8rem;font-weight:700">'
                    f'✓</div>',
                    unsafe_allow_html=True,
                )
            elif status == "skipped":
                st.markdown(
                    '<div style="width:28px;height:28px;border-radius:50%;'
                    'background:#d97706;color:#fff;display:flex;align-items:center;'
                    'justify-content:center;font-size:0.8rem;font-weight:700">'
                    '↷</div>',
                    unsafe_allow_html=True,
                )
            elif status == "failed":
                st.markdown(
                    f'<div style="width:28px;height:28px;border-radius:50%;'
                    f'background:{L};color:#fff;display:flex;align-items:center;'
                    f'justify-content:center;font-size:0.8rem;font-weight:700">'
                    f'✗</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="width:28px;height:28px;border-radius:50%;'
                    'background:#27272a;color:#a1a1aa;display:flex;'
                    'align-items:center;justify-content:center;'
                    f'font-size:0.8rem;font-weight:700">'
                    f'{i + 1}</div>',
                    unsafe_allow_html=True,
                )

        with col_body:
            status_label = {
                "completed": "完了",
                "skipped": "スキップ",
                "failed": "失敗",
                "pending": "未実行",
            }.get(status, status)

            extra = ""
            if key == "signals" and count > 0:
                buy_cnt = step.get("buy", 0)
                sell_cnt = step.get("sell", 0)
                parts = []
                if buy_cnt:
                    parts.append(f":green[買 {buy_cnt}]")
                if sell_cnt:
                    parts.append(f":red[売 {sell_cnt}]")
                if parts:
                    extra = f" ({' / '.join(parts)})"

            st.markdown(f"**{label}**{extra}")
            st.caption(f"{desc} / 状態: {status_label}")

        with col_right:
            count_str = f"{count}件" if count > 0 else "-"
            if count > 0:
                st.markdown(f"**{count_str}**")
            else:
                st.markdown(
                    f'<span style="color:#52525b">{count_str}</span>',
                    unsafe_allow_html=True,
                )
            if time_str:
                st.caption(time_str)

    # 本日の実行情報
    total_errors = pipeline["total_errors"]
    if runs_today:
        mode_labels = sorted(
            {MODE_LABELS.get(r["run_mode"], r["run_mode"]) for r in runs_today}
        )
        run_info = f"本日 {len(runs_today)}回実行（{', '.join(mode_labels)}）"
        if total_errors > 0:
            run_info += f" / :red[異常 {total_errors}件]"
        st.caption(run_info)
    else:
        st.caption("本日はまだ実行されていません")


# ============================================================
# ROW 3: [運用品質] | [日付ドリルダウン] — 2-column grid
# ============================================================

grid_left, grid_right = st.columns(2)

with grid_left:
    with st.container(border=True):
        card_title("運用品質", color=W, subtitle="過去7日間")

        success_rate = max(0.0, 100.0 - health["error_rate"])
        h_items = [
            ("情報収集", f"{health['news_per_day']:.0f}", "件/日",
             health["news_per_day"] > 0),
            ("AI分析", f"{health['analysis_per_day']:.1f}", "件/日",
             health["analysis_per_day"] > 0),
            ("売買判断", f"{health['signals_per_day']:.1f}", "件/日",
             health["signals_per_day"] > 0),
        ]

        for label, val, sub, is_ok in h_items:
            display_val = f"{val}{sub}" if sub else val
            st.metric(label, display_val)

        st.divider()

        q1, q2 = st.columns(2)
        q1.metric("正常処理率", f"{success_rate:.0f}%")
        q2.metric("稼働継続率", f"{health['uptime_pct']:.0f}%")

        if success_rate >= 90 and health["uptime_pct"] >= 95:
            st.success("品質基準を達成")
        elif success_rate < 80 or health["uptime_pct"] < 90:
            st.error("品質基準を下回っています")
        else:
            st.warning("品質基準にやや届いていません")

with grid_right:
    with st.container(border=True):
        card_title("運用履歴", color="#d97706", subtitle="日付選択")

        log_dates = _dm.get_available_log_dates(30)
        date_options = (
            sorted([_date.fromisoformat(d) for d in log_dates], reverse=True)
            if log_dates
            else [_date.today()]
        )

        pick_col, move_col = st.columns([3, 1])
        with pick_col:
            selected_date = st.selectbox(
                "対象日",
                options=date_options,
                format_func=lambda dd: (
                    f"{dd.isoformat()} ({WEEKDAY_JP[dd.weekday()]})"
                ),
                index=0,
            )
        with move_col:
            st.markdown("")
            st.markdown("")
            if st.button("詳細へ", key="goto_selected_date",
                         use_container_width=True):
                st.query_params["date"] = selected_date.isoformat()
                st.switch_page("pages/date_detail.py")

        with st.expander("最近14日をクイック選択", expanded=False):
            for row_start in range(0, min(14, len(date_options)), 7):
                row_dates = date_options[row_start: row_start + 7]
                cols = st.columns(7)
                for j, dd in enumerate(row_dates):
                    wd = WEEKDAY_JP[dd.weekday()]
                    with cols[j]:
                        label = f"{dd.month}/{dd.day}({wd})"
                        if st.button(
                            label, key=f"goto_date_{dd}",
                            use_container_width=True,
                        ):
                            st.query_params["date"] = dd.isoformat()
                            st.switch_page("pages/date_detail.py")


# ============================================================
# ROW 4: 日次運用カレンダー (full width)
# ============================================================

with st.container(border=True):
    card_title("日次カレンダー", color=P, subtitle="直近14日")

    st.markdown(
        f'{status_dot_html("completed")} 正常&nbsp;&nbsp;'
        f'{status_dot_html("interrupted")} 一部異常&nbsp;&nbsp;'
        f'{status_dot_html("failed")} 失敗&nbsp;&nbsp;'
        f'{status_dot_html("pending")} 未実行',
        unsafe_allow_html=True,
    )

    if len(timeline_df) > 0:
        for idx, (_, day) in enumerate(timeline_df.iterrows()):
            if idx > 0:
                st.divider()

            run_date = day["run_date"]
            try:
                dt_obj = _datetime.strptime(run_date, "%Y-%m-%d")
                wd = WEEKDAY_JP[dt_obj.weekday()]
                date_label = f"{run_date[5:]} ({wd})"
            except Exception:
                date_label = run_date[5:] if len(run_date) > 5 else run_date

            failed = int(day["failed"] or 0)
            interrupted = int(day["interrupted"] or 0)
            completed = int(day["completed"] or 0)
            total_runs = int(day["total_runs"] or 0)
            errors = int(day["total_errors"] or 0)
            signals = int(day["total_signals"] or 0)
            t_trades = int(day["total_trades"] or 0)
            modes_raw = day["modes"] or ""

            if failed > 0:
                dot_status = "failed"
            elif errors > 0 or interrupted > 0:
                dot_status = "interrupted"
            elif completed > 0:
                dot_status = "completed"
            else:
                dot_status = "pending"

            mode_parts = [
                MODE_LABELS.get(m.strip(), m.strip())
                for m in modes_raw.split(",")
                if m.strip()
            ]
            mode_display = ", ".join(mode_parts) if mode_parts else "-"

            nums_parts = []
            if signals > 0:
                nums_parts.append(f":blue[判断 {signals}件]")
            if t_trades > 0:
                nums_parts.append(f":green[約定 {t_trades}件]")
            if errors > 0:
                nums_parts.append(f":red[異常 {errors}件]")
            nums_str = " · ".join(nums_parts) if nums_parts else "-"

            col_date, col_dot, col_info, col_nums = st.columns(
                [2, 0.5, 4, 3]
            )
            with col_date:
                st.markdown(f"**{date_label}**")
            with col_dot:
                st.markdown(
                    status_dot_html(dot_status), unsafe_allow_html=True
                )
            with col_info:
                st.markdown(f"{mode_display}")
                st.caption(f"{completed}/{total_runs}回 正常完了")
            with col_nums:
                st.markdown(nums_str)
    else:
        st.info("直近14日間の実行記録なし")


# ============================================================
# ニュース・分析活用（expander）
# ============================================================

with st.expander("ニュース・分析活用（直近14日）", expanded=False):
    news_trend = _dm.get_news_collection_trend(14)
    news_sources = _dm.get_news_source_breakdown(14)
    news_tickers = _dm.get_news_ticker_coverage(14)
    analysis_trend = _dm.get_analysis_trend(14)
    theme_scores = _dm.get_analysis_theme_scores(7)
    ns_conn = _dm.get_news_signal_connection(14)

    total_news = (
        int(news_trend["article_count"].sum())
        if len(news_trend) > 0
        else 0
    )
    total_analysis = (
        int(analysis_trend["total"].sum())
        if len(analysis_trend) > 0
        else 0
    )
    total_signals = ns_conn["total_signals"]
    news_influenced = ns_conn["news_influenced_signals"]
    flow_df = ns_conn["flow_df"]

    st.markdown(
        '<div class="section-label">データフロー（14日間合計）</div>',
        unsafe_allow_html=True,
    )
    fc1, fc2, fc3, fc4 = st.columns(4)
    fc1.metric("ニュース収集", f"{total_news:,}")
    fc2.metric("AI分析", f"{total_analysis}")
    fc3.metric("シグナル", f"{total_signals}")
    fc4.metric("ニュース活用", f"{news_influenced}")

    if len(flow_df) > 0:
        fig_flow = go.Figure()
        fig_flow.add_trace(
            go.Bar(
                x=flow_df["date"],
                y=flow_df["news"],
                name="ニュース",
                marker_color="#8b5cf6",
                opacity=0.8,
            )
        )
        fig_flow.add_trace(
            go.Bar(
                x=flow_df["date"],
                y=flow_df["analysis"],
                name="AI分析",
                marker_color="#6366f1",
                opacity=0.8,
            )
        )
        fig_flow.add_trace(
            go.Scatter(
                x=flow_df["date"],
                y=flow_df["signals"],
                name="シグナル",
                mode="lines+markers",
                line=dict(color="#22c55e", width=2),
                marker=dict(size=6),
            )
        )
        fig_flow.update_layout(
            height=200,
            margin=dict(l=0, r=0, t=25, b=0),
            plot_bgcolor="#18181b",
            paper_bgcolor="#18181b",
            font=dict(family="Inter, sans-serif", color="#a1a1aa", size=11),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.15,
                xanchor="center",
                x=0.5,
                font=dict(size=11, color="#a1a1aa"),
            ),
            xaxis=dict(
                showgrid=False,
                tickfont=dict(size=10, color="#71717a"),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#27272a",
                tickfont=dict(size=10, color="#71717a"),
            ),
            barmode="group",
            bargap=0.3,
            hoverlabel=dict(
                bgcolor="#27272a", bordercolor="#3f3f46",
                font=dict(color="#fafafa", size=12),
            ),
        )
        st.plotly_chart(fig_flow, use_container_width=True, theme=None)

    nu_col1, nu_col2 = st.columns(2)
    with nu_col1:
        if len(news_sources) > 0:
            st.markdown("**ニュースソース TOP**")
            for _, row in news_sources.head(7).iterrows():
                st.markdown(
                    f"- {row['source']}  ({int(row['cnt']):,}件)"
                )

        if len(news_tickers) > 0:
            st.markdown("**関連銘柄**")
            ticker_parts = []
            for _, row in news_tickers.head(12).iterrows():
                ticker_parts.append(
                    f":blue[**{row['ticker']}**] "
                    f"{int(row['article_count'])}"
                )
            st.markdown("  |  ".join(ticker_parts))

    with nu_col2:
        if len(theme_scores) > 0:
            st.markdown("**AI分析テーマ**")
            for _, t in theme_scores.iterrows():
                score = t.get("score", 0) or 0
                direction = t.get("direction", "") or ""
                dir_label = {
                    "bullish": "強気",
                    "bearish": "弱気",
                    "neutral": "中立",
                }.get(direction, direction)
                dir_color = (
                    "green"
                    if direction == "bullish"
                    else ("red" if direction == "bearish" else "gray")
                )
                st.markdown(
                    f"- {t['theme']}  "
                    f":{dir_color}[{score:.0f} {dir_label}]"
                )

        if len(analysis_trend) > 0:
            total_b = int(analysis_trend["bullish"].sum())
            total_bear = int(analysis_trend["bearish"].sum())
            total_n = int(analysis_trend["neutral"].sum())
            total_all = total_b + total_bear + total_n
            if total_all > 0:
                st.markdown("**方向性分布**")
                b_pct = total_b / total_all
                st.progress(
                    b_pct,
                    text=(
                        f"強気 {total_b} / 中立 {total_n} "
                        f"/ 弱気 {total_bear}"
                    ),
                )
