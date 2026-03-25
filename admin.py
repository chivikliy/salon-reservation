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
selected_date = st.sidebar.date_input("確認する日付をカレンダーから選択", datetime.today().date())
search_query = st.sidebar.text_input("お客様のお名前で検索（任意）")

# システムが選択された日付のデータを抽出し、検索条件があればさらに絞り込みます
day_reservations = [req for req in st.session_state.admin_db if req["date"] == selected_date]
if search_query:
    day_reservations = [req for req in day_reservations if search_query in req["name"]]
day_reservations.sort(key=lambda x: x["time"])

# --- 2. 経営指標（KPI）ダッシュボード ---
st.markdown("---")
st.markdown(f"### 📊 {selected_date} の予約サマリー")
col1, col2, col3 = st.columns(3)
col1.metric("本日の総予約数", f"{len(day_reservations)} 件")
# 管理者が直感的に把握できるよう、指標を最上部に配置いたしました

st.markdown("---")

# --- 3. 自動振り分けタブシステム（読者の画像に基づく完全再現） ---
CATEGORY_TABS = ["すべて", "✂️ ヘア", "💆‍♀️ スパ", "👘 着付け", "💅 ネイル", "🧘 瞑想教室", "🦷 歯医者"]
tabs = st.tabs(CATEGORY_TABS)

for i, tab_name in enumerate(CATEGORY_TABS):
    with tabs[i]:
        # システムが各タブに合わせてデータを自動で振り分けます
        if tab_name == "すべて":
            filtered_res = day_reservations
        else:
            filtered_res = [req for req in day_reservations if req["service"] == tab_name]
        
        # 4. ノードベース（カード形式）での詳細表示
        if not filtered_res:
            st.info(f"システムからのご案内：このカテゴリ（{tab_name}）には、現在予約が入っておりません。")
        else:
            for req in filtered_res:
                # 視認性を極限まで高めた美しいカードデザイン
                st.markdown(f"""
                <div style="border:2px solid #d9b38c; border-radius: 8px; padding: 15px; margin-bottom: 15px; background-color: #fdfaf6; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h4 style="margin:0; color:#333333;">⏰ {req['time']} - {req['name']} 様</h4>
                    <hr style="margin: 10px 0; border: none; border-top: 1px dashed #d9b38c;">
                    <p style="margin:0; color:#555555; font-size: 16px; line-height: 1.6;">
                        <b>カテゴリ:</b> {req['service']} <br>
                        <b>指名担当者:</b> {req['staff']} <br>
                        <b>現在の状況:</b> <span style="color:white; background-color:green; padding: 2px 8px; border-radius: 4px; font-size: 14px; font-weight:bold;">{req['status']}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
