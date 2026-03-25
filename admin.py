import streamlit as st
from datetime import datetime, timedelta
import random

# ⚙️ 管理者画面 UI レイアウト設定
# v4.0.0：全日程エラー修正、表示件数制限、カードフォント最適化、シック＆モダンベース
VERSION = "v4.0.0 (Admin ダッシュボード シック＆モダンベース)"

# お客様画面と共通のシック＆モダンベースカラー
BASE_BG = "#2c3e50" # シックダーク背景
BASE_TEXT = "#ecf0f1" # ライトテキスト
ACCENT_GOLD = "#d9b38c" # アクセントゴールド

st.set_page_config(page_title=f"サロン管理者ダッシュボード {VERSION}", layout="wide")

# 管理画面用シック＆モダンデザイン適用（CSS）
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BASE_BG}; color: {BASE_TEXT}; }}
    /* サイドバー */
    [data-testid="stSidebar"] {{ background-color: rgba(0,0,0,0.2); }}
    [data-testid="stSidebar"] * {{ color: {BASE_TEXT}; }}
    /* タブ */
    .stTabs [data-baseweb="tab-list"] button {{ color: {BASE_TEXT}; font-weight: bold; padding: 10px; }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{ color: {ACCENT_GOLD}; border-bottom-color: {ACCENT_GOLD}; }}
    /* KPI */
    [data-testid="stMetricValue"] {{ color: {ACCENT_GOLD}; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

st.title("管理者専用ダッシュボード")
st.subheader("総合オンライン予約 ＆ 商品購入管理システム")

# データベース接続前のテスト用ダミーデータ生成システム（最新仕様に同期）
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
    today = datetime.today().date()
    
    # テスト用に、今日から20日間分の重複しないダミーデータを200件生成いたします
    for day_offset in range(20):
        target_date = today + timedelta(days=day_offset)
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

# --- 1. 高度なフィルター機能（サイドバー） ---
st.sidebar.markdown("### 🔍 予約フィルター")

period_option = st.sidebar.selectbox(
    "表示期間を指定してください", # 表記を分かりやすく整理
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
    req_date = req["date"]
    
    is_in_period = False
    if period_option == "全日程": is_in_period = True
    elif period_option == "1日単位": is_in_period = (req_date == base_date)
    elif period_option == "1週間単位": is_in_period = (base_date <= req_date <= base_date + timedelta(days=6))
    elif period_option == "2週間単位": is_in_period = (base_date <= req_date <= base_date + timedelta(days=13))
    elif period_option == "3週間単位": is_in_period = (base_date <= req_date <= base_date + timedelta(days=20))
    elif period_option == "月単位": is_in_period = (req_date.year == base_date.year and req_date.month == base_date.month)
    elif period_option == "年単位": is_in_period = (req_date.year == base_date.year)
    
    if is_in_period: target_reservations.append(req)

# 名前で検索
if search_query:
    target_reservations = [req for req in target_reservations if search_query in req["name"] or search_query in req["furigana"]]

# 日付と時間で並べ替え
target_reservations.sort(key=lambda x: (x["date"], x["time"]))

# 【解決策3 - エラー修正】表示件数に安全装置（MAX 100件）を組み込みました
MAX_DISPLAY_CARDS = 100
display_reservations = target_reservations[:MAX_DISPLAY_CARDS]

# --- 2. 経営指標（KPI）ダッシュボード ---
st.markdown("---")
st.markdown(f"### 📊 指定期間（{period_option}）の予約サマリー")
col1, col2 = st.columns(2)
col1.metric("総予約数", f"{len(target_reservations)} 件")
# 100件を超えた場合、案内を表示いたします
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
            filtered_res = [req for req in display_reservations if req["service"] == tab_name]
        
        if not filtered_res:
            st.write(f"ℹ️ このカテゴリ（{tab_name}）には、指定された期間内に予約が入っておりません。")
        else:
            for req in filtered_res:
                # 【解決策4 - フォント調整】カテゴリ名をボールド体にし、フォントサイズを周囲と同じにいたしました
                st.markdown(f"""
                <div style="border:2px solid #d9b38c; border-radius: 8px; padding: 15px; margin-bottom: 15px; background-color: #fdfaf6; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h4 style="margin:0; color:#333333; display:flex; align-items:center; flex-wrap:wrap;">
                        📅 {req['date']} 
                        <span style="font-weight:bold; color:#d9b38c; margin: 0 10px;">【{req['service']}】</span> 
                        ⏰ {req['time']} - {req['name']}（{req['furigana']}）様
                    </h4>
                    <hr style="margin: 10px 0; border: none; border-top: 1px dashed #d9b38c;">
                    <p style="margin:0; color:#555555; font-size: 16px; line-height: 1.6;">
                        <b>指名担当者:</b> {req['staff']} <br>
                        <b>現在の状況:</b> <span style="color:white; background-color:green; padding: 2px 8px; border-radius: 4px; font-size: 14px; font-weight:bold;">{req['status']}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
