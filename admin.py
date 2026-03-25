import streamlit as st
from datetime import datetime, timedelta
import random

# ⚙️ 管理者画面 UI レイアウト設定
VERSION = "v1.0.0 (Admin Dashboard)"
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

# 1. カレンダーによる日付選択機能
selected_date = st.date_input("システムから予約を呼び出したい日付を、カレンダーから選択してください")

st.markdown("---")
st.markdown(f"#### 📝 {selected_date} の予約リスト")

# 2. 選択された日付のデータのみをシステムが抽出し、時間順に並べ替えます
day_reservations = [req for req in st.session_state.admin_db if req["date"] == selected_date]
day_reservations.sort(key=lambda x: x["time"])

# 3. ノードベース（カード形式）での詳細表示
if not day_reservations:
    st.info("システムからのご案内：選択された日付には、現在予約が入っておりません。")
else:
    for req in day_reservations:
        with st.container():
            # HTMLとCSSを用いて、情報を枠で囲み、直感的に見やすいカード型のデザインを構築いたします
            st.markdown(f"""
            <div style="border:2px solid #d9b38c; border-radius: 8px; padding: 15px; margin-bottom: 10px; background-color: #fdfaf6;">
                <h4 style="margin:0; color:#333333;">⏰ {req['time']} - {req['name']} 様</h4>
                <p style="margin:8px 0 0 0; color:#555555; font-size: 16px;">
                    <b>予約サービス:</b> {req['service']} <br>
                    <b>指名担当者:</b> {req['staff']} <br>
                    <b>現在の状況:</b> <span style="color:green; font-weight:bold;">{req['status']}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
