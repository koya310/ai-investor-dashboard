"""Home -- ポートフォリオ概要（大セクション・カード統合版）"""

import logging
from datetime import datetime

import dashboard_data as _dm
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.shared import (
    P, W, L,
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

st.title("ポートフォリオ")
st.caption("Phase 3 ペーパートレードの運用状況")


# ============================================================
# 詳細分析ダイアログ（変更なし）
# ============================================================

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
                f"勝率が{summary['win_rate']}%と低い: "
                f"{summary['losses']}回中ほとんどが損失。"
                "シグナル品質（銘柄選定・タイミング）の改善が最優先。"
            )
        if summary["avg_loss_pct"] != 0 and summary["avg_profit_pct"] != 0:
            rr = abs(summary["avg_profit_pct"] / summary["avg_loss_pct"])
            if rr < 1.5:
                insights.append(
                    f"リスクリワード比が{rr:.2f}と不十分 "
                    f"（勝ち平均{summary['avg_profit_pct']:+.2f}% vs "
                    f"負け平均{summary['avg_loss_pct']:+.2f}%）。"
                    "利確を伸ばすか、損切りを早くする必要あり。"
                )
        pf = summary["profit_factor"]
        if pf != float("inf") and pf < 1.0:
            insights.append(
                f"プロフィットファクターが{pf:.2f}（1.0未満 = 損失 > 利益）。"
                "トータルで負けている状態。"
            )
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

    by_theme = patterns.get("by_theme", {})
    if by_theme:
        st.subheader("テーマ別", divider="gray")
        for theme, tdata in sorted(by_theme.items(), key=lambda x: x[1]["total_pnl"]):
            col_th, col_pnl = st.columns([3, 2])
            with col_th:
                st.markdown(f"{theme} ({tdata['trades']}回, 勝率{tdata['win_rate']}%)")
            with col_pnl:
                pnl = tdata["total_pnl"]
                color = "green" if pnl >= 0 else "red"
                st.markdown(f":{color}[**{fmt_currency(pnl, show_sign=True)}**]")

    st.subheader("改善アクション", divider="gray")
    actions = []
    if summary["win_rate"] < 50:
        actions.append("シグナルのフィルタリング強化（確信度の閾値引き上げ）")
    if summary["avg_loss_pct"] != 0 and abs(summary["avg_loss_pct"]) > abs(
        summary["avg_profit_pct"]
    ):
        actions.append("ストップロスを現在より浅く設定（損切りを早める）")
    if summary["profit_factor"] < 1.0:
        actions.append("利益確定の目標幅を拡大（テイクプロフィットの見直し）")
    if summary["avg_holding_days"] < 1:
        actions.append("保有期間が短すぎる可能性。デイトレ傾向を見直し")
    if not actions:
        actions.append("現在のパラメータを維持しつつデータ蓄積を継続")
    for i, a in enumerate(actions, 1):
        st.markdown(f"{i}. {a}")


# ============================================================
# 事前計算
# ============================================================

_deadline_dt = datetime.strptime(_dm.GONOGO_DEADLINE, "%Y-%m-%d")
_days_left = max((_deadline_dt - datetime.now()).days, 0)
_targets = _dm.KPI_TARGETS
_v = verdict["status"]
_passed = verdict["passed"]
_total = verdict["total"]
_wr = kpi["win_rate"]
_pnl_total = kpi.get("total_pnl", 0)
_last_run = d["last_run"]

if _last_run:
    _run_status = _last_run["status"]
    _sys_label = {"completed": "正常稼働", "running": "実行中"}.get(
        _run_status, "異常あり"
    )
else:
    _sys_label = "データなし"

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


# ============================================================
# CARD 1: 概要 — 判定 + ポートフォリオ + 保有銘柄
# ============================================================

with st.container(border=True):
    card_title("概要", color=P, subtitle=f"{_passed}/{_total}項目達成")

    # ── 判定サマリー ──
    _progress = (_passed / _total) if _total > 0 else 0.0
    st.progress(min(1.0, max(0.0, _progress)))
    st.caption(
        f"Go/No-Go 達成率: {_passed}/{_total}  "
        f"（判定期限: {_dm.GONOGO_DEADLINE} / 残り {_days_left}日）"
    )

    qs1, qs2, qs3, qs4 = st.columns(4)
    qs1.metric("システム状態", _sys_label)
    qs2.metric("勝率", fmt_pct(_wr, decimals=0),
               delta=f"目標 {_targets['win_rate']:.0f}%", delta_color="off")
    qs3.metric("累積損益", fmt_currency(_pnl_total, show_sign=True),
               delta=fmt_delta(_pnl_total))
    qs4.metric("運用日数", f"{kpi.get('days_running', 0)}日")

    verdict_col, action_col = st.columns([5, 1])
    with verdict_col:
        if _v == "GO":
            st.success(f"**GO** — 全{_total}項目を達成。Phase 4 へ移行可能。")
        elif _v == "CONDITIONAL_GO":
            _recs = " / ".join(verdict["recommendations"][:2])
            st.warning(f"**条件付き** — {_passed}/{_total}項目を達成。  \n{_recs}")
        else:
            st.error(
                f"**未達** — {_passed}/{_total}項目のみ。"
                f"残り{_days_left}日で改善が必要。"
            )
    with action_col:
        if st.button("今日の実行 →", use_container_width=True):
            st.switch_page("pages/pipeline.py")

    st.divider()

    # ── ポートフォリオ + 保有銘柄 ──
    if total_val > 0:
        pnl = total_val - capital
        pnl_pct = pnl / capital * 100
        source_label = "Alpaca" if alpaca_pf is not None else "推定"
        equity_pct = (equity_val / total_val * 100) if total_val > 0 else 0
        cash_pct = 100 - equity_pct

        pf_left, pf_right = st.columns([3, 2])

        with pf_left:
            st.markdown(
                f"**ポートフォリオ総額**  {render_pill(source_label)}",
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
            if alpaca_pf is None:
                st.caption("Alpaca未接続 — 取引履歴と終値から推定")

            eq_col, cash_col, cap_col = st.columns(3)
            eq_col.metric("株式", fmt_currency(equity_val),
                          f"{equity_pct:.0f}%", delta_color="off")
            cash_col.metric("現金", fmt_currency(cash_val),
                            f"{cash_pct:.0f}%", delta_color="off")
            cap_col.metric("初期資本", fmt_currency(capital))

        with pf_right:
            st.markdown("**保有銘柄**")
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
                            f'<span style="color:#94a3b8;font-size:0.82rem">'
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
    else:
        st.info("まだデータがありません")

# 注記（カード外、小さなキャプション）
_total_trades = kpi.get("total_trades", 0)
_days_running = kpi.get("days_running", 0)
if _total_trades < 20 and _days_running < 30:
    st.caption(
        f"注記: データ {_total_trades}件 / {_days_running}日間のため統計的信頼性はまだ低めです。"
    )


# ============================================================
# CARD 2: パフォーマンス — チャート + KPIチェックリスト
# ============================================================

deadline_dt = datetime.strptime(_dm.GONOGO_DEADLINE, "%Y-%m-%d")
days_left = max((deadline_dt - datetime.now()).days, 0)
targets = _dm.KPI_TARGETS

with st.container(border=True):
    card_title("パフォーマンス", color=P, subtitle="資産推移 + 目標達成度")

    # ── チャート ──
    if len(daily) > 0:
        pnl = total_val - capital
        fill_color = ("rgba(5,150,105,0.05)" if pnl >= 0
                      else "rgba(220,38,38,0.04)")
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
            line=dict(color=P, width=2.5), marker=dict(size=4, color=P),
            hovertemplate="%{x|%m/%d}  $%{y:,.0f}<extra></extra>",
        ))
        if len(spy) > 0:
            fig.add_trace(go.Scatter(
                x=spy["date"], y=spy["spy_total"],
                name="SPY", mode="lines",
                line=dict(color="#a3a3a3", width=1.2, dash="dot"),
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
                    marker=dict(symbol="triangle-up", size=12, color=W,
                                line=dict(width=1.5, color="#fff")),
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
                    marker=dict(symbol="triangle-down", size=12, color=L,
                                line=dict(width=1.5, color="#fff")),
                    hovertemplate="%{x|%m/%d} 売り %{text}<extra></extra>",
                    text=merged["ticker"], showlegend=False,
                ))

        fig.add_hline(y=capital, line_dash="dot", line_color="#cbd5e1", line_width=1)
        fig.add_annotation(
            x=daily["date"].iloc[0], y=capital,
            text=f"スタート ${capital:,.0f}", showarrow=False,
            font=dict(size=10, color="#94a3b8"), xanchor="left", yshift=10,
        )
        fig.update_layout(
            template="plotly_white", height=280,
            margin=dict(t=8, b=24, l=50, r=16),
            xaxis=dict(
                title="",
                gridcolor="#f1f5f9",
                linecolor="#e2e8f0",
                tickfont=dict(size=10, color="#94a3b8"),
            ),
            yaxis=dict(
                title="", tickprefix="$", tickformat=",",
                gridcolor="#f1f5f9",
                linecolor="#e2e8f0",
                tickfont=dict(size=10, color="#94a3b8"),
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="right", x=1,
                font=dict(size=10, color="#64748b"),
            ),
            font=dict(
                family="Inter, Hiragino Kaku Gothic ProN, sans-serif",
                size=11,
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            hoverlabel=dict(
                bgcolor="#1e293b",
                font=dict(color="#f8fafc", size=11),
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("資産推移データがありません。")

    st.divider()

    # ── KPIチェックリスト ──
    kpi_checks = []

    wr = kpi["win_rate"]
    wr_tgt = targets["win_rate"]
    wr_ok = wr >= wr_tgt
    wr_pct = min(100, max(0, wr / wr_tgt * 100)) if wr_tgt > 0 else 0
    kpi_checks.append({
        "label": "勝率", "tip": "利益が出た取引の割合",
        "current": fmt_pct(wr, decimals=0),
        "target_str": fmt_pct(wr_tgt, decimals=0),
        "ok": wr_ok, "bar_pct": wr_pct / 100,
        "gap_txt": "達成" if wr_ok else f"あと{wr_tgt - wr:.0f}pp",
        "gap_sub": "" if wr_ok else "勝てる銘柄選定が必要",
    })

    ar = kpi["annual_return"]
    ar_tgt = targets["annual_return"]
    ar_ok = ar >= ar_tgt
    ar_pct = min(100, max(0, ar / ar_tgt * 100)) if ar_tgt > 0 and ar > 0 else 0
    actual_ret = kpi.get("actual_return_pct", 0)
    ar_note = (f"（{_days_running}日間で{actual_ret:+.2f}%→年率換算）"
               if _days_running < 30 else "")
    kpi_checks.append({
        "label": "年率リターン",
        "tip": f"今の成績を1年に換算した利回り{ar_note}",
        "current": fmt_pct(ar, show_sign=True),
        "target_str": fmt_pct(ar_tgt, decimals=0),
        "ok": ar_ok, "bar_pct": ar_pct / 100,
        "gap_txt": "達成" if ar_ok else f"あと{ar_tgt - ar:.1f}%",
        "gap_sub": ("" if ar_ok else
                    (f"マイナス圏。利確精度の向上が必要{ar_note}" if ar < 0 else ar_note)),
    })

    dd = kpi["max_drawdown"]
    dd_tgt = targets["max_drawdown"]
    dd_ok = dd <= dd_tgt
    dd_pct = 100 if dd_ok else (min(100, max(0, dd_tgt / dd * 100)) if dd_tgt > 0 else 0)
    kpi_checks.append({
        "label": "最大DD", "tip": "資産が最も下がった時の下落幅（小さいほど良い）",
        "current": fmt_pct(dd),
        "target_str": f"{dd_tgt:.0f}%以下",
        "ok": dd_ok, "bar_pct": dd_pct / 100,
        "gap_txt": "達成" if dd_ok else f"{dd - dd_tgt:.0f}%超過",
        "gap_sub": "" if dd_ok else "損切りルールの改善が急務",
    })

    up = kpi["uptime"]
    up_tgt = targets["uptime"]
    up_ok = up >= up_tgt
    up_pct = min(100, max(0, up / up_tgt * 100)) if up_tgt > 0 else 0
    kpi_checks.append({
        "label": "稼働率", "tip": "システムが正常に動いていた割合",
        "current": fmt_pct(up, decimals=0),
        "target_str": fmt_pct(up_tgt, decimals=0),
        "ok": up_ok, "bar_pct": up_pct / 100,
        "gap_txt": "達成" if up_ok else f"あと{up_tgt - up:.0f}pp",
        "gap_sub": "" if up_ok else "システム安定性の改善が必要",
    })

    achieved_count = sum(1 for item in kpi_checks if item["ok"])
    pending_count = len(kpi_checks) - achieved_count

    title_col, btn_col = st.columns([5, 1])
    with title_col:
        st.markdown(
            f'<div class="section-label">実取引チェックリスト</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"残り{days_left}日で Go/No-Go 判定")
    with btn_col:
        if st.button("詳細分析", type="secondary", use_container_width=True):
            show_analysis_dialog()

    sum1, sum2, sum3 = st.columns(3)
    sum1.metric("達成項目", f"{achieved_count}/{len(kpi_checks)}")
    sum2.metric("未達項目", f"{pending_count}")
    sum3.metric("総合判定", {"GO": "GO", "CONDITIONAL_GO": "条件付き",
                            "NO_GO": "NO_GO"}.get(_v, _v))

    if verdict["recommendations"]:
        st.caption(f"優先改善: {' / '.join(verdict['recommendations'][:3])}")

    for i, item in enumerate(kpi_checks):
        if i > 0:
            st.divider()
        col_label, col_bar, col_gap = st.columns([2, 4, 2])
        with col_label:
            st.markdown(f"**{item['label']}**")
            st.caption(item["tip"])
        with col_bar:
            st.progress(min(1.0, max(0.0, item["bar_pct"])))
            val_col, tgt_col = st.columns(2)
            val_col.markdown(f"**{item['current']}**")
            tgt_col.markdown(
                f'<span style="color:#94a3b8;font-size:0.82rem">'
                f"目標 {item['target_str']}</span>",
                unsafe_allow_html=True,
            )
        with col_gap:
            if item["ok"]:
                st.success(f"✓ {item['gap_txt']}")
            else:
                st.error(item["gap_txt"])
                if item["gap_sub"]:
                    st.caption(item["gap_sub"])


# ============================================================
# CARD 3: 取引履歴
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
            sm3.metric("累計損益", fmt_currency(total_pnl, show_sign=True),
                       delta_color="normal" if total_pnl >= 0 else "inverse")
            sm4.metric("平均損益/回", fmt_currency(avg_pnl, show_sign=True),
                       delta_color="normal" if avg_pnl >= 0 else "inverse")

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
                    hd_str = f" · {int(hd)}日保有" if pd.notna(hd) and hd else ""
                    ed = t["entry_timestamp"][:10] if pd.notna(t.get("entry_timestamp")) else ""
                    xd = t["exit_timestamp"][:10] if pd.notna(t.get("exit_timestamp")) else ""
                    pnl_color = "green" if pnl_val >= 0 else "red"

                    col_info, col_result = st.columns([4, 2])
                    with col_info:
                        st.markdown(
                            f"**{ticker}** {render_pill(label, label_color)}  "
                            f'<span style="color:#94a3b8;font-size:0.82rem">'
                            f"{shares}株 · ${t['entry_price']:.2f} → ${t['exit_price']:.2f}"
                            f" · {ed} → {xd}{hd_str}</span>",
                            unsafe_allow_html=True,
                        )
                    with col_result:
                        st.markdown(
                            f":{pnl_color}[**{fmt_currency(pnl_val, show_sign=True)}** "
                            f"({fmt_pct(pct_val, show_sign=True)})]"
                        )
                elif t["status"] == "OPEN":
                    ed = t["entry_timestamp"][:10] if pd.notna(t.get("entry_timestamp")) else ""
                    col_info, col_result = st.columns([4, 2])
                    with col_info:
                        st.markdown(
                            f"**{ticker}** {render_pill('OPEN', P)}  "
                            f'<span style="color:#94a3b8;font-size:0.82rem">'
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
