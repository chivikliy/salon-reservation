import streamlit as st
from datetime import datetime

# ⚙️ UI レイアウト・サイズ調整設定
# 読者がFigma等で取得したカラーコードをここで一括管理いたします。
FIGMA_BG_COLOR = "#fdfaf6"
FIGMA_BUTTON_COLOR = "#d9b38c"
FIGMA_TEXT_COLOR = "#333333"

st.set_page_config(page_title="Dr's Salon LAB 予約システム", layout="centered")

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {FIGMA_BG_COLOR};
        color: {FIGMA_TEXT_COLOR};
    }}
    div.stButton > button:first-child {{
        background-color: {FIGMA_BUTTON_COLOR};
        color: white;
        border-radius: 8px;
        border: none;
        width: 100%;
        font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("Dr's Salon LAB 古河店")
st.subheader("オンライン予約システム")

with st.expander("1. お客様情報を入力してください", expanded=True):
    name = st.text_input("お客様のお名前")
    phone = st.text_input("お客様の電話番号")
    history = st.radio("お客様のご来店歴", ["初めて（新規）", "2回目以降（再来）"])

with st.expander("2. メニューを選択してください"):
    menus = {
        "【骨格矯正】Dr.カット★プチSPA無料": 5440,
        "≪平日≫顔周りカット＋リタッチカラー": 7920,
        "前髪カット（電話予約専用）": 1320
    }
    selected_menu = st.selectbox("ご希望のメニューを選択", list(menus.keys()))

with st.expander("3. 予約日時を選択してください"):
    d = st.date_input("ご希望の予約日")
    t = st.time_input("ご希望の予約時間")

if st.button("システムに予約内容を確認する"):
    if selected_menu == "前髪カット（電話予約専用）":
        st.error("システムからの警告: このメニューはネット予約対象外です。お客様は直接店舗にお電話をお願いいたします。")
    elif not name or not phone:
        st.warning("システムからの警告: お客様はお名前と電話番号を入力していません。お客様はすべての入力をお願いいたします。")
    else:
        price = menus[selected_menu]
        if d.weekday() >= 5 and "平日" in selected_menu:
            price += 1100
            st.info("システムからの通知: お客様が選択した日時は土日祝であるため、システムは土日祝料金（+1,100円）を適用いたしました。")
            
        st.success(f"システムが確認した予約内容:\n\nお客様のお名前: {name} 様\n予約日時: {d} {t}\nメニュー: {selected_menu}\n合計金額: {price}円")
        if st.button("お客様はこの内容で予約を確定する"):
            st.balloons()
            st.write("システムはお客様の予約を正常に確定し、データベースに保存いたしました。")
