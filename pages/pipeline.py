"""Pipeline — パイプライン監視"""

import json as _json
import logging
from datetime import date as _date
from datetime import datetime as _datetime

import dashboard_data as _dm
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.shared import P, W, L, WEEKDAY_JP, MODE_LABELS, load_pipeline_status, load_runs_timeline, load_health_metrics

logger = logging.getLogger(__name__)

# ── データ読み込み ──
pipeline = load_pipeline_status()
timeline_df = load_runs_timeline()
health = load_health_metrics()

# ── 1. 本日の投資プロセス ──

st.markdown(
    f'<div class="sec-hdr">'
    f'<div class="bar" style="background:{P}"></div>'
    f'<div class="txt">本日の投資プロセス'
    f'<span class="sub">{pipeline["date"]}</span></div>'
    f"</div>",
    unsafe_allow_html=True,
)

steps_config = [
    (
        "news",
        "情報収集",
        "市場ニュースを自動取得",
        "Finnhub・Google News RSS・Yahoo Finance等から自動収集。8つ以上の金融メディアRSSを15分間隔で巡回。URLベースで重複排除。",
    ),
    (
        "analysis",
        "AI分析",
        "テーマ・銘柄をAIが評価",
        "Gemini Proが「シニアアナリスト」として6種類の定性分析を実施。テーマ評価・センチメント(CoT推論)・イベント分類・ディープニュース分析・メガトレンド5軸採点・トレード戦略生成。",
    ),
    (
        "signals",
        "売買判断",
        "買い・売りのシグナルを生成",
        "3戦略（押し目買い・トレンド追従・VIX逆張り）のテクニカル指標＋AIニュース分析を統合。最低3カテゴリ一致＆確信度6以上で発出。AIがrejectなら取消。",
    ),
    (
        "trading",
        "注文執行",
        "条件を満たす注文を自動発注",
        "7段階のリスクチェック（価格検証→CB→市場レジーム→重複→決算→マクロ→相関）を全て通過した場合のみAlpaca APIで発注。VIXに応じてSL/TPを動的調整。",
    ),
    (
        "portfolio",
        "資産記録",
        "取引後の資産を記録・更新",
        "取引後にAlpacaからポジション・残高を取得し、DBにスナップショットを記録。日次でパフォーマンスを算出。",
    ),
]

steps_html = ""
for i, (key, label, desc, tip) in enumerate(steps_config):
    step = pipeline["steps"][key]
    status = step["status"]
    count = step["count"]
    time_str = step["last_at"]

    if status == "completed":
        n_cls = "wf-n-ok"
        icon = "&#10003;"
    elif status == "failed":
        n_cls = "wf-n-fail"
        icon = "&#10007;"
    else:
        n_cls = "wf-n-wait"
        icon = f"{i + 1}"

    # 補足情報（売買判断の内訳など）
    extra = ""
    if key == "signals" and count > 0:
        buy_cnt = step.get("buy", 0)
        sell_cnt = step.get("sell", 0)
        parts = []
        if buy_cnt:
            parts.append(f'<span class="c-pos">買 {buy_cnt}</span>')
        if sell_cnt:
            parts.append(f'<span class="c-neg">売 {sell_cnt}</span>')
        if parts:
            extra = (
                f' <span style="font-size:0.7rem">（{" / ".join(parts)}）</span>'
            )

    count_str = f"{count}件" if count > 0 else "-"
    val_color = "#0f172a" if count > 0 else "#cbd5e1"

    steps_html += f"""
    <div class="wf-step">
        <div class="wf-num {n_cls}">{icon}</div>
        <div class="wf-body">
            <div class="wf-name">{label}{extra}<span class="wf-info">?<span class="wf-tip">{tip}</span></span></div>
            <div class="wf-desc">{desc}</div>
        </div>
        <div class="wf-right">
            <div class="wf-val" style="color:{val_color}">{count_str}</div>
            <div class="wf-ts">{time_str}</div>
        </div>
    </div>"""

# 本日の実行情報
runs_today = pipeline["runs_today"]
total_errors = pipeline["total_errors"]
if runs_today:
    mode_labels = sorted(
        {MODE_LABELS.get(r["run_mode"], r["run_mode"]) for r in runs_today}
    )
    run_info = (
        f'<span class="c-sub" style="font-size:0.72rem">'
        f'本日 {len(runs_today)}回実行（{", ".join(mode_labels)}）'
    )
    if total_errors > 0:
        run_info += f' / <span class="c-neg">異常 {total_errors}件</span>'
    run_info += "</span>"
else:
    run_info = '<span class="c-dim" style="font-size:0.72rem">本日はまだ実行されていません</span>'

st.markdown(
    f'<div class="card" style="padding:0.5rem 0.3rem">'
    f"{steps_html}"
    f'<div style="text-align:center; padding:0.5rem 0; border-top:1px solid #f1f5f9">{run_info}</div>'
    f"</div>",
    unsafe_allow_html=True,
)

# ── 日付ドリルダウン（プロセスの直後に配置）──

log_dates = _dm.get_available_log_dates(30)
date_options = [_date.fromisoformat(d) for d in log_dates] if log_dates else [_date.today()]

st.markdown(
    f'<div style="display:flex; align-items:center; gap:0.5rem; margin-top:1rem; margin-bottom:0.5rem">'
    f'<div style="width:4px; height:1.2rem; border-radius:2px; background:{P}"></div>'
    f'<div style="font-size:0.88rem; font-weight:700; color:#0f172a">日付別の詳細を見る</div>'
    f"</div>",
    unsafe_allow_html=True,
)

for row_start in range(0, min(14, len(date_options)), 7):
    row_dates = date_options[row_start : row_start + 7]
    cols = st.columns(7)
    for j, dd in enumerate(row_dates):
        wd = WEEKDAY_JP[dd.weekday()]
        with cols[j]:
            label = f"{dd.month}/{dd.day}({wd})"
            if st.button(label, key=f"goto_date_{dd}", use_container_width=True):
                st.query_params["date"] = dd.isoformat()
                st.switch_page("pages/date_detail.py")

# ── 2. 過去7日間の運用品質 ──

st.markdown(
    f'<div class="sec-hdr">'
    f'<div class="bar" style="background:{W}"></div>'
    f'<div class="txt">運用品質'
    f'<span class="sub">過去7日間の平均</span></div>'
    f"</div>",
    unsafe_allow_html=True,
)

success_rate = max(0.0, 100.0 - health["error_rate"])
hcols = st.columns(5)
h_items = [
    (
        "情報収集",
        f"{health['news_per_day']:.0f}",
        "件/日",
        health["news_per_day"] > 0,
    ),
    (
        "AI分析",
        f"{health['analysis_per_day']:.1f}",
        "件/日",
        health["analysis_per_day"] > 0,
    ),
    (
        "売買判断",
        f"{health['signals_per_day']:.1f}",
        "件/日",
        health["signals_per_day"] > 0,
    ),
    ("正常処理率", f"{success_rate:.0f}%", "", success_rate >= 90),
    ("稼働継続率", f"{health['uptime_pct']:.0f}%", "", health["uptime_pct"] >= 95),
]

for col, (label, val, sub, is_ok) in zip(hcols, h_items):
    val_color = W if is_ok else L
    sub_html = (
        f'<span style="font-size:0.6rem; color:#94a3b8; font-weight:400">{sub}</span>'
        if sub
        else ""
    )
    with col:
        st.markdown(
            f'<div class="card-sm" style="text-align:center; padding:0.8rem 0.5rem">'
            f'<div class="health-val" style="color:{val_color}">{val}{sub_html}</div>'
            f'<div class="health-label">{label}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

# ── 3. ニュース・分析活用（expander内） ──

def _nu_cls(v):
    return "nu-active" if v > 0 else "nu-empty"


with st.expander("ニュース・分析活用（直近14日）", expanded=False):
    news_trend = _dm.get_news_collection_trend(14)
    news_sources = _dm.get_news_source_breakdown(14)
    news_tickers = _dm.get_news_ticker_coverage(14)
    analysis_trend = _dm.get_analysis_trend(14)
    theme_scores = _dm.get_analysis_theme_scores(7)
    ns_conn = _dm.get_news_signal_connection(14)

    total_news = int(news_trend["article_count"].sum()) if len(news_trend) > 0 else 0
    total_analysis = int(analysis_trend["total"].sum()) if len(analysis_trend) > 0 else 0
    total_signals = ns_conn["total_signals"]
    news_influenced = ns_conn["news_influenced_signals"]
    flow_df = ns_conn["flow_df"]

    st.markdown(
        f'<div style="font-size:0.72rem; color:#64748b; font-weight:600; margin-bottom:0.4rem">データフロー（14日間合計）</div>'
        f'<div class="nu-flow">'
        f'<div class="nu-node {_nu_cls(total_news)}"><div class="nu-icon">📰</div><div class="nu-val">{total_news:,}</div><div class="nu-label">ニュース収集</div></div>'
        f'<div class="nu-arrow">→</div>'
        f'<div class="nu-node {_nu_cls(total_analysis)}"><div class="nu-icon">🧠</div><div class="nu-val">{total_analysis}</div><div class="nu-label">AI分析</div></div>'
        f'<div class="nu-arrow">→</div>'
        f'<div class="nu-node {_nu_cls(total_signals)}"><div class="nu-icon">🎯</div><div class="nu-val">{total_signals}</div><div class="nu-label">シグナル</div></div>'
        f'<div class="nu-arrow">→</div>'
        f'<div class="nu-node {_nu_cls(news_influenced)}"><div class="nu-icon">📊</div><div class="nu-val">{news_influenced}</div><div class="nu-label">ニュース活用</div></div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    if len(flow_df) > 0:
        fig_flow = go.Figure()
        fig_flow.add_trace(go.Bar(x=flow_df["date"], y=flow_df["news"], name="ニュース", marker_color="#8b5cf6", opacity=0.7))
        fig_flow.add_trace(go.Bar(x=flow_df["date"], y=flow_df["analysis"], name="AI分析", marker_color="#2563eb", opacity=0.7))
        fig_flow.add_trace(go.Scatter(x=flow_df["date"], y=flow_df["signals"], name="シグナル", mode="lines+markers", line=dict(color="#059669", width=2), marker=dict(size=6)))
        fig_flow.update_layout(
            height=200, margin=dict(l=0, r=0, t=25, b=0),
            legend=dict(orientation="h", yanchor="top", y=1.15, xanchor="center", x=0.5, font_size=11),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=False, tickfont_size=10),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont_size=10),
            barmode="group", bargap=0.3,
        )
        st.plotly_chart(fig_flow, use_container_width=True)

    nu_col1, nu_col2 = st.columns(2)
    with nu_col1:
        if len(news_sources) > 0:
            max_cnt = int(news_sources["cnt"].max())
            src_html = '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.3rem">ニュースソース TOP</div>'
            for _, row in news_sources.head(7).iterrows():
                pct = int(row["cnt"]) / max_cnt * 100 if max_cnt > 0 else 0
                src_html += (
                    f'<div class="nu-src-bar">'
                    f'<div class="nu-src-name">{row["source"]}</div>'
                    f'<div style="flex:1"><div class="nu-src-fill" style="width:{pct:.0f}%"></div></div>'
                    f'<div class="nu-src-cnt">{int(row["cnt"]):,}</div>'
                    f"</div>"
                )
            st.markdown(src_html, unsafe_allow_html=True)

        if len(news_tickers) > 0:
            tk_html = '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin:0.5rem 0 0.3rem">関連銘柄</div>'
            for _, row in news_tickers.head(12).iterrows():
                tk_html += (
                    f'<span class="nu-theme-card">'
                    f'<span style="color:{P}; font-weight:600">{row["ticker"]}</span>'
                    f'<span class="nu-score" style="color:#64748b">{int(row["article_count"])}</span>'
                    f"</span>"
                )
            st.markdown(tk_html, unsafe_allow_html=True)

    with nu_col2:
        if len(theme_scores) > 0:
            themes_html = '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.3rem">AI分析テーマ</div>'
            for _, t in theme_scores.iterrows():
                score = t.get("score", 0) or 0
                direction = t.get("direction", "") or ""
                dir_label = {"bullish": "強気", "bearish": "弱気", "neutral": "中立"}.get(direction, direction)
                dir_color = W if direction == "bullish" else (L if direction == "bearish" else "#64748b")
                themes_html += (
                    f'<span class="nu-theme-card">'
                    f'<span>{t["theme"]}</span>'
                    f'<span class="nu-score" style="color:{dir_color}">{score:.0f}</span>'
                    f'<span style="font-size:0.6rem; color:{dir_color}">{dir_label}</span>'
                    f"</span>"
                )
            st.markdown(themes_html, unsafe_allow_html=True)

        if len(analysis_trend) > 0:
            total_b = int(analysis_trend["bullish"].sum())
            total_bear = int(analysis_trend["bearish"].sum())
            total_n = int(analysis_trend["neutral"].sum())
            total_all = total_b + total_bear + total_n
            if total_all > 0:
                b_pct = total_b / total_all * 100
                bear_pct = total_bear / total_all * 100
                n_pct = total_n / total_all * 100
                avg_score = analysis_trend["avg_score"].mean()
                st.markdown(
                    f'<div style="margin-top:0.5rem; font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.3rem">方向性分布</div>'
                    f'<div style="display:flex; height:10px; border-radius:5px; overflow:hidden; margin-bottom:0.3rem">'
                    f'<div style="width:{b_pct:.0f}%; background:{W}"></div>'
                    f'<div style="width:{n_pct:.0f}%; background:#94a3b8"></div>'
                    f'<div style="width:{bear_pct:.0f}%; background:{L}"></div>'
                    f"</div>"
                    f'<div style="display:flex; justify-content:space-between; font-size:0.68rem; color:#64748b">'
                    f'<span style="color:{W}">強気 {total_b}</span>'
                    f"<span>中立 {total_n}</span>"
                    f'<span style="color:{L}">弱気 {total_bear}</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

# ── 4. 日次運用カレンダー（直近14日） ──

st.markdown(
    f'<div class="sec-hdr">'
    f'<div class="bar" style="background:#f59e0b"></div>'
    f'<div class="txt">日次運用カレンダー'
    f'<span class="sub">直近14日</span></div>'
    f"</div>",
    unsafe_allow_html=True,
)

# 凡例
st.markdown(
    '<div style="display:flex; gap:1.2rem; margin-bottom:0.5rem; font-size:0.68rem; color:#64748b">'
    '<span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#059669;margin-right:0.3rem"></span>正常</span>'
    '<span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#f59e0b;margin-right:0.3rem"></span>一部異常</span>'
    '<span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#e11d48;margin-right:0.3rem"></span>失敗</span>'
    '<span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#e2e8f0;margin-right:0.3rem"></span>未実行</span>'
    "</div>",
    unsafe_allow_html=True,
)

if len(timeline_df) > 0:
    tl_html = ""
    for _, day in timeline_df.iterrows():
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
            dot_cls = "tl-fail"
        elif errors > 0 or interrupted > 0:
            dot_cls = "tl-warn"
        elif completed > 0:
            dot_cls = "tl-ok"
        else:
            dot_cls = "tl-empty"

        # ラン種別を業務名に変換
        mode_parts = [
            MODE_LABELS.get(m.strip(), m.strip())
            for m in modes_raw.split(",")
            if m.strip()
        ]
        mode_display = ", ".join(mode_parts) if mode_parts else "-"

        nums_parts = []
        if signals > 0:
            nums_parts.append(f'<span class="c-pri">判断 {signals}件</span>')
        if t_trades > 0:
            nums_parts.append(f'<span class="c-pos">約定 {t_trades}件</span>')
        if errors > 0:
            nums_parts.append(f'<span class="c-neg">異常 {errors}件</span>')
        nums_html = (
            " &middot; ".join(nums_parts)
            if nums_parts
            else '<span class="c-dim">&ndash;</span>'
        )

        tl_html += f"""
        <div class="tl-row">
            <div class="tl-date">{date_label}</div>
            <div class="tl-dot {dot_cls}"></div>
            <div class="tl-info">{mode_display}<span class="tl-sub">{completed}/{total_runs}回 正常完了</span></div>
            <div class="tl-nums">{nums_html}</div>
        </div>"""

    st.markdown(
        f'<div class="card" style="padding:0.5rem 0.3rem">{tl_html}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="card-sm" style="color:#94a3b8; text-align:center; padding:1.2rem">'
        "直近14日間の実行記録なし</div>",
        unsafe_allow_html=True,
    )

# （日付ドリルダウンはページ上部に移動済み）
