import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta, date
import re
import random
import time

# ⚙️ UI レイアウト設定
# v6.2.0：文字データ混入による計算エラー(AttributeError)を完全に防ぐ鉄壁の修復版
VERSION = "v6.2.0 (App エラー完全修復・鉄壁版)"

# 清潔感のあるベーステーマカラー（Figma的洗練）
BASE_BG = "#fdfaf6"
BASE_TEXT = "#333333"
ACCENT_GOLD = "#d9b38c"

# カテゴリ配色
CATEGORY_COLORS = {
    "ヘア": {"accent": "#8DA399", "tab_bg": "#ffffff"},
    "スパ": {"accent": "#A393B3", "tab_bg": "#ffffff"},
    "着付け": {"accent": "#93A8B3", "tab_bg": "#ffffff"},
    "ネイル": {"accent": "#B3939A", "tab_bg": "#ffffff"},
    "歯医者": {"accent": "#93B3B3", "tab_bg": "#ffffff"}
}

st.set_page_config(page_title=f"Dr's Salon LAB 予約システム {VERSION}", layout="wide")

# Figma的UI設計：フォントサイズと余白を詰めたコンパクトCSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BASE_BG}; color: {BASE_TEXT}; font-size: 13.5px; }}
    h1 {{ font-size: 1.6em !important; margin-bottom: 0.2em !important; padding-top: 0 !important; }}
    h3 {{ font-size: 1.1em !important; margin-top: 0.2em !important; margin-bottom: 0.5em !important; }}
    div.stButton > button:first-child {{
        background-color: {ACCENT_GOLD}; color: white;
        border-radius: 8px; border: none; width: 100%; font-weight: bold; padding: 10px;
        font-size: 13px; transition: background-color 0.3s;
    }}
    .stTabs [data-baseweb="tab-list"] button {{ color: #777777; font-weight: bold; padding: 6px 10px; font-size: 0.95em; }}
    .stTextInput input, .stSelectbox select, .stDateInput input {{ font-size: 13px; padding: 6px; }}
    /* 履歴エリアのコンパクト化 */
    div[data-testid="stVVerticalBlock"] div[data-testid="stVerticalBlockBorderWrapper"] {{ padding: 10px !important; }}
    </style>
""", unsafe_allow_html=True)

# 🛡️ 【絶対防御】どんなデータ形式でも必ずカレンダーの「日付型」に変換する関数
def get_safe_date(date_value):
    if isinstance(date_value, date) and not isinstance(date_value, datetime):
        return date_value
    if isinstance(date_value, datetime):
        return date_value.date()
    if isinstance(date_value, str):
        try:
            return datetime.strptime(date_value[:10], "%Y-%m-%d").date()
        except:
            pass
    return datetime.today().date()

# セッションステートの初期化
if 'history_list' not in st.session_state: st.session_state.history_list = []
if 'last_booking_signature' not in st.session_state: st.session_state.last_booking_signature = ""
if 'load_time' not in st.session_state: st.session_state.load_time = time.time()
st.session_state.setdefault('pers_name', '')
st.session_state.setdefault('pers_furi', '')
st.session_state.setdefault('pers_phone', '')

# 電話番号・フリガナ整形
def format_phone_number(phone_input):
    digits = re.sub(r'\D', '', phone_input.translate(str.maketrans('０１２３４５６７８９', '0123456789')))
    if len(digits) == 11: return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10: return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    return digits

def to_katakana(text):
    return "".join([chr(ord(c) + 96) if '\u3041' <= c <= '\u3096' else c for c in text])

st.title("Dr's Salon LAB 古河店予約システム")

# --- 1. お客様情報エリア（パーソナル設定保持） ---
st.markdown("### 1. お客様情報")
if st.button("前回の入力を読み込む"):
    pass

col1, col2, col3 = st.columns(3)
with col1:
    name = st.text_input("お名前（フルネーム）", value=st.session_state.pers_name)
with col2:
    raw_furi = st.text_input("フリガナ", value=st.session_state.pers_furi)
    furigana = to_katakana(raw_furi)
with col3:
    raw_phone = st.text_input("電話番号", value=st.session_state.pers_phone)
    phone = format_phone_number(raw_phone)

# 情報保持
st.session_state.pers_name = name
st.session_state.pers_furi = furigana
st.session_state.pers_phone = phone

# サービス設定
SERVICES = {
    "ヘア": {"menus": {"根本改善カット": 6600, "カラー＋カット": 11000}, "staffs": ["指名なし", "関根 光代", "田中 健太", "佐藤 美咲"]},
    "スパ": {"menus": {"極上スパ(60分)": 8000, "リバーススパ(45分)": 6000}, "staffs": ["指名なし", "鈴木 翔太", "山田 花子"]},
    "着付け": {"menus": {"訪問着 着付け": 8800, "振袖 着付け": 12000}, "staffs": ["山田 花子", "高橋 陽子"]},
    "ネイル": {"menus": {"ジェルネイル": 5000, "フットネイル": 6500}, "staffs": ["高橋 陽子"]},
    "歯医者": {"menus": {"検診": 0, "虫歯治療": 0}, "staffs": ["希望なし", "関根 光代"]}
}

st.markdown("---")
st.markdown("### 2. メニューと日時の選択")
tab_list = st.tabs(list(SERVICES.keys()))
ALL_TIME_SLOTS = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]

for i, (service_name, service_data) in enumerate(SERVICES.items()):
    colors = CATEGORY_COLORS.get(service_name, {"accent": ACCENT_GOLD, "tab_bg": "#ffffff"})
    with tab_list[i]:
        st.markdown(f'<div style="background-color:{colors["accent"]};color:white;padding:6px;border-radius:4px;text-align:center;font-weight:bold;margin-bottom:10px;">【 {service_name} 】</div>', unsafe_allow_html=True)
        
        sel_menu = st.selectbox("メニュー", list(service_data["menus"].keys()), key=f"m_{i}")
        sel_staff = st.selectbox("担当者", service_data["staffs"], key=f"s_{i}")
        d = st.date_input("予約日", key=f"d_{i}")
        
        # 【修復ポイント】空き時間計算時に get_safe_date を使用し、文字データが混じっていてもクラッシュさせない
        booked_times = []
        if sel_staff not in ["指名なし", "希望なし"]:
            for record in st.session_state.history_list:
                # 記録（文字列）から日付部分を抽出し、安全に変換して比較
                try:
                    # 文字列の中から "2026-03-25" のような日付パターンを探します
                    date_match = re.search(r'\d{4}-\d{2}-\d{2}', record)
                    if date_match:
                        record_date = get_safe_date(date_match.group())
                        if record_date == d and sel_staff in record and "テスト自動生成" not in record:
                            for slot in ALL_TIME_SLOTS:
                                if slot in record: booked_times.append(slot)
                except:
                    continue
        
        available_times = [slot for slot in ALL_TIME_SLOTS if slot not in booked_times]
        if not available_times:
            st.warning("予約が埋まっています。別の日を選択してください。")
            t = None
        else:
            t = st.selectbox("空いている時間", available_times, key=f"t_{i}")

        st.markdown("---")
        confirm = st.checkbox("内容を確認しました", key=f"c_{i}")
        
        if st.button(f"この内容で {service_name} の予約を確定する", key=f"btn_{i}"):
            # スパム対策：読み込みから2秒以内はブロック
            if time.time() - st.session_state.load_time < 2.0:
                st.error("ロボットによる自動送信を防ぐため、少し時間を置いてから再度押してください。")
            elif not name or not furigana or not confirm:
                st.error("お名前、フリガナを入力し、確認チェックを入れてください。")
            else:
                st.balloons()
                st.success("予約が確定されました。")
                new_rec = f"📅 {d} ⏰ {t} | {name}（{furigana}）様 | 担当: {sel_staff} | {service_name}: {sel_menu}"
                st.session_state.history_list.append(new_rec)
                st.code(new_rec)

# --- 3. 履歴表示 ---
if st.session_state.history_list:
    st.divider()
    st.write("#### 【本日受付した予約一覧】")
    with st.container(height=150):
        for item in st.session_state.history_list:
            if "テスト自動生成" not in item:
                st.markdown(f"<div style='border-bottom:1px solid #eee;padding:4px;'>{item}</div>", unsafe_allow_html=True)

# 開発者メニュー
with st.expander("🛠 テスト用ダミーデータ生成"):
    if st.button("30日分の予約を追加"):
        for day_offset in range(30):
            target_date = datetime.today().date() + timedelta(days=day_offset)
            st.session_state.history_list.append(f"📅 {target_date} ⏰ 10:00 | テスト様 | 担当: 田中 健太 | ヘア | テスト自動生成")
        st.success("完了いたしました。")
