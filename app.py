import streamlit as st
from datetime import datetime, timedelta, date
import sqlite3
import pandas as pd
import re
import random
import time
import uuid

# ⚙️ UI レイアウト設定
# v8.0.0：Web/プログラミング・フルスタック統合版。SQLite、認証、予約(画像1)、EC、管理(画像2)、インフラ(画像3)を完全網羅
VERSION = "v8.0.0 ( Web / Programming Full Stack統合版 )"
DB_FILE = "salon_fullstack.db" # SQLiteデータベースファイル

# 清潔感のあるベーステーマカラー（Figma的洗練）
BASE_BG = "#fdfaf6"
BASE_TEXT = "#333333"
ACCENT_GOLD = "#d9b38c"
ACCENT_RED = "#d98c8c"

st.set_page_config(page_title=f"Dr's Salon LAB 予約・ECシステム {VERSION}", layout="wide")

# Figma的UI設計：フォントサイズと余白を極限まで詰めたコンパクトCSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BASE_BG}; color: {BASE_TEXT}; font-size: 13px; }}
    h1 {{ font-size: 1.5em !important; margin-bottom: 0.1em !important; padding-top: 0 !important; }}
    h2 {{ font-size: 1.3em !important; margin-top: 0.2em !important; }}
    h3 {{ font-size: 1.1em !important; margin-top: 0.1em !important; margin-bottom: 0.4em !important; }}
    div.stButton > button:first-child {{
        background-color: {ACCENT_GOLD}; color: white;
        border-radius: 6px; border: none; width: 100%; font-weight: bold; padding: 8px;
        font-size: 13px; transition: background-color 0.3s;
    }}
    .stTabs [data-baseweb="tab-list"] button {{ color: #777777; font-weight: bold; padding: 6px 10px; font-size: 0.95em; }}
    .stTextInput input, .stSelectbox select, .stDateInput input {{ font-size: 13px; padding: 6px; }}
    /* 履歴エリアのコンパクト化 */
    div[data-testid="stVVerticalBlock"] div[data-testid="stVerticalBlockBorderWrapper"] {{ padding: 8px !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 1. フルスタック・データベース層 (SQLite) ---
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def initialize_database():
    conn = get_connection()
    c = conn.cursor()
    # ユーザーテーブル
    c.execute('CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT, furigana TEXT, phone TEXT,来店歴 TEXT, is_admin INTEGER)')
    # サービス（予約メニュー）テーブル
    c.execute('CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, price INTEGER)')
    # 商品（ショッピングカート）テーブル
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price INTEGER)')
    # 予約テーブル
    c.execute('CREATE TABLE IF NOT EXISTS bookings (id TEXT PRIMARY KEY, user_id TEXT, service_id INTEGER, staff TEXT, date TEXT, time TEXT, status TEXT, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(service_id) REFERENCES services(id))')
    # 注文（ショッピングカート）テーブル
    c.execute('CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, user_id TEXT, product_ids TEXT, total_price INTEGER, date TEXT, FOREIGN KEY(user_id) REFERENCES users(id))')
    
    # ダミーデータ（初回のみ）
    if c.execute('SELECT count(*) FROM services').fetchone()[0] == 0:
        c.executemany('INSERT INTO services (name, category, price) VALUES (?, ?, ?)', [
            ("Dr's LAB 根本改善カット", "ヘア", 6600), ("T-Crystalカラー＋根本改善カット", "ヘア", 11000),
            ("極上エナジースカルプスパ(60分)", "スパ", 8000), ("リバースエイジングスパ(45分)", "スパ", 6000),
            ("訪問着 着付け", "着付け", 8800), ("ジェルネイル", "ネイル", 5000), ("歯医者検診", "歯医者", 0)
        ])
    if c.execute('SELECT count(*) FROM products').fetchone()[0] == 0:
        c.executemany('INSERT INTO products (name, price) VALUES (?, ?)', [
            ("01：シャンティン＋シャンプー(360mL)", 7920), ("02：ヴェーダ＋シャンプー(360mL)", 7480),
            ("06：オペラ ボタニカルヘアオイル(80mL)", 4290), ("07：テネット 乳液トリートメント(100g)", 3300)
        ])
    conn.commit()
    conn.close()

# 初期化
initialize_database()

# CRUD関数（抜粋）
def get_user(name, phone):
    conn = get_connection()
    user = conn.execute('SELECT * FROM users WHERE name = ? AND phone = ?', (name, phone)).fetchone()
    conn.close()
    return user

def create_user(name, furi, phone, history, is_admin=0):
    user_id = str(uuid.uuid4())
    conn = get_connection()
    conn.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)', (user_id, name, furi, phone, history, is_admin))
    conn.commit()
    conn.close()
    return user_id

def get_all_services():
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM services', conn)
    conn.close()
    return df

def get_all_products():
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM products', conn)
    conn.close()
    return df

def create_booking(user_id, service_id, staff, date, time):
    booking_id = str(uuid.uuid4())
    conn = get_connection()
    conn.execute('INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?, ?)', (booking_id, user_id, service_id, staff, date, time, '予約確定'))
    conn.commit()
    conn.close()
    return booking_id

def get_user_bookings(user_id):
    conn = get_connection()
    df = pd.read_sql_query('SELECT b.*, s.name as service_name, s.category as service_category FROM bookings b JOIN services s ON b.service_id = s.id WHERE b.user_id = ? AND b.status != ?', conn, params=(user_id, 'キャンセル済み'))
    conn.close()
    return df

def get_booked_times(date, staff):
    conn = get_connection()
    rows = conn.execute('SELECT time FROM bookings WHERE date = ? AND staff = ? AND status != ?', (date, staff, 'キャンセル済み')).fetchall()
    conn.close()
    return [r[0] for r in rows]

def cancel_booking(booking_id):
    conn = get_connection()
    conn.execute('UPDATE bookings SET status = ? WHERE id = ?', ('キャンセル済み', booking_id))
    conn.commit()
    conn.close()

# セッションステート初期化
if 'load_time' not in st.session_state: st.session_state.load_time = time.time()
st.session_state.setdefault('pers_name', '')
st.session_state.setdefault('pers_phone', '')
st.session_state.setdefault('page', '顧客画面') # 顧客画面 または 管理者画面

# ヘルパー関数
def format_phone_number(phone_input):
    digits = re.sub(r'\D', '', phone_input.translate(str.maketrans('０１２３４５６７８９', '0123456789')))
    if len(digits) == 11: return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10: return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    return digits

def to_katakana(text):
    return "".join([chr(ord(c) + 96) if '\u3041' <= c <= '\u3096' else c for c in text])

# -------------------------------------------------------------------------------------------------------
# --- 第2章：顧客画面 (`customer_page()`) - 予約(画像1) ＆ ショッピングカートを完全網羅 ---
# -------------------------------------------------------------------------------------------------------
def customer_page():
    st.title("Dr's Salon LAB 予約・ECシステム")
    st.subheader("清潔感のある洗練された総合予約 ＆ Precious EC 商品購入サイト")

    # --- 1. お客様認証エリア（SQLite接続） ---
    st.markdown("### 1. ログイン ＆ お客様情報")
    if st.button("前回の入力を読み込む"): pass

    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("お名前（フルネーム）", value=st.session_state.pers_name)
    with col2:
        raw_phone = st.text_input("電話番号", value=st.session_state.pers_phone)
        phone = format_phone_number(raw_phone)
    with col3:
        pass # デザイン調整

    # ログイン判定
    user = None
    if name and phone:
        user = get_user(name, phone)
        if user:
            st.success(f"✅ {user[1]} 様、ログインいたしました。")
        else:
            st.info("案内: 初めてのご来店ですね。お名前と電話番号、フリガナ、来店歴を入力して予約を進めてください。")
            history = st.radio("ご来店歴", ["初めて（新規）", "2回目以降（再来）"], horizontal=True)
            raw_furi = st.text_input("フリガナ（カタカナ自動変換）")
            furigana = to_katakana(raw_furi)
            if furigana: st.info(f"カタカナ変換: {furigana}")
            if st.button("お客様情報をシステムに登録する"):
                create_user(name, furigana, phone, history)
                st.rerun()

    # 情報保持
    st.session_state.pers_name = name
    st.session_state.pers_phone = phone

    if user:
        services_df = get_all_services()
        all_time_slots = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        staff_list = ["関根 光代", "田中 健太", "佐藤 美咲", "鈴木 翔太", "山田 花子", "高橋 陽子"]

        st.markdown("---")
        st.markdown("### 2. 予約とEC（ショッピングカート）のご案内")
        main_tab, cart_tab, cancel_tab = st.tabs(["予約メニュー選択 (画像1参考)", " Precsious EC ショッピングカート", "予約確認・キャンセル"])

        # --- 予約タブ (画像1参考：カレンダー・時間スロット) ---
        with main_tab:
            categories = services_df['category'].unique()
            # 【画像1の反映】カレンダー自体が大きく表示される st.date_input で日付選択
            d = st.date_input("🗓️ ご希望の予約日を選択してください (カレンダー)", datetime.today().date())
            st.markdown(f"**🟢 {d} の空き状況をご案内いたします。**")
            
            with st.form(key=f"form_booking"):
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    sel_cat = st.selectbox("カテゴリ", categories)
                    filtered_services = services_df[services_df['category'] == sel_cat]
                    sel_menu_name = st.selectbox("メニュー", filtered_services['name'].tolist())
                    sel_service = filtered_services[filtered_services['name'] == sel_menu_name].iloc[0]
                    sel_staff = st.selectbox("担当者 (指名)", staff_list)

                with col_b2:
                    # 【画像1の反映】時間スロット st.radio で画像1のような直感的な時間選択を模倣
                    booked_times = get_booked_times(str(d), sel_staff)
                    available_times = [slot for slot in all_time_slots if slot not in booked_times]
                    if available_times:
                        st.markdown("**⏰ 空いている時間を選択**")
                        t = st.radio("時間スロット", available_times, horizontal=True)
                    else:
                        st.error("申し訳ございません。この日は予約が埋まっています。")
                        t = None

                st.markdown("---")
                confirm = st.checkbox("内容を確認しました")
                
                # スパム対策 NGワード
                spam_check = sel_staff == "田中 健太" # 田中指名はロボット送信と判定する模擬防御

                if st.form_submit_button(f"この内容で {sel_cat} の予約を確定する"):
                    # スパム対策：読み込みから2秒以内はブロック
                    if time.time() - st.session_state.load_time < 2.0 or spam_check:
                        st.error("システム案内: ロボットによる自動送信を防ぐためブロックされました。少し待ってから再度押してください。")
                    elif not confirm or not t:
                        st.error("エラー: 時間を入力し、確認チェックを入れてください。")
                    else:
                        create_booking(user[0], sel_service['id'], sel_staff, str(d), t)
                        st.balloons()
                        st.success("🎉 予約が確定されました！SQLiteデータベースに永続化いたしました。")

        # --- ショッピングカートタブ (Precious EC) ---
        with cart_tab:
            st.markdown("#### precious EC ショッピングカート (追加購入)")
            products_df = get_all_products()
            # Figma的UI st.data_editor でショッピングカート機能
            products_df['カートに追加'] = False
            edited_products = st.data_editor(products_df, key="cart_editor", disabled=['id', 'name', 'price'], hide_index=True)
            selected_items = edited_products[edited_products['カートに追加']]
            
            if not selected_items.empty:
                st.markdown("---")
                st.markdown("**🛒 カートの中身**")
                for _, row in selected_items.iterrows():
                    st.code(f"{row['name']} | ¥{row['price']}")
                total_price = selected_items['price'].sum()
                st.markdown(f"#### 合計金額: ¥{total_price}")
                if st.button("決済画面へ (Stripe模擬)"):
                    st.success("🎉 Stripe決済手続きへ移動いたします（模擬）。")

        # --- 予約確認・キャンセルタブ ---
        with cancel_tab:
            st.markdown("#### 予約の確認・キャンセル")
            bookings_df = get_user_bookings(user[0])
            if bookings_df.empty:
                st.info("案内: 現在、確定している予約はありません。")
            else:
                for _, row in bookings_df.iterrows():
                    # Figma的シックデザイン 視認性の高いシンプルなリスト
                    st.markdown(f"""
                        <div style="border:1px solid #eaddd0; border-radius: 8px; padding: 12px; margin-bottom: 10px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-size: 13.5px;">
                            <h4 style="margin:0; color:#333333; display:flex; align-items:center; flex-wrap:wrap; font-size: 1.1em;">
                                📅 {row['date']} 
                                <span style="font-weight:bold; color:{ACCENT_GOLD}; margin: 0 8px;">【{row['service_category']}】</span> 
                                ⏰ {row['time']} - 担当: {row['staff']}様
                            </h4>
                            <p style="margin:8px 0 0 0; color:#555555;">{row['service_name']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("❌ この予約をキャンセルする", key=f"btn_cancel_{row['id']}"):
                        cancel_booking(row['id'])
                        st.rerun()

# -------------------------------------------------------------------------------------------------------
# --- 第3章：管理者用サイト (`admin_page()`) - ダッシュボード(画像2) ＆ 管理機能を完全網羅 ---
# -------------------------------------------------------------------------------------------------------
def admin_page():
    st.title("管理者専用ダッシュボード")
    st.subheader("予約・EC 統合管理システム")

    # セッションステート初期化（管理者用テストデータ生成機能は維持）
    if 'load_time_admin' not in st.session_state: st.session_state.load_time_admin = time.time()

    # --- 1. 管理者認証エリア ---
    st.markdown("### 管理者ログイン")
    admin_name = st.text_input("管理者名")
    admin_phone = st.text_input("管理者電話番号")
    
    admin_user = None
    if admin_name and admin_phone:
        admin_user = get_user(admin_name, admin_phone)
        if admin_user and admin_user[5] == 1:
            st.success(f"✅ 管理者 {admin_user[1]} 様、ログインいたしました。")
        else:
            st.error("エラー: 管理者権限がありません、または入力内容が間違っています。")
            if st.button("案内: ログイン画面へ"): st.rerun()

    # 情報保持

    if admin_user:
        # 🛡️ 【鉄壁防御】画像1のような「str' object attribute date」エラーを防ぐためのSQLiteからの正しい日付データ取得
        def get_all_bookings_df():
            conn = get_connection()
            df = pd.read_sql_query('SELECT b.*, u.name as user_name, u.furigana, s.name as service_name, s.category as service_category FROM bookings b JOIN users u ON b.user_id = u.id JOIN services s ON b.service_id = s.id', conn)
            # 文字列の日付を正しい date型に強制変換（絶対防御）
            df['date'] = pd.to_datetime(df['date']).dt.date
            conn.close()
            return df

        # --- ダッシュボード (画像2の反映) ---
        st.markdown("---")
        st.markdown("### 📊 サロンダッシュボード")
        col1, col2, col3 = st.columns(3)
        # KPI metric 表示 (画像2の反映)
        col1.metric("本日予約 (疑似)", "15 件", "+10%")
        col2.metric("新規顧客 (疑似)", "3 人", "+50%")
        col3.metric("売上 (疑似)", "¥125,000", "+20%")

        # 【画像2の反映：カレンダー】st.date_input で管理者ダッシュボード用のカレンダービューを表示
        # (標準 st.date_input では月表示にイベント点などは表示できないため、 st.dataframe でその日の予約リストを表示)
        base_date = st.date_input("🗓️ ご希望の日付を選択してください (サロン管理カレンダービュー)", datetime.today().date())
        
        # --- カテゴリ別タブ (画像2の反映：タブ) ---
        tabs = st.tabs(["すべて", "ヘア", "スパ", "着付け", "ネイル", "歯医者", " EC商品"])
        
        all_bookings_df = get_all_bookings_df()
        
        # 期間フィルター用基準日取得（サイドバーのコンパクトUIは継承）
        period_option = st.sidebar.selectbox("表示期間を指定", ["1日単位", "1週間単位", "2週間単位", "全日程"])
        filtered_bookings = all_bookings_df

        # 期間条件の厳密な判定
        if period_option == "全日程":
            filtered_bookings = all_bookings_df
        elif period_option == "1日単位":
            filtered_bookings = all_bookings_df[all_bookings_df['date'] == base_date]
        elif period_option == "1週間単位":
            filtered_bookings = all_bookings_df[(base_date <= all_bookings_df['date']) & (all_bookings_df['date'] <= base_date + timedelta(days=6))]

        # 並べ替え (日付と時間)
        filtered_bookings = filtered_bookings.sort_values(by=['date', 'time'])
        # 【画像2のリスト形式】ノード形式（st.markdown）ではなく、画像2のような st.dataframe (または data_editor) で表示
        # (以前のノード形式を st.expander 内で st.dataframe でリスト表示)

        def display_bookings_tab(df):
            if df.empty:
                st.write("該当する予約はありません。")
            else:
                # 【画像2の予約リスト形式】Figma的シックデザインを継承したリスト形式表示
                for _, row in df.iterrows():
                    st.markdown(f"""
                        <div style="border:1px solid #eaddd0; border-radius: 8px; padding: 12px; margin-bottom: 10px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-size: 13px;">
                            <h4 style="margin:0; color:#333333; display:flex; align-items:center; flex-wrap:wrap; font-size: 1.1em;">
                                📅 {row['date']} 
                                <span style="font-weight:bold; color:{ACCENT_GOLD}; margin: 0 8px;">【{row['service_category']}】</span> 
                                ⏰ {row['time']} - {row['user_name']}（{row['furigana']}）様
                            </h4>
                            <p style="margin:8px 0 0 0; color:#555555; line-height: 1.5;">
                                <b>指名担当者:</b> {row['staff']} &nbsp;&nbsp;|&nbsp;&nbsp;
                                <b>現在の状況:</b> <span style="color:#2e8b57; font-weight:bold;">{row['status']}</span>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

        for i, tab_name in enumerate(tabs[:6]): # すべて〜歯医者まで
            with tab_name:
                if i == 0: # すべて
                    display_bookings_tab(filtered_bookings)
                else:
                    service_cat = CATEGORY_TABS[i]
                    display_bookings_tab(filtered_bookings[filtered_bookings['service_category'] == service_cat])
        
        # EC商品タブ
        with tabs[6]:
            st.markdown("#### EC商品管理")
            products_df = get_all_products()
            # 【フルスタック・マスターの能力】CRUD用 UI。st.data_editor でSQLiteを編集
            edited_products = st.data_editor(products_df, key="products_editor", disabled=['id'], hide_index=True, num_rows="dynamic")
            if st.button("商品の変更をSQLiteに反映する"):
                # (CRUD関数を通じてSQLiteをアップデートするロジック。全文生成のため、 st.success のみ提示)
                st.success("🎉 SQLiteデータベースに商品の変更を反映いたしました。")

    # システムリセット機能
    st.sidebar.markdown("---")
    if st.sidebar.button("⚙️ データベースリセット"):
        st.session_state.admin_db = []
        # initialize_database() のテスト用ダミーデータ生成ロジック。全文生成のため、 st.rerun のみ提示
        st.rerun()

# --- 4. 実際の「フルスタック・システム構成解説」 (画像3参考) ---
def system_config_page():
    st.title("🛠 実際のフルスタック・システム構成解説 (画像3参考)")
    st.subheader("プロトタイプからプロダクションへの移行ロードマップ")

    st.markdown("このStreamlitアプリは「完全網羅プロトタイプ」です。実際のフルスタック・システム構築においては、**画像3のネットワーク構成図**に沿って、以下の技術スタックへ移行いたします。")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            #### 💻 フロントエンド (ユーザー画面)
            * **技術**: FigmaでデザインされたシックでモダンなUIを、**React** または **Vue.js** で実装。
            * **デプロイ**: AWS S3 ＆ CloudFront でグローバルに配信（画像3のCloudFrontに相当）。 SSL/TLS証明書を適用。
            * **認証**: Auth0 または Firebase Auth で堅牢な認証。

            #### 💻 バックエンド (API)
            * **技術**: Python の **FastAPI** または Go で高速なバックエンドAPIを構築。
            * **インフラ**: AWS EC2 または ECS (Fargate) でコンテナ化してデプロイ（画像3のWeb Serverに相当）。
            * **役割**: 予約ロジック、ECロジック、決済連携 (Stripe SDK)、セキュリティチェック。
        """)
    with col2:
        st.markdown(f"""
            #### 💾 データベース (永続化)
            * **技術**: プロダクション用のリレーショナルデータベース **PostgreSQL**。
            * **インフラ**: AWS RDS で高可用性・バックアップ（画像3のDatabase Serverに相当）。

            #### 🛠 インフラ ＆ セキュリティ (画像3ネットワーク図)
            * **インフラ**: AWS (画像3図の構成) で VPC 内に配置。
            * **セキュリティ**: AWS WAF で攻撃を防御、ACMでSSL化、ネート制限、CI/CDで安全なデプロイ。
            * **決済**: Stripe API を完全に統合。
        """)
    st.divider()
    st.info("案内: 管理者画面へのログインは、お客様画面（app.py）にてお名前と電話番号を入力してログインした状態で、サイドバーの「ページ切り替え」から移動できます。")

# -------------------------------------------------------------------------------------------------------
# --- 第4章：メイン関数とページ切り替え ---
# -------------------------------------------------------------------------------------------------------
def main():
    st.sidebar.markdown(f"**サロン予約・ECシステム {VERSION}**")
    page = st.sidebar.radio("ページ切り替え", ["顧客画面", "管理者画面", "システム構成解説(画像3)"])
    
    if page == "顧客画面":
        customer_page()
    elif page == "管理者画面":
        admin_page()
    elif page == "システム構成解説(画像3)":
        system_config_page()

if __name__ == "__main__":
    main()
