"""
ダッシュボード用データ取得・計算レイヤー

Streamlitダッシュボードで使用するすべてのデータアクセスと
KPI計算ロジックを集約する。
"""

import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent

logger = logging.getLogger(__name__)
PORTFOLIO_CONFIG = PROJECT_ROOT / "data" / "portfolio.json"
HOLDINGS_CONFIG = PROJECT_ROOT / "data" / "my_holdings.json"
ENV_PATH = PROJECT_ROOT / "data" / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# Phase 3 開始日・Go/No-Go期限
PHASE3_START = "2026-01-24"
GONOGO_DEADLINE = "2026-02-28"

# KPI目標値
KPI_TARGETS = {
    "win_rate": 55.0,
    "annual_return": 12.0,
    "max_drawdown": 15.0,
    "uptime": 99.0,
}


DB_PATH = PROJECT_ROOT / "data" / "ai_investor.db"


def _connect():
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _build_ticker_theme_map() -> dict[str, str]:
    """portfolio.json からティッカー → テーマの辞書を構築"""
    try:
        with open(PORTFOLIO_CONFIG) as f:
            config = json.load(f)
        mapping = {}
        for theme in config.get("monitoring_themes", []):
            name = theme["name"]
            for ticker in theme.get("tickers", []):
                if ticker not in mapping:
                    mapping[ticker] = name
        return mapping
    except Exception:
        return {}


INITIAL_CAPITAL = 100_000.0


# ============================================================
# 日次資産推移（トレード履歴 + yfinance から再構築）
# ============================================================


def build_daily_portfolio(start_date: str = PHASE3_START) -> pd.DataFrame:
    """トレード履歴と市場価格から日次の資産推移を再構築する。

    Returns:
        DataFrame with columns:
            date, cash, equity, total, daily_change, daily_change_pct,
            events (その日の売買イベント文字列)
    """
    with _connect() as conn:
        trades = pd.read_sql_query(
            "SELECT ticker, action, shares, entry_price, exit_price, "
            "       total_value, profit_loss, entry_timestamp, exit_timestamp, status "
            "FROM trades WHERE entry_timestamp >= ? ORDER BY entry_timestamp",
            conn,
            params=[start_date],
        )

    if len(trades) == 0:
        return pd.DataFrame()

    trades["entry_date"] = pd.to_datetime(
        trades["entry_timestamp"], format="ISO8601", errors="coerce"
    ).dt.normalize()
    trades["exit_date"] = pd.to_datetime(
        trades["exit_timestamp"], format="ISO8601", errors="coerce"
    ).dt.normalize()

    # --- 日付範囲 ---
    first_date = trades["entry_date"].min()
    today = pd.Timestamp.now().normalize()
    date_range = pd.date_range(first_date, today, freq="B")  # 営業日のみ

    # --- 各日のポジション状況を構築 ---
    # BUYイベント: entry_date に shares を保有開始、cash減少
    # SELLイベント (CLOSED): exit_date に shares を売却、cash増加
    holdings: dict[str, dict] = {}  # ticker -> {shares, entry_price}
    cash = INITIAL_CAPITAL
    events_by_date: dict = {}

    for _, t in trades.iterrows():
        # BUY
        ed = t["entry_date"]
        if pd.notna(ed):
            key = ed
            cost = t["shares"] * t["entry_price"]
            cash -= cost
            ticker = t["ticker"]
            if ticker not in holdings:
                holdings[ticker] = {"shares": 0, "entry_price": 0}
            prev = holdings[ticker]
            total_shares = prev["shares"] + t["shares"]
            if total_shares > 0:
                holdings[ticker] = {
                    "shares": total_shares,
                    "entry_price": (
                        prev["entry_price"] * prev["shares"]
                        + t["entry_price"] * t["shares"]
                    )
                    / total_shares,
                }
            events_by_date.setdefault(key, []).append(
                f"BUY {ticker} {int(t['shares'])}株 @${t['entry_price']:.2f}"
            )

    # CLOSEDトレードのexit処理をまとめて記録
    sell_events: list[tuple] = []
    for _, t in trades[trades["status"] == "CLOSED"].iterrows():
        if pd.notna(t["exit_date"]):
            sell_events.append(
                (
                    t["exit_date"],
                    t["ticker"],
                    t["shares"],
                    t["exit_price"],
                    t["profit_loss"] or 0,
                )
            )

    # --- 保有ティッカーの価格を取得 ---
    all_tickers = list(set(trades["ticker"].tolist()))
    # yfinanceで一括取得
    price_data = {}
    if all_tickers:
        try:
            raw = yf.download(
                all_tickers,
                start=first_date - timedelta(days=5),
                end=today + timedelta(days=1),
                progress=False,
                auto_adjust=True,
            )
            if len(all_tickers) == 1:
                # 単一ティッカーの場合、columnsにティッカー名がない
                price_data[all_tickers[0]] = raw["Close"]
            elif "Close" in raw.columns.get_level_values(0):
                for ticker in all_tickers:
                    if ticker in raw["Close"].columns:
                        price_data[ticker] = raw["Close"][ticker]
        except Exception as e:
            logger.warning(f"価格データ取得エラー: {e}")

    # --- 日次ポートフォリオ計算 ---
    rows = []
    current_holdings: dict[str, dict] = {}  # ticker -> {shares, entry_price}
    current_cash = INITIAL_CAPITAL
    prev_total = INITIAL_CAPITAL

    for date in date_range:
        day_events = []

        # この日のBUY処理
        buys_today = trades[trades["entry_date"] == date]
        for _, t in buys_today.iterrows():
            ticker = t["ticker"]
            cost = t["shares"] * t["entry_price"]
            current_cash -= cost
            if ticker not in current_holdings:
                current_holdings[ticker] = {"shares": 0, "entry_price": 0}
            prev = current_holdings[ticker]
            new_shares = prev["shares"] + t["shares"]
            if new_shares > 0:
                current_holdings[ticker] = {
                    "shares": new_shares,
                    "entry_price": (
                        prev["entry_price"] * prev["shares"]
                        + t["entry_price"] * t["shares"]
                    )
                    / new_shares,
                }
            day_events.append(
                f"BUY {ticker} {int(t['shares'])}株 @${t['entry_price']:.2f}"
            )

        # この日のSELL処理
        for sell_date, ticker, shares, exit_price, pnl in sell_events:
            if sell_date == date:
                proceeds = shares * exit_price
                current_cash += proceeds
                if ticker in current_holdings:
                    current_holdings[ticker]["shares"] -= shares
                    if current_holdings[ticker]["shares"] <= 0:
                        del current_holdings[ticker]
                day_events.append(
                    f"SELL {ticker} {int(shares)}株 @${exit_price:.2f} "
                    f"({'+'if pnl>=0 else ''}${pnl:,.0f})"
                )

        # 株式評価額
        equity = 0.0
        for ticker, info in current_holdings.items():
            if info["shares"] > 0:
                if ticker in price_data:
                    series = price_data[ticker]
                    # その日以前の最新価格
                    available = series[series.index <= date].dropna()
                    if len(available) > 0:
                        price = float(available.iloc[-1])
                    else:
                        price = info["entry_price"]
                else:
                    price = info["entry_price"]
                equity += info["shares"] * price

        total = current_cash + equity
        daily_change = total - prev_total
        daily_change_pct = (daily_change / prev_total * 100) if prev_total > 0 else 0

        rows.append(
            {
                "date": date,
                "cash": round(current_cash, 2),
                "equity": round(equity, 2),
                "total": round(total, 2),
                "daily_change": round(daily_change, 2),
                "daily_change_pct": round(daily_change_pct, 2),
                "events": " / ".join(day_events) if day_events else "",
            }
        )
        prev_total = total

    return pd.DataFrame(rows)


# ============================================================
# SPY ベンチマーク
# ============================================================


def get_spy_benchmark(start_date: str = PHASE3_START) -> pd.DataFrame:
    """SPYの日次推移を取得し、初期資本ベースに正規化する。

    Returns:
        DataFrame with columns: date, spy_total
        spy_total は INITIAL_CAPITAL を基準に正規化した値
    """
    sd = pd.Timestamp(start_date)
    today = pd.Timestamp.now().normalize()

    try:
        raw = yf.download(
            "SPY",
            start=sd - timedelta(days=5),
            end=today + timedelta(days=1),
            progress=False,
            auto_adjust=True,
        )
        if raw.empty:
            return pd.DataFrame()

        close = raw["Close"].dropna()
        if hasattr(close, "columns"):
            close = close.iloc[:, 0]

        # start_date 以降で最初の営業日を基準に正規化
        close_from_start = close[close.index >= sd]
        if len(close_from_start) == 0:
            return pd.DataFrame()

        base_price = float(close_from_start.iloc[0])
        normalized = close_from_start / base_price * INITIAL_CAPITAL

        df = pd.DataFrame({"date": normalized.index, "spy_total": normalized.values})
        df["date"] = df["date"].dt.normalize()
        return df
    except Exception:
        return pd.DataFrame()


# ============================================================
# システム最終実行
# ============================================================


def get_last_system_run() -> dict | None:
    """最新のシステム実行情報を1件返す"""
    with _connect() as conn:
        row = conn.execute(
            "SELECT started_at, status, errors_count, error_message "
            "FROM system_runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return {
            "started_at": row[0],
            "status": row[1],
            "errors_count": row[2] or 0,
            "error_message": row[3] or "",
        }


# ============================================================
# KPI
# ============================================================


def get_kpi_summary(start_date: str = PHASE3_START) -> dict:
    """Go/No-Go判定用KPIサマリ"""
    with _connect() as conn:
        trades_df = pd.read_sql_query(
            """
            SELECT ticker, action, entry_price, exit_price, shares, total_value,
                   profit_loss, profit_loss_pct, status, holding_days,
                   entry_timestamp, exit_timestamp, strategy_used, exit_reason
            FROM trades
            WHERE entry_timestamp >= ? AND status = 'CLOSED'
            ORDER BY entry_timestamp
            """,
            conn,
            params=[start_date],
        )

        # 勝率
        total = len(trades_df)
        wins = len(trades_df[trades_df["profit_loss"] > 0]) if total > 0 else 0
        win_rate = (wins / total * 100) if total > 0 else 0.0

        # 年間リターン（年率換算）
        total_pnl = trades_df["profit_loss"].sum() if total > 0 else 0.0
        initial_capital = 100000.0  # ペーパートレード初期資本
        days_running = max(
            (datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")).days, 1
        )
        actual_return_pct = (total_pnl / initial_capital) * 100
        annual_return = actual_return_pct * (365 / days_running)

        # 最大ドローダウン
        max_drawdown = _calc_max_drawdown(conn, start_date, trades_df)

        # 稼働率
        uptime = _calc_uptime(conn, start_date)

        # 残日数
        deadline = datetime.strptime(GONOGO_DEADLINE, "%Y-%m-%d")
        days_remaining = max((deadline - datetime.now()).days, 0)
        elapsed_days = max(
            (datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")).days, 1
        )
        total_days = max((deadline - datetime.strptime(start_date, "%Y-%m-%d")).days, 1)
        progress_pct = min(elapsed_days / total_days * 100, 100)

        return {
            "win_rate": round(win_rate, 1),
            "annual_return": round(annual_return, 1),
            "max_drawdown": round(max_drawdown, 1),
            "uptime": round(uptime, 1),
            "total_trades": total,
            "wins": wins,
            "losses": total - wins,
            "total_pnl": round(total_pnl, 2),
            "actual_return_pct": round(actual_return_pct, 2),
            "days_running": days_running,
            "days_remaining": days_remaining,
            "progress_pct": round(progress_pct, 1),
        }


def _calc_max_drawdown(
    conn: sqlite3.Connection, start_date: str, trades_df: pd.DataFrame
) -> float:
    """portfolio_snapshotsから最大ドローダウンを計算。データがなければトレードから推定"""
    snapshots = pd.read_sql_query(
        "SELECT timestamp, total_value FROM portfolio_snapshots "
        "WHERE timestamp >= ? ORDER BY timestamp",
        conn,
        params=[start_date],
    )
    if len(snapshots) >= 2:
        values = snapshots["total_value"].values
        peak = values[0]
        max_dd = 0.0
        for v in values:
            if v > peak:
                peak = v
            dd = (peak - v) / peak * 100 if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
        return max_dd

    # フォールバック: トレードの累積損益からDD推定
    if len(trades_df) == 0:
        return 0.0
    cumulative = trades_df["profit_loss"].cumsum()
    peak = cumulative.cummax()
    drawdown = peak - cumulative
    return float(drawdown.max() / max(peak.max(), 1) * 100) if peak.max() > 0 else 0.0


def get_go_nogo_verdict(kpi: dict) -> dict:
    """Go/No-Go判定ステータスと推奨アクションを返す"""
    targets = KPI_TARGETS
    checks = [
        kpi["win_rate"] >= targets["win_rate"],
        kpi["annual_return"] >= targets["annual_return"],
        kpi["max_drawdown"] <= targets["max_drawdown"],
        kpi["uptime"] >= targets["uptime"],
    ]
    passed = sum(checks)
    if passed == 4:
        status = "GO"
    elif passed >= 3:
        status = "CONDITIONAL_GO"
    else:
        status = "NO_GO"

    recommendations = []
    if kpi["win_rate"] < targets["win_rate"]:
        gap = targets["win_rate"] - kpi["win_rate"]
        recommendations.append(f"勝率: あと{gap:.1f}pp改善が必要")
    if kpi["annual_return"] < targets["annual_return"]:
        gap = targets["annual_return"] - kpi["annual_return"]
        recommendations.append(f"リターン: あと{gap:.1f}%改善が必要")
    if kpi["max_drawdown"] > targets["max_drawdown"]:
        gap = kpi["max_drawdown"] - targets["max_drawdown"]
        recommendations.append(f"DD: {gap:.1f}%削減が必要")
    if kpi["uptime"] < targets["uptime"]:
        recommendations.append("稼働率: システム安定性の改善が必要")

    return {
        "status": status,
        "passed": passed,
        "total": 4,
        "recommendations": recommendations,
    }


def _calc_uptime(conn: sqlite3.Connection, start_date: str) -> float:
    """system_runsから稼働率を計算（直近7日間のローリングウィンドウ）

    Phase 3開始日からの全期間ではなく、直近7日の稼働率を使う。
    古い障害が長期間スコアを押し下げるのを防止。
    """
    runs = pd.read_sql_query(
        "SELECT status FROM system_runs WHERE started_at >= datetime('now', '-7 days')",
        conn,
    )
    if len(runs) == 0:
        # 直近7日に実行なし → 稼働率0%
        return 0.0
    completed = len(runs[runs["status"] == "completed"])
    return completed / len(runs) * 100


# ============================================================
# ポートフォリオ
# ============================================================


def get_positions() -> pd.DataFrame:
    """現在のペーパートレードポジション"""
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT ticker, side, shares, entry_price, current_price,
                   stop_loss_price, take_profit_price,
                   unrealized_pnl, unrealized_pnl_pct,
                   entry_timestamp, last_updated
            FROM positions
            WHERE shares > 0
            ORDER BY entry_timestamp
            """,
            conn,
        )
        return df


def get_manual_holdings() -> list[dict]:
    """my_holdings.jsonの手動保有"""
    try:
        with open(HOLDINGS_CONFIG) as f:
            data = json.load(f)
        return data.get("holdings", [])
    except Exception:
        return []


# ============================================================
# Alpaca API 直接参照（Source of Truth）
# ============================================================


def _get_alpaca_client():
    """Alpaca TradingClient を取得（シングルトン的にキャッシュ）"""
    try:
        from alpaca.trading.client import TradingClient

        key = os.getenv("ALPACA_API_KEY")
        secret = os.getenv("ALPACA_SECRET_KEY")
        base_url = os.getenv("ALPACA_BASE_URL", "")
        if not key or not secret:
            return None
        is_paper = "paper" in base_url.lower()
        return TradingClient(api_key=key, secret_key=secret, paper=is_paper)
    except Exception as e:
        logger.warning(f"Alpaca client init failed: {e}")
        return None


def get_alpaca_portfolio() -> dict | None:
    """Alpaca APIからリアルタイムのポートフォリオ情報を取得。

    Returns:
        dict with keys: portfolio_value, cash, equity, buying_power
        or None if API is unavailable
    """
    client = _get_alpaca_client()
    if client is None:
        return None
    try:
        account = client.get_account()
        return {
            "portfolio_value": float(account.portfolio_value),
            "cash": float(account.cash),
            "equity": float(account.equity),
            "buying_power": float(account.buying_power),
        }
    except Exception as e:
        logger.warning(f"Alpaca account fetch failed: {e}")
        return None


def get_alpaca_positions() -> list[dict]:
    """Alpaca APIからリアルタイムのポジション情報を取得。

    Returns:
        list of dicts with keys: ticker, shares, entry_price, current_price,
        market_value, unrealized_pnl, unrealized_pnl_pct
    """
    client = _get_alpaca_client()
    if client is None:
        return []
    try:
        positions = client.get_all_positions()
        result = []
        for p in positions:
            result.append(
                {
                    "ticker": p.symbol,
                    "shares": int(float(p.qty)),
                    "entry_price": float(p.avg_entry_price),
                    "current_price": float(p.current_price),
                    "market_value": float(p.market_value),
                    "unrealized_pnl": float(p.unrealized_pl),
                    "unrealized_pnl_pct": float(p.unrealized_plpc) * 100,
                }
            )
        return result
    except Exception as e:
        logger.warning(f"Alpaca positions fetch failed: {e}")
        return []


def get_open_positions_from_trades() -> list[dict]:
    """tradesテーブルからOPENポジションを再構築（Alpaca API不可時のフォールバック）。"""
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT ticker, entry_price, shares
            FROM trades
            WHERE status = 'OPEN' AND action = 'BUY'
            """,
            conn,
        )
    if len(df) == 0:
        return []
    result = []
    for _, row in df.iterrows():
        ticker = row["ticker"]
        entry = float(row["entry_price"])
        shares = int(row["shares"])
        try:
            tk = yf.Ticker(ticker)
            hist = tk.history(period="1d")
            current = float(hist["Close"].iloc[-1]) if len(hist) > 0 else entry
        except Exception:
            current = entry
        pnl = (current - entry) * shares
        pnl_pct = ((current / entry) - 1) * 100 if entry > 0 else 0
        result.append(
            {
                "ticker": ticker,
                "shares": shares,
                "entry_price": entry,
                "current_price": current,
                "market_value": current * shares,
                "unrealized_pnl": pnl,
                "unrealized_pnl_pct": pnl_pct,
            }
        )
    return result


def get_portfolio_snapshots(start_date: str = PHASE3_START) -> pd.DataFrame:
    """ポートフォリオスナップショット時系列"""
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT timestamp, total_value, cash_balance, equity_value
            FROM portfolio_snapshots
            WHERE timestamp >= ?
            ORDER BY timestamp
            """,
            conn,
            params=[start_date],
        )
        if len(df) > 0:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df


# ============================================================
# トレード分析
# ============================================================


def get_trades(start_date: str = PHASE3_START) -> pd.DataFrame:
    """全トレード（OPEN + CLOSED）"""
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT t.id, t.trade_id, t.ticker, t.action,
                   t.entry_price, t.exit_price, t.shares, t.total_value,
                   t.profit_loss, t.profit_loss_pct, t.status,
                   t.holding_days, t.entry_timestamp, t.exit_timestamp,
                   t.strategy_used, t.exit_reason, t.engine,
                   s.confidence, s.conviction, s.reasoning
            FROM trades t
            LEFT JOIN signals s ON t.signal_id = s.id
            WHERE t.entry_timestamp >= ?
            ORDER BY t.entry_timestamp DESC
            """,
            conn,
            params=[start_date],
        )
        return df


def get_trade_summary(trades_df: pd.DataFrame) -> dict:
    """トレードサマリ統計"""
    closed = trades_df[trades_df["status"] == "CLOSED"]
    if len(closed) == 0:
        return {
            "total": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "avg_profit_pct": 0.0,
            "avg_loss_pct": 0.0,
            "largest_win_pct": 0.0,
            "largest_loss_pct": 0.0,
            "avg_holding_days": 0.0,
            "total_pnl": 0.0,
        }

    winners = closed[closed["profit_loss"] > 0]
    losers = closed[closed["profit_loss"] <= 0]
    total_profit = winners["profit_loss"].sum() if len(winners) > 0 else 0.0
    total_loss = abs(losers["profit_loss"].sum()) if len(losers) > 0 else 0.0

    return {
        "total": len(closed),
        "wins": len(winners),
        "losses": len(losers),
        "win_rate": round(len(winners) / len(closed) * 100, 1),
        "profit_factor": (
            round(total_profit / total_loss, 2) if total_loss > 0 else 99.99
        ),
        "avg_profit_pct": (
            round(winners["profit_loss_pct"].mean(), 2) if len(winners) > 0 else 0.0
        ),
        "avg_loss_pct": (
            round(losers["profit_loss_pct"].mean(), 2) if len(losers) > 0 else 0.0
        ),
        "largest_win_pct": round(closed["profit_loss_pct"].max(), 2),
        "largest_loss_pct": round(closed["profit_loss_pct"].min(), 2),
        "avg_holding_days": round(
            (
                closed["holding_days"].mean()
                if closed["holding_days"].notna().any()
                else 0
            ),
            1,
        ),
        "total_pnl": round(closed["profit_loss"].sum(), 2),
    }


def get_trade_patterns(trades_df: pd.DataFrame) -> dict:
    """テーマ別・戦略別・確信度別・曜日別のパターン分析"""
    closed = trades_df[trades_df["status"] == "CLOSED"].copy()
    if len(closed) == 0:
        return {
            "by_theme": {},
            "by_strategy": {},
            "by_conviction": {},
            "by_weekday": {},
        }

    theme_map = _build_ticker_theme_map()
    closed["theme"] = closed["ticker"].map(theme_map).fillna("Unknown")

    # テーマ別
    by_theme = {}
    for theme, grp in closed.groupby("theme"):
        wins = len(grp[grp["profit_loss"] > 0])
        by_theme[theme] = {
            "trades": len(grp),
            "win_rate": round(wins / len(grp) * 100, 1),
            "avg_return": round(grp["profit_loss_pct"].mean(), 2),
            "total_pnl": round(grp["profit_loss"].sum(), 2),
        }

    # 戦略別
    by_strategy = {}
    for strategy, grp in closed.groupby("strategy_used"):
        if pd.isna(strategy):
            strategy = "N/A"
        wins = len(grp[grp["profit_loss"] > 0])
        by_strategy[strategy] = {
            "trades": len(grp),
            "win_rate": round(wins / len(grp) * 100, 1),
            "avg_return": round(grp["profit_loss_pct"].mean(), 2),
            "total_pnl": round(grp["profit_loss"].sum(), 2),
        }

    # 確信度(Conviction)別
    by_conviction = {}
    conv_col = closed["conviction"].dropna()
    if len(conv_col) > 0:
        for conv, grp in closed.dropna(subset=["conviction"]).groupby("conviction"):
            wins = len(grp[grp["profit_loss"] > 0])
            by_conviction[int(conv)] = {
                "trades": len(grp),
                "win_rate": round(wins / len(grp) * 100, 1),
                "avg_return": round(grp["profit_loss_pct"].mean(), 2),
            }

    # 曜日別
    by_weekday = {}
    closed["entry_timestamp"] = pd.to_datetime(closed["entry_timestamp"])
    closed["weekday"] = closed["entry_timestamp"].dt.day_name()
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for wd in weekday_order:
        grp = closed[closed["weekday"] == wd]
        if len(grp) > 0:
            wins = len(grp[grp["profit_loss"] > 0])
            by_weekday[wd] = {
                "trades": len(grp),
                "win_rate": round(wins / len(grp) * 100, 1),
                "avg_return": round(grp["profit_loss_pct"].mean(), 2),
            }

    return {
        "by_theme": by_theme,
        "by_strategy": by_strategy,
        "by_conviction": by_conviction,
        "by_weekday": by_weekday,
    }


# ============================================================
# シグナル分析
# ============================================================


def get_signals(start_date: str = PHASE3_START) -> pd.DataFrame:
    """全シグナル"""
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT id, signal_id, ticker, signal_type, detected_at, price,
                   rsi, macd, ma200_position, volume_ratio,
                   confidence, conviction, target_price, stop_loss,
                   status, reasoning, decision_factors_json
            FROM signals
            WHERE detected_at >= ?
            ORDER BY detected_at DESC
            """,
            conn,
            params=[start_date],
        )
        return df


def get_signal_funnel(start_date: str = PHASE3_START) -> dict:
    """シグナルファネル（生成→執行→結果）"""
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM signals WHERE detected_at >= ?", (start_date,)
        ).fetchone()
        total = row[0] if row else 0

        status_counts = {}
        for r in conn.execute(
            "SELECT status, COUNT(*) FROM signals WHERE detected_at >= ? GROUP BY status",
            (start_date,),
        ).fetchall():
            status_counts[r[0]] = r[1]

        executed = status_counts.get("executed", 0)
        pending = status_counts.get("pending", 0)
        expired = status_counts.get("expired", 0)
        cancelled = status_counts.get("cancelled", 0)

        # 実行されたシグナルの勝敗
        tracking = pd.read_sql_query(
            "SELECT outcome, COUNT(*) as cnt FROM signal_tracking "
            "WHERE outcome IN ('WIN','LOSS') GROUP BY outcome",
            conn,
        )
        wins = 0
        losses = 0
        for _, r in tracking.iterrows():
            if r["outcome"] == "WIN":
                wins = r["cnt"]
            elif r["outcome"] == "LOSS":
                losses = r["cnt"]

        return {
            "total": total,
            "executed": executed,
            "pending": pending,
            "expired": expired,
            "cancelled": cancelled,
            "wins": wins,
            "losses": losses,
            "execution_rate": round(executed / total * 100, 1) if total > 0 else 0,
        }


def get_signal_tracking() -> pd.DataFrame:
    """シグナルトラッキング（成績追跡）"""
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT ticker, strategy_type, tier, conviction,
                   signal_price, target_price, stop_loss,
                   outcome, exit_price, return_pct,
                   holding_days, max_drawdown_pct, max_gain_pct,
                   signal_timestamp
            FROM signal_tracking
            ORDER BY signal_timestamp DESC
            """,
            conn,
        )
        return df


# ============================================================
# システムヘルス
# ============================================================


def get_system_runs(days: int = 30) -> pd.DataFrame:
    """直近N日のシステム実行履歴"""
    with _connect() as conn:
        df = pd.read_sql_query(
            f"""
            SELECT run_id, run_mode, environment, started_at, ended_at,
                   status, signals_detected, trades_executed,
                   news_collected, errors_count, error_message, host_name
            FROM system_runs
            WHERE started_at >= datetime('now', '-{days} days')
            ORDER BY started_at DESC
            """,
            conn,
        )
        if len(df) > 0:
            df["started_at"] = pd.to_datetime(df["started_at"], format="ISO8601")
            if "ended_at" in df.columns:
                df["ended_at"] = pd.to_datetime(
                    df["ended_at"], format="ISO8601", errors="coerce"
                )
                df["duration_min"] = (
                    (df["ended_at"] - df["started_at"]).dt.total_seconds() / 60
                ).round(1)
        return df


def get_system_health_summary(runs_df: pd.DataFrame) -> dict:
    """システムヘルスサマリ"""
    if len(runs_df) == 0:
        return {
            "total_runs": 0,
            "completed": 0,
            "failed": 0,
            "interrupted": 0,
            "success_rate": 0.0,
            "avg_duration_min": 0.0,
            "total_errors": 0,
            "total_signals": 0,
            "total_trades_executed": 0,
        }

    completed = len(runs_df[runs_df["status"] == "completed"])
    failed = len(runs_df[runs_df["status"] == "failed"])
    interrupted = len(runs_df[runs_df["status"] == "interrupted"])

    return {
        "total_runs": len(runs_df),
        "completed": completed,
        "failed": failed,
        "interrupted": interrupted,
        "success_rate": round(completed / len(runs_df) * 100, 1),
        "avg_duration_min": (
            round(runs_df["duration_min"].mean(), 1)
            if "duration_min" in runs_df.columns
            and runs_df["duration_min"].notna().any()
            else 0.0
        ),
        "total_errors": int(runs_df["errors_count"].sum() or 0),
        "total_signals": int(runs_df["signals_detected"].sum() or 0),
        "total_trades_executed": int(runs_df["trades_executed"].sum() or 0),
    }


# ============================================================
# System Operations タブ用
# ============================================================


def get_todays_pipeline_status() -> dict:
    """今日のパイプライン各ステップの状態を返す。"""
    today = datetime.now().strftime("%Y-%m-%d")
    with _connect() as conn:
        cur = conn.cursor()

        # system_runs today
        cur.execute(
            "SELECT run_mode, status, started_at, ended_at, "
            "news_collected, signals_detected, trades_executed, errors_count "
            "FROM system_runs WHERE date(started_at) = ? ORDER BY started_at",
            (today,),
        )
        runs_today = [dict(r) for r in cur.fetchall()]

        # news today (use created_at since published_at may be older)
        cur.execute(
            "SELECT COUNT(*) as cnt, MAX(created_at) as last_at "
            "FROM news WHERE date(created_at) = ?",
            (today,),
        )
        news_row = dict(cur.fetchone())

        # ai_analysis today
        cur.execute(
            "SELECT COUNT(*) as cnt, MAX(analyzed_at) as last_at "
            "FROM ai_analysis WHERE date(analyzed_at) = ?",
            (today,),
        )
        analysis_row = dict(cur.fetchone())

        # signals today
        cur.execute(
            "SELECT signal_type, status, COUNT(*) as cnt "
            "FROM signals WHERE date(detected_at) = ? "
            "GROUP BY signal_type, status",
            (today,),
        )
        sig_rows = [dict(r) for r in cur.fetchall()]
        cur.execute(
            "SELECT MAX(detected_at) as last_at FROM signals WHERE date(detected_at) = ?",
            (today,),
        )
        sig_last = dict(cur.fetchone())

        sig_total = sum(r["cnt"] for r in sig_rows)
        sig_buy = sum(r["cnt"] for r in sig_rows if r["signal_type"] == "BUY")
        sig_sell = sum(r["cnt"] for r in sig_rows if r["signal_type"] == "SELL")

        # trades today
        cur.execute(
            "SELECT action, COUNT(*) as cnt "
            "FROM trades WHERE date(entry_timestamp) = ? OR date(exit_timestamp) = ? "
            "GROUP BY action",
            (today, today),
        )
        trade_rows = [dict(r) for r in cur.fetchall()]
        cur.execute(
            "SELECT MAX(COALESCE(exit_timestamp, entry_timestamp)) as last_at "
            "FROM trades WHERE date(entry_timestamp) = ? OR date(exit_timestamp) = ?",
            (today, today),
        )
        trade_last = dict(cur.fetchone())
        trade_total = sum(r["cnt"] for r in trade_rows)

        # portfolio snapshots today
        cur.execute(
            "SELECT COUNT(*) as cnt, MAX(timestamp) as last_at "
            "FROM portfolio_snapshots WHERE date(timestamp) = ?",
            (today,),
        )
        snap_row = dict(cur.fetchone())

        total_errors = sum(r.get("errors_count", 0) or 0 for r in runs_today)
        has_full_run = any(r["run_mode"] == "full" for r in runs_today)

        def _time_part(ts):
            if ts and len(ts) >= 16:
                return ts[11:16]
            return ""

        def _step_status(count, has_run):
            if count > 0:
                return "completed"
            if has_run:
                return "skipped"
            return "pending"

        return {
            "date": today,
            "steps": {
                "news": {
                    "status": _step_status(news_row["cnt"] or 0, has_full_run),
                    "count": news_row["cnt"] or 0,
                    "last_at": _time_part(news_row["last_at"]),
                },
                "analysis": {
                    "status": _step_status(analysis_row["cnt"] or 0, has_full_run),
                    "count": analysis_row["cnt"] or 0,
                    "last_at": _time_part(analysis_row["last_at"]),
                },
                "signals": {
                    "status": _step_status(sig_total, len(runs_today) > 0),
                    "count": sig_total,
                    "buy": sig_buy,
                    "sell": sig_sell,
                    "last_at": _time_part(sig_last.get("last_at")),
                },
                "trading": {
                    "status": _step_status(trade_total, len(runs_today) > 0),
                    "count": trade_total,
                    "last_at": _time_part(trade_last.get("last_at")),
                },
                "portfolio": {
                    "status": _step_status(snap_row["cnt"] or 0, len(runs_today) > 0),
                    "count": snap_row["cnt"] or 0,
                    "last_at": _time_part(snap_row["last_at"]),
                },
            },
            "runs_today": runs_today,
            "total_errors": total_errors,
        }


def get_recent_runs_timeline(days: int = 14) -> pd.DataFrame:
    """日次集計のラン履歴を返す。"""
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT date(started_at) as run_date,
                   COUNT(*) as total_runs,
                   SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
                   SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed,
                   SUM(CASE WHEN status='interrupted' THEN 1 ELSE 0 END) as interrupted,
                   GROUP_CONCAT(DISTINCT run_mode) as modes,
                   SUM(signals_detected) as total_signals,
                   SUM(trades_executed) as total_trades,
                   SUM(errors_count) as total_errors,
                   MIN(started_at) as first_run,
                   MAX(ended_at) as last_run
            FROM system_runs
            WHERE started_at >= datetime('now', :offset)
            GROUP BY date(started_at)
            ORDER BY run_date DESC
            """,
            conn,
            params={"offset": f"-{days} days"},
        )
        return df


def get_pipeline_health_metrics(days: int = 7) -> dict:
    """パイプラインヘルス指標を返す。"""
    with _connect() as conn:
        cur = conn.cursor()
        offset = f"-{days} days"

        # news
        cur.execute(
            "SELECT COUNT(*) as cnt, COUNT(DISTINCT date(created_at)) as days "
            "FROM news WHERE created_at >= datetime('now', ?)",
            (offset,),
        )
        news = dict(cur.fetchone())

        # ai_analysis
        cur.execute(
            "SELECT COUNT(*) as cnt, COUNT(DISTINCT date(analyzed_at)) as days "
            "FROM ai_analysis WHERE analyzed_at >= datetime('now', ?)",
            (offset,),
        )
        analysis = dict(cur.fetchone())

        # signals
        cur.execute(
            "SELECT COUNT(*) as cnt, COUNT(DISTINCT date(detected_at)) as days "
            "FROM signals WHERE detected_at >= datetime('now', ?)",
            (offset,),
        )
        sigs = dict(cur.fetchone())

        # trades
        cur.execute(
            "SELECT COUNT(*) as cnt, COUNT(DISTINCT date(entry_timestamp)) as days "
            "FROM trades WHERE entry_timestamp >= datetime('now', ?)",
            (offset,),
        )
        trd = dict(cur.fetchone())

        # system_runs
        cur.execute(
            "SELECT COUNT(*) as total, "
            "SUM(errors_count) as errors, "
            "SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed, "
            "COUNT(DISTINCT date(started_at)) as run_days "
            "FROM system_runs WHERE started_at >= datetime('now', ?)",
            (offset,),
        )
        runs = dict(cur.fetchone())

        total_runs = runs["total"] or 0
        total_errors = runs["errors"] or 0
        completed = runs["completed"] or 0
        run_days = runs["run_days"] or 0

        return {
            "news_per_day": round((news["cnt"] or 0) / max(days, 1), 1),
            "analysis_per_day": round((analysis["cnt"] or 0) / max(days, 1), 1),
            "signals_per_day": round((sigs["cnt"] or 0) / max(days, 1), 1),
            "trades_per_day": round((trd["cnt"] or 0) / max(days, 1), 1),
            "error_rate": round(total_errors / max(total_runs, 1) * 100, 1),
            "uptime_pct": round(completed / max(total_runs, 1) * 100, 1),
            "coverage_pct": round(run_days / max(days, 1) * 100, 1),
        }


def get_todays_news(limit: int = 30) -> pd.DataFrame:
    """今日収集したニュース一覧。"""
    today = datetime.now().strftime("%Y-%m-%d")
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT n.title, n.content, n.source, n.url,
                   n.published_at, n.sentiment_score,
                   n.quality_score, n.importance,
                   n.theme, n.tickers_json
            FROM news n
            WHERE date(n.created_at) = ?
            ORDER BY n.created_at DESC LIMIT ?
            """,
            conn,
            params=(today, limit),
        )
        return df


def get_todays_signals() -> pd.DataFrame:
    """今日検出したシグナル一覧。"""
    today = datetime.now().strftime("%Y-%m-%d")
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT ticker, signal_type, detected_at, price,
                   rsi, macd, confidence, conviction,
                   target_price, stop_loss, status, reasoning,
                   decision_factors_json
            FROM signals
            WHERE date(detected_at) = ?
            ORDER BY detected_at DESC
            """,
            conn,
            params=(today,),
        )
        return df


def get_todays_trades() -> pd.DataFrame:
    """今日の取引一覧。"""
    today = datetime.now().strftime("%Y-%m-%d")
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT ticker, action, entry_price, exit_price, shares,
                   profit_loss, profit_loss_pct, holding_days, status,
                   entry_timestamp, exit_timestamp, exit_reason
            FROM trades
            WHERE date(entry_timestamp) = ? OR date(exit_timestamp) = ?
            ORDER BY entry_timestamp DESC
            """,
            conn,
            params=(today, today),
        )
        return df


def get_todays_analyses(limit: int = 50) -> pd.DataFrame:
    """今日のAI分析結果一覧。"""
    today = datetime.now().strftime("%Y-%m-%d")
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT theme, ticker, analysis_type, score, direction,
                   summary, detailed_analysis, key_points_json,
                   recommendation, tickers_analyzed_json,
                   news_count, model_used, analyzed_at
            FROM ai_analysis
            WHERE date(analyzed_at) = ?
            ORDER BY analyzed_at DESC LIMIT ?
            """,
            conn,
            params=(today, limit),
        )
        return df


# ============================================================
# ニュース活用・分析可視化
# ============================================================


def get_news_collection_trend(days: int = 14) -> pd.DataFrame:
    """日別のニュース収集件数・ソース数を返す。"""
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT date(created_at) as collect_date,
                   COUNT(*) as article_count,
                   COUNT(DISTINCT source) as source_count
            FROM news
            WHERE created_at >= datetime('now', ? || ' days')
            GROUP BY date(created_at)
            ORDER BY collect_date
            """,
            conn,
            params=(f"-{days}",),
        )
        return df


def get_news_source_breakdown(days: int = 14) -> pd.DataFrame:
    """直近N日のニュースソース別件数。"""
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT source, COUNT(*) as cnt
            FROM news
            WHERE created_at >= datetime('now', ? || ' days')
            GROUP BY source
            ORDER BY cnt DESC
            LIMIT 10
            """,
            conn,
            params=(f"-{days}",),
        )
        return df


def get_news_ticker_coverage(days: int = 14) -> pd.DataFrame:
    """直近N日でニュースが紐付いたティッカー別件数。"""
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT tickers_json, COUNT(*) as cnt
            FROM news
            WHERE created_at >= datetime('now', ? || ' days')
              AND tickers_json IS NOT NULL
              AND tickers_json != ''
              AND tickers_json != '[]'
            GROUP BY tickers_json
            ORDER BY cnt DESC
            """,
            conn,
            params=(f"-{days}",),
        )
        # tickers_json を展開してティッカー別に集計
        ticker_counts: dict[str, int] = {}
        for _, row in df.iterrows():
            try:
                tickers = json.loads(row["tickers_json"])
                for t in tickers:
                    ticker_counts[t] = ticker_counts.get(t, 0) + int(row["cnt"])
            except Exception:
                pass
        result = pd.DataFrame(
            sorted(ticker_counts.items(), key=lambda x: -x[1]),
            columns=["ticker", "article_count"],
        )
        return result


def get_analysis_trend(days: int = 14) -> pd.DataFrame:
    """日別のAI分析件数・平均スコア・方向性。"""
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT date(analyzed_at) as analysis_date,
                   COUNT(*) as total,
                   ROUND(AVG(score), 1) as avg_score,
                   SUM(CASE WHEN direction='bullish' THEN 1 ELSE 0 END) as bullish,
                   SUM(CASE WHEN direction='bearish' THEN 1 ELSE 0 END) as bearish,
                   SUM(CASE WHEN direction='neutral' THEN 1 ELSE 0 END) as neutral,
                   COUNT(DISTINCT theme) as themes_covered
            FROM ai_analysis
            WHERE analyzed_at >= datetime('now', ? || ' days')
            GROUP BY date(analyzed_at)
            ORDER BY analysis_date
            """,
            conn,
            params=(f"-{days}",),
        )
        return df


def get_analysis_theme_scores(days: int = 7) -> pd.DataFrame:
    """直近のテーマ別最新スコア・方向性。"""
    with _connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT theme, score, direction, recommendation,
                   news_count, analyzed_at
            FROM ai_analysis
            WHERE analyzed_at >= datetime('now', ? || ' days')
              AND analysis_type = 'theme_report'
            ORDER BY analyzed_at DESC
            """,
            conn,
            params=(f"-{days}",),
        )
        # テーマごとに最新1件のみ
        if len(df) > 0:
            df = df.drop_duplicates(subset=["theme"], keep="first")
        return df


def get_news_signal_connection(days: int = 14) -> dict:
    """ニュース→分析→シグナルの接続状況を集計。"""
    with _connect() as conn:
        # 日別: ニュース件数、分析件数、シグナル件数
        flow = pd.read_sql_query(
            """
            SELECT d.dt as date,
                   COALESCE(n.news_cnt, 0) as news,
                   COALESCE(a.analysis_cnt, 0) as analysis,
                   COALESCE(s.signal_cnt, 0) as signals
            FROM (
                SELECT DISTINCT date(created_at) as dt FROM news
                WHERE created_at >= datetime('now', ? || ' days')
                UNION
                SELECT DISTINCT date(analyzed_at) FROM ai_analysis
                WHERE analyzed_at >= datetime('now', ? || ' days')
                UNION
                SELECT DISTINCT date(detected_at) FROM signals
                WHERE detected_at >= datetime('now', ? || ' days')
            ) d
            LEFT JOIN (
                SELECT date(created_at) as dt, COUNT(*) as news_cnt
                FROM news WHERE created_at >= datetime('now', ? || ' days')
                GROUP BY date(created_at)
            ) n ON d.dt = n.dt
            LEFT JOIN (
                SELECT date(analyzed_at) as dt, COUNT(*) as analysis_cnt
                FROM ai_analysis WHERE analyzed_at >= datetime('now', ? || ' days')
                GROUP BY date(analyzed_at)
            ) a ON d.dt = a.dt
            LEFT JOIN (
                SELECT date(detected_at) as dt, COUNT(*) as signal_cnt
                FROM signals WHERE detected_at >= datetime('now', ? || ' days')
                GROUP BY date(detected_at)
            ) s ON d.dt = s.dt
            ORDER BY d.dt
            """,
            conn,
            params=(f"-{days}",) * 6,
        )

        # シグナルのdecision_factorsにnews_scoreがあるか
        sig_with_news = pd.read_sql_query(
            """
            SELECT ticker, signal_type, conviction, decision_factors_json, detected_at
            FROM signals
            WHERE detected_at >= datetime('now', ? || ' days')
              AND decision_factors_json IS NOT NULL
              AND decision_factors_json != ''
            ORDER BY detected_at DESC
            """,
            conn,
            params=(f"-{days}",),
        )
        news_influenced = 0
        for _, row in sig_with_news.iterrows():
            try:
                factors = json.loads(row["decision_factors_json"])
                if factors.get("news_score") or factors.get("news_reason"):
                    news_influenced += 1
            except Exception:
                pass

        return {
            "flow_df": flow,
            "total_signals": len(sig_with_news),
            "news_influenced_signals": news_influenced,
        }
