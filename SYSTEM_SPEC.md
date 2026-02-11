# AI Investor Dashboard - System Specification

## 1. Purpose
- This dashboard is for **Phase 3 paper trading** monitoring and Go/No-Go judgment.
- It consolidates:
  - KPI judgment status
  - daily operations health
  - date-level traceability from news to trade

## 2. Evaluation Window
- Phase 3 start: `2026-01-24`
- Go/No-Go deadline: `2026-02-28`
- Initial capital: `$100,000`

## 3. Go/No-Go KPI Definitions

| KPI | Target | Formula | Source |
|---|---:|---|---|
| Win Rate | `>= 55%` | `wins / closed_trades * 100` | `trades` |
| Annual Return | `>= 12%` | `actual_return_pct * (365 / days_running)` | `trades` |
| Max Drawdown | `<= 15%` | max decline from equity peak | `portfolio_snapshots` (fallback from trades) |
| Uptime | `>= 99%` | `completed_runs / total_runs * 100` | `system_runs` |

Notes:
- Annual return is an annualized value from current period return.
- Uptime uses full period when run history is 7 days or less; otherwise rolling 7 days.

## 4. Verdict Logic

| Status | Condition |
|---|---|
| `GO` | 4 / 4 KPIs passed |
| `CONDITIONAL_GO` | 3 / 4 KPIs passed |
| `NO_GO` | 0 - 2 / 4 KPIs passed |

Recommendation messages are generated for every failed KPI.

## 5. Pipeline Specification

| Step | Input | Output | Failure Impact |
|---|---|---|---|
| 1. News Collection | market news APIs / RSS | `news` table | downstream analysis volume drops |
| 2. AI Analysis | news + ticker universe | `ai_analysis` table | lower signal quality |
| 3. Signal Generation | technicals + AI analysis | `signals` table | no actionable signal for the day |
| 4. Order Execution | signals + risk rules | `trades` table | missing execution records |
| 5. Portfolio Snapshot | positions + trade history | `portfolio_snapshots` | KPI/DD precision fallback |

## 6. Strategy Summary

### Mean Reversion
- Oversold context (RSI low)
- Long-term trend maintained (above MA200)
- Volume confirmation

### Trend Following
- MA50 > MA200
- MACD momentum confirmation
- positive sector momentum

### VIX Contrarian
- entry in panic regimes (high VIX)
- stronger conviction threshold in high-volatility regimes
- conservative sizing under stress

## 7. Risk Controls

| Control | Rule |
|---|---|
| Hard Stop Loss | `-8%` |
| Minimum Risk/Reward | `>= 1.5:1` |
| Max New Buys / Day | `3` |
| Sector Concentration | max 1 new position per sector/day |
| Earnings Blackout | 7 days around earnings |
| Minimum Cash | `$5,000` |

## 8. Data Freshness and Caching

| Data | Cache TTL |
|---|---|
| Alpaca portfolio / positions | 120 sec |
| Pipeline status | 120 sec |
| Daily portfolio / SPY benchmark | 600 sec |
| Health metrics / timeline | 600 sec |

Portfolio display priority:
1. Alpaca realtime values
2. fallback estimation from trades + market price

## 9. Page Responsibilities

| Page | Responsibility |
|---|---|
| `pages/home.py` | verdict + KPI checklist + performance + trade history |
| `pages/pipeline.py` | today pipeline status + 7-day quality + operation calendar |
| `pages/date_detail.py` | date-level trace from news to execution |
| `pages/reference.py` | in-app detailed specification |
