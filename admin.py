import streamlit as st
from datetime import datetime, timedelta
import random

# ⚙️ 管理者画面 UI レイアウト設定
VERSION = "v3.0.0 (LabPeace & Precious EC 統合管理ダッシュボード)"
st.set_page_config(page_title=f"サロン管理者ダッシュボード {VERSION}", layout="wide")

st.title("管理者専用ダッシュボード")
st.markdown("### 📅 日別・期間別 予約管理システム")

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
    
    for i in range(50): # 管理画面での表示テスト用に50件生成
        r_date = today + timedelta(days=random.randint(0, 10))
        r_time = random.choice(times)
        r_person = random.choice(dummy_data)
        r_staff = random.choice(staff_list)
        r_service = random.choice(services)
        
        st.session_state.admin_db.append({
            "date": r_date,
            "time": r_time,
            "name": r_person[0],
            "furigana": r_person[1],
            "staff": r_staff,
            "service": r_service,
            "status": "予約確定"
        })

# --- 1. 高度なフィルター機能（サイドバー） ---
st.sidebar.markdown("### 🔍 予約フィルター")

period_option = st.sidebar.selectbox(
    "検索する期間の単位を指定してください",
    ["1日単位", "1週間単位", "2週間単位", "3週間単位", "月単位", "年単位", "全日程"]
)

if period_option != "全日程":
    base_date = st.sidebar.date_input("基準となる日付をカレンダーから選択してください", datetime.today().date())
else:
    base_date = datetime.today().date()

search_query = st.sidebar.text_input("お客様のお名前（漢字・カナ）で検索（任意）")

target_reservations = []
for req in st.session_state.admin_db:
    req_date = req["date"]
    
    is_in_period = False
    if period_option == "全日程":
        is_in_period = True
    elif period_option == "1日単位":
        is_in_period = (req_date == base_date)
    elif period_option == "1週間単位":
        is_in_period = (base_date <= req_date <= base_date + timedelta(days=6))
    elif period_option == "2週間単位":
        is_in_period = (base_date <= req_date <= base_date + timedelta(days=13))
    elif period_option == "3週間単位":
        is_in_period = (base_date <= req_date <= base_date + timedelta(days=20))
    elif period_option == "月単位":
        is_in_period = (req_date.year == base_date.year and req_date.month == base_date.month)
    elif period_option == "年単位":
        is_in_period = (req_date.year == base_date.year)
        
    if is_in_period:
        target_reservations.append(req)

if search_query:
    target_reservations = [req for req in target_reservations if search_query in req["name"] or search_query in req["furigana"]]

target_reservations.sort(key=lambda x: (x["date"], x["time"]))

# --- 2. 経営指標（KPI）ダッシュボード ---
st.markdown("---")
st.markdown(f"### 📊 指定期間（{period_option}）の予約サマリー")
col1, col2, col3 = st.columns(3)
col1.metric("指定期間内の総予約数", f"{len(target_reservations)} 件")

st.markdown("---")

# --- 3. 自動振り分けタブシステム ---
CATEGORY_TABS = ["すべて"] + services
tabs = st.tabs(CATEGORY_TABS)

for i, tab_name in enumerate(CATEGORY_TABS):
    with tabs[i]:
        if tab_name == "すべて":
            filtered_res = target_reservations
        else:
            filtered_res = [req for req in target_reservations if req["service"] == tab_name]
        
        if not filtered_res:
            st.info(f"システムからのご案内：このカテゴリ（{tab_name}）には、指定された期間内に予約が入っておりません。")
        else:
            for req in filtered_res:
                # 読者の指示通り、日付と時間の間にカテゴリを大きく挿入し、フルネーム・フリガナを表示いたします
                st.markdown(f"""
                <div style="border:2px solid #d9b38c; border-radius: 8px; padding: 15px; margin-bottom: 15px; background-color: #fdfaf6; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h4 style="margin:0; color:#333333; display:flex; align-items:center; flex-wrap:wrap;">
                        📅 {req['date']} 
                        <span style="font-size:1.4em; font-weight:bold; color:#d9b38c; margin: 0 10px;">【{req['service']}】</span> 
                        ⏰ {req['time']} - {req['name']}（{req['furigana']}）様
                    </h4>
                    <hr style="margin: 10px 0; border: none; border-top: 1px dashed #d9b38c;">
                    <p style="margin:0; color:#555555; font-size: 16px; line-height: 1.6;">
                        <b>指名担当者:</b> {req['staff']} <br>
                        <b>現在の状況:</b> <span style="color:white; background-color:green; padding: 2px 8px; border-radius: 4px; font-size: 14px; font-weight:bold;">{req['status']}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
