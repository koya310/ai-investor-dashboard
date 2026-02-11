"""Reference — システム仕様リファレンス（詳細版）"""

from datetime import datetime

import dashboard_data as _dm
import streamlit as st

from components.shared import section_header, P, W, L


st.title("システム仕様")
st.caption(
    "AI Investor Phase 3 ペーパートレードの詳細仕様。"
    "KPI定義・判定ロジック・データ更新ルールを確認できます。"
)

with st.expander("このページの使い方", expanded=False):
    st.markdown(
        """
        1. `Go/No-Go KPI仕様` で評価基準と計算式を確認  
        2. `判定ロジック` で GO / 条件付き / NO_GO の条件を確認  
        3. `パイプライン詳細` で各ステップの入出力と失敗時挙動を確認  
        4. `データ更新・表示ルール` で数値の鮮度と出所を確認
        """
    )


# ── 概要 ──
section_header("運用スコープ", color=P)

ov1, ov2, ov3, ov4 = st.columns(4)
ov1.metric("Phase 3 開始日", _dm.PHASE3_START)
ov2.metric("判定期限", _dm.GONOGO_DEADLINE)
ov3.metric("初期資本", f"${_dm.INITIAL_CAPITAL:,.0f}")
ov4.metric("判定KPI数", "4項目")

st.caption(
    f"最終更新日時: {datetime.now().strftime('%Y-%m-%d %H:%M')} "
    "（表示はダッシュボード生成時点）"
)


# ── KPI仕様 ──
section_header("Go/No-Go KPI仕様", color="#f59e0b")

st.markdown(
    f"""
| KPI | 目標値 | 計算式（概要） | 主データソース |
|---|---:|---|---|
| 勝率 | **{_dm.KPI_TARGETS['win_rate']:.0f}%以上** | `利益取引数 / 決済済取引数 × 100` | `trades` |
| 年率リターン | **{_dm.KPI_TARGETS['annual_return']:.0f}%以上** | `実績収益率 × (365 / 運用日数)` | `trades` |
| 最大DD | **{_dm.KPI_TARGETS['max_drawdown']:.0f}%以下** | `ピーク比の最大下落率` | `portfolio_snapshots`（なければ`trades`推定） |
| 稼働率 | **{_dm.KPI_TARGETS['uptime']:.0f}%以上** | `completed runs / total runs × 100` | `system_runs` |
"""
)

with st.container(border=True):
    st.markdown(
        """
        **計算ロジック詳細**

        - 勝率: `status='CLOSED'` の取引のみ対象
        - 年率リターン: `total_pnl / 初期資本` を年換算
        - 最大DD: `portfolio_snapshots` が2点以上ある場合は実値、ない場合は累積損益から推定
        - 稼働率: 開始7日以内は全期間、8日目以降は直近7日ローリングで算出
        """
    )


# ── 判定ロジック ──
section_header("判定ロジック", color=W)

st.markdown(
    """
| ステータス | 条件 | 意味 |
|---|---|---|
| `GO` | 4/4達成 | 実取引移行可能 |
| `CONDITIONAL_GO` | 3/4達成 | 条件付きで継続可（不足1項目を重点改善） |
| `NO_GO` | 0〜2/4達成 | 実取引不可。改善優先 |
"""
)

with st.container(border=True):
    st.markdown(
        """
        **未達時の改善提案出力ルール**

        - 勝率未達: `あとX.Xpp改善が必要`
        - 年率リターン未達: `あとX.X%改善が必要`
        - 最大DD超過: `X.X%削減が必要`
        - 稼働率未達: `システム安定性の改善が必要`
        """
    )


# ── パイプライン詳細 ──
section_header("5ステップパイプライン詳細", color=P)

tab_news, tab_analysis, tab_signal, tab_trade, tab_portfolio = st.tabs(
    ["1. 情報収集", "2. AI分析", "3. 売買判断", "4. 注文執行", "5. 資産記録"]
)

with tab_news:
    st.markdown(
        """
        **入力**: 市場ニュースAPI・RSS  
        **出力**: `news` テーブル（件数・ソース・本文・作成時刻）  
        **失敗時**: 当日ステップは未完了扱い。後続の分析件数が減少
        """
    )

with tab_analysis:
    st.markdown(
        """
        **入力**: `news` と対象銘柄リスト  
        **出力**: `ai_analysis` テーブル（テーマ・方向性・スコア・要約）  
        **失敗時**: シグナル確信度に使う材料が減るため、判断精度が低下
        """
    )

with tab_signal:
    st.markdown(
        """
        **入力**: テクニカル指標 + AI分析結果  
        **出力**: `signals` テーブル（BUY/SELL、confidence、conviction、理由）  
        **失敗時**: 当日の新規シグナルが欠落
        """
    )

with tab_trade:
    st.markdown(
        """
        **入力**: `signals` とリスク制約  
        **出力**: `trades` テーブル（約定・価格・損益・保有日数）  
        **失敗時**: 約定記録なし、もしくは中断ステータスとして `system_runs` に記録
        """
    )

with tab_portfolio:
    st.markdown(
        """
        **入力**: 約定履歴・ポジション情報  
        **出力**: `portfolio_snapshots`（時点資産、現金、エクイティ）  
        **失敗時**: DD/KPIの精度低下（フォールバック計算に切替）
        """
    )


# ── 戦略仕様 ──
section_header("シグナル戦略仕様（要約）", color=W)

s1, s2, s3 = st.tabs(["押し目買い", "トレンド追従", "VIX逆張り"])

with s1:
    st.markdown(
        """
        - RSIが低位（過熱売り）  
        - 長期トレンド（MA200）を維持  
        - 出来高増加を伴う反発兆候を重視
        """
    )

with s2:
    st.markdown(
        """
        - MA50 > MA200 の上昇トレンド  
        - MACDの上向きクロス  
        - セクター相対強度がプラス
        """
    )

with s3:
    st.markdown(
        """
        - VIX上昇時の過度悲観を逆張りで活用  
        - 市場不安局面では確信度閾値を引き上げ  
        - 資金配分を保守化してエントリー
        """
    )


# ── リスク管理 ──
section_header("リスク管理仕様", color=L)

st.markdown(
    """
| 項目 | ルール | 意図 |
|---|---|---|
| ハードストップロス | -8% | 単一ポジションの下振れ抑制 |
| 最低リスクリワード | 1.5:1 以上 | 損益期待値の維持 |
| 1日最大買付件数 | 3件 | 過剰取引の抑制 |
| セクター集中制限 | 1件/セクター/日 | 同一テーマ集中リスク低減 |
| 決算ブラックアウト | 前後7日 | イベントギャップ回避 |
| 最低現金保有 | $5,000 | 追加入金なしでの運用継続性確保 |
"""
)


# ── データ更新・表示ルール ──
section_header("データ更新・表示ルール", color=P)

st.markdown(
    """
| 項目 | 更新頻度 | 備考 |
|---|---|---|
| Alpaca系（ポートフォリオ・ポジション） | 120秒TTL | 接続失敗時はトレード履歴推定にフォールバック |
| パイプライン状態 | 120秒TTL | 当日進捗を短周期で更新 |
| 日次資産推移・SPY比較 | 600秒TTL | 中長期推移のため更新間隔を長めに設定 |
| 運用品質集計 | 600秒TTL | 直近7日平均を使用 |
"""
)

with st.container(border=True):
    st.markdown(
        """
        **表示優先順位（ポートフォリオ）**

        1. Alpaca API実値（`portfolio_value`, `cash`）  
        2. フォールバック: 取引履歴 + 市場価格再構築値
        """
    )


# ── 画面別役割 ──
section_header("画面別の確認ポイント", color=W)

st.markdown(
    """
| 画面 | 目的 | 主な判断 |
|---|---|---|
| ポートフォリオ | Go/No-Go 判定と損益把握 | KPI未達項目を特定 |
| パイプライン | 当日処理の健全性把握 | どの工程で停止/欠落したか |
| 日付詳細 | 日次の原因追跡 | ニュース→分析→シグナル→取引の流れ検証 |
"""
)

