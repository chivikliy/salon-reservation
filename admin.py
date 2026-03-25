import streamlit as st
from datetime import datetime, timedelta, date
import random

# ⚙️ 管理者画面 UI レイアウト設定
# v6.1.0：予約ページへの相互リンク、コンパクトUI、鉄壁のエラー対策
VERSION = "v6.1.0 (Admin 相互リンク・鉄壁版)"

BASE_BG = "#fdfaf6"
BASE_TEXT = "#333333"
ACCENT_GOLD = "#d9b38c"

st.set_page_config(page_title=f"サロン管理者ダッシュボード {VERSION}", layout="wide")

# Figma的UI設計：フォントサイズと余白を詰めたコンパクトCSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BASE_BG}; color: {BASE_TEXT}; font-size: 14px; }}
    h1 {{ font-size: 1.6em !important; margin-bottom: 0.2em !important; }}
    h3 {{ font-size: 1.1em !important; margin-top: 0.2em !important; }}
    [data-testid="stSidebar"] {{ background-color: #f7f3ed; border-right: 1px solid #eaddd0; }}
    /* リンクボタンを強調するデザイン */
    .nav-link-btn {{
        display: inline-block; padding: 8px 16px; background-color: {ACCENT_GOLD};
        color: white !important; text-decoration: none; border-radius: 6px;
        font-weight: bold; font-size: 13px; text-align: center; margin-bottom: 20px;
    }}
    .nav-link-btn:hover {{ background-color: #c79a72; }}
    </style>
""", unsafe_allow_html=True)

st.title("管理者専用ダッシュボード")

# --- 1. 相互リンクエリア（サイドバー最上部） ---
# 【新機能】お客様予約ページへ飛ぶためのリンクを設置いたしました
st.sidebar.markdown("### 🔗 ナビゲーション")
# 注意：URL部分は読者が実際に公開している予約ページのURLに書き換えてください
st.sidebar.markdown('<a href="https://app-py-xxxx.streamlit.app/" target="_blank" class="nav-link-btn">👉 お客様用予約ページを開く</a>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# 予約履歴とデータの準備
if 'admin_db' not in st.session_state:
    st.session_state.admin_db = []
    # （中略：ダミーデータ生成ロジックは維持）
    dummy_data = [("佐藤 健太", "サトウ ケンタ"), ("鈴木 美咲", "スズキ ミサキ")]
    staff_list = ["関根 光代", "田中 健太", "佐藤 美咲", "鈴木 翔太", "山田 花子", "高橋 陽子"]
    services = ["ヘア", "スパ", "着付け", "ネイル", "歯医者"]
    times = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    today_date = datetime.today().date()
    for day_offset in range(10):
        target_date = today_date + timedelta(days=day_offset)
        st.session_state.admin_db.append({
            "date": target_date, "time": random.choice(times),
            "name": dummy_data[0][0], "furigana": dummy_data[0][1],
            "staff": random.choice(staff_list), "service": random.choice(services), "status": "予約確定"
        })

# 日付変換の安全装置
def get_safe_date(date_value):
    if isinstance(date_value, date) and not isinstance(date_value, datetime): return date_value
    if isinstance(date_value, datetime): return date_value.date()
    if isinstance(date_value, str):
        try: return datetime.strptime(date_value[:10], "%Y-%m-%d").date()
        except: pass
    return datetime.today().date()

# --- 2. 検索・フィルターエリア ---
st.sidebar.markdown("### 🔍 予約フィルター")
period_option = st.sidebar.selectbox("表示期間", ["1日単位", "1週間単位", "2週間単位", "全日程"])
base_date = st.sidebar.date_input("基準日", datetime.today().date()) if period_option != "全日程" else datetime.today().date()
search_query = st.sidebar.text_input("お名前検索")

# データ抽出ロジック
target_reservations = []
for req in st.session_state.admin_db:
    req_date = get_safe_date(req.get("date"))
    is_in_period = False
    if period_option == "全日程": is_in_period = True
    elif period_option == "1日単位": is_in_period = (req_date == base_date)
    elif period_option == "1週間単位": is_in_period = (base_date <= req_date <= base_date + timedelta(days=6))
    if is_in_period: target_reservations.append(req)

if search_query:
    target_reservations = [req for req in target_reservations if search_query in req.get("name", "") or search_query in req.get("furigana", "")]

target_reservations.sort(key=lambda x: (get_safe_date(x.get("date")), x.get("time", "00:00")))
MAX_DISPLAY = 200
display_reservations = target_reservations[:MAX_DISPLAY]

# --- 3. 表示エリア ---
st.markdown(f"### 📊 予約サマリー（{period_option}）")
st.metric("総予約数", f"{len(target_reservations)} 件")

CATEGORY_TABS = ["すべて", "ヘア", "スパ", "着付け", "ネイル", "歯医者"]
tabs = st.tabs(CATEGORY_TABS)

for i, tab_name in enumerate(CATEGORY_TABS):
    with tabs[i]:
        res = display_reservations if tab_name == "すべて" else [r for r in display_reservations if r.get("service") == tab_name]
        if not res:
            st.write("予約はありません。")
        else:
            for req in res:
                st.markdown(f"""
                <div style="border:1px solid #eaddd0; border-radius: 8px; padding: 12px; margin-bottom: 10px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-size: 13px;">
                    <h4 style="margin:0; font-size: 1.1em;">
                        📅 {str(req.get('date'))[:10]} <span style="color:{ACCENT_GOLD};">【{req.get('service')}】</span> ⏰ {req.get('time')} - {req.get('name')}様
                    </h4>
                </div>
                """, unsafe_allow_html=True)

# データベースリセット
st.sidebar.markdown("---")
if st.sidebar.button("⚙️ データをリセット"):
    st.session_state.admin_db = []
    st.rerun()
