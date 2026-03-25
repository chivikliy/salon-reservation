import streamlit as st
from datetime import datetime
import re

# ⚙️ UI レイアウト・サイズ調整設定
# 1.0.1：電話番号自動整形機能（ハイフン・全角対応）を追加
# 2.0.0：タブ切り替え拡張システム（ネイル・瞑想・歯医者等）を追加
VERSION = "v2.0.0"
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

# --- 2. 予約カテゴリ（タブ切り替え）と柔軟な拡張システム ---
# 後から項目を無制限に増やせるよう、システムは辞書（リスト）形式でメニューを管理いたします。
SERVICES = {
    "✂️ ヘア": {
        "menus": {"【骨格矯正】Dr.カット★プチSPA無料": 5440, "≪平日≫顔周りカット＋リタッチカラー": 7920, "前髪カット（電話予約専用）": 1320},
        "staffs": ["指名なし", "田中（トップスタイリスト）", "佐藤（カラーリスト）"]
    },
    "💆‍♀️ スパ": {
        "menus": {"【究極癒し】極上流頭筋ヘッドスパ(60分)": 6800, "ショートスパ(30分)": 4000},
        "staffs": ["指名なし", "鈴木（スパニスト）"]
    },
    "👘 着付け": {
        "menus": {"訪問着・留袖 着付け": 8800, "振袖 着付け": 12000, "浴衣 着付け": 4500},
        "staffs": ["専属着付師 山田"]
    },
    "💅 ネイル": {
        "menus": {"ジェルネイル（ワンカラー）": 5000, "フットネイル": 6500, "ネイルオフのみ": 2000},
        "staffs": ["指名なし", "高橋（ネイリスト）"]
    },
    "🧘 瞑想教室(SP4)": {
        "menus": {"初心者向けマインドフルネス": 3000, "プライベートレッスン": 8000},
        "staffs": ["インストラクター 伊藤"]
    },
    "🦷 歯医者": {
        "menus": {"検診・歯のクリーニング": 0, "虫歯治療・痛みがある": 0, "歯茎の腫れ・出血": 0, "親知らず・抜歯相談": 0, "歯並び・矯正相談": 0},
        "staffs": ["担当医の希望なし", "院長希望", "女性医師希望"]
    }
}

st.write("### 2. ご希望のサービスを選択してください")
tab_list = st.tabs(list(SERVICES.keys()))

for i, (service_name, service_data) in enumerate(SERVICES.items()):
    with tab_list[i]:
        # Streamlitのform機能を使用し、システムはタブごとの予約情報を独立して処理いたします
        with st.form(key=f"form_{i}"):
            st.write(f"#### {service_name} のご予約内容")
            
            sel_menu = st.selectbox("ご希望のメニューを選択", list(service_data["menus"].keys()))
            sel_staff = st.selectbox("ご希望の担当者・担当医", service_data["staffs"])
            
            d = st.date_input("ご希望の予約日")
            t = st.time_input("ご希望の予約時間")
            
            # --- 歯医者専用：全ネットワーク網羅の必須WEB問診票 ---
            dentist_info = ""
            if service_name == "🦷 歯医者":
                st.markdown("---")
                st.markdown("#### 📝 事前WEB問診票（※歯科予約の必須項目です）")
                q_symptom = st.text_area("1. いつ頃から、どのような症状ですか？（痛みの種類など具体的に）")
                q_meds = st.text_input("2. 現在服用中のお薬・これまでの大きな病気（既往歴）")
                q_allergy = st.text_input("3. アレルギーの有無（薬・食べ物・金属・麻酔など）")
                q_preg = st.radio("4. 妊娠中・授乳中ですか？（X線撮影や投薬の判断に必要です）", ["いいえ", "はい（妊娠中）", "はい（授乳中）", "男性のため対象外"])
                q_other = st.text_area("5. その他ご要望（過去の治療での不安、自由診療の希望など）")
                
                dentist_info = f"\n【問診票】\n症状: {q_symptom}\n服薬: {q_meds}\nアレルギー: {q_allergy}\n妊娠/授乳: {q_preg}\nその他: {q_other}"
            
            st.markdown("---")
            confirm_check = st.checkbox("システムに送信する前に、上記の内容（お名前・電話番号含む）に間違いがないか確認しました")
            submit_btn = st.form_submit_button(f"{service_name} の予約をシステムに送信・確定する")
            
            if submit_btn:
                if not name or len(phone) < 10:
                    st.error("システムからの警告: 画面上部の「1. お客様情報」で、お名前と正しい電話番号を入力してください。")
                elif not confirm_check:
                    st.warning("システムからの警告: 「確認しました」のチェックボックスをマウスでクリックしてチェックを入れてください。")
                elif service_name == "🦷 歯医者" and not q_symptom:
                    st.warning("システムからの警告: 歯科予約の場合は、システムが症状を把握するため、問診票の「1. 症状」を必ず入力してください。")
                else:
                    price = service_data["menus"][sel_menu]
                    price_str = f"{price}円" if price > 0 else "保険適用（または窓口で要相談）"
                    
                    st.success("### 🎉 予約が正常にシステムへ確定されました！")
                    st.write("システムは以下の内容でデータベースに予約情報を送信いたしました。")
                    
                    final_data = f"【予約完了】\nお名前: {name} 様\n電話番号: {phone}\n来店歴: {history}\n\nカテゴリ: {service_name}\nメニュー: {sel_menu}\n担当: {sel_staff}\n日時: {d} {t}\n目安金額: {price_str}{dentist_info}"
                    st.code(final_data)
                    
                    new_history_line = f"{d} {t} | {name} 様 | {service_name}: {sel_menu} | {price_str}"
                    st.session_state.history_list.append(new_history_line)
                    st.balloons()

# --- 3. 簡易履歴表示 ---
if st.session_state.history_list:
    st.divider()
    st.write("#### 【システムが本日受付した予約一覧】")
    for item in st.session_state.history_list:
        st.code(item)

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
