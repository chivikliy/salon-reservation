import streamlit as st
from datetime import datetime, timedelta, date
import sqlite3
import pandas as pd
import re
import random
import time
import uuid

# ⚙️ UI レイアウト設定
# v8.1.0：CATEGORY_TABS未定義エラーの修正、固定ログインID(admin/1234)の実装
VERSION = "v8.1.0 ( フルスタック・マスター修復版 )"
DB_FILE = "salon_fullstack.db"

# デザイン設定
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
    </style>
""", unsafe_allow_html=True)

# --- 1. データベース層 ---
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def initialize_database():
    conn = get_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT, furigana TEXT, phone TEXT, history TEXT, is_admin INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, price INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS bookings (id TEXT PRIMARY KEY, user_id TEXT, service_id INTEGER, staff TEXT, date TEXT, time TEXT, status TEXT)')
    
    if c.execute('SELECT count(*) FROM services').fetchone()[0] == 0:
        c.executemany('INSERT INTO services (name, category, price) VALUES (?, ?, ?)', [
            ("根本改善カット", "ヘア", 6600), ("エナジースパ", "スパ", 8000),
            ("着付け", "着付け", 8800), ("ジェルネイル", "ネイル", 5000), ("歯科検診", "歯医者", 0)
        ])
    conn.commit()
    conn.close()

initialize_database()

# 基本カテゴリ定義（エラー回避のためグローバルに配置）
CATEGORY_TABS = ["ヘア", "スパ", "着付け", "ネイル", "歯医者"]

# ユーザー取得関数
def get_user(name, phone):
    conn = get_connection()
    user = conn.execute('SELECT * FROM users WHERE name = ? AND phone = ?', (name, phone)).fetchone()
    conn.close()
    return user

# -------------------------------------------------------------------------------------------------------
# --- 2. 顧客画面 ---
# -------------------------------------------------------------------------------------------------------
def customer_page():
    st.title("Dr's Salon LAB 予約システム")
    st.markdown("### 1. ログイン ＆ お客様情報")
    
    name = st.text_input("お名前（フルネーム）", key="c_name")
    phone = st.text_input("電話番号", key="c_phone")
    
    if name and phone:
        st.success(f"✅ {name} 様として一時ログイン中（デモ版）")
        st.info("下のタブからメニューを選んで予約してください。")

    st.divider()
    tabs = st.tabs(CATEGORY_TABS + ["予約確認"])
    
    for i, cat in enumerate(CATEGORY_TABS):
        with tabs[i]:
            st.write(f"【 {cat} 】の予約フォーム")
            st.date_input("希望日", key=f"date_{cat}")
            st.selectbox("時間", ["10:00", "11:00", "13:00", "15:00"], key=f"time_{cat}")
            st.button(f"{cat}の予約を確定する", key=f"btn_{cat}")

# -------------------------------------------------------------------------------------------------------
# --- 3. 管理者画面 (ログインID: admin / パスワード: 1234) ---
# -------------------------------------------------------------------------------------------------------
def admin_page():
    st.title("管理者専用ダッシュボード")
    
    # 【フルスタック・マスターの修正】固定IDとパスワードによる認証
    with st.sidebar:
        st.markdown("### 🔐 管理者認証")
        input_id = st.text_input("管理者ID (admin)", key="admin_id")
        input_pw = st.text_input("パスワード (1234)", type="password", key="admin_pw")
    
    if input_id == "admin" and input_pw == "1234":
        st.success("✅ マスター権限で認証されました。")
        
        # ダッシュボード表示
        col1, col2 = st.columns(2)
        col1.metric("本日の予約数", "12 件")
        col2.metric("新規顧客数", "3 名")
        
        st.divider()
        st.markdown("### 📅 予約リスト管理")
        
        # 【解決策】CATEGORY_TABSをここでも安全に参照
        admin_tabs = st.tabs(["すべて"] + CATEGORY_TABS)
        for i, tab_name in enumerate(["すべて"] + CATEGORY_TABS):
            with admin_tabs[i]:
                st.write(f"--- {tab_name} の予約一覧を表示中 ---")
                st.info("現在はデモデータのみを表示しています。")
    else:
        if input_id or input_pw:
            st.error("❌ IDまたはパスワードが正しくありません。")
        else:
            st.warning("サイドバーから管理者情報を入力してください。")

# -------------------------------------------------------------------------------------------------------
# --- 4. メイン制御 ---
# -------------------------------------------------------------------------------------------------------
def main():
    st.sidebar.title("MENU")
    mode = st.sidebar.radio("モード切替", ["顧客画面", "管理者画面"])
    
    if mode == "顧客画面":
        customer_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()
