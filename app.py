import streamlit as st
from datetime import datetime
import re

# ⚙️ UI レイアウト・サイズ調整設定
# v2.1.0：画面幅ワイド化、重複ボタンの統合、二重予約防止、タブ視覚強化
VERSION = "v2.1.0"
FIGMA_BG_COLOR = "#fdfaf6"
FIGMA_BUTTON_COLOR = "#d9b38c"
FIGMA_TEXT_COLOR = "#333333"

# 【解決策1】layout="wide" に変更し、横幅の固定を解除して全体を見やすくしました
st.set_page_config(page_title=f"Dr's Salon LAB 予約システム {VERSION}", layout="wide")

# デザイン適用（CSS）
st.markdown(f"""
    <style>
    .stApp {{ background-color: {FIGMA_BG_COLOR}; color: {FIGMA_TEXT_COLOR}; }}
    div.stButton > button:first-child {{
        background-color: {FIGMA_BUTTON_COLOR}; color: white;
        border-radius: 8px; border: none; width: 100%; font-weight: bold; padding: 10px;
    }}
    /* 確認用の文字が画面外にはみ出さないように折り返しを設定 */
    code {{ white-space: pre-wrap !important; word-break: break-all; }}
    </style>
""", unsafe_allow_html=True)

st.title(f"Dr's Salon LAB 古河店 ({VERSION})")
st.subheader("総合オンライン予約システム")

# 予約履歴と、二重予約防止のためのシステムメモリを準備
if 'history_list' not in st.session_state:
    st.session_state.history_list = []
if 'last_booking_signature' not in st.session_state:
    st.session_state.last_booking_signature = ""

# 電話番号整形関数
def format_phone_number(phone_input):
    digits = re.sub(r'\D', '', phone_input.translate(str.maketrans('０１２３４５６７８９', '0123456789')))
    if len(digits) == 11: return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10: return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    return digits

# --- 1. お客様情報エリア ---
st.markdown("### 1. お客様情報を入力してください")
col1, col2 = st.columns(2) # 画面を左右に分割してスッキリ配置
with col1:
    name = st.text_input("お客様のお名前（必須）")
    raw_phone = st.text_input("お客様の電話番号（必須）")
    phone = format_phone_number(raw_phone)
    if raw_phone: st.info(f"整えた番号：{phone}")
with col2:
    history = st.radio("ご来店歴", ["初めて（新規）", "2回目以降（再来）"])

# --- 2. 予約カテゴリ（タブ切り替え） ---
SERVICES = {
    "✂️ ヘア": {"menus": {"【骨格矯正】Dr.カット★プチSPA無料": 5440, "≪平日≫顔周りカット＋リタッチカラー": 7920}, "staffs": ["指名なし", "田中", "佐藤"]},
    "💆‍♀️ スパ": {"menus": {"【究極癒し】極上流頭筋ヘッドスパ(60分)": 6800}, "staffs": ["指名なし", "鈴木"]},
    "👘 着付け": {"menus": {"訪問着・留袖 着付け": 8800, "振袖 着付け": 12000}, "staffs": ["専属着付師 山田"]},
    "💅 ネイル": {"menus": {"ジェルネイル（ワンカラー）": 5000, "フットネイル": 6500}, "staffs": ["指名なし", "高橋"]},
    "🧘 瞑想教室": {"menus": {"初心者向けマインドフルネス": 3000}, "staffs": ["インストラクター 伊藤"]},
    "🦷 歯医者": {"menus": {"検診・クリーニング": 0, "虫歯治療": 0, "親知らず相談": 0}, "staffs": ["希望なし", "院長希望"]}
}

st.markdown("---")
st.markdown("### 2. ご希望のサービスを選択し、予約を確定してください")
tab_list = st.tabs(list(SERVICES.keys()))

for i, (service_name, service_data) in enumerate(SERVICES.items()):
    with tab_list[i]:
        # 【解決策2】どのタブを開いているか、色付きで強調表示します
        st.success(f"🟢 現在 **【 {service_name} 】** の予約画面を開いています")
        
        # 【解決策3】不要な「確認ボタン」を削除し、送信ボタン1つに統合しました
        with st.form(key=f"form_{i}"):
            sel_menu = st.selectbox(f"{service_name} のメニューを選択", list(service_data["menus"].keys()))
            sel_staff = st.selectbox("ご希望の担当者", service_data["staffs"])
            
            d = st.date_input("ご希望の予約日", key=f"date_{i}")
            t = st.time_input("ご希望の予約時間", key=f"time_{i}")
            
            # 歯医者専用の問診票
            dentist_info = ""
            if service_name == "🦷 歯医者":
                st.markdown("#### 📝 事前WEB問診票（必須）")
                q_symptom = st.text_area("1. 具体的な症状をご記入ください")
                dentist_info = f"\n症状: {q_symptom}"
            
            st.markdown("---")
            confirm_check = st.checkbox("上記の内容（お名前・日時など）に間違いがないか確認しました")
            
            # ただ一つの確定ボタン
            submit_btn = st.form_submit_button(f"この内容で {service_name} の予約を確定する")
            
            if submit_btn:
                # 【解決策4】二重予約（連打）防止システム
                current_booking_signature = f"{name}_{sel_menu}_{d}_{t}"
                
                if not name or len(phone) < 10:
                    st.error("システムからの警告: 上部の「1. お客様情報」で、お名前と正しい電話番号を入力してください。")
                elif not confirm_check:
                    st.warning("システムからの警告: 「確認しました」のチェックボックスをクリックしてください。")
                elif service_name == "🦷 歯医者" and not q_symptom:
                    st.warning("システムからの警告: 歯科予約の場合は、問診票の「症状」を必ず入力してください。")
                elif current_booking_signature == st.session_state.last_booking_signature:
                    st.warning("システムからの案内: 既に同じ内容での予約が完了しています。二重送信は防がれました。")
                else:
                    # 全て正しい場合、システムは予約を確定します
                    st.session_state.last_booking_signature = current_booking_signature # 二重予約防止の鍵をかける
                    
                    price = service_data["menus"][sel_menu]
                    price_str = f"{price}円" if price > 0 else "窓口でご相談"
                    
                    st.balloons()
                    st.success("### 🎉 予約が正常にシステムへ確定されました！")
                    
                    final_data = f"【予約完了】\nお名前: {name} 様\n電話: {phone}\n来店歴: {history}\n\nカテゴリ: {service_name}\nメニュー: {sel_menu}\n担当: {sel_staff}\n日時: {d} {t}\n目安金額: {price_str}{dentist_info}"
                    st.code(final_data)
                    
                    new_history_line = f"{d} {t} | {name} 様 | {service_name}: {sel_menu} | {price_str}"
                    st.session_state.history_list.append(new_history_line)

# --- 3. 簡易履歴表示 ---
if st.session_state.history_list:
    st.divider()
    st.write("#### 【システムが本日受付した予約一覧】")
    for item in st.session_state.history_list:
        st.code(item)
