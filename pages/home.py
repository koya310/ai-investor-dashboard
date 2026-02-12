"""Home -- ポートフォリオ概要（グリッドレイアウト版）

Design: Focused cards in 2-column grid.
Each card = ONE purpose. Hero number at top.
"""

import logging
from datetime import datetime

import dashboard_data as _dm
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.shared import (
    P, W, L, TEXT_SECONDARY,
    fmt_currency, fmt_pct, fmt_delta,
    card_title, render_pill,
    load_common_data,
)

logger = logging.getLogger(__name__)

# ── データ読み込み ──
d = load_common_data()
start = d["start"]
daily = d["daily"]
spy = d["spy"]
trades = d["trades"]
kpi = d["kpi"]
verdict = d["verdict"]
capital = d["capital"]
alpaca_pf = d["alpaca_pf"]
alpaca_positions = d["alpaca_positions"]

_deadline_dt = datetime.strptime(_dm.GONOGO_DEADLINE, "%Y-%m-%d")
_days_left = max((_deadline_dt - datetime.now()).days, 0)
_targets = _dm.KPI_TARGETS
_v = verdict["status"]
_passed = verdict["passed"]
_total = verdict["total"]
_last_run = d["last_run"]
_days_running = kpi.get("days_running", 0)
_total_trades = kpi.get("total_trades", 0)

if alpaca_pf is not None:
    total_val = alpaca_pf["portfolio_value"]
    cash_val = alpaca_pf["cash"]
    equity_val = total_val - cash_val
elif len(daily) > 0:
    now = daily.iloc[-1]
    total_val = now["total"]
    cash_val = now["cash"]
    equity_val = now["equity"]
else:
    total_val = cash_val = equity_val = 0


# ── 詳細分析ダイアログ ──

@st.dialog("パフォーマンス詳細分析", width="large")
def show_analysis_dialog():
    tr = _dm.get_trades(start)
    summary = _dm.get_trade_summary(tr)
    patterns = _dm.get_trade_patterns(tr)

    st.subheader("損益の全体像", divider="gray")
    m1, m2, m3 = st.columns(3)
    m1.metric("決済回数", f"{summary['total']}回",
              f"{summary['wins']}勝 {summary['losses']}敗")
    m2.metric("勝率", f"{summary['win_rate']}%")
    pf_display = ("∞" if summary['profit_factor'] == float('inf')
                  else f"{summary['profit_factor']:.2f}")
    m3.metric("プロフィットファクター", pf_display)

    m4, m5, m6 = st.columns(3)
    m4.metric("累積損益", fmt_currency(summary['total_pnl'], show_sign=True))
    m5.metric("平均利益（勝ち）", fmt_pct(summary['avg_profit_pct'], show_sign=True))
    m6.metric("平均損失（負け）", fmt_pct(summary['avg_loss_pct'], show_sign=True))

    m7, m8, m9 = st.columns(3)
    m7.metric("最大利益", fmt_pct(summary['largest_win_pct'], show_sign=True))
    m8.metric("最大損失", fmt_pct(summary['largest_loss_pct'], show_sign=True))
    m9.metric("平均保有日数", f"{summary['avg_holding_days']:.1f}日")

    insights = []
    if summary["total"] > 0:
        if summary["win_rate"] < 50:
            insights.append(
                f"勝率が{summary['win_rate']}%と低い。"
                "シグナル品質の改善が最優先。"
            )
        if summary["avg_loss_pct"] != 0 and summary["avg_profit_pct"] != 0:
            rr = abs(summary["avg_profit_pct"] / summary["avg_loss_pct"])
            if rr < 1.5:
                insights.append(
                    f"リスクリワード比 {rr:.2f}。"
                    "利確を伸ばすか損切りを早める。"
                )
        pf = summary["profit_factor"]
        if pf != float("inf") and pf < 1.0:
            insights.append(f"PF {pf:.2f}（1.0未満 = 損失超過）。")
    for i in insights:
        st.warning(i)

    closed = tr[tr["status"] == "CLOSED"]
    if len(closed) > 0:
        st.subheader("銘柄別パフォーマンス", divider="gray")
        ticker_stats = []
        for ticker, grp in closed.groupby("ticker"):
            wins = len(grp[grp["profit_loss"] > 0])
            ticker_stats.append({
                "銘柄": ticker, "取引数": len(grp), "勝数": wins,
                "損益": grp["profit_loss"].sum(),
                "平均%": grp["profit_loss_pct"].mean(),
            })
        ticker_stats.sort(key=lambda x: x["損益"])
        for ts in ticker_stats:
            col_tk, col_pnl = st.columns([3, 2])
            with col_tk:
                st.markdown(f"**{ts['銘柄']}**  {ts['勝数']}/{ts['取引数']}勝")
            with col_pnl:
                pnl = ts["損益"]
                color = "green" if pnl >= 0 else "red"
                st.markdown(
                    f":{color}[**{fmt_currency(pnl, show_sign=True)}** "
                    f"({fmt_pct(ts['平均%'], show_sign=True)})]"
                )


# ============================================================
# ROW 1: Hero — ポートフォリオ総額 (full width)
# ============================================================

with st.container(border=True):
    if total_val > 0:
        pnl = total_val - capital
        pnl_pct = pnl / capital * 100
        source_label = "Alpaca" if alpaca_pf is not None else "推定"

        st.markdown(
            f'<div class="section-label">ポートフォリオ総額'
            f' &nbsp;{render_pill(source_label)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="hero-value">${total_val:,.0f}</div>',
            unsafe_allow_html=True,
        )

        spy_info = ""
        if len(spy) > 0:
            spy_now = spy.iloc[-1]["spy_total"]
            spy_pnl_pct = (spy_now - capital) / capital * 100
            diff = pnl_pct - spy_pnl_pct
            diff_color = "green" if diff >= 0 else "red"
            spy_info = (
                f"  |  SPY {spy_pnl_pct:+.2f}%  |  "
                f"差 :{diff_color}[**{diff:+.2f}%**]"
            )
        pnl_color = "green" if pnl >= 0 else "red"
        st.markdown(
            f":{pnl_color}[**{fmt_currency(pnl, show_sign=True)}** "
            f"({fmt_pct(pnl_pct, show_sign=True)})]"
            f"{spy_info}"
        )

        m1, m2, m3, m4 = st.columns(4)
        equity_pct = (equity_val / total_val * 100) if total_val > 0 else 0
        m1.metric("株式", fmt_currency(equity_val),
                  f"{equity_pct:.0f}%", delta_color="off")
        m2.metric("現金", fmt_currency(cash_val),
                  f"{100 - equity_pct:.0f}%", delta_color="off")
        m3.metric("初期資本", fmt_currency(capital))
        m4.metric("運用日数", f"{_days_running}日")
    else:
        st.info("まだデータがありません")

if _total_trades < 20 and _days_running < 30:
    st.caption(
        f"データ {_total_trades}件 / {_days_running}日間。統計的信頼性はまだ低めです。"
    )


# ============================================================
# ROW 2: [Go/No-Go] | [保有銘柄] — 2-column grid
# ============================================================

grid_left, grid_right = st.columns(2)

with grid_left:
    with st.container(border=True):
        card_title("Go/No-Go", color=P, subtitle=f"残り{_days_left}日")

        _progress = (_passed / _total) if _total > 0 else 0.0
        st.progress(min(1.0, max(0.0, _progress)))

        if _v == "GO":
            st.success(f"**GO** — 全{_total}項目を達成")
        elif _v == "CONDITIONAL_GO":
            _recs = " / ".join(verdict["recommendations"][:2])
            st.warning(f"**条件付き** — {_passed}/{_total}項目。{_recs}")
        else:
            st.error(f"**未達** — {_passed}/{_total}項目のみ")

        q1, q2 = st.columns(2)
        q1.metric("勝率", fmt_pct(kpi["win_rate"], decimals=0),
                  f"目標 {_targets['win_rate']:.0f}%", delta_color="off")
        q2.metric("累積損益", fmt_currency(kpi.get("total_pnl", 0), show_sign=True))

        if st.button("今日の実行 →", use_container_width=True):
            st.switch_page("pages/pipeline.py")

with grid_right:
    with st.container(border=True):
        card_title("保有銘柄", color=W)

        if alpaca_positions:
            for i, p in enumerate(alpaca_positions):
                if i > 0:
                    st.divider()
                p_pnl = p["unrealized_pnl"]
                p_pct = p["unrealized_pnl_pct"]
                col_name, col_val = st.columns([3, 2])
                with col_name:
                    st.markdown(
                        f"**{p['ticker']}**  "
                        f'<span style="color:#a1a1aa;font-size:0.8rem">'
                        f'{p["shares"]}株</span>',
                        unsafe_allow_html=True,
                    )
                with col_val:
                    pnl_color = "green" if p_pnl >= 0 else "red"
                    st.markdown(
                        f":{pnl_color}[**{fmt_currency(p_pnl, show_sign=True)}** "
                        f"({fmt_pct(p_pct, show_sign=True)})]"
                    )
        else:
            st.info("ポジションなし")


# ============================================================
# ROW 3: チャート (full width)
# ============================================================

with st.container(border=True):
    card_title("資産推移", color=P)

    if len(daily) > 0:
        pnl = total_val - capital
        fill_color = ("rgba(34,197,94,0.08)" if pnl >= 0
                      else "rgba(239,68,68,0.06)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily["date"], y=[capital] * len(daily),
            mode="lines", line=dict(width=0),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=daily["date"], y=daily["total"],
            fill="tonexty", fillcolor=fill_color,
            mode="none", showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=daily["date"], y=daily["total"],
            name="ポートフォリオ", mode="lines+markers",
            line=dict(color="#6366f1", width=2.5), marker=dict(size=4, color="#6366f1"),
            hovertemplate="%{x|%m/%d}  $%{y:,.0f}<extra></extra>",
        ))
        if len(spy) > 0:
            fig.add_trace(go.Scatter(
                x=spy["date"], y=spy["spy_total"],
                name="SPY", mode="lines",
                line=dict(color="#71717a", width=1.2, dash="dot"),
                hovertemplate="%{x|%m/%d}  SPY $%{y:,.0f}<extra></extra>",
            ))

        buy_rows = trades[
            (trades["action"] == "BUY") & trades["entry_timestamp"].notna()
        ].copy()
        if len(buy_rows) > 0:
            buy_rows["entry_date"] = pd.to_datetime(
                buy_rows["entry_timestamp"], format="mixed"
            ).dt.normalize()
            merged = buy_rows.merge(
                daily[["date", "total"]], left_on="entry_date",
                right_on="date", how="inner",
            )
            if len(merged) > 0:
                fig.add_trace(go.Scatter(
                    x=merged["date"], y=merged["total"], name="買い",
                    mode="markers",
                    marker=dict(symbol="triangle-up", size=10, color="#22c55e",
                                line=dict(width=1, color="#18181b")),
                    hovertemplate="%{x|%m/%d} 買い %{text}<extra></extra>",
                    text=merged["ticker"], showlegend=False,
                ))

        sell_rows = trades[
            (trades["status"] == "CLOSED") & trades["exit_timestamp"].notna()
        ].copy()
        if len(sell_rows) > 0:
            sell_rows["exit_date"] = pd.to_datetime(
                sell_rows["exit_timestamp"], format="mixed"
            ).dt.normalize()
            merged = sell_rows.merge(
                daily[["date", "total"]], left_on="exit_date",
                right_on="date", how="inner",
            )
            if len(merged) > 0:
                fig.add_trace(go.Scatter(
                    x=merged["date"], y=merged["total"], name="売り",
                    mode="markers",
                    marker=dict(symbol="triangle-down", size=10, color="#ef4444",
                                line=dict(width=1, color="#18181b")),
                    hovertemplate="%{x|%m/%d} 売り %{text}<extra></extra>",
                    text=merged["ticker"], showlegend=False,
                ))

        fig.add_hline(y=capital, line_dash="dot", line_color="#3f3f46", line_width=1)
        fig.update_layout(
            height=320,
            margin=dict(l=0, r=0, t=24, b=0),
            plot_bgcolor="#18181b",
            paper_bgcolor="#18181b",
            font=dict(family="Inter, sans-serif", color="#a1a1aa", size=12),
            xaxis=dict(
                title="", gridcolor="#27272a", linecolor="#3f3f46",
                tickfont=dict(size=11, color="#71717a"), showgrid=True,
            ),
            yaxis=dict(
                title="", tickprefix="$", tickformat=",.0f",
                gridcolor="#27272a", linecolor="#3f3f46",
                tickfont=dict(size=11, color="#71717a"), showgrid=True,
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="right", x=1,
                font=dict(size=11, color="#a1a1aa"),
            ),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="#27272a", bordercolor="#3f3f46",
                font=dict(color="#fafafa", size=12),
            ),
        )
        st.plotly_chart(fig, use_container_width=True, theme=None)
    else:
        st.info("資産推移データがありません。")


# ============================================================
# ROW 4: KPIチェックリスト (full width)
# ============================================================

targets = _dm.KPI_TARGETS

kpi_checks = []

wr = kpi["win_rate"]
wr_tgt = targets["win_rate"]
wr_ok = wr >= wr_tgt
wr_pct = min(100, max(0, wr / wr_tgt * 100)) if wr_tgt > 0 else 0
kpi_checks.append({
    "label": "勝率", "current": fmt_pct(wr, decimals=0),
    "target_str": fmt_pct(wr_tgt, decimals=0),
    "ok": wr_ok, "bar_pct": wr_pct / 100,
    "gap_txt": "達成" if wr_ok else f"あと{wr_tgt - wr:.0f}pp",
})

ar = kpi["annual_return"]
ar_tgt = targets["annual_return"]
ar_ok = ar >= ar_tgt
ar_pct = min(100, max(0, ar / ar_tgt * 100)) if ar_tgt > 0 and ar > 0 else 0
kpi_checks.append({
    "label": "年率リターン", "current": fmt_pct(ar, show_sign=True),
    "target_str": fmt_pct(ar_tgt, decimals=0),
    "ok": ar_ok, "bar_pct": ar_pct / 100,
    "gap_txt": "達成" if ar_ok else f"あと{ar_tgt - ar:.1f}%",
})

dd = kpi["max_drawdown"]
dd_tgt = targets["max_drawdown"]
dd_ok = dd <= dd_tgt
dd_pct = 100 if dd_ok else (min(100, max(0, dd_tgt / dd * 100)) if dd_tgt > 0 else 0)
kpi_checks.append({
    "label": "最大DD", "current": fmt_pct(dd),
    "target_str": f"{dd_tgt:.0f}%以下",
    "ok": dd_ok, "bar_pct": dd_pct / 100,
    "gap_txt": "達成" if dd_ok else f"{dd - dd_tgt:.0f}%超過",
})

up = kpi["uptime"]
up_tgt = targets["uptime"]
up_ok = up >= up_tgt
up_pct = min(100, max(0, up / up_tgt * 100)) if up_tgt > 0 else 0
kpi_checks.append({
    "label": "稼働率", "current": fmt_pct(up, decimals=0),
    "target_str": fmt_pct(up_tgt, decimals=0),
    "ok": up_ok, "bar_pct": up_pct / 100,
    "gap_txt": "達成" if up_ok else f"あと{up_tgt - up:.0f}pp",
})

achieved = sum(1 for item in kpi_checks if item["ok"])

with st.container(border=True):
    title_col, btn_col = st.columns([5, 1])
    with title_col:
        card_title("実取引チェックリスト", color=P,
                   subtitle=f"{achieved}/{len(kpi_checks)}達成")
    with btn_col:
        if st.button("詳細分析", type="secondary", use_container_width=True):
            show_analysis_dialog()

    if verdict["recommendations"]:
        st.caption(f"優先改善: {' / '.join(verdict['recommendations'][:3])}")

    kpi_cols = st.columns(len(kpi_checks))
    for col, item in zip(kpi_cols, kpi_checks):
        with col:
            st.markdown(f"**{item['label']}**")
            st.progress(min(1.0, max(0.0, item["bar_pct"])))
            if item["ok"]:
                st.markdown(f":green[**{item['current']}**]")
            else:
                st.markdown(f":red[**{item['current']}**]")
            st.caption(f"目標 {item['target_str']}")


# ============================================================
# ROW 5: 取引履歴 (collapsible)
# ============================================================

with st.container(border=True):
    card_title("取引履歴", color=W)

    if len(trades) > 0:
        trades_sorted_all = trades.sort_values("entry_timestamp", ascending=False)

        view_mode = st.radio(
            "表示対象", ["すべて", "決済済み", "保有中"],
            horizontal=True, label_visibility="collapsed",
        )

        if view_mode == "決済済み":
            trades_sorted = trades_sorted_all[trades_sorted_all["status"] == "CLOSED"]
        elif view_mode == "保有中":
            trades_sorted = trades_sorted_all[trades_sorted_all["status"] == "OPEN"]
        else:
            trades_sorted = trades_sorted_all

        closed_trades = trades_sorted_all[trades_sorted_all["status"] == "CLOSED"]
        best_id = worst_id = None
        if len(closed_trades) > 0:
            best_id = closed_trades.loc[closed_trades["profit_loss"].idxmax(), "id"]
            worst_id = closed_trades.loc[closed_trades["profit_loss"].idxmin(), "id"]

            wins = len(closed_trades[closed_trades["profit_loss"] > 0])
            losses = len(closed_trades) - wins
            total_pnl = closed_trades["profit_loss"].sum()
            avg_pnl = total_pnl / len(closed_trades)

            sm1, sm2, sm3, sm4 = st.columns(4)
            sm1.metric("決済回数", f"{len(closed_trades)}回")
            sm2.metric("勝敗", f"{wins}勝 {losses}敗")
            sm3.metric("累計損益", fmt_currency(total_pnl, show_sign=True))
            sm4.metric("平均損益/回", fmt_currency(avg_pnl, show_sign=True))

        if len(trades_sorted) == 0:
            st.info(f"{view_mode}に該当する取引はありません。")
        else:
            st.divider()
            _show_limit = 5
            _trades_list = list(trades_sorted.iterrows())
            _visible = _trades_list[:_show_limit]
            _hidden = _trades_list[_show_limit:]

            def _render_trade_row(t, best_id, worst_id):
                ticker = t["ticker"]
                shares = int(t["shares"])
                if t["status"] == "CLOSED":
                    pnl_val = t["profit_loss"] or 0
                    pct_val = t["profit_loss_pct"] or 0
                    if t["id"] == best_id and pnl_val > 0:
                        label = "BEST"
                    elif t["id"] == worst_id and pnl_val < 0:
                        label = "WORST"
                    else:
                        label = "WIN" if pnl_val >= 0 else "LOSS"
                    label_color = {"BEST": "#d97706", "WORST": "#7c3aed",
                                   "WIN": W, "LOSS": L}.get(label, P)
                    hd = t.get("holding_days")
                    hd_str = f" · {int(hd)}日" if pd.notna(hd) and hd else ""
                    ed = t["entry_timestamp"][:10] if pd.notna(
                        t.get("entry_timestamp")) else ""
                    xd = t["exit_timestamp"][:10] if pd.notna(
                        t.get("exit_timestamp")) else ""
                    pnl_color = "green" if pnl_val >= 0 else "red"

                    col_info, col_result = st.columns([4, 2])
                    with col_info:
                        st.markdown(
                            f"**{ticker}** {render_pill(label, label_color)}  "
                            f'<span style="color:#a1a1aa;font-size:0.8rem">'
                            f"{shares}株 · ${t['entry_price']:.2f} → "
                            f"${t['exit_price']:.2f} · {ed}→{xd}{hd_str}</span>",
                            unsafe_allow_html=True,
                        )
                    with col_result:
                        st.markdown(
                            f":{pnl_color}[**{fmt_currency(pnl_val, show_sign=True)}** "
                            f"({fmt_pct(pct_val, show_sign=True)})]"
                        )
                elif t["status"] == "OPEN":
                    ed = t["entry_timestamp"][:10] if pd.notna(
                        t.get("entry_timestamp")) else ""
                    col_info, col_result = st.columns([4, 2])
                    with col_info:
                        st.markdown(
                            f"**{ticker}** {render_pill('OPEN', P)}  "
                            f'<span style="color:#a1a1aa;font-size:0.8rem">'
                            f"{shares}株 @ ${t['entry_price']:.2f} · {ed}〜</span>",
                            unsafe_allow_html=True,
                        )
                    with col_result:
                        st.markdown(":blue[**保有中**]")

            for i, (_, t) in enumerate(_visible):
                if i > 0:
                    st.divider()
                _render_trade_row(t, best_id, worst_id)

            if _hidden:
                with st.expander(f"過去の取引をすべて表示（残り{len(_hidden)}件）"):
                    for i, (_, t) in enumerate(_hidden):
                        if i > 0:
                            st.divider()
                        _render_trade_row(t, best_id, worst_id)
    else:
        st.info("まだ取引がありません")
