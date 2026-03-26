import streamlit as st
from datetime import datetime, timedelta, date
import sqlite3
import pandas as pd
import re
import time
import uuid

# ⚙️ UI レイアウト設定
# v9.0.0：フルスタック・マスター統合復元版（EC、キャンセル、スパム対策、詳細フィルターをエラーフリーで全復元）
VERSION = "v9.0.0 ( フルスタック完全復元版 )"
DB_FILE = "salon_fullstack.db"

BASE_BG = "#fdfaf6"
BASE_TEXT = "#333333"
ACCENT_GOLD = "#d9b38c"

st.set_page_config(page_title=f"Dr's Salon LAB {VERSION}", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {BASE_BG}; color: {BASE_TEXT}; font-size: 13.5px; }}
    div.stButton > button:first-child {{
        background-color: {ACCENT_GOLD}; color: white;
        border-radius: 6px; border: none; width: 100%; font-weight: bold; padding: 10px;
    }}
    .stTabs [data-baseweb="tab-list"] button {{ color: #777777; font-weight: bold; padding: 8px 10px; }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{ color: {BASE_TEXT}; border-bottom-color: {ACCENT_GOLD}; }}
    .config-box {{ border: 1px solid #eaddd0; border-radius: 8px; padding: 15px; background-color: #ffffff; margin-bottom: 20px; }}
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------------
# --- 1. データベース層 (完全復元) ---
# -------------------------------------------------------------------------------------------------------
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def initialize_database():
    conn = get_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT, phone TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, price INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS bookings (id TEXT PRIMARY KEY, user_id TEXT, service_id INTEGER, staff TEXT, date TEXT, time TEXT, status TEXT)')
    
    # サービスの初期データ
    if c.execute('SELECT count(*) FROM services').fetchone()[0] == 0:
        c.executemany('INSERT INTO services (name, category, price) VALUES (?, ?, ?)', [
            ("Dr's LAB 根本改善カット", "ヘア", 6600), ("T-Crystalカラー＋根本改善カット", "ヘア", 11000),
            ("極上エナジースカルプスパ(60分)", "スパ", 8000), ("リバースエイジングスパ(45分)", "スパ", 6000),
            ("訪問着 着付け", "着付け", 8800), ("ジェルネイル", "ネイル", 5000), ("歯科検診", "歯医者", 0)
        ])
    # EC商品の初期データ（復元）
    if c.execute('SELECT count(*) FROM products').fetchone()[0] == 0:
        c.executemany('INSERT INTO products (name, price) VALUES (?, ?)', [
            ("シャンティン＋シャンプー(360mL)", 7920), ("ヴェーダ＋シャンプー(360mL)", 7480),
            ("オペラ ボタニカルヘアオイル(80mL)", 4290), ("テネット 乳液トリートメント(100g)", 3300)
        ])
    conn.commit()
    conn.close()

initialize_database()

# グローバル定数
CATEGORY_TABS = ["ヘア", "スパ", "着付け", "ネイル", "歯医者"]
ALL_TIME_SLOTS = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
STAFF_LIST = ["関根 光代", "田中 健太", "佐藤 美咲", "鈴木 翔太", "山田 花子", "高橋 陽子"]

# 🛡️ 【絶対防御】日付変換関数
def get_safe_date(date_value):
    if isinstance(date_value, date) and not isinstance(date_value, datetime): return date_value
    if isinstance(date_value, datetime): return date_value.date()
    if isinstance(date_value, str):
        try: return datetime.strptime(date_value[:10], "%Y-%m-%d").date()
        except: pass
    return datetime.today().date()

# --- CRUDヘルパー関数 ---
def get_user(name, phone):
    conn = get_connection()
    user = conn.execute('SELECT * FROM users WHERE name = ? AND phone = ?', (name, phone)).fetchone()
    conn.close()
    return user

def create_user(name, phone):
    user_id = str(uuid.uuid4())
    conn = get_connection()
    conn.execute('INSERT INTO users VALUES (?, ?, ?)', (user_id, name, phone))
    conn.commit()
    conn.close()
    return user_id

def create_booking(user_id, service_id, staff, date_str, time_str):
    booking_id = str(uuid.uuid4())
    conn = get_connection()
    conn.execute('INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?, ?)', (booking_id, user_id, service_id, staff, date_str, time_str, '予約確定'))
    conn.commit()
    conn.close()

def cancel_booking(booking_id):
    conn = get_connection()
    conn.execute('UPDATE bookings SET status = ? WHERE id = ?', ('キャンセル済み', booking_id))
    conn.commit()
    conn.close()

def format_phone_number(phone_input):
    digits = re.sub(r'\D', '', phone_input.translate(str.maketrans('０１２３４５６７８９', '0123456789')))
    if len(digits) == 11: return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    return digits

# セッションステート初期化
if 'load_time' not in st.session_state: st.session_state.load_time = time.time()
st.session_state.setdefault('pers_name', '')
st.session_state.setdefault('pers_phone', '')

# -------------------------------------------------------------------------------------------------------
# --- 2. 顧客画面 (予約・EC・キャンセル 完全復元) ---
# -------------------------------------------------------------------------------------------------------
def customer_page():
    st.title("Dr's Salon LAB 予約システム")
    st.markdown("### 1. ログイン ＆ お客様情報")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("お名前（フルネーム）", value=st.session_state.pers_name)
    with col2:
        raw_phone = st.text_input("電話番号", value=st.session_state.pers_phone)
        phone = format_phone_number(raw_phone)
        
    st.session_state.pers_name = name
    st.session_state.pers_phone = phone

    user = None
    if name and phone:
        user = get_user(name, phone)
        if not user:
            if st.button("お客様情報をシステムに登録する"):
                create_user(name, phone)
                st.rerun()
        else:
            st.success(f"✅ {name} 様、ログインいたしました。")

    if user:
        st.divider()
        st.markdown("### 2. サービスメニュー")
        
        main_tab, cart_tab, cancel_tab = st.tabs(["🗓️ 予約フォーム", "🛒 Precious EC", "❌ 予約確認・キャンセル"])
        
        # --- 予約フォーム ---
        with main_tab:
            conn = get_connection()
            services_df = pd.read_sql_query('SELECT * FROM services', conn)
            conn.close()
            
            d = st.date_input("ご希望の予約日を選択してください", datetime.today().date())
            
            with st.form(key="booking_form"):
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    sel_cat = st.selectbox("カテゴリ", CATEGORY_TABS)
                    filtered_services = services_df[services_df['category'] == sel_cat]
                    if not filtered_services.empty:
                        sel_menu_name = st.selectbox("メニュー", filtered_services['name'].tolist())
                        sel_service = filtered_services[filtered_services['name'] == sel_menu_name].iloc[0]
                    else:
                        st.warning("このカテゴリにはメニューがありません。")
                        sel_service = None
                    sel_staff = st.selectbox("担当者", STAFF_LIST)
                
                with col_b2:
                    if sel_service is not None:
                        # データベースから空き時間を計算
                        conn = get_connection()
                        booked = conn.execute('SELECT time FROM bookings WHERE date = ? AND staff = ? AND status != ?', (str(d), sel_staff, 'キャンセル済み')).fetchall()
                        conn.close()
                        booked_times = [r[0] for r in booked]
                        available_times = [t for t in ALL_TIME_SLOTS if t not in booked_times]
                        
                        if available_times:
                            t = st.radio("空いている時間スロット", available_times, horizontal=True)
                        else:
                            st.error("予約が埋まっています。")
                            t = None
                
                confirm = st.checkbox("内容を確認しました")
                if st.form_submit_button("予約を確定する"):
                    if time.time() - st.session_state.load_time < 2.0:
                        st.error("システム案内: ロボット行為を防ぐためブロックされました。再度お試しください。")
                    elif not confirm or not t or sel_service is None:
                        st.error("入力内容に不備があります。")
                    else:
                        create_booking(user[0], sel_service['id'], sel_staff, str(d), t)
                        st.balloons()
                        st.success("🎉 予約が確定されました！")

        # --- ECショッピングカート (復元) ---
        with cart_tab:
            st.markdown("#### Precious EC 商品購入")
            conn = get_connection()
            products_df = pd.read_sql_query('SELECT * FROM products', conn)
            conn.close()
            
            products_df['カートに追加'] = False
            edited_products = st.data_editor(products_df, key="cart", disabled=['id', 'name', 'price'], hide_index=True)
            selected = edited_products[edited_products['カートに追加']]
            
            if not selected.empty:
                st.markdown("**🛒 カートの中身**")
                for _, row in selected.iterrows():
                    st.code(f"{row['name']} | ¥{row['price']}")
                st.markdown(f"#### 合計: ¥{selected['price'].sum()}")
                if st.button("決済画面へ (模擬)"):
                    st.success("Stripe決済へ移行します（プロトタイプ）。")

        # --- 予約確認・キャンセル (復元) ---
        with cancel_tab:
            st.markdown("#### 現在の予約状況")
            conn = get_connection()
            my_bookings = pd.read_sql_query('SELECT b.*, s.name as s_name, s.category as s_cat FROM bookings b JOIN services s ON b.service_id = s.id WHERE b.user_id = ? AND b.status != ?', conn, params=(user[0], 'キャンセル済み'))
            conn.close()
            
            if my_bookings.empty:
                st.info("確定している予約はありません。")
            else:
                for _, row in my_bookings.iterrows():
                    st.markdown(f"""
                        <div style="border:1px solid #eaddd0; border-radius: 8px; padding: 12px; margin-bottom: 10px; background-color: #ffffff;">
                            <h4 style="margin:0;">📅 {row['date']} <span style="color:{ACCENT_GOLD};">【{row['s_cat']}】</span> ⏰ {row['time']}</h4>
                            <p style="margin:5px 0 0 0;">担当: {row['staff']} | メニュー: {row['s_name']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("❌ キャンセルする", key=f"cancel_{row['id']}"):
                        cancel_booking(row['id'])
                        st.rerun()

# -------------------------------------------------------------------------------------------------------
# --- 3. 管理者画面 (詳細フィルター・リスト表示 完全復元) ---
# -------------------------------------------------------------------------------------------------------
def admin_page():
    st.sidebar.markdown("### 🔐 管理者認証")
    aid = st.sidebar.text_input("ID (admin)", key="aid")
    apw = st.sidebar.text_input("PW (1234)", type="password", key="apw")
    
    if aid == "admin" and apw == "1234":
        st.title("管理者専用ダッシュボード")
        
        # --- 詳細フィルター (復元) ---
        st.sidebar.markdown("### 🔍 予約フィルター")
        period = st.sidebar.selectbox("表示期間", ["1日単位", "1週間単位", "全日程"])
        base_date = st.sidebar.date_input("基準日", datetime.today().date()) if period != "全日程" else datetime.today().date()
        search_q = st.sidebar.text_input("お名前で検索")
        
        # データベースから全予約を取得
        conn = get_connection()
        all_bookings = pd.read_sql_query('SELECT b.*, u.name as u_name, u.phone as u_phone, s.name as s_name, s.category as s_cat FROM bookings b JOIN users u ON b.user_id = u.id JOIN services s ON b.service_id = s.id', conn)
        conn.close()
        
        # フィルター適用 (安全な日付計算)
        all_bookings['safe_date'] = all_bookings['date'].apply(get_safe_date)
        
        if period == "1日単位":
            filtered = all_bookings[all_bookings['safe_date'] == base_date]
        elif period == "1週間単位":
            filtered = all_bookings[(all_bookings['safe_date'] >= base_date) & (all_bookings['safe_date'] <= base_date + timedelta(days=6))]
        else:
            filtered = all_bookings
            
        if search_q:
            filtered = filtered[filtered['u_name'].str.contains(search_q, na=False)]
            
        filtered = filtered.sort_values(by=['safe_date', 'time'])
        
        # ダッシュボード表示
        st.metric(f"総予約件数 ({period})", f"{len(filtered)} 件")
        st.divider()
        
        admin_tabs = st.tabs(["すべて"] + CATEGORY_TABS + ["EC商品管理"])
        
        def display_list(df):
            if df.empty:
                st.write("該当する予約はありません。")
            else:
                for _, row in df.iterrows():
                    st.markdown(f"""
                        <div style="border:1px solid #eaddd0; border-radius: 8px; padding: 12px; margin-bottom: 10px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-size: 13.5px;">
                            <h4 style="margin:0; color:#333333; display:flex; align-items:center; flex-wrap:wrap;">
                                📅 {row['date']} 
                                <span style="font-weight:bold; color:{ACCENT_GOLD}; margin: 0 8px;">【{row['s_cat']}】</span> 
                                ⏰ {row['time']} - {row['u_name']} 様
                            </h4>
                            <p style="margin:8px 0 0 0; color:#555555;">
                                <b>担当:</b> {row['staff']} &nbsp;&nbsp;|&nbsp;&nbsp;
                                <b>状況:</b> <span style="color:#2e8b57; font-weight:bold;">{row['status']}</span>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    
        for i, tab_name in enumerate(["すべて"] + CATEGORY_TABS):
            with admin_tabs[i]:
                if tab_name == "すべて":
                    display_list(filtered)
                else:
                    display_list(filtered[filtered['s_cat'] == tab_name])
                    
        with admin_tabs[6]:
            st.markdown("#### EC商品データベース管理")
            conn = get_connection()
            p_df = pd.read_sql_query('SELECT * FROM products', conn)
            conn.close()
            st.data_editor(p_df, key="admin_products", disabled=['id'])
            st.info("データベースへの直接編集は、本番環境移行時に完全実装されます。")
            
    else:
        st.warning("左側のサイドバーから管理者ID(admin)とパスワード(1234)を入力してください。")

# -------------------------------------------------------------------------------------------------------
# --- 4. システム構成解説 ＆ メイン ---
# -------------------------------------------------------------------------------------------------------
def system_config_page():
    st.title("🛠 フルスタック・システム構成解説")
    st.markdown("### AWS クラウド・アーキテクチャ詳細 (画像 17255a.png 参考)")
    st.markdown("""
    <div class="config-box">
        <h4>🌐 1. フロントエンド ＆ エッジセキュリティ</h4>
        <p><b>Route 53 / CloudFront / AWS WAF:</b> ドメイン管理、高速配信、およびスパム攻撃からの鉄壁の防御を担当。</p>
    </div>
    <div class="config-box">
        <h4>🚀 2. アプリケーション層 (コンピューティング)</h4>
        <p><b>ALB / EC2 (Auto Scaling):</b> Pythonが稼働する仮想サーバー。予約集中時に自動で増設され、システムダウンを防ぐ。</p>
    </div>
    <div class="config-box">
        <h4>💾 3. データ ＆ ストレージ層</h4>
        <p><b>Amazon RDS (PostgreSQL) / S3:</b> このアプリで使用しているSQLiteを、本番環境ではRDSへ移行し堅牢にデータを保護。</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.sidebar.title("MENU")
    mode = st.sidebar.radio("モード切替", ["顧客画面", "管理者画面", "システム構成解説"])
    
    if mode == "顧客画面":
        customer_page()
    elif mode == "管理者画面":
        admin_page()
    elif mode == "システム構成解説":
        system_config_page()

if __name__ == "__main__":
    main()
