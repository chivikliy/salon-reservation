import streamlit as st
from datetime import datetime
import re

# ⚙️ UI レイアウト・サイズ調整設定
# 1.0.1：電話番号自動整形機能（ハイフン・全角対応）を追加
VERSION = "v1.0.1"
FIGMA_BG_COLOR = "#fdfaf6"
FIGMA_BUTTON_COLOR = "#d9b38c"
FIGMA_TEXT_COLOR = "#333333"

st.set_page_config(page_title=f"Dr's Salon LAB 予約システム {VERSION}", layout="centered")

# デザイン適用（CSS）
st.markdown(f"""
    <style>
    .stApp {{ background-color: {FIGMA_BG_COLOR}; color: {FIGMA_TEXT_COLOR}; }}
    div.stButton > button:first-child {{
        background-color: {FIGMA_BUTTON_COLOR}; color: white;
        border-radius: 8px; border: none; width: 100%; font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# タイトルにバージョンを表示
st.title(f"Dr's Salon LAB 古河店 ({VERSION})")
st.subheader("オンライン予約システム")

# 予約履歴を一時的に保存する入れ物
if 'history_list' not in st.session_state:
    st.session_state.history_list = []

# 電話番号を「000-0000-0000」の形式に整える魔法の関数
def format_phone_number(phone_input):
    # 全角数字を半角数字に変換し、数字以外の文字（ハイフンなど）をすべて消去します
    digits = re.sub(r'\D', '', phone_input.translate(str.maketrans('０１２３４５６７８９', '0123456789')))
    
    # 数字が11桁の場合、ハイフンを挿入します（例：08043500108 -> 080-4350-0108）
    if len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    # 数字が10桁の場合（固定電話など）
    elif len(digits) == 10:
        return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    return digits # 桁数が合わない場合はそのまま返します

# --- 1. 入力エリア ---
with st.expander("1. お客様情報を入力してください", expanded=True):
    name = st.text_input("お客様のお名前")
    raw_phone = st.text_input("お客様の電話番号（例：080-4350-0108）")
    
    # 入力された瞬間にシステムが番号をきれいに整えます
    phone = format_phone_number(raw_phone)
    if raw_phone:
        st.info(f"システムが番号を整えました：{phone}")
        
    history = st.radio("お客様のご来店歴", ["初めて（新規）", "2回目以降（再来）"])

# --- 2. メニューエリア ---
with st.expander("2. メニューを選択してください"):
    menus = {
        "【骨格矯正】Dr.カット★プチSPA無料": 5440,
        "≪平日≫顔周りカット＋リタッチカラー": 7920,
        "前髪カット（電話予約専用）": 1320
    }
    selected_menu = st.selectbox("ご希望のメニューを選択", list(menus.keys()))

# --- 3. 日時エリア ---
with st.expander("3. 予約日時を選択してください"):
    d = st.date_input("ご希望の予約日")
    t = st.time_input("ご希望の予約時間")

# --- 4. 確認と確定ロジック ---
if st.button("システムに予約内容を確認する"):
    if selected_menu == "前髪カット（電話予約専用）":
        st.error("システムからの警告: このメニューはネット予約対象外です。")
    elif not name or not phone or len(phone) < 10:
        st.warning("システムからの警告: お名前と正しい電話番号を入力してください。")
    else:
        price = menus[selected_menu]
        if d.weekday() >= 5 and "平日" in selected_menu:
            price += 1100
            
        st.success(f"確認内容:\n{name} 様 / {phone}\n日時: {d} {t}\n合計: {price}円")
        
        if st.button("お客様はこの内容で予約を確定する"):
            st.balloons()
            new_data = f"{d} {t} | {name} 様 | {phone} | {price}円"
            st.session_state.history_list.append(new_data)
            st.write("### 🎉 予約が正常に確定されました！")

# --- 5. 簡易履歴表示 ---
if st.session_state.history_list:
    st.divider()
    st.write("#### 【本日受付した予約一覧】")
    for item in st.session_state.history_list:
        st.code(item)
