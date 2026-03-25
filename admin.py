import streamlit as st
from datetime import datetime, timedelta
import random

# ⚙️ 管理者画面 UI レイアウト設定
VERSION = "v2.0.0 (Admin Dashboard)" # 高度な管理機能と自動タブ振り分けを追加
st.set_page_config(page_title=f"サロン管理者ダッシュボード {VERSION}", layout="wide")

st.title("管理者専用ダッシュボード")
st.markdown("### 📅 日別予約カレンダー確認システム")

# データベース接続前のテスト用ダミーデータ生成システム
if 'admin_db' not in st.session_state:
    st.session_state.admin_db = []
    # システムが今日から3日間のダミーデータを20件作成いたします
    dummy_names = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "小林"]
    staff_list = ["田中", "佐藤", "鈴木", "専属着付師 山田", "高橋", "インストラクター 伊藤", "院長希望"]
    services = ["✂️ ヘア", "💆‍♀️ スパ", "👘 着付け", "💅 ネイル", "🧘 瞑想教室", "🦷 歯医者"]
    times = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    today = datetime.today().date()
    
    for i in range(20):
        r_date = today + timedelta(days=random.randint(0, 2))
        r_time = random.choice(times)
        r_name = random.choice(dummy_names)
        r_staff = random.choice(staff_list)
        r_service = random.choice(services)
        
        st.session_state.admin_db.append({
            "date": r_date,
            "time": r_time,
            "name": r_name,
            "staff": r_staff,
            "service": r_service,
            "status": "予約確定"
        })

# --- 1. 高度なフィルター機能（サイドバー） ---
st.sidebar.markdown("### 🔍 予約フィルター")

# システムが期間を細かく指定できる選択肢を提示いたします
period_option = st.sidebar.selectbox(
    "検索する期間の単位を指定してください",
    ["1日単位", "1週間単位", "2週間単位", "3週間単位", "月単位", "年単位", "全日程"]
)

# 全日程以外の場合、システムは基準となる日付をカレンダーから取得いたします
if period_option != "全日程":
    base_date = st.sidebar.date_input("基準となる日付をカレンダーから選択してください", datetime.today().date())
else:
    base_date = datetime.today().date()

search_query = st.sidebar.text_input("お客様のお名前で検索（任意）")

# システムが選択された期間のデータを抽出いたします
from datetime import timedelta

target_reservations = []
for req in st.session_state.admin_db:
    req_date = req["date"]
    
    # 期間条件の厳密な判定を行います
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

# 名前の検索条件があれば、システムはさらに絞り込みを行います
if search_query:
    target_reservations = [req for req in target_reservations if search_query in req["name"]]

# 複数日のデータが混ざるため、日付と時間の両方で順番に並べ替えます
target_reservations.sort(key=lambda x: (x["date"], x["time"]))

# --- 2. 経営指標（KPI）ダッシュボード ---
st.markdown("---")
st.markdown(f"### 📊 指定期間（{period_option}）の予約サマリー")
col1, col2, col3 = st.columns(3)
col1.metric("指定期間内の総予約数", f"{len(target_reservations)} 件")

st.markdown("---")

# --- 3. 自動振り分けタブシステム ---
CATEGORY_TABS = ["すべて", "✂️ ヘア", "💆‍♀️ スパ", "👘 着付け", "💅 ネイル", "🧘 瞑想教室", "🦷 歯医者"]
tabs = st.tabs(CATEGORY_TABS)

for i, tab_name in enumerate(CATEGORY_TABS):
    with tabs[i]:
        # システムが各タブに合わせてデータを自動で振り分けます
        if tab_name == "すべて":
            filtered_res = target_reservations
        else:
            filtered_res = [req for req in target_reservations if req["service"] == tab_name]
        
        # 4. ノードベース（カード形式）での詳細表示
        if not filtered_res:
            st.info(f"システムからのご案内：このカテゴリ（{tab_name}）には、指定された期間内に予約が入っておりません。")
        else:
            for req in filtered_res:
                # 複数日の予約を区別できるよう、日付の表示をカードに追加いたしました
                st.markdown(f"""
                <div style="border:2px solid #d9b38c; border-radius: 8px; padding: 15px; margin-bottom: 15px; background-color: #fdfaf6; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h4 style="margin:0; color:#333333;">📅 {req['date']} ⏰ {req['time']} - {req['name']} 様</h4>
                    <hr style="margin: 10px 0; border: none; border-top: 1px dashed #d9b38c;">
                    <p style="margin:0; color:#555555; font-size: 16px; line-height: 1.6;">
                        <b>カテゴリ:</b> {req['service']} <br>
                        <b>指名担当者:</b> {req['staff']} <br>
                        <b>現在の状況:</b> <span style="color:white; background-color:green; padding: 2px 8px; border-radius: 4px; font-size: 14px; font-weight:bold;">{req['status']}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
