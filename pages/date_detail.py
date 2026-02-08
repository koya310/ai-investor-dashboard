"""Date Detail — 日付別パイプライントレース"""

import json as _json
import logging
from datetime import date as _date

import dashboard_data as _dm
import pandas as pd
import streamlit as st

from components.shared import P, W, L, WEEKDAY_JP, MODE_LABELS

logger = logging.getLogger(__name__)

# ── 日付取得 ──
target = st.query_params.get("date")
log_dates = _dm.get_available_log_dates(30)

if not target:
    if log_dates:
        target = log_dates[0]
    else:
        st.markdown(
            '<div style="color:#94a3b8; text-align:center; padding:3rem; font-size:0.85rem">'
            "直近30日間のデータがありません</div>",
            unsafe_allow_html=True,
        )
        st.stop()

try:
    selected_date = _date.fromisoformat(target)
except ValueError:
    selected_date = _date.today()
    target = selected_date.isoformat()

wd_jp = WEEKDAY_JP[selected_date.weekday()]

# ── ナビゲーション: ← Pipeline | ◀前日 | 日付 | 翌日▶ | カレンダー ──
_date_opts = [_date.fromisoformat(d) for d in log_dates] if log_dates else []
_cur_idx = _date_opts.index(selected_date) if selected_date in _date_opts else -1
_has_newer = _cur_idx > 0
_has_older = _cur_idx >= 0 and _cur_idx < len(_date_opts) - 1

nav_c = st.columns([1, 1, 3, 1, 1])
with nav_c[0]:
    if st.button("← Pipeline", use_container_width=True):
        st.switch_page("pages/pipeline.py")
with nav_c[1]:
    if _has_older:
        _older = _date_opts[_cur_idx + 1]
        if st.button(f"◀ {_older.month}/{_older.day}", key="nav_prev", use_container_width=True):
            st.query_params["date"] = _older.isoformat()
            st.rerun()
with nav_c[2]:
    st.markdown(
        f'<div style="text-align:center; padding:0.4rem 0">'
        f'<span style="font-size:1.1rem; font-weight:800; color:#0f172a">{selected_date.month}/{selected_date.day}</span>'
        f'<span style="font-size:0.85rem; color:#64748b; margin-left:0.3rem">({wd_jp})</span>'
        f'<span style="font-size:0.72rem; color:#94a3b8; margin-left:0.4rem">{target}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )
with nav_c[3]:
    if _has_newer:
        _newer = _date_opts[_cur_idx - 1]
        if st.button(f"{_newer.month}/{_newer.day} ▶", key="nav_next", use_container_width=True):
            st.query_params["date"] = _newer.isoformat()
            st.rerun()
with nav_c[4]:
    if log_dates:
        _new_d = st.date_input("日付", value=selected_date, label_visibility="collapsed", key="dp")
        if _new_d.isoformat() != target:
            st.query_params["date"] = _new_d.isoformat()
            st.rerun()

# ── データ読み込み ──
summary = _dm.get_log_day_summary(target)
pipeline = _dm.get_pipeline_status(target)
ticker_flow = _dm.get_date_ticker_flow(target)

# ── ファネル型サマリーフロー ──
steps_data = [
    ("📰", "ニュース", summary["news"]),
    ("🧠", "AI分析", summary["analysis"]),
    ("⚡", "シグナル", summary["signals"]),
    ("💰", "取引", summary["trades"]),
]

funnel_html = '<div class="funnel-flow">'
for i, (icon, label, cnt) in enumerate(steps_data):
    v_cls = "" if cnt > 0 else "funnel-val-zero"
    s_cls = "funnel-step-active" if cnt > 0 else ""
    funnel_html += (
        f'<div class="funnel-step {s_cls}">'
        f'<div class="funnel-icon">{icon}</div>'
        f'<div class="funnel-val {v_cls}">{cnt:,}</div>'
        f'<div class="funnel-label">{label}</div>'
        f"</div>"
    )
    if i < len(steps_data) - 1:
        funnel_html += '<div class="funnel-arrow">→</div>'
funnel_html += "</div>"
st.markdown(funnel_html, unsafe_allow_html=True)

# ============================================================
# ★ ティッカー別フロー（核心セクション）
# ============================================================

st.markdown(
    f'<div class="sec-hdr">'
    f'<div class="bar" style="background:{P}"></div>'
    f'<div class="txt">ティッカー別フロー'
    f'<span class="sub">{len(ticker_flow)}銘柄</span></div>'
    f"</div>",
    unsafe_allow_html=True,
)

if ticker_flow:
    for item in ticker_flow:
        tk = item["ticker"]
        n_cnt = item["news_count"]
        a_cnt = item["analysis_count"]
        a_score = item["analysis_avg_score"]
        a_dir = item["analysis_direction"]
        sig = item["signal"]
        trd = item["trade"]

        # カード左ボーダー色
        card_cls = "tf-card"
        if trd:
            card_cls += " tf-card-trade"
        elif sig:
            card_cls += " tf-card-signal"

        # 方向ラベル
        dir_map = {"bullish": "強気", "bearish": "弱気", "neutral": "中立"}
        dir_label = dir_map.get(a_dir, a_dir)
        dir_color = W if a_dir == "bullish" else (L if a_dir == "bearish" else "#64748b")

        # 結果バッジ（右上）
        if trd:
            trd_label = "買い" if trd["action"] == "BUY" else "売り"
            outcome_cls = "tf-outcome-buy" if trd["action"] == "BUY" else "tf-outcome-sell"
            pnl_badge = ""
            if trd["pnl"] is not None and pd.notna(trd["pnl"]):
                pc = "c-pos" if trd["pnl"] >= 0 else "c-neg"
                ps = "+" if trd["pnl"] >= 0 else ""
                pnl_badge = f' <span class="{pc}" style="margin-left:0.3rem">{ps}${trd["pnl"]:,.0f}</span>'
            outcome_html = (
                f'<span class="tf-outcome {outcome_cls}">{trd_label} {trd["shares"]}株 @${trd["price"]:.2f}{pnl_badge}</span>'
            )
        elif sig:
            sig_label = "BUY" if sig["type"] == "BUY" else "SELL"
            outcome_cls = "tf-outcome-buy" if sig["type"] == "BUY" else "tf-outcome-sell"
            outcome_html = f'<span class="tf-outcome {outcome_cls}">{sig_label} 確信{sig["conviction"]}/10</span>'
        else:
            outcome_html = '<span class="tf-outcome tf-outcome-none">データ収集のみ</span>'

        # フローステップ（下段）
        flow_parts = []
        if n_cnt > 0:
            flow_parts.append(f'<span class="tf-step">📰 {n_cnt}件</span>')
        if a_cnt > 0:
            flow_parts.append(
                f'<span class="tf-step">🧠 {a_cnt}件 '
                f'<span style="color:{dir_color}; font-weight:600">{a_score:.0f}/{dir_label}</span></span>'
            )
        if sig:
            flow_parts.append(
                f'<span class="tf-step">⚡ シグナル</span>'
            )
        if trd:
            flow_parts.append(
                f'<span class="tf-step" style="background:#ecfdf5">💰 約定</span>'
            )

        flow_content = ' <span class="tf-arrow">→</span> '.join(flow_parts) if flow_parts else '<span style="color:#94a3b8">データなし</span>'

        st.markdown(
            f'<div class="{card_cls}">'
            f'<div class="tf-header-row">'
            f'<span class="tf-ticker">{tk}</span>'
            f'{outcome_html}'
            f"</div>"
            f'<div class="tf-flow">{flow_content}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        '<div class="card-sm" style="color:#94a3b8; text-align:center; padding:1.2rem">'
        "この日のティッカー別データはありません</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# ステップ詳細（ドリルダウン expanders）
# ============================================================

st.markdown(
    f'<div class="sec-hdr">'
    f'<div class="bar" style="background:#64748b"></div>'
    f'<div class="txt">ステップ詳細</div>'
    f"</div>",
    unsafe_allow_html=True,
)

# ── システム実行 ──
log_runs = _dm.get_log_system_runs(target)
with st.expander(f"⚙️ システム実行 ({len(log_runs)}件)", expanded=False):
    if len(log_runs) > 0:
        for _, run in log_runs.iterrows():
            r_mode = run.get("run_mode", "")
            r_status = run.get("status", "")
            r_started = str(run.get("started_at", ""))[:19].replace("T", " ")
            r_ended = str(run.get("ended_at", "") or "")[:19].replace("T", " ")
            r_host = run.get("host_name", "") or ""
            r_news = run.get("news_collected", 0) or 0
            r_sig = run.get("signals_detected", 0) or 0
            r_trd = run.get("trades_executed", 0) or 0
            r_err = run.get("errors_count", 0) or 0
            r_msg = run.get("error_message", "") or ""
            s_c = W if r_status == "completed" else (L if r_status == "failed" else "#f59e0b")
            detail_r = (
                f'<div class="dd-detail">'
                f'<div class="dd-kv"><span class="dd-k">開始</span><span class="dd-v">{r_started}</span></div>'
                f'<div class="dd-kv"><span class="dd-k">終了</span><span class="dd-v">{r_ended}</span></div>'
                f'<div class="dd-kv"><span class="dd-k">ホスト</span><span class="dd-v">{r_host}</span></div>'
                f'<div class="dd-kv"><span class="dd-k">処理</span><span class="dd-v">ニュース{r_news} / シグナル{r_sig} / 取引{r_trd}</span></div>'
                + (f'<div class="dd-kv"><span class="dd-k">エラー</span><span class="dd-v" style="color:{L}">{r_err}件: {r_msg}</span></div>' if r_err else "")
                + f"</div>"
            )
            st.markdown(
                f'<div class="dd-item"><details><summary class="dd-summary">'
                f'<span style="color:{s_c}; font-weight:600">{r_status}</span> '
                f'<b>{MODE_LABELS.get(r_mode, r_mode)}</b> '
                f'<span style="color:#94a3b8">{r_started[11:16]}</span>'
                f'</summary>{detail_r}</details></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<span style="color:#94a3b8; font-size:0.82rem">この日の実行記録はありません</span>', unsafe_allow_html=True)

# ── ニュース詳細 ──
news_cnt = summary["news"]
with st.expander(f"📰 ニュース収集 ({news_cnt:,}件)", expanded=False):
    today_news = _dm.get_log_news(target)
    if len(today_news) > 0:
        # ソース別集計
        src_counts = today_news["source"].value_counts().head(10)
        src_pills = " ".join(
            f'<span class="pill pill-blue" style="font-size:0.6rem; margin:0.1rem">{src} ({cnt})</span>'
            for src, cnt in src_counts.items()
        )
        st.markdown(
            f'<div style="margin-bottom:0.5rem; font-size:0.72rem; color:#64748b">'
            f"ソース: {src_pills}</div>",
            unsafe_allow_html=True,
        )

        # ティッカーフィルター
        all_tickers_set = set()
        for tj in today_news["tickers_json"].dropna():
            try:
                for t in _json.loads(tj):
                    all_tickers_set.add(t)
            except Exception:
                pass
        ticker_filter = st.selectbox(
            "銘柄フィルター",
            ["すべて"] + sorted(all_tickers_set),
            key="news_ticker_filter",
        )

        filtered_news = today_news
        if ticker_filter != "すべて":
            filtered_news = today_news[
                today_news["tickers_json"].fillna("").str.contains(ticker_filter)
            ]

        news_html = ""
        for _, n in filtered_news.head(50).iterrows():
            title = n.get("title", "") or ""
            source = n.get("source", "") or ""
            content = n.get("content", "") or ""
            theme = n.get("theme", "") or ""
            tickers_raw = n.get("tickers_json", "") or ""
            sent = n.get("sentiment_score")
            created = str(n.get("created_at", ""))[:19].replace("T", " ")

            # ティッカーピル
            tk_pills = ""
            try:
                tickers = _json.loads(tickers_raw) if tickers_raw else []
                for tk in tickers[:8]:
                    tk_pills += f'<span style="font-size:0.6rem; color:{P}; margin-right:0.2rem">${tk}</span>'
            except Exception:
                pass

            detail = ""
            if content:
                detail += f'<div class="dd-kv"><span class="dd-k">内容</span><span class="dd-v">{content[:500]}</span></div>'
            if sent is not None and pd.notna(sent):
                s_color = W if sent > 0 else (L if sent < 0 else "#94a3b8")
                detail += f'<div class="dd-kv"><span class="dd-k">感情</span><span class="dd-v" style="color:{s_color}">{sent:+.2f}</span></div>'
            if theme:
                detail += f'<div class="dd-kv"><span class="dd-k">テーマ</span><span class="dd-v">{theme}</span></div>'
            if tk_pills:
                detail += f'<div class="dd-kv"><span class="dd-k">関連銘柄</span><span class="dd-v">{tk_pills}</span></div>'
            detail += f'<div class="dd-kv"><span class="dd-k">取得時刻</span><span class="dd-v">{created}</span></div>'

            news_html += (
                f'<div class="dd-item"><details>'
                f'<summary class="dd-summary">{title}'
                f'<span style="color:#94a3b8; font-size:0.68rem; margin-left:0.3rem">{source}</span>'
                f'</summary>'
                f'<div class="dd-detail">{detail}</div>'
                f'</details></div>'
            )

        st.markdown(news_html, unsafe_allow_html=True)

        if len(filtered_news) > 50:
            st.markdown(
                f'<div style="color:#94a3b8; font-size:0.72rem; text-align:center; padding:0.5rem">'
                f"他 {len(filtered_news) - 50}件は省略</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<span style="color:#94a3b8; font-size:0.82rem">この日のニュースはありません</span>',
            unsafe_allow_html=True,
        )

# ── AI分析詳細 ──
analysis_cnt = summary["analysis"]
with st.expander(f"🧠 AI分析 ({analysis_cnt}件)", expanded=False):
    today_analysis = _dm.get_log_analyses(target)
    if len(today_analysis) > 0:
        ana_html = ""
        for _, a in today_analysis.iterrows():
            theme = a.get("theme", "") or ""
            ticker = a.get("ticker", "") or ""
            a_type = a.get("analysis_type", "") or ""
            score = a.get("score") or 0
            direction = a.get("direction", "") or ""
            summary_txt = a.get("summary", "") or ""
            detailed = a.get("detailed_analysis", "") or ""
            kp_raw = a.get("key_points_json", "") or ""
            rec = a.get("recommendation", "") or ""
            model = a.get("model_used", "") or ""
            time_a = str(a.get("analyzed_at", ""))[:19].replace("T", " ")

            dir_label = {"bullish": "強気", "bearish": "弱気", "neutral": "中立"}.get(direction, direction)
            dir_color = W if direction == "bullish" else (L if direction == "bearish" else "#64748b")
            type_label = {"theme_report": "テーマ", "ticker_analysis": "銘柄", "impact_analysis": "インパクト"}.get(a_type, a_type)

            header = (
                f'<span class="pill pill-blue" style="font-size:0.6rem; padding:0.03rem 0.25rem">{type_label}</span> '
                f'<b>{theme}</b>'
            )
            if ticker:
                header += f' <span style="color:{P}; font-weight:600">{ticker}</span>'
            header += f' <span style="color:{dir_color}; font-weight:600">スコア{score:.0f} / {dir_label}</span>'

            detail = ""
            if rec:
                detail += f'<div class="dd-kv"><span class="dd-k">推奨</span><span class="dd-v" style="font-weight:600">{rec}</span></div>'
            if summary_txt:
                detail += f'<div class="dd-kv"><span class="dd-k">要約</span><span class="dd-v">{summary_txt}</span></div>'
            try:
                kps = _json.loads(kp_raw) if kp_raw else []
                if kps:
                    kp_list = "".join(f"<li>{kp}</li>" for kp in kps[:8])
                    detail += f'<div class="dd-kv"><span class="dd-k">注目点</span><span class="dd-v"><ul style="margin:0; padding-left:1.2rem">{kp_list}</ul></span></div>'
            except Exception:
                pass
            if detailed:
                detail += (
                    f'<div style="margin-top:0.4rem; padding-top:0.4rem; border-top:1px solid #e2e8f0">'
                    f'<span class="dd-k">詳細分析</span>'
                    f'<div style="margin-top:0.2rem; white-space:pre-wrap; font-size:0.72rem">{detailed[:1200]}</div></div>'
                )
            detail += f'<div class="dd-kv" style="margin-top:0.3rem"><span class="dd-k">モデル</span><span class="dd-v">{model} / {time_a}</span></div>'

            ana_html += (
                f'<div class="dd-item"><details>'
                f'<summary class="dd-summary">{header}</summary>'
                f'<div class="dd-detail">{detail}</div>'
                f'</details></div>'
            )

        st.markdown(ana_html, unsafe_allow_html=True)
    else:
        st.markdown(
            '<span style="color:#94a3b8; font-size:0.82rem">この日のAI分析はありません</span>',
            unsafe_allow_html=True,
        )

# ── シグナル詳細 ──
sig_cnt = summary["signals"]
with st.expander(f"⚡ シグナル ({sig_cnt}件)", expanded=False):
    today_sigs = _dm.get_log_signals(target)
    if len(today_sigs) > 0:
        sig_html = ""
        for _, s in today_sigs.iterrows():
            sig_type = s["signal_type"]
            sig_label = "買い" if sig_type == "BUY" else "売り"
            sig_cls = "pill-green" if sig_type == "BUY" else "pill-red"
            ticker = s["ticker"]
            price = s.get("price", 0) or 0
            conv = s.get("conviction") or 0
            conf = s.get("confidence") or 0
            status_s = s.get("status", "")
            rsi = s.get("rsi")
            macd = s.get("macd")
            target_p = s.get("target_price")
            sl = s.get("stop_loss")
            reasoning = s.get("reasoning", "") or ""
            df_raw = s.get("decision_factors_json", "") or ""
            time_s = str(s.get("detected_at", ""))[:19].replace("T", " ")

            status_label = {
                "pending": "待機中", "executed": "執行済", "rejected": "見送り",
                "cancelled": "取消", "expired": "期限切れ",
            }.get(status_s, status_s)

            header = (
                f'<span class="pill {sig_cls}" style="font-size:0.7rem">{sig_label}</span> '
                f'<b>{ticker}</b> '
                f'<span style="color:#64748b">@${price:.2f}</span> '
                f'<span class="pill pill-blue" style="font-size:0.58rem; padding:0.03rem 0.25rem">{status_label}</span>'
            )
            if conv:
                header += f' <span style="color:#64748b; font-size:0.72rem">確信度 {conv}/10</span>'

            detail = ""
            detail += f'<div class="dd-kv"><span class="dd-k">検出時刻</span><span class="dd-v">{time_s}</span></div>'
            if conv:
                detail += f'<div class="dd-kv"><span class="dd-k">確信度</span><span class="dd-v">{conv} / 10</span></div>'
            if conf:
                detail += f'<div class="dd-kv"><span class="dd-k">信頼度</span><span class="dd-v">{conf:.0%}</span></div>'
            if rsi is not None and pd.notna(rsi):
                rsi_color = L if rsi > 70 else (W if rsi < 30 else "#0f172a")
                detail += f'<div class="dd-kv"><span class="dd-k">RSI</span><span class="dd-v" style="color:{rsi_color}">{rsi:.1f}</span></div>'
            if macd is not None and pd.notna(macd):
                detail += f'<div class="dd-kv"><span class="dd-k">MACD</span><span class="dd-v">{macd:.4f}</span></div>'
            if target_p:
                detail += f'<div class="dd-kv"><span class="dd-k">目標価格</span><span class="dd-v">${target_p:.2f}</span></div>'
            if sl:
                detail += f'<div class="dd-kv"><span class="dd-k">損切ライン</span><span class="dd-v">${sl:.2f}</span></div>'
            if reasoning:
                detail += (
                    f'<div style="margin-top:0.4rem; padding-top:0.4rem; border-top:1px solid #e2e8f0">'
                    f'<span class="dd-k">判断理由</span>'
                    f'<div style="margin-top:0.2rem; white-space:pre-wrap; font-size:0.72rem">{reasoning}</div></div>'
                )

            # decision_factors 詳細展開
            if df_raw:
                try:
                    factors = _json.loads(df_raw)
                    if isinstance(factors, dict):
                        factor_detail = ""
                        ns = factors.get("news_score")
                        nr = factors.get("news_reason", "")
                        if ns is not None:
                            ns_color = W if ns > 0 else (L if ns < 0 else "#94a3b8")
                            factor_detail += f'<div class="dd-kv"><span class="dd-k">ニューススコア</span><span class="dd-v" style="color:{ns_color}">{ns:+.2f}</span></div>'
                        if nr:
                            factor_detail += f'<div class="dd-kv"><span class="dd-k">ニュース理由</span><span class="dd-v">{nr}</span></div>'
                        tr = factors.get("technical_reason", "")
                        if tr:
                            factor_detail += f'<div class="dd-kv"><span class="dd-k">テクニカル</span><span class="dd-v">{tr}</span></div>'
                        fr = factors.get("fundamental_reason", "")
                        if fr:
                            factor_detail += f'<div class="dd-kv"><span class="dd-k">ファンダ</span><span class="dd-v">{fr}</span></div>'
                        strat = factors.get("strategy_type", "")
                        if strat:
                            factor_detail += f'<div class="dd-kv"><span class="dd-k">戦略</span><span class="dd-v">{strat}</span></div>'
                        dr = factors.get("detailed_reason", "")
                        chg = factors.get("change_pct")
                        if dr:
                            factor_detail += f'<div class="dd-kv"><span class="dd-k">詳細根拠</span><span class="dd-v">{dr}</span></div>'
                        if chg is not None:
                            chg_color = W if chg > 0 else L
                            factor_detail += f'<div class="dd-kv"><span class="dd-k">変動率</span><span class="dd-v" style="color:{chg_color}">{chg:+.1f}%</span></div>'

                        if factor_detail:
                            detail += (
                                f'<div style="margin-top:0.4rem; padding-top:0.4rem; border-top:1px solid #e2e8f0">'
                                f'<span class="dd-k" style="font-weight:600">判断要因</span>'
                                f'{factor_detail}</div>'
                            )
                except Exception:
                    pass

            sig_html += (
                f'<div class="dd-item"><details open>'
                f'<summary class="dd-summary">{header}</summary>'
                f'<div class="dd-detail">{detail}</div>'
                f'</details></div>'
            )

        st.markdown(sig_html, unsafe_allow_html=True)
    else:
        st.markdown(
            '<span style="color:#94a3b8; font-size:0.82rem">この日のシグナルはありません</span>',
            unsafe_allow_html=True,
        )

# ── 取引詳細 ──
trade_cnt = summary["trades"]
with st.expander(f"💰 取引 ({trade_cnt}件)", expanded=False):
    today_trades = _dm.get_log_trades(target)
    if len(today_trades) > 0:
        trade_html = ""
        for _, t in today_trades.iterrows():
            action = t["action"]
            a_label = "買い" if action == "BUY" else "売り"
            a_cls = "pill-green" if action == "BUY" else "pill-red"
            ticker = t["ticker"]
            entry_p = t["entry_price"]
            exit_p = t.get("exit_price")
            shares = int(t["shares"])
            pnl = t.get("profit_loss") or 0
            pnl_pct = t.get("profit_loss_pct") or 0
            status_t = t.get("status", "")
            exit_reason = t.get("exit_reason", "") or ""
            strategy = t.get("strategy_used", "") or ""
            entry_ts = str(t.get("entry_timestamp", ""))[:19].replace("T", " ")
            exit_ts = str(t.get("exit_timestamp", "") or "")[:19].replace("T", " ")
            holding = t.get("holding_days")

            pnl_c = "c-pos" if pnl >= 0 else "c-neg"
            pnl_s = "+" if pnl >= 0 else ""

            if status_t == "CLOSED":
                pnl_txt = f'<span class="{pnl_c}" style="font-weight:600">{pnl_s}${pnl:,.2f} ({pnl_s}{pnl_pct:.1f}%)</span>'
            else:
                pnl_txt = '<span class="pill pill-blue" style="font-size:0.6rem">保有中</span>'

            header = (
                f'<span class="pill {a_cls}" style="font-size:0.7rem">{a_label}</span> '
                f'<b>{ticker}</b> '
                f'<span style="color:#64748b">{shares}株 @${entry_p:.2f}</span> {pnl_txt}'
            )

            detail = ""
            detail += f'<div class="dd-kv"><span class="dd-k">エントリー</span><span class="dd-v">${entry_p:.2f} ({entry_ts})</span></div>'
            if exit_p and pd.notna(exit_p):
                detail += f'<div class="dd-kv"><span class="dd-k">エグジット</span><span class="dd-v">${exit_p:.2f} ({exit_ts})</span></div>'
            if holding is not None and pd.notna(holding):
                detail += f'<div class="dd-kv"><span class="dd-k">保有日数</span><span class="dd-v">{int(holding)}日</span></div>'
            if exit_reason:
                reason_label = {"STOP_LOSS": "損切り", "TAKE_PROFIT": "利確", "SIGNAL": "シグナル", "MANUAL": "手動"}.get(exit_reason, exit_reason)
                detail += f'<div class="dd-kv"><span class="dd-k">決済理由</span><span class="dd-v">{reason_label}</span></div>'
            if strategy:
                detail += f'<div class="dd-kv"><span class="dd-k">戦略</span><span class="dd-v">{strategy}</span></div>'

            trade_html += (
                f'<div class="dd-item"><details>'
                f'<summary class="dd-summary">{header}</summary>'
                f'<div class="dd-detail">{detail}</div>'
                f'</details></div>'
            )

        st.markdown(trade_html, unsafe_allow_html=True)
    else:
        st.markdown(
            '<span style="color:#94a3b8; font-size:0.82rem">この日の取引はありません</span>',
            unsafe_allow_html=True,
        )
