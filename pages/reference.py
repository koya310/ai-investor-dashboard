"""Reference — システム仕様"""

import dashboard_data as _dm
import streamlit as st

from components.shared import L, P, W

# ── 目次 ──
st.markdown(
    '<div class="card" style="padding:0.8rem 1.2rem">'
    '<div style="font-size:0.78rem; font-weight:700; color:#0f172a; margin-bottom:0.4rem">目次</div>'
    '<div style="display:grid; grid-template-columns:1fr 1fr; gap:0.15rem 1.5rem; font-size:0.75rem; color:#2563eb">'
    "<div>1. システム概要・フェーズ</div>"
    "<div>2. 実行スケジュール</div>"
    "<div>3. 情報収集の仕組み</div>"
    "<div>4. AI（LLM）定性分析</div>"
    "<div>5. 売買判断の基準</div>"
    "<div>6. 注文執行・リスク管理</div>"
    "<div>7. ポートフォリオ構成</div>"
    "<div>8. 障害対応</div>"
    "<div>9. 通知・モニタリング</div>"
    "<div>10. 自己改善・制約事項</div>"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)

# ── 0. システム概要（常に表示） ──

st.markdown(
    '<div class="card">'
    '<div class="spec-title"><span class="spec-icon">&#127919;</span>AI Investor とは</div>'
    '<div style="padding:0.5rem 1rem; font-size:0.76rem; color:#475569; line-height:1.8">'
    "米国株式市場を対象とした<b>完全自動AI投資システム</b>です。"
    "ニュース収集からAI分析、売買判断、注文執行、資産記録までを人間の介入なしに24時間稼働します。<br>"
    "テクニカル指標（定量）とGoogle Gemini LLMによる定性分析を組み合わせ、"
    "3つの売買戦略で米国株115銘柄（15テーマ）を監視・取引します。"
    "</div>"
    '<div class="spec-grid">'
    '<div class="spec-row"><span class="spec-k">対象市場</span><span class="spec-v">米国株式（NYSE / NASDAQ）</span></div>'
    '<div class="spec-row"><span class="spec-k">取引種別</span><span class="spec-v">現物ロングのみ（空売り・オプション非対応）</span></div>'
    '<div class="spec-row"><span class="spec-k">取引時間</span><span class="spec-v">通常取引時間のみ（9:30-16:00 ET）</span></div>'
    '<div class="spec-row"><span class="spec-k">人的介入</span><span class="spec-v">0%（完全自動）</span></div>'
    '<div class="spec-row"><span class="spec-k">実行環境</span><span class="spec-v">GCP VM（e2-micro / us-central1-a）</span></div>'
    '<div class="spec-row"><span class="spec-k">データベース</span><span class="spec-v">SQLite（16テーブル / ニュース30日保持）</span></div>'
    '<div class="spec-row"><span class="spec-k">月額コスト</span><span class="spec-v">約¥5,000（API利用料）</span></div>'
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="card">'
    '<div class="spec-title"><span class="spec-icon">&#128200;</span>現在のフェーズと目標</div>'
    '<div style="padding:0.5rem 1rem; font-size:0.76rem; color:#475569; line-height:1.8">'
    "<b>Phase 3: ペーパートレード検証</b>（2026年1月24日〜）<br>"
    "Alpacaのペーパートレード環境で実際の市場データを使い、"
    "初期資本 $100,000 で完全自動運用を行い、実取引移行の可否を判定します。"
    "</div>"
    '<div class="spec-grid">'
    '<div class="spec-row"><span class="spec-k">初期資本</span><span class="spec-v">$100,000（ペーパー）</span></div>'
    f'<div class="spec-row"><span class="spec-k">Go/No-Go判定</span><span class="spec-v">{_dm.GONOGO_DEADLINE}</span></div>'
    "</div>"
    '<div style="padding:0.5rem 1rem 0.2rem">'
    '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">Go/No-Go 判定基準</div>'
    "</div>"
    '<div class="spec-grid">'
    '<div class="spec-row"><span class="spec-k">勝率</span><span class="spec-v">&ge; 55%（目標 60%）</span></div>'
    '<div class="spec-row"><span class="spec-k">累積リターン</span><span class="spec-v">&ge; +5%（3ヶ月間）</span></div>'
    '<div class="spec-row"><span class="spec-k">最大ドローダウン</span><span class="spec-v">&le; -15%</span></div>'
    '<div class="spec-row"><span class="spec-k">システム稼働率</span><span class="spec-v">&ge; 99%</span></div>'
    '<div class="spec-row"><span class="spec-k">注文成功率</span><span class="spec-v">&ge; 95%</span></div>'
    '<div class="spec-row"><span class="spec-k">人的介入率</span><span class="spec-v">0%</span></div>'
    "</div>"
    '<div class="spec-note">'
    "<b>Go:</b> 全基準達成 → Phase 4（実資金少額運用）に移行 / "
    "<b>条件付き:</b> 勝率55-60%＋改善傾向あり → Phase 3を3ヶ月延長 / "
    "<b>No-Go:</b> 勝率55%未満 or 重大問題 → Phase 2に差し戻し"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)

# ── 1. スケジュール ──

with st.expander("実行スケジュール", expanded=False):
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128339;</span>日次スケジュール（米国東部時間）</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">プレマーケット分析</span><span class="spec-v">09:00 ET（毎日）</span></div>'
        '<div class="spec-row"><span class="spec-k">シグナル検出</span><span class="spec-v">9:30〜15:30 ET / 30分毎</span></div>'
        '<div class="spec-row"><span class="spec-k">日次サマリー</span><span class="spec-v">16:30 ET（市場終了後）</span></div>'
        '<div class="spec-row"><span class="spec-k">ニュース収集</span><span class="spec-v">9:15〜15:15 ET / 1時間毎</span></div>'
        '<div class="spec-row"><span class="spec-k">経済データ更新</span><span class="spec-v">08:00 ET（FRED）</span></div>'
        '<div class="spec-row"><span class="spec-k">日次シグナル回数</span><span class="spec-v">13回/日</span></div>'
        "</div>"
        '<div class="spec-note">土日・祝日は自動スキップ。全ての時刻はサマータイムに自動対応。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#9881;</span>実行モード</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">定時分析（Full）</span><span class="spec-v">AI分析+ニュース+全指標</span></div>'
        '<div class="spec-row"><span class="spec-k">シグナル検出（Signal）</span><span class="spec-v">リアルタイム売買判断</span></div>'
        '<div class="spec-row"><span class="spec-k">日次サマリー</span><span class="spec-v">ポジション確認+通知</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

# ── 2. 情報収集の仕組み ──

with st.expander("情報収集の仕組み", expanded=False):
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128225;</span>データソース</div>'
        '<div style="padding:0.4rem 1rem 0.3rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.3rem">'
        '<span class="spec-badge spec-b1">Tier 1</span>公式データ（高信頼性）</div>'
        '<ul class="spec-list" style="margin:0 0 0.5rem; padding-left:1.5rem">'
        "<li>FRED - 米国経済指標（GDP, 雇用統計, CPI等）</li>"
        "<li>Alpha Vantage - 決算カレンダー</li>"
        "<li>Alpaca - 株価データ + 取引API</li>"
        "</ul>"
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.3rem">'
        '<span class="spec-badge spec-b2">Tier 2</span>金融メディア</div>'
        '<ul class="spec-list" style="margin:0 0 0.5rem; padding-left:1.5rem">'
        "<li>Yahoo Finance / Google News RSS / NewsAPI</li>"
        "<li>Finnhub（60req/分）/ FMP（250req/日）</li>"
        "</ul>"
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.3rem">'
        '<span class="spec-badge spec-b3">Tier 3</span>コミュニティ</div>'
        '<ul class="spec-list" style="margin:0 0 0.3rem; padding-left:1.5rem">'
        "<li>Reddit（wallstreetbets, stocks, investing）</li>"
        "</ul>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128240;</span>RSSフィード（8+メディア）</div>'
        '<ul class="spec-list" style="padding-left:2rem">'
        "<li>MarketWatch Top Stories</li>"
        "<li>CNBC Finance / CNBC Top News</li>"
        "<li>Nasdaq RSS</li>"
        "<li>Seeking Alpha</li>"
        "<li>Yahoo Finance RSS</li>"
        "<li>Investing.com</li>"
        "<li>Benzinga</li>"
        "</ul>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">巡回間隔</span><span class="spec-v">15分</span></div>'
        '<div class="spec-row"><span class="spec-k">重複排除</span><span class="spec-v">URLベースUNIQUE制約</span></div>'
        '<div class="spec-row"><span class="spec-k">類似記事判定</span><span class="spec-v">85%以上で重複扱い</span></div>'
        '<div class="spec-row"><span class="spec-k">保存期間</span><span class="spec-v">30日間</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128279;</span>ニュースが投資判断に影響する流れ</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.7">'
        "収集されたニュースは以下の3段階で処理され、売買シグナルの確信度に反映されます:"
        "</div>"
        '<div style="padding:0 1rem 0.5rem; font-size:0.72rem; color:#64748b; line-height:1.7">'
        "<b>Step 1. イベント分類:</b> AIが各ニュースを9カテゴリ（決算・アナリスト・M&amp;A等）に分類し、"
        "影響の大きさ(0-1)とセンチメント(-1〜+1)を付与<br>"
        "<b>Step 2. 時間減衰:</b> イベントの種類ごとに半減期を設定（決算3日、M&amp;A 30日、一般2日等）。"
        "古いニュースの影響を指数関数的に減少<br>"
        "<b>Step 3. テーマ波及:</b> リーダー銘柄のニュースをフォロワー銘柄に0.7倍で波及。"
        "例: NVDAの好決算 → AMD・TSMに+0.56のスコアが波及<br>"
        "<b>Step 4. マクロ影響:</b> FRB金利・CPI等のマクロニュースは該当セクター全体に影響"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

# ── 3. AI分析の仕組み ──

with st.expander("AI（LLM）による定性分析", expanded=False):
    st.markdown(
        '<div class="spec-highlight">'
        "本システムでは、テクニカル指標（定量分析）だけでなく、"
        "Google Gemini LLMを活用した<b>6種類の定性分析</b>を組み合わせて投資判断を行います。"
        "LLMは「シニアアナリスト」「ヘッジファンドマネージャー」等の役割を与えられ、"
        "構造化されたプロンプトに基づき、ニュースの本質的な意味や市場の方向性を判断します。"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#129302;</span>AIモデル構成</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">メインモデル</span><span class="spec-v">Gemini 3 Pro Preview</span></div>'
        '<div class="spec-row"><span class="spec-k">フォールバック</span><span class="spec-v">Gemini 2.5 Pro</span></div>'
        '<div class="spec-row"><span class="spec-k">軽量処理用</span><span class="spec-v">Gemini 2.5 Flash</span></div>'
        '<div class="spec-row"><span class="spec-k">最終手段</span><span class="spec-v">Deepseek（Gemini全障害時）</span></div>'
        '<div class="spec-row"><span class="spec-k">API制限</span><span class="spec-v">50リクエスト/日（動的スロットル）</span></div>'
        '<div class="spec-row"><span class="spec-k">キャッシュ</span><span class="spec-v">1時間TTL / 最大100件</span></div>'
        '<div class="spec-row"><span class="spec-k">リトライ</span><span class="spec-v">最大3回 / 指数バックオフ</span></div>'
        "</div>"
        '<div class="spec-note">重要な売買判断（テーマ分析・トレード戦略）にはProモデル、ニュース要約やセンチメント分類にはFlashモデルを使用。'
        "API使用量80%超で自動的に間隔を広げるスロットル機構付き。</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128209;</span>LLM定性分析の6つのレイヤー</div>'
        '<div style="padding:0.5rem 1rem">'
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin-bottom:0.3rem">'
        "1. テーマ分析（メガトレンド評価）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.7">'
        "AIに「<b>シニアアナリスト（3-6ヶ月メガトレンド投資専門）</b>」の役割を与え、"
        "各投資テーマを包括的に評価させます。</div>"
        '<div style="font-size:0.72rem; color:#64748b; margin-top:0.3rem; line-height:1.6">'
        "<b>AIへの入力:</b> テーマ根拠 + マクロ環境（金利・インフレ）+ 市場データ（変動率・高安）"
        "+ テクニカル（RSI・MA50）+ ニュース上位3件<br>"
        "<b>AIの出力:</b> 現状分析(200字) / 3-6ヶ月見通し(250字) / メガトレンドスコア(0-100) / "
        "推奨保有期間 / 触媒リスト / リスク要因 / 信頼度(0-100) / セクターローテーション適合度<br>"
        "<b>判断基準:</b> 週次〜月次のトレンド重視。日次変動は無視。景気サイクルにおけるセクター位置を考慮。</div>"
        "</div>"
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin-bottom:0.3rem">'
        "2. ニュースセンチメント分析（Chain-of-Thought）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.7">'
        "AIに「<b>プロの投資アナリスト</b>」の役割を与え、段階的推論（Chain-of-Thought）で"
        "ニュースの投資への影響を評価させます。</div>"
        '<div style="font-size:0.72rem; color:#64748b; margin-top:0.3rem; line-height:1.6">'
        "<b>分析手順（Step by Step）:</b><br>"
        "&ensp;Step 1. 各ニュースの本質的な意味を理解<br>"
        "&ensp;Step 2. 短期(1-5日)と中期(1-4週間)の株価への影響を<b>別々に</b>評価<br>"
        "&ensp;Step 3. ポジティブ要因（触媒）とネガティブ要因（逆風）を列挙<br>"
        "&ensp;Step 4. 総合的な投資判断を導出<br>"
        "<b>AIの出力:</b> センチメントスコア(-1.0〜+1.0) / 短期・中期見通し / 触媒3件 / 逆風3件 / "
        "重要イベント3件 / 総合判断理由</div>"
        "</div>"
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin-bottom:0.3rem">'
        "3. イベント分類と影響度評価</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.7">'
        "各ニュースを9カテゴリに自動分類し、カテゴリごとに異なる<b>影響の持続期間</b>を適用します。</div>"
        '<div style="font-size:0.72rem; color:#64748b; margin-top:0.3rem; line-height:1.6">'
        "<b>分類カテゴリ:</b> 決算(半減期3日) / アナリスト評価(7日) / 新製品(14日) / M&amp;A(30日) / "
        "人事異動(7日) / 法規制(21日) / マクロ経済(14日) / セクター動向(7日) / 一般(2日)<br>"
        "<b>AIの判断:</b> カテゴリ + センチメント(-1〜+1) + 影響の大きさ(0〜1)<br>"
        "<b>時間減衰:</b> 古いニュースほど影響を指数関数的に減少させ、鮮度を重視。</div>"
        "</div>"
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin-bottom:0.3rem">'
        "4. ディープニュース分析（2段階分析）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.7">'
        "シグナル検出時に、その銘柄に関する全ニュースをAIが<b>深掘り分析</b>して確信度を調整します。</div>"
        '<div style="font-size:0.72rem; color:#64748b; margin-top:0.3rem; line-height:1.6">'
        "<b>Tier 1（背景蓄積）:</b> RSS・DB・Redditから記事を収集・蓄積。URLで重複排除。<br>"
        "<b>Tier 2（深層分析）:</b> Gemini Proに全記事のブリーフィングを渡し、以下を判断:<br>"
        "&ensp;- クロスソース合意度（複数メディアが同じ論調か？ 分散が小さい＝合意高い）<br>"
        "&ensp;- センチメント推移（直近3日 vs 4-7日前。±0.15以上の差で改善/悪化と判定）<br>"
        "&ensp;- 確信度調整（-3〜+3。AIの判断でシグナルの確信度を上下）<br>"
        "<b>推奨アクション:</b> confirm（そのまま） / increase（確信度UP） / decrease（DOWN） / reject（取消）<br>"
        "<b>フォールバック:</b> AI障害時はキーワードベース分析に自動切替。</div>"
        "</div>"
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin-bottom:0.3rem">'
        "5. メガトレンドスコアリング（5軸×20点）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.7">'
        "AIに「<b>ベテラン投資ストラテジスト</b>」の役割を与え、"
        "各テーマを5つの観点で定量スコアリングさせます。</div>"
        '<div style="font-size:0.72rem; color:#64748b; margin-top:0.3rem; line-height:1.6">'
        "<b>5つの評価軸（各0-20点、計100点満点）:</b><br>"
        "&ensp;1. <b>ニュース出現頻度</b> - 連日トップニュース=20点、ほぼ話題なし=0点<br>"
        "&ensp;2. <b>投資額（資金流入）</b> - 政府補助金+メガテック全力投資=20点、限定的=0点<br>"
        "&ensp;3. <b>技術成熟度</b> - 商用化・収益化済=20点、実験室レベル=0点（ガートナーハイプサイクル準拠）<br>"
        "&ensp;4. <b>市場予測</b> - CAGR 30%以上+巨大TAM=20点、成長鈍化=0点<br>"
        "&ensp;5. <b>企業決算での言及</b> - 主要企業の最重要トピック=20点、言及なし=0点<br>"
        "<b>ライフサイクル判定:</b> 0-39=萌芽期 / 40-69=成長期 / 70-85=成熟期 / 86-100=過熱期</div>"
        "</div>"
        "<div>"
        '<div style="font-size:0.82rem; font-weight:700; color:#1e40af; margin-bottom:0.3rem">'
        "6. トレード戦略生成（最終意思決定支援）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.7">'
        "AIに「<b>ヘッジファンドのシニアポートフォリオマネージャー</b>」の役割を与え、"
        "具体的な売買プランを生成させます。</div>"
        '<div style="font-size:0.72rem; color:#64748b; margin-top:0.3rem; line-height:1.6">'
        "<b>AIへの入力:</b> 現在価格・変動率 + MA50/MA200/RSI/52週高安/出来高比 + 過去24hの重要ニュース + ポジション状況<br>"
        "<b>AIの出力:</b><br>"
        "&ensp;- 推奨アクション: BUY / SELL / HOLD / REDUCE / WATCH（5段階）<br>"
        "&ensp;- 確信度: 1-10（曖昧さ禁止、具体的な数値で理由付き）<br>"
        "&ensp;- エントリー戦略: 推奨価格 + 条件（例:「$XXX突破後、RSI 50以下で押し目」）<br>"
        "&ensp;- エグジット戦略: 利確2段階（第1・第2目標）+ 損切ライン + 各条件<br>"
        "&ensp;- リスクリワード比: 計算に基づく数値（BUYは2.5倍以上が必須）<br>"
        "&ensp;- 触媒: 日付付きのカタリスト一覧<br>"
        "&ensp;- リスク: 具体的なリスク要因と影響<br>"
        "&ensp;- アクションプラン: 「今日→今週→来月」の時系列行動計画<br>"
        "&ensp;- 代替シナリオ: 想定外の展開時の対応策</div>"
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128279;</span>定量×定性の統合（最終判断の仕組み）</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.7">'
        "テクニカル指標（定量）とAI分析（定性）は以下の流れで統合されます:"
        "</div>"
        '<div style="padding:0 1rem 0.5rem">'
        '<div style="display:flex; flex-direction:column; gap:0.3rem; font-size:0.72rem">'
        '<div style="display:flex; align-items:center; gap:0.5rem">'
        '<span style="background:#dbeafe; color:#1d4ed8; padding:0.2rem 0.5rem; border-radius:6px; font-weight:600; min-width:5rem; text-align:center">定量分析</span>'
        '<span style="color:#94a3b8">&rarr;</span>'
        '<span style="color:#475569">RSI・MACD・出来高等でベースのシグナルスコア(0-100)を算出</span>'
        "</div>"
        '<div style="display:flex; align-items:center; gap:0.5rem">'
        '<span style="background:#f3e8ff; color:#7c3aed; padding:0.2rem 0.5rem; border-radius:6px; font-weight:600; min-width:5rem; text-align:center">AI定性</span>'
        '<span style="color:#94a3b8">&rarr;</span>'
        '<span style="color:#475569">ニュースセンチメント・ディープ分析で確信度を -3〜+3 調整</span>'
        "</div>"
        '<div style="display:flex; align-items:center; gap:0.5rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.2rem 0.5rem; border-radius:6px; font-weight:600; min-width:5rem; text-align:center">候補選定</span>'
        '<span style="color:#94a3b8">&rarr;</span>'
        '<span style="color:#475569">複合スコアでランク付け（下記配分）</span>'
        "</div>"
        '<div style="display:flex; align-items:center; gap:0.5rem">'
        '<span style="background:#fff7ed; color:#c2410c; padding:0.2rem 0.5rem; border-radius:6px; font-weight:600; min-width:5rem; text-align:center">最終判断</span>'
        '<span style="color:#94a3b8">&rarr;</span>'
        '<span style="color:#475569">リスク管理チェックを通過した候補のみ注文執行</span>'
        "</div>"
        "</div>"
        "</div>"
        '<div style="padding:0.4rem 1rem 0.3rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">候補選定の複合スコア配分</div>'
        "</div>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">確信度（Conviction）</span><span class="spec-v">20%</span></div>'
        '<div class="spec-row"><span class="spec-k">リスクリワード比</span><span class="spec-v">15%</span></div>'
        '<div class="spec-row"><span class="spec-k">セクターモメンタム</span><span class="spec-v">15%</span></div>'
        '<div class="spec-row"><span class="spec-k">相対強度（vs SPY・セクター）</span><span class="spec-v">15%</span></div>'
        '<div class="spec-row"><span class="spec-k">ニューススコア（AI定性）</span><span class="spec-v">15%</span></div>'
        '<div class="spec-row"><span class="spec-k">セクター分散ボーナス</span><span class="spec-v">10%</span></div>'
        '<div class="spec-row"><span class="spec-k">相関ペナルティ（低い方が有利）</span><span class="spec-v">10%</span></div>'
        "</div>"
        '<div class="spec-note">'
        "<b>ニュースによる確信度調整の例:</b> "
        "ニューススコア &gt; 0.5 → +2 / &gt; 0.3 → +1 / &lt; -0.3 → -1 / "
        "短期見通しが弱気 → -2。AIが「reject」を返した場合はシグナル自体を取消。"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

# ── 4. 売買判断の基準 ──

with st.expander("売買判断の基準", expanded=False):
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128200;</span>3つの売買戦略</div>'
        '<div style="padding:0.5rem 1rem">'
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#0f172a; margin-bottom:0.2rem">'
        "1. 押し目買い（Mean Reversion）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.6; margin-bottom:0.3rem">'
        "RSIが40以下に下がった銘柄を「売られすぎ」と判断し買いシグナルを出す。"
        "相場の行き過ぎた下落からの反発を狙う戦略。</div>"
        '<div style="font-size:0.72rem; color:#64748b; line-height:1.6">'
        "<b>必須条件:</b> ADX&ge;20（レンジ相場を除外）+ MA200デッドゾーン外（&plusmn;0.5%以上離れていること）<br>"
        "<b>確信度加点:</b> MA200上=+2 / RSI 40-60=+2 / ゴールデンクロス=+2 / BB下限接近=+2 / 出来高急増=+1 / MACD&gt;Signal=+2 / ストキャスティクス&lt;20=+2<br>"
        "<b>追加検証（Tier 1のみ）:</b> 週足トレンド確認(+2/-5) / ファンダメンタル(&plusmn;2) / セクター相対強度(&plusmn;2)</div>"
        "</div>"
        '<div style="margin-bottom:1rem; padding-bottom:0.8rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.82rem; font-weight:700; color:#0f172a; margin-bottom:0.2rem">'
        "2. トレンド追従（Trend Following）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.6; margin-bottom:0.3rem">'
        "MACD・ゴールデンクロス・出来高急増等で上昇トレンドの初動を検出。"
        "ADXが20以上で明確なトレンドがあることを確認して発出。</div>"
        '<div style="font-size:0.72rem; color:#64748b; line-height:1.6">'
        "<b>必須条件（全て満たす）:</b> MA20 &gt; MA50（短期上昇）+ 価格 &gt; 20日高値（ブレイクアウト）"
        "+ 出来高 &gt; 平均×1.5倍（勢い確認）+ RSI &gt; 50（過熱なし）<br>"
        "<b>ベース確信度:</b> 8（高い）+ Tier 1強化あり</div>"
        "</div>"
        "<div>"
        '<div style="font-size:0.82rem; font-weight:700; color:#0f172a; margin-bottom:0.2rem">'
        "3. VIX逆張り（VIX Contrarian）</div>"
        '<div style="font-size:0.74rem; color:#475569; line-height:1.6; margin-bottom:0.3rem">'
        "VIX（恐怖指数）が25以上に急騰した際、パニック売りからの反発を狙う。"
        "市場全体が過度に悲観的なときに買い向かう逆張り戦略。</div>"
        '<div style="font-size:0.72rem; color:#64748b; line-height:1.6">'
        "<b>発動条件:</b> VIX &ge; 25 または VIX前日比+15%以上<br>"
        "<b>必須条件:</b> RSI &le; 40（売られすぎ）+ MA200からの乖離 &ge; -10%（長期トレンド健全）<br>"
        "<b>確信度:</b> ベース5 + VIXスパイク加算(+2) + RSI加算(+3)</div>"
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#9989;</span>シグナル発出の必須条件</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.7">'
        "テクニカル指標は5カテゴリ（トレンド・モメンタム・出来高・ボラティリティ・MACD）に分類されます。"
        "シグナルが発出されるには、<b>2カテゴリ以上</b>が同じ方向を示していることが必須です。"
        "これにより「RSIだけ低いが他は全て正常」のような偽シグナルを排除します。"
        "</div>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">多カテゴリ検証</span><span class="spec-v">最低3カテゴリ一致（強カテゴリ含む場合2で可）</span></div>'
        '<div class="spec-row"><span class="spec-k">確信度の閾値</span><span class="spec-v">6以上（10点満点）で発出</span></div>'
        '<div class="spec-row"><span class="spec-k">シグナル有効期限</span><span class="spec-v">2営業日（価格乖離10%超で自動失効）</span></div>'
        '<div class="spec-row"><span class="spec-k">処理順序</span><span class="spec-v">確信度が高い順に優先処理</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#127919;</span>テクニカル指標と閾値</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">RSI（買いゾーン）</span><span class="spec-v">&le; 40（強い買い: &le; 30）</span></div>'
        '<div class="spec-row"><span class="spec-k">RSI（売りゾーン）</span><span class="spec-v">&ge; 70</span></div>'
        '<div class="spec-row"><span class="spec-k">MACD</span><span class="spec-v">12/26/9（Fast/Slow/Signal）</span></div>'
        '<div class="spec-row"><span class="spec-k">ボリンジャーバンド</span><span class="spec-v">20期間, 2&sigma;</span></div>'
        '<div class="spec-row"><span class="spec-k">ADX（トレンド強度）</span><span class="spec-v">&ge; 20 で有効</span></div>'
        '<div class="spec-row"><span class="spec-k">出来高スパイク</span><span class="spec-v">&ge; 1.5倍（強: &ge; 2.0倍）</span></div>'
        '<div class="spec-row"><span class="spec-k">VIX閾値</span><span class="spec-v">&ge; 25（極端: &ge; 35）</span></div>'
        '<div class="spec-row"><span class="spec-k">移動平均線</span><span class="spec-v">MA20 / MA50 / MA200</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#9878;</span>シグナル総合スコア（0〜100点）</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">RSI</span><span class="spec-v">最大 25点</span></div>'
        '<div class="spec-row"><span class="spec-k">MACD</span><span class="spec-v">最大 20点</span></div>'
        '<div class="spec-row"><span class="spec-k">ボリンジャーバンド</span><span class="spec-v">最大 15点</span></div>'
        '<div class="spec-row"><span class="spec-k">出来高</span><span class="spec-v">最大 15点</span></div>'
        '<div class="spec-row"><span class="spec-k">ストキャスティクス</span><span class="spec-v">最大 15点</span></div>'
        '<div class="spec-row"><span class="spec-k">ADX</span><span class="spec-v">最大 10点</span></div>'
        "</div>"
        '<div class="spec-note">確信度（Conviction）が6以上（10点満点中）のシグナルのみ発出。70点以上で注文執行対象。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

# ── 5. 注文執行とリスク管理 ──

with st.expander("注文執行とリスク管理", expanded=False):
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128269;</span>注文前チェック（7段階ゲート）</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.7; margin-bottom:0.3rem">'
        "シグナルが検出された後、以下の7つのチェックを<b>順番に</b>通過した場合のみ注文が執行されます。"
        "いずれか1つでも不合格なら注文は中止されます。"
        "</div>"
        '<div style="padding:0 1rem 0.5rem; font-size:0.72rem">'
        '<div style="display:flex; flex-direction:column; gap:0.25rem">'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">1</span>'
        '<span style="color:#0f172a; font-weight:600">価格検証</span>'
        '<span style="color:#64748b">— Alpaca実勢価格との乖離20%未満か確認</span></div>'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">2</span>'
        '<span style="color:#0f172a; font-weight:600">サーキットブレーカー</span>'
        '<span style="color:#64748b">— 連続損失・日次損失リミットに抵触していないか</span></div>'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">3</span>'
        '<span style="color:#0f172a; font-weight:600">市場レジーム</span>'
        '<span style="color:#64748b">— VIX &lt; 30 かつ SPY 5日間リターン &gt; -3%</span></div>'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">4</span>'
        '<span style="color:#0f172a; font-weight:600">重複チェック</span>'
        '<span style="color:#64748b">— 同銘柄のポジション・注文が既にないか</span></div>'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">5</span>'
        '<span style="color:#0f172a; font-weight:600">決算ブラックアウト</span>'
        '<span style="color:#64748b">— 決算発表7日以内の銘柄は取引停止</span></div>'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">6</span>'
        '<span style="color:#0f172a; font-weight:600">マクロ・セクター</span>'
        '<span style="color:#64748b">— FRB金利環境・CPI + セクター相対強度で確信度調整(&plusmn;2)</span></div>'
        '<div style="display:flex; align-items:center; gap:0.4rem">'
        '<span style="background:#ecfdf5; color:#059669; padding:0.15rem 0.35rem; border-radius:4px; font-weight:700; font-size:0.65rem">7</span>'
        '<span style="color:#0f172a; font-weight:600">相関チェック</span>'
        '<span style="color:#64748b">— 既存保有との60日間ピアソン相関が0.7未満か（超過時は株数半減）</span></div>'
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128184;</span>ポジション管理</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">取引API</span><span class="spec-v">Alpaca（ペーパートレード）</span></div>'
        '<div class="spec-row"><span class="spec-k">1銘柄あたり上限</span><span class="spec-v">ポートフォリオの20%</span></div>'
        '<div class="spec-row"><span class="spec-k">同時保有上限</span><span class="spec-v">5銘柄</span></div>'
        '<div class="spec-row"><span class="spec-k">1サイクルの最大買い</span><span class="spec-v">3銘柄</span></div>'
        '<div class="spec-row"><span class="spec-k">同セクター上限</span><span class="spec-v">1銘柄/日</span></div>'
        '<div class="spec-row"><span class="spec-k">注文タイムアウト</span><span class="spec-v">300秒（5分）</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128737;</span>リスク管理</div>'
        '<div style="padding:0.4rem 1rem 0.2rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">固定パラメータ</div>'
        "</div>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">HARD STOP LOSS（絶対防衛）</span><span class="spec-v" style="color:#e11d48">-8%</span></div>'
        '<div class="spec-row"><span class="spec-k">最大利確目標</span><span class="spec-v" style="color:#059669">+20%</span></div>'
        '<div class="spec-row"><span class="spec-k">最低リスクリワード比</span><span class="spec-v">1.5倍</span></div>'
        '<div class="spec-row"><span class="spec-k">日次損失リミット</span><span class="spec-v" style="color:#e11d48">-5%</span></div>'
        "</div>"
        '<div class="spec-note">通常のSL/TPは下記の動的VIX連動値が適用されます。'
        "HARD STOP LOSSは全ての条件を無視して強制発動する最終防衛ラインです。</div>"
        '<div style="padding:0.5rem 1rem 0.2rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">動的SL/TP（VIXレベルで自動調整）</div>'
        "</div>"
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">VIX &lt; 15（低ボラ）</span><span class="spec-v">SL 4% / TP 18%</span></div>'
        '<div class="spec-row"><span class="spec-k">VIX 15-20（通常）</span><span class="spec-v">SL 5% / TP 15%</span></div>'
        '<div class="spec-row"><span class="spec-k">VIX 20-30（やや高）</span><span class="spec-v">SL 6% / TP 12%</span></div>'
        '<div class="spec-row"><span class="spec-k">VIX &gt; 30（高ボラ）</span><span class="spec-v">SL 7% / TP 10%</span></div>'
        "</div>"
        '<div class="spec-note">ATR（14日間の平均変動幅）も考慮し、SL = max(2×ATR, VIXベースSL) で算出。'
        "VIXが高い局面ではSLを広めに取り、TPを控えめに設定する保守的な運用。</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128276;</span>決済（エグジット）条件</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.7">'
        "以下のいずれかの条件を満たすと自動で売却シグナルが発出されます:"
        "</div>"
        '<div style="padding:0 1rem 0.5rem; font-size:0.72rem; color:#64748b; line-height:1.7">'
        "<b>1. ストップロス:</b> 損失が固定SL%またはATRベースSLに到達<br>"
        "<b>2. テイクプロフィット:</b> 利益が15%以上（無条件） / 10%以上かつRSI&gt;65 / 12%以上かつRSI&gt;70<br>"
        "<b>3. テクニカル悪化:</b> RSI &gt; 80（含み益があれば） / MACDデスクロス（損益&plusmn;3%圏内）<br>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#9888;</span>サーキットブレーカー</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">発動条件</span><span class="spec-v">3回連続損失</span></div>'
        '<div class="spec-row"><span class="spec-k">効果</span><span class="spec-v">新規注文を一時停止</span></div>'
        '<div class="spec-row"><span class="spec-k">クールダウン</span><span class="spec-v">1日</span></div>'
        '<div class="spec-row"><span class="spec-k">自動解除</span><span class="spec-v">クールダウン後に復帰</span></div>'
        '<div class="spec-row"><span class="spec-k">通知</span><span class="spec-v">Discord（発動時/解除時）</span></div>'
        "</div>"
        '<div class="spec-note">サーキットブレーカーはシグナル検出には影響しません。注文執行のみを停止し、シグナル分析は継続します。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

# ── 6. ポートフォリオ構成 ──

with st.expander("ポートフォリオ構成", expanded=False):
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#127919;</span>投資テーマ（15テーマ / 115銘柄）</div>'
        '<div style="padding:0.5rem 1rem">'
        '<div style="margin-bottom:0.6rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">'
        '<span class="spec-badge spec-b1">Tier 1</span>コア（フル分析・全シグナル通知）</div>'
        '<div style="font-size:0.76rem; color:#0f172a; line-height:1.7">'
        "Market Index / Sector ETFs / AI Semiconductor / Cloud AI Infrastructure<br>"
        '<span style="color:#64748b; font-size:0.7rem">主要銘柄: NVDA, MSFT, GOOGL, AMZN, AAPL, META, TSM, ASML, CRWD, CCJ</span>'
        "</div></div>"
        '<div style="margin-bottom:0.6rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">'
        '<span class="spec-badge spec-b2">Tier 2</span>ウォッチ（確信度80%以上のみ通知）</div>'
        '<div style="font-size:0.76rem; color:#0f172a; line-height:1.7">'
        "Cybersecurity / Energy Infrastructure / Defense Space / Bio Genomics"
        "</div></div>"
        "<div>"
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">'
        '<span class="spec-badge spec-b3">Tier 3</span>アーカイブ（週次レポートのみ）</div>'
        '<div style="font-size:0.76rem; color:#0f172a; line-height:1.7">'
        "Robotics / Quantum / RareEarth / CleanEnergy / Fintech / Consumer Tech / Enterprise SaaS"
        "</div></div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128260;</span>テーマローテーション</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">最大同時投資テーマ</span><span class="spec-v">3テーマ</span></div>'
        '<div class="spec-row"><span class="spec-k">選定方法</span><span class="spec-v">モメンタムランキング</span></div>'
        '<div class="spec-row"><span class="spec-k">リバランス頻度</span><span class="spec-v">週次</span></div>'
        "</div>"
        '<div style="padding:0.3rem 1rem 0.5rem">'
        '<div style="font-size:0.72rem; font-weight:600; color:#64748b; margin-bottom:0.25rem">モメンタム配分</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">価格モメンタム（1M）</span><span class="spec-v">30%</span></div>'
        '<div class="spec-row"><span class="spec-k">価格モメンタム（3M）</span><span class="spec-v">20%</span></div>'
        '<div class="spec-row"><span class="spec-k">ニュースセンチメント</span><span class="spec-v">20%</span></div>'
        '<div class="spec-row"><span class="spec-k">セクターローテーション</span><span class="spec-v">15%</span></div>'
        '<div class="spec-row"><span class="spec-k">ファンダメンタル強度</span><span class="spec-v">15%</span></div>'
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

# ── 7. 障害対応とフォールバック ──

with st.expander("障害対応とフォールバック", expanded=False):
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128260;</span>AI（Gemini）障害時</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.7; margin-bottom:0.3rem">'
        "Gemini APIが応答しない場合、以下の順に自動フォールバックします:"
        "</div>"
        '<div style="padding:0 1rem 0.3rem; font-size:0.72rem">'
        '<div style="display:flex; flex-direction:column; gap:0.2rem">'
        '<div style="display:flex; align-items:center; gap:0.3rem">'
        '<span style="background:#dbeafe; color:#1d4ed8; padding:0.1rem 0.3rem; border-radius:4px; font-weight:700; font-size:0.6rem">1</span>'
        '<span style="color:#0f172a">Gemini 3 Pro Preview（メイン）</span></div>'
        '<div style="color:#94a3b8; font-size:0.65rem; padding-left:1.8rem">&darr; 障害時</div>'
        '<div style="display:flex; align-items:center; gap:0.3rem">'
        '<span style="background:#dbeafe; color:#1d4ed8; padding:0.1rem 0.3rem; border-radius:4px; font-weight:700; font-size:0.6rem">2</span>'
        '<span style="color:#0f172a">Gemini 2.5 Pro（フォールバック）</span></div>'
        '<div style="color:#94a3b8; font-size:0.65rem; padding-left:1.8rem">&darr; 障害時</div>'
        '<div style="display:flex; align-items:center; gap:0.3rem">'
        '<span style="background:#dbeafe; color:#1d4ed8; padding:0.1rem 0.3rem; border-radius:4px; font-weight:700; font-size:0.6rem">3</span>'
        '<span style="color:#0f172a">Gemini Flash（軽量モデル）</span></div>'
        '<div style="color:#94a3b8; font-size:0.65rem; padding-left:1.8rem">&darr; Gemini全障害時</div>'
        '<div style="display:flex; align-items:center; gap:0.3rem">'
        '<span style="background:#fff7ed; color:#c2410c; padding:0.1rem 0.3rem; border-radius:4px; font-weight:700; font-size:0.6rem">4</span>'
        '<span style="color:#0f172a">Deepseek API（最終手段）</span></div>'
        '<div style="color:#94a3b8; font-size:0.65rem; padding-left:1.8rem">&darr; 全AI障害時</div>'
        '<div style="display:flex; align-items:center; gap:0.3rem">'
        '<span style="background:#f1f5f9; color:#64748b; padding:0.1rem 0.3rem; border-radius:4px; font-weight:700; font-size:0.6rem">5</span>'
        '<span style="color:#64748b">キーワードベース分析（ルールベース）</span></div>'
        "</div>"
        "</div>"
        '<div class="spec-note">各リトライは最大3回・指数バックオフ(2秒→4秒→8秒)。1時間のキャッシュにより同一プロンプトの再呼び出しを回避。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#9888;</span>その他の障害対応</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">Alpaca API障害</span><span class="spec-v">3回リトライ+指数バックオフ。失敗時はDiscord通知</span></div>'
        '<div class="spec-row"><span class="spec-k">ニュースソース障害</span><span class="spec-v">個別ソース障害は他ソースで継続。全障害時はDB蓄積分を使用</span></div>'
        '<div class="spec-row"><span class="spec-k">DB障害</span><span class="spec-v">SQLite UNIQUE制約でデータ整合性を保護。障害時はログに記録</span></div>'
        '<div class="spec-row"><span class="spec-k">スケジューラ停止</span><span class="spec-v">ハートビート監視（60分警告/120分重大 → Discord通知）</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

# ── 8. 通知とモニタリング ──

with st.expander("通知とモニタリング", expanded=False):
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128276;</span>Discord通知チャンネル</div>'
        '<div style="padding:0.5rem 1rem">'
        '<div style="display:flex; align-items:baseline; gap:0.5rem; padding:0.35rem 0; border-bottom:1px solid #f1f5f9; font-size:0.74rem">'
        '<span style="color:#059669; font-weight:700; min-width:8rem">買いシグナル</span>'
        '<span style="color:#475569">銘柄・価格・戦略・確信度・理由を即時通知</span>'
        "</div>"
        '<div style="display:flex; align-items:baseline; gap:0.5rem; padding:0.35rem 0; border-bottom:1px solid #f1f5f9; font-size:0.74rem">'
        '<span style="color:#e11d48; font-weight:700; min-width:8rem">売りシグナル</span>'
        '<span style="color:#475569">決済価格・損益・保有日数・決済理由を即時通知</span>'
        "</div>"
        '<div style="display:flex; align-items:baseline; gap:0.5rem; padding:0.35rem 0; border-bottom:1px solid #f1f5f9; font-size:0.74rem">'
        '<span style="color:#2563eb; font-weight:700; min-width:8rem">日次サマリー</span>'
        '<span style="color:#475569">本日の損益・取引・保有状況・累積成績（毎日16:30 ET）</span>'
        "</div>"
        '<div style="display:flex; align-items:baseline; gap:0.5rem; padding:0.35rem 0; border-bottom:1px solid #f1f5f9; font-size:0.74rem">'
        '<span style="color:#7c3aed; font-weight:700; min-width:8rem">パフォーマンス</span>'
        '<span style="color:#475569">週次・月次の成績レポート（勝率・リターン・セクター別）</span>'
        "</div>"
        '<div style="display:flex; align-items:baseline; gap:0.5rem; padding:0.35rem 0; font-size:0.74rem">'
        '<span style="color:#f59e0b; font-weight:700; min-width:8rem">システム警告</span>'
        '<span style="color:#475569">エラー・API制限(80%超)・CB発動/解除・ハートビート異常</span>'
        "</div>"
        "</div>"
        '<div class="spec-note">シグナル通知は48時間のスライディングウィンドウで重複排除。エラー通知は1時間のクールダウン。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128202;</span>ヘルスモニタリング</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">ハートビート</span><span class="spec-v">5分毎にJSONファイル更新</span></div>'
        '<div class="spec-row"><span class="spec-k">警告閾値</span><span class="spec-v">60分間更新なしで警告</span></div>'
        '<div class="spec-row"><span class="spec-k">重大閾値</span><span class="spec-v">120分間更新なしでクリティカル</span></div>'
        '<div class="spec-row"><span class="spec-k">ログ保存先</span><span class="spec-v">92_logs/（scheduler, trader, error）</span></div>'
        '<div class="spec-row"><span class="spec-k">API使用量監視</span><span class="spec-v">70-90%で段階的に警告</span></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

# ── 9. 自己改善・制約事項 ──

with st.expander("自己改善・制約事項", expanded=False):
    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128257;</span>PDCAサイクル</div>'
        '<div style="padding:0.5rem 1rem">'
        '<div style="margin-bottom:0.8rem; padding-bottom:0.6rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.78rem; font-weight:700; color:#0f172a; margin-bottom:0.2rem">日次レビュー（自動）</div>'
        '<div style="font-size:0.72rem; color:#64748b; line-height:1.6">'
        "毎日の取引結果を自動分析し、KPI進捗（勝率・リターン・ドローダウン）を追跡。"
        "7日間 vs 14日間のトレンド比較で改善/悪化を検出しDiscordに通知。</div>"
        "</div>"
        '<div style="margin-bottom:0.8rem; padding-bottom:0.6rem; border-bottom:1px solid #f1f5f9">'
        '<div style="font-size:0.78rem; font-weight:700; color:#0f172a; margin-bottom:0.2rem">週次レビュー（土曜日）</div>'
        '<div style="font-size:0.72rem; color:#64748b; line-height:1.6">'
        "損失取引（-5%以上）をAIが深掘り分析。原因分類（損切発動・シグナルロジック・市場変動）を行い、"
        "PDCA形式で改善提案を生成。パラメータ調整案やフィルター追加を提示。</div>"
        "</div>"
        "<div>"
        '<div style="font-size:0.78rem; font-weight:700; color:#0f172a; margin-bottom:0.2rem">改善の実行</div>'
        '<div style="font-size:0.72rem; color:#64748b; line-height:1.6">'
        "改善提案はバックテスト（過去データでの検証）を経て適用。"
        "現時点では人間の承認が必要（完全自動化はPhase 4以降に予定）。"
        "過去の教訓は38件が体系的に記録・分類されています。</div>"
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128218;</span>シグナル精度の追跡</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">シグナル記録</span><span class="spec-v">全シグナルをDBに保存（戦略・確信度・結果）</span></div>'
        '<div class="spec-row"><span class="spec-k">損益との紐付け</span><span class="spec-v">signal_id で取引と連結</span></div>'
        '<div class="spec-row"><span class="spec-k">戦略別成績</span><span class="spec-v">押し目・トレンド・VIX逆張りの個別分析</span></div>'
        '<div class="spec-row"><span class="spec-k">パターン検出</span><span class="spec-v">連続負け・セクター集中・早期損切の自動検出</span></div>'
        "</div>"
        '<div class="spec-note">現在は週次レポートで手動確認。リアルタイム精度トラッキングの自動化はPhase 4の改善項目。</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#9940;</span>対応していないこと</div>'
        '<div style="padding:0.5rem 1rem; font-size:0.74rem; color:#475569; line-height:1.8">'
        '<div style="display:grid; grid-template-columns:1fr 1fr; gap:0.2rem 1.5rem">'
        "<div>&#x2716; 空売り・オプション・先物</div>"
        "<div>&#x2716; 暗号資産</div>"
        "<div>&#x2716; 米国以外の市場</div>"
        "<div>&#x2716; プレマーケット / アフターアワーズ取引</div>"
        "<div>&#x2716; 高頻度トレード（ミリ秒単位）</div>"
        "<div>&#x2716; トレーリングストップ</div>"
        "<div>&#x2716; 自動リバランス（手動のみ）</div>"
        "<div>&#x2716; リアルタイムストリーミング（ポーリング方式）</div>"
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="spec-title"><span class="spec-icon">&#128295;</span>API制約とコスト</div>'
        '<div class="spec-grid">'
        '<div class="spec-row"><span class="spec-k">Alpaca</span><span class="spec-v">200 req/日（無料ペーパー）</span></div>'
        '<div class="spec-row"><span class="spec-k">Gemini</span><span class="spec-v">50 req/日（動的スロットル）</span></div>'
        '<div class="spec-row"><span class="spec-k">NewsAPI</span><span class="spec-v">100 req/日（無料枠）</span></div>'
        '<div class="spec-row"><span class="spec-k">Finnhub</span><span class="spec-v">60 req/分</span></div>'
        '<div class="spec-row"><span class="spec-k">yfinance</span><span class="spec-v">制限なし（429エラー頻発時あり）</span></div>'
        '<div class="spec-row"><span class="spec-k">月額予算</span><span class="spec-v">約¥5,000（API利用料合計）</span></div>'
        "</div>"
        '<div class="spec-note">API使用量が80%を超えるとDiscordに警告通知。Geminiは使用量80%超で呼び出し間隔を自動延長。</div>'
        "</div>",
        unsafe_allow_html=True,
    )
