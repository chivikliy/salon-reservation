import streamlit as st
from datetime import datetime, timedelta
import random

# ⚙️ 管理者画面 UI レイアウト設定
VERSION = "v5.0.0 (Admin ダッシュボード シンプル統合版)"

BASE_BG = "#fdfaf6"
BASE_TEXT = "#333333"
ACCENT_GOLD = "#d9b38c"

st.set_page_config(page_title=f"サロン管理者ダッシュボード {VERSION}", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {BASE_BG}; color: {BASE_TEXT}; }}
    [data-testid="stSidebar"] {{ background-color: #f7f3ed; border-right: 1px solid #eaddd0; }}
    .stTabs [data-baseweb="tab-list"] button {{ color: #777777; font-weight: bold; padding: 10px; font-size: 1.1em; }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{ color: {BASE_TEXT}; border-bottom-color: {ACCENT_GOLD}; }}
    [data-testid="stMetricValue"] {{ color: {ACCENT_GOLD}; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

st.title("管理者専用ダッシュボード")
st.subheader("予約管理システム")

# 最新のカテゴリ構成に同期
if 'admin_db' not in st.session_state:
    st.session_state.admin_db = []
    
    dummy_data = [
        ("佐藤 健太", "サトウ ケンタ"), ("鈴木 美咲", "スズキ ミサキ"), ("高橋 翔太", "タカハシ ショウタ"), 
        ("田中 花子", "タナカ ハナコ"), ("伊藤 翼", "イトウ ツバサ"), ("渡辺 陽子", "ワタナベ ヨウコ"), 
        ("山本 大地", "ヤマモト ダイチ"), ("中村 さくら", "ナカムラ サクラ")
    ]
    staff_list = ["関根 光代", "田中 健太", "佐藤 美咲", "鈴木 翔太", "山田 花子", "高橋 陽子"]
    services = ["ヘア", "スパ", "着付け", "ネイル", "歯医者"]
    times = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    today = datetime.today().date()
    
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
    "表示期間を指定",
    ["1日単位", "1週間単位", "2週間単位", "3週間単位", "月単位", "年単位", "全日程"]
)

if period_option != "全日程":
    base_date = st.sidebar.date_input("基準日を選択", datetime.today().date())
else:
    base_date = datetime.today().date()
    if not st.session_state.admin_db:
        st.warning("システム内に予約データがありません。")

search_query = st.sidebar.text_input("お名前（漢字・カナ）で検索")

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

if search_query:
    target_reservations = [req for req in target_reservations if search_query in req["name"] or search_query in req["furigana"]]

target_reservations.sort(key=lambda x: (x["date"], x["time"]))

MAX_DISPLAY_CARDS = 100
display_reservations = target_reservations[:MAX_DISPLAY_CARDS]

# --- 2. 経営指標（KPI）ダッシュボード ---
st.markdown("---")
st.markdown(f"### 📊 指定期間の予約サマリー")
col1, col2 = st.columns(2)
col1.metric("総予約数", f"{len(target_reservations)} 件")

if len(target_reservations) > MAX_DISPLAY_CARDS:
    st.warning(f"ℹ️ 表示上限に達したため、最新の {MAX_DISPLAY_CARDS} 件のみを表示しています。")

st.markdown("---")

# --- 3. 自動振り分けタブシステム ---
CATEGORY_TABS = ["すべて"] + services
tabs = st.tabs(CATEGORY_TABS)

for i, tab_name in enumerate(CATEGORY_TABS):
    with tabs[i]:
        if tab_name == "すべて":
            filtered_res = display_reservations
        else:
            filtered_res = [req for req in display_reservations if req["service"] == tab_name]
        
        if not filtered_res:
            st.write(f"ℹ️ このカテゴリ（{tab_name}）には予約が入っておりません。")
        else:
            for req in filtered_res:
                st.markdown(f"""
                <div style="border:1px solid #eaddd0; border-radius: 8px; padding: 15px; margin-bottom: 12px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h4 style="margin:0; color:#333333; display:flex; align-items:center; flex-wrap:wrap;">
                        📅 {req['date']} 
                        <span style="font-weight:bold; color:#d9b38c; margin: 0 10px;">【{req['service']}】</span> 
                        ⏰ {req['time']} - {req['name']}（{req['furigana']}）様
                    </h4>
                    <hr style="margin: 10px 0; border: none; border-top: 1px dashed #eaddd0;">
                    <p style="margin:0; color:#555555; font-size: 15px; line-height: 1.5;">
                        <b>指名担当者:</b> {req['staff']} &nbsp;&nbsp;|&nbsp;&nbsp;
                        <b>状況:</b> <span style="color:#2e8b57; font-weight:bold;">{req['status']}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
