import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta, date
import re
import random
import time
import uuid

# ⚙️ UI レイアウト設定
# v7.0.0：お客様向け「摩擦ゼロ」の予約確認・キャンセル機能を完全統合
VERSION = "v7.0.0 (キャンセル機能・完全統合版)"

# 清潔感のあるベーステーマカラー（Figma的洗練）
BASE_BG = "#fdfaf6"
BASE_TEXT = "#333333"
ACCENT_GOLD = "#d9b38c"
ACCENT_RED = "#d98c8c" # キャンセル用の落ち着いたレッド

CATEGORY_COLORS = {
    "ヘア": {"accent": "#8DA399", "tab_bg": "#ffffff"},
    "スパ": {"accent": "#A393B3", "tab_bg": "#ffffff"},
    "着付け": {"accent": "#93A8B3", "tab_bg": "#ffffff"},
    "ネイル": {"accent": "#B3939A", "tab_bg": "#ffffff"},
    "歯医者": {"accent": "#93B3B3", "tab_bg": "#ffffff"}
}

st.set_page_config(page_title=f"Dr's Salon LAB 予約システム {VERSION}", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {BASE_BG}; color: {BASE_TEXT}; font-size: 13.5px; }}
    h1 {{ font-size: 1.6em !important; margin-bottom: 0.2em !important; padding-top: 0 !important; }}
    h3 {{ font-size: 1.1em !important; margin-top: 0.2em !important; margin-bottom: 0.5em !important; }}
    /* メインボタンの洗練 */
    div.stButton > button:first-child {{
        background-color: {ACCENT_GOLD}; color: white;
        border-radius: 8px; border: none; width: 100%; font-weight: bold; padding: 10px;
        font-size: 13px; transition: background-color 0.3s;
    }}
    .stTabs [data-baseweb="tab-list"] button {{ color: #777777; font-weight: bold; padding: 6px 10px; font-size: 0.95em; }}
    .stTextInput input, .stSelectbox select, .stDateInput input {{ font-size: 13px; padding: 6px; }}
    div[data-testid="stVVerticalBlock"] div[data-testid="stVerticalBlockBorderWrapper"] {{ padding: 10px !important; }}
    </style>
""", unsafe_allow_html=True)

# 🛡️ 【絶対防御】日付変換
def get_safe_date(date_value):
    if isinstance(date_value, date) and not isinstance(date_value, datetime): return date_value
    if isinstance(date_value, datetime): return date_value.date()
    if isinstance(date_value, str):
        try: return datetime.strptime(date_value[:10], "%Y-%m-%d").date()
        except: pass
    return datetime.today().date()

# セッションステート初期化
if 'history_list' not in st.session_state: st.session_state.history_list = []
if 'last_booking_signature' not in st.session_state: st.session_state.last_booking_signature = ""
if 'load_time' not in st.session_state: st.session_state.load_time = time.time()
if 'cancel_search_ids' not in st.session_state: st.session_state.cancel_search_ids = None

st.session_state.setdefault('pers_name', '')
st.session_state.setdefault('pers_furi', '')
st.session_state.setdefault('pers_phone', '')

# 🛡️ 【絶対防御】過去の「文字データ」が残っていてもクラッシュさせず「辞書型」に強制変換する安全装置
valid_history = []
for item in st.session_state.history_list:
    if isinstance(item, dict):
        valid_history.append(item)
    elif isinstance(item, str):
        valid_history.append({
            "id": str(uuid.uuid4()), "name": "不明", "phone": "不明",
            "date": datetime.today().date(), "display": item, "is_test": "テスト自動生成" in item
        })
st.session_state.history_list = valid_history

# 電話番号・フリガナ整形
def format_phone_number(phone_input):
    digits = re.sub(r'\D', '', phone_input.translate(str.maketrans('０１２３４５６７８９', '0123456789')))
    if len(digits) == 11: return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10: return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    return digits

def to_katakana(text):
    return "".join([chr(ord(c) + 96) if '\u3041' <= c <= '\u3096' else c for c in text])

st.title("Dr's Salon LAB 古河店予約システム")

# --- 1. お客様情報エリア ---
st.markdown("### 1. お客様情報")
if st.button("前回の入力を読み込む"): pass

col1, col2, col3 = st.columns(3)
with col1:
    name = st.text_input("お名前（フルネーム）", value=st.session_state.pers_name)
with col2:
    raw_furi = st.text_input("フリガナ", value=st.session_state.pers_furi)
    furigana = to_katakana(raw_furi)
with col3:
    raw_phone = st.text_input("電話番号", value=st.session_state.pers_phone)
    phone = format_phone_number(raw_phone)

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
        
        # 空き時間計算（辞書型データに対応）
        booked_times = []
        if sel_staff not in ["指名なし", "希望なし"]:
            for record in st.session_state.history_list:
                rec_date = get_safe_date(record.get("date"))
                if rec_date == d and sel_staff in record.get("display", "") and not record.get("is_test"):
                    for slot in ALL_TIME_SLOTS:
                        if slot in record.get("display", ""): booked_times.append(slot)
        
        available_times = [slot for slot in ALL_TIME_SLOTS if slot not in booked_times]
        if not available_times:
            st.warning("予約が埋まっています。別の日を選択してください。")
            t = None
        else:
            t = st.selectbox("空いている時間", available_times, key=f"t_{i}")

        st.markdown("---")
        confirm = st.checkbox("内容を確認しました", key=f"c_{i}")
        
        if st.button(f"この内容で {service_name} の予約を確定する", key=f"btn_{i}"):
            if time.time() - st.session_state.load_time < 2.0:
                st.error("ロボットによる自動送信を防ぐためブロックされました。少し待ってから再度押してください。")
            elif not name or not furigana or not phone or not confirm:
                st.error("お名前、電話番号を入力し、確認チェックを入れてください。")
            else:
                st.balloons()
                st.success("予約が確定されました。")
                display_text = f"📅 {d} ⏰ {t} | {name}（{furigana}）様 | 担当: {sel_staff} | {service_name}: {sel_menu}"
                
                # 高度な辞書型データとして保存（キャンセル機能のため）
                new_rec = {
                    "id": str(uuid.uuid4()), "name": name, "phone": phone,
                    "date": d, "time": t, "display": display_text, "is_test": False
                }
                st.session_state.history_list.append(new_rec)
                st.code(display_text)

# --- 3. 予約の確認・キャンセル（新機能） ---
st.markdown("---")
st.markdown("### 3. ご予約の確認・キャンセル")
st.markdown("ご予約時の「お名前」と「電話番号」を入力することで、現在の予約を確認し、キャンセルすることができます。")

with st.container(border=True):
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cancel_name = st.text_input("ご予約時のお名前（フルネーム）", key="c_name")
    with col_c2:
        cancel_phone_raw = st.text_input("ご予約時の電話番号", key="c_phone")
        cancel_phone = format_phone_number(cancel_phone_raw)
    
    if st.button("ご予約を検索する", key="btn_search_cancel"):
        if not cancel_name or not cancel_phone_raw:
            st.error("お名前と電話番号の両方を入力してください。")
        else:
            matches = []
            for item in st.session_state.history_list:
                # テストデータ以外の本番予約から、名前と電話番号が完全に一致するものを検索
                if not item.get("is_test") and item.get("name") == cancel_name and item.get("phone") == cancel_phone:
                    matches.append(item["id"])
            st.session_state.cancel_search_ids = matches

# 検索結果とキャンセルボタンの表示
if st.session_state.cancel_search_ids is not None:
    if len(st.session_state.cancel_search_ids) == 0:
        st.warning("⚠️ 該当するご予約が見つかりませんでした。入力内容（スペースの有無など）をご確認ください。")
    else:
        st.success(f"✅ {len(st.session_state.cancel_search_ids)}件のご予約が見つかりました。")
        for item_id in st.session_state.cancel_search_ids:
            target_item = next((i for i in st.session_state.history_list if i.get("id") == item_id), None)
            if target_item:
                st.markdown(f"""
                <div style="border:1px solid #eaddd0; border-radius: 8px; padding: 15px; margin-bottom: 10px; background-color: #ffffff;">
                    <h4 style="margin:0; font-size: 1.1em; color: #333;">{target_item.get('display', '')}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # キャンセルボタンが押された時の処理
                if st.button("❌ この予約をキャンセルする", key=f"btn_do_cancel_{item_id}"):
                    # 対象の予約をリストから完全に削除
                    st.session_state.history_list = [i for i in st.session_state.history_list if i.get("id") != item_id]
                    st.session_state.cancel_search_ids = None # 検索結果をリセット
                    st.session_state.cancel_success = True
                    st.rerun() # 画面をリロードして最新状態を反映

# キャンセル成功時のメッセージ表示
if st.session_state.get('cancel_success', False):
    st.success("手続きが完了いたしました。ご予約をキャンセルしました。")
    st.session_state.cancel_success = False

# --- 4. 本日の受付一覧 ---
if st.session_state.history_list:
    st.divider()
    st.write("#### 【本日受付した予約一覧】")
    with st.container(height=150):
        for item in st.session_state.history_list:
            if not item.get("is_test"):
                st.markdown(f"<div style='border-bottom:1px solid #eee;padding:4px;'>{item.get('display', '')}</div>", unsafe_allow_html=True)

# 開発者メニュー
with st.expander("🛠 テスト用ダミーデータ生成"):
    if st.button("30日分の予約を追加"):
        for day_offset in range(30):
            target_date = datetime.today().date() + timedelta(days=day_offset)
            st.session_state.history_list.append({
                "id": str(uuid.uuid4()), "name": "テスト", "phone": "000-0000-0000",
                "date": target_date, "time": "10:00",
                "display": f"📅 {target_date} ⏰ 10:00 | テスト様 | 担当: 田中 健太 | ヘア | テスト自動生成",
                "is_test": True
            })
        st.success("ダミーデータを追加いたしました。")
