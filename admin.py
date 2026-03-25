import streamlit as st
from datetime import datetime, timedelta, date
import random

# ⚙️ 管理者画面 UI レイアウト設定
# v6.0.0：コンパクト化、Figma的洗練UI、表示件数拡大(200)、エラー鉄壁対策、共通スパム対策
VERSION = "v6.0.0 (Admin ダッシュボード コンパクト・鉄壁版)"

# 洗練された明るいデザインベース（清潔感のあるナチュラルベージュ）
BASE_BG = "#fdfaf6"
BASE_TEXT = "#333333"
ACCENT_GOLD = "#d9b38c"

# Streamlit set_page_config（画面幅ワイド化、タイトル設定）
st.set_page_config(page_title=f"サロン管理者ダッシュボード {VERSION}", layout="wide")

# 【Figma的UI設計】Figmaによるデザイン思想を適用し、フォントサイズと余白を詰めたコンパクトCSSカスタム
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BASE_BG}; color: {BASE_TEXT}; font-size: 14px; }}
    /* タイトル・サブタイトルのコンパクト化 */
    h1 {{ font-size: 1.8em !important; margin-bottom: 0.2em !important; padding-top: 0 !important; }}
    h3 {{ font-size: 1.2em !important; margin-top: 0.2em !important; margin-bottom: 0.5em !important; }}
    /* サイドバーのコンパクト化 */
    [data-testid="stSidebar"] {{ background-color: #f7f3ed; border-right: 1px solid #eaddd0; font-size: 13px; }}
    [data-testid="stSidebar"] p {{ margin-bottom: 0.5em !important; }}
    [data-testid="stSidebar"] label {{ font-weight: bold; font-size: 13px !important; color: {BASE_TEXT}; }}
    /* タブのコンパクト化 */
    .stTabs [data-baseweb="tab-list"] button {{ color: #777777; font-weight: bold; padding: 6px 10px; font-size: 1.0em; }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{ color: {BASE_TEXT}; border-bottom-color: {ACCENT_GOLD}; }}
    /* KPI（Metric）のコンパクト化 */
    [data-testid="stMetricValue"] {{ color: {ACCENT_GOLD}; font-weight: bold; font-size: 2.0em !important; }}
    [data-testid="stMetricLabel"] p {{ font-size: 1.1em !important; }}
    /* コンポーネントの余白詰め */
    .stMarkdown p, .stAlert p {{ margin-bottom: 0.5em !important; }}
    </style>
""", unsafe_allow_html=True)

st.title("管理者専用ダッシュボード")
st.subheader("総合オンライン予約 ＆ 商品購入管理システム")

# 最新のカテゴリ構成に同期
if 'admin_db' not in st.session_state:
    st.session_state.admin_db = []
    
    dummy_data = [
        ("佐藤 健太", "サトウ ケンタ"), ("鈴木 美咲", "スズキ ミサキ"), ("高橋 翔太", "タカハシ ショウタ"), 
        ("田中 花子", "タナカ ハナコ"), ("伊藤 翼", "イトウ ツバサ"), ("渡辺 陽子", "ワタナベ ヨウコ"), 
        ("山本 大地", "ヤマモト ダイチ"), ("中村 さくら", "ナカムラ サクラ")
    ]
    staff_list = ["関根 光代", "田中 健太", "佐藤 美咲", "鈴木 翔太", "山田 花子", "高橋 陽子", "伊藤 翼"]
    services = [
        "✂️ ヘア (LAB Peace 予防医学)", "💆‍♀️ スパ (ドクターラブシステム)", "🛒 商品販売 (Precious EC)", 
        "👘 着付け", "💅 ネイル", "🧘 瞑想教室", "🦷 歯医者"
    ]
    times = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    today_date = datetime.today().date()
    
    # テスト用に、今日から20日間分の重複しないダミーデータを生成いたします
    for day_offset in range(20):
        target_date = today_date + timedelta(days=day_offset)
        used_time_staff, used_names = set(), set()
        daily_count, attempts = 0, 0
        while daily_count < 10 and attempts < 100:
            attempts += 1
            r_time = random.choice(times)
            r_staff = random.choice(staff_list)
            r_person = random.choice(dummy_data)
            r_service = random.choice(services)
            if (r_time, r_staff) not in used_time_staff and r_person[0] not in used_names:
                used_time_staff.add((r_time, r_staff))
                used_names.add(r_person[0])
                st.session_state.admin_db.append({
                    "date": target_date, "time": r_time,
                    "name": r_person[0], "furigana": r_person[1],
                    "staff": r_staff, "service": r_service, "status": "予約確定"
                })
                daily_count += 1

# 🛡️ 【絶対防御】どんなデータでも必ずカレンダーの「日付型」に変換する関数
def get_safe_date(date_value):
    # すでに正しい日付型の場合
    if isinstance(date_value, date) and not isinstance(date_value, datetime):
        return date_value
    # 時間が含まれるDatetime型の場合、日付のみを取り出す
    if isinstance(date_value, datetime):
        return date_value.date()
    # 文字列（String型）として混入している場合、強制的に日付型に翻訳する
    if isinstance(date_value, str):
        try:
            # "2026-03-25" のような最初の10文字を日付として読み取る
            return datetime.strptime(date_value[:10], "%Y-%m-%d").date()
        except ValueError:
            pass
    # 判別不能なデータや空っぽの場合は、システムを止めず「今日」を返す
    return datetime.today().date()


# --- 1. 高度なフィルター機能（サイドバー） ---
st.sidebar.markdown("### 🔍 予約フィルター")

period_option = st.sidebar.selectbox(
    "表示期間を指定",
    ["1日単位", "1週間単位", "2週間単位", "3週間単位", "月単位", "年単位", "全日程"]
)

# システムは期間に応じてサイドバーの表示を切り替えます
if period_option != "全日程":
    base_date = st.sidebar.date_input("基準日を選択", datetime.today().date()) # 表記を分かりやすく整理
else:
    # 全日程の場合、st.date_inputは表示いたしません
    base_date = datetime.today().date()
    # データが空の場合、案内を表示いたします
    if not st.session_state.admin_db:
        st.warning("システム内に予約データがありません（お客様サイトでダミーデータを生成してください）。")

search_query = st.sidebar.text_input("お名前（漢字・カナ）で検索（任意）")

# システムが期間内のデータを抽出いたします
target_reservations = []
for req in st.session_state.admin_db:
    # ⚠️ ここで絶対防御システムを起動。req.get("date") が文字であっても強制的に日付型に直す
    req_date = get_safe_date(req.get("date"))
    
    is_in_period = False
    if period_option == "全日程": is_in_period = True
    elif period_option == "1日単位": is_in_period = (req_date == base_date)
    elif period_option == "1週間単位": is_in_period = (base_date <= req_date <= base_date + timedelta(days=6))
    elif period_option == "2週間単位": is_in_period = (base_date <= req_date <= base_date + timedelta(days=13))
    elif period_option == "3週間単位": is_in_period = (base_date <= req_date <= base_date + timedelta(days=20))
    elif period_option == "月単位": is_in_period = (req_date.year == base_date.year and req_date.month == base_date.month)
    elif period_option == "年単位": is_in_period = (req_date.year == base_date.year)
    
    if is_in_period: target_reservations.append(req)

# 名前で検索（漢字・カナ両対応）
if search_query:
    target_reservations = [req for req in target_reservations if search_query in req.get("name", "") or search_query in req.get("furigana", "")]

# 並べ替え時にも絶対防御システムを通して安全に処理する
target_reservations.sort(key=lambda x: (get_safe_date(x.get("date")), x.get("time", "00:00")))

# 【解決策3 - 表示件数拡大】最大表示数を200件に拡大いたしました
MAX_DISPLAY_CARDS = 200
display_reservations = target_reservations[:MAX_DISPLAY_CARDS]

# --- 2. 経営指標（KPI）ダッシュボード ---
st.markdown("---")
st.markdown(f"### 📊 指定期間（{period_option}）の予約サマリー")
col1, col2 = st.columns(2)
col1.metric("総予約数", f"{len(target_reservations)} 件")

# 200件を超えた場合、案内を表示いたします
if len(target_reservations) > MAX_DISPLAY_CARDS:
    st.warning(f"ℹ️ システムからの案内: 表示上のエラーを避けるため、最新の {MAX_DISPLAY_CARDS} 件のみを表示しています。全日程から探す場合は、お名前で検索してください。")

st.markdown("---")

# --- 3. 自動振り分けタブシステム ---
CATEGORY_TABS = ["すべて"] + services
tabs = st.tabs(CATEGORY_TABS)

for i, tab_name in enumerate(CATEGORY_TABS):
    with tabs[i]:
        # タブごとのデータを抽出
        if tab_name == "すべて":
            filtered_res = display_reservations # 表示用データを使用
        else:
            filtered_res = [req for req in display_reservations if req.get("service") == tab_name]
        
        if not filtered_res:
            st.write(f"ℹ️ このカテゴリ（{tab_name}）には、指定された期間内に予約が入っておりません。")
        else:
            for req in filtered_res:
                # 画面表示用のデータを安全に取得
                r_date_raw = req.get('date', '')
                r_date_str = str(r_date_raw)[:10] if r_date_raw else "不明"
                r_time = req.get('time', '')
                r_service = req.get('service', '不明')
                r_name = req.get('name', '不明')
                r_furi = req.get('furigana', '')
                r_staff = req.get('staff', '未定')
                r_status = req.get('status', '不明')
                
                furi_display = f"（{r_furi}）" if r_furi else ""

                # 【Figma的UI設計】コンパクト化された洗練されたカードデザイン
                st.markdown(f"""
                <div style="border:1px solid #eaddd0; border-radius: 8px; padding: 12px; margin-bottom: 10px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-size: 13.5px;">
                    <h4 style="margin:0; color:#333333; display:flex; align-items:center; flex-wrap:wrap; font-size: 1.1em;">
                        📅 {r_date_str} 
                        <span style="font-weight:bold; color:#d9b38c; margin: 0 8px;">【{r_service}】</span> 
                        ⏰ {r_time} - {r_name}{furi_display}様
                    </h4>
                    <hr style="margin: 8px 0; border: none; border-top: 1px dashed #eaddd0;">
                    <p style="margin:0; color:#555555; font-size: 1.0em; line-height: 1.5;">
                        <b>指名担当者:</b> {r_staff} &nbsp;&nbsp;|&nbsp;&nbsp;
                        <b>現在の状況:</b> <span style="color:#2e8b57; font-weight:bold;">{r_status}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)

# --- 4. データベースリセット機能（完全初期化） ---
st.sidebar.markdown("---")
if st.sidebar.button("⚙️ 古いデータを削除してリセット"):
    st.session_state.admin_db = []
    st.sidebar.success("システム内の古いデータを完全に消去しました。ブラウザの更新ボタン（F5キー）を押してください。")
