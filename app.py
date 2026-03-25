import streamlit as st
from datetime import datetime, timedelta
import re
import random

# ⚙️ UI レイアウト設定
# v4.0.0：シック＆モダンデザイン刷新、カテゴリ別動的配色、全日程エラー修正（Admin同期）
VERSION = "v4.0.0 (LabPeace シック＆モダン統合版)"

# シックでモダンなベーステーマカラー（ネイビーグレー ＆ クリームゴールド）
BASE_BG = "#2c3e50" # シックダーク背景
BASE_TEXT = "#ecf0f1" # ライトテキスト
ACCENT_GOLD = "#d9b38c" # アクセントゴールド

# カテゴリ別動的配色設定（通知エリア accent / タブ内背景 tab_bg）
CATEGORY_COLORS = {
    "✂️ ヘア (LAB Peace 予防医学)": {"accent": "#4f6c56", "tab_bg": "#f0f4f1"}, # モスグリーン
    "💆‍♀️ スパ (ドクターラブシステム)": {"accent": "#6a5acd", "tab_bg": "#f3f0f7"}, # ラベンダー
    "🛒 商品販売 (Precious EC)": {"accent": "#a0522d", "tab_bg": "#f7f0ed"}, # テラコッタ
    "👘 着付け": {"accent": "#4682b4", "tab_bg": "#f0f6fa"}, # アイリスブルー
    "💅 ネイル": {"accent": "#bc8f8f", "tab_bg": "#f7f0f0"}, # ローズマダー
    "🧘 瞑想教室": {"accent": "#98fb98", "tab_bg": "#f0f7f0"}, # ティーグリーン
    "🦷 歯医者": {"accent": "#5f9ea0", "tab_bg": "#f0f7f7"} # セルリアンブルー
}

st.set_page_config(page_title=f"Dr's Salon LAB 予約・商品購入システム {VERSION}", layout="wide")

# シック＆モダンデザイン適用（CSS）
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BASE_BG}; color: {BASE_TEXT}; }}
    /* ボタンデザイン */
    div.stButton > button:first-child {{
        background-color: {ACCENT_GOLD}; color: {BASE_BG};
        border-radius: 8px; border: none; width: 100%; font-weight: bold; padding: 12px;
        transition: background-color 0.3s;
    }}
    div.stButton > button:first-child:hover {{ background-color: #e5c3a1; }}
    /* タブデザイン */
    .stTabs [data-baseweb="tab-list"] button {{ color: {BASE_TEXT}; font-weight: bold; padding: 10px; }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{ color: {ACCENT_GOLD}; border-bottom-color: {ACCENT_GOLD}; }}
    /* エキスパンダーデザイン */
    .stExpander {{ background-color: rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; }}
    /* テキストコードデザイン */
    code {{ white-space: pre-wrap !important; word-break: break-all; color: {ACCENT_GOLD}; background-color: rgba(0,0,0,0.2); }}
    /* フォーム入力フィールドのデザイン（ネイビーグレー背景に合わせる） */
    .stTextInput input, .stSelectbox select, .stDateInput input, .stTimeInput input {{ color: {BASE_TEXT}; background-color: rgba(0,0,0,0.3); border-color: rgba(255,255,255,0.1); }}
    /* ラジオボタン */
    div[data-baseweb="radio"] label {{ color: {BASE_TEXT}; }}
    </style>
""", unsafe_allow_html=True)

st.title(f"Dr's Salon LAB 古河店 ({VERSION})")
st.subheader("総合オンライン予約 ＆ Precious EC 商品購入システム")

if 'history_list' not in st.session_state:
    st.session_state.history_list = []
if 'last_booking_signature' not in st.session_state:
    st.session_state.last_booking_signature = ""

def format_phone_number(phone_input):
    digits = re.sub(r'\D', '', phone_input.translate(str.maketrans('０１２３４５６７８９', '0123456789')))
    if len(digits) == 11: return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10: return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    return digits

def to_katakana(text):
    return "".join([chr(ord(c) + 96) if '\u3041' <= c <= '\u3096' else c for c in text])

# --- 1. お客様情報エリア ---
st.markdown("### 1. お客様情報を入力してください")
col1, col2, col3 = st.columns(3)
with col1:
    name = st.text_input("お名前（フルネーム・必須）")
with col2:
    raw_furigana = st.text_input("フリガナ（ひらがな・カタカナ自動変換）")
    furigana = to_katakana(raw_furigana)
    if raw_furigana:
        st.info(f"カタカナ変換: {furigana}")
with col3:
    raw_phone = st.text_input("電話番号（必須）")
    phone = format_phone_number(raw_phone)
    if raw_phone: 
        st.info(f"整えた番号: {phone}")

history = st.radio("ご来店歴", ["初めて（新規）", "2回目以降（再来）"], horizontal=True)

# LabPeace & Precious EC 統合サービス一覧
SERVICES = {
    "✂️ ヘア (LAB Peace 予防医学)": {
        "menus": {
            "【予防医学】Dr's LAB 根本改善カット": 6600, 
            "【T-Crystal】髪質改善カラー＋根本改善カット": 11000, 
            "【リバースエイジング】頭皮洗浄＋根本改善カット": 8800
        }, 
        "staffs": ["指名なし", "関根 光代", "田中 健太", "佐藤 美咲"]
    },
    "💆‍♀️ スパ (ドクターラブシステム)": {
        "menus": {
            "【フムスエキス配合】極上エナジースカルプスパ(60分)": 8000, 
            "【毛髪科学に基づく】リバースエイジングスパ(45分)": 6000
        }, 
        "staffs": ["指名なし", "鈴木 翔太", "山田 花子"]
    },
    "🛒 商品販売 (Precious EC)": {
        "menus": {
            "【新】01：シャンティン＋シャンプー(360mL)": 7920,
            "【新】02：ヴェーダ＋シャンプー(360mL)": 7480,
            "03：エナジースカルプトリートメント(550mL)": 6600,
            "06：オペラ ボタニカルヘアオイル(80mL)": 4290,
            "07：テネット 乳液トリートメント(100g)": 3300,
            "08：ロータス(150mL)": 3960,
            "ハードWAX": 2420,
            "01：ブラックシリカボール(1個)": 1980
        },
        "staffs": ["担当者不要（店舗受け取り）"]
    },
    "👘 着付け": {"menus": {"訪問着・留袖 着付け": 8800, "振袖 着付け": 12000}, "staffs": ["指名なし", "山田 花子", "高橋 陽子"]},
    "💅 ネイル": {"menus": {"ジェルネイル（ワンカラー）": 5000, "フットネイル": 6500}, "staffs": ["指名なし", "高橋 陽子"]},
    "🧘 瞑想教室": {"menus": {"初心者向けマインドフルネス": 3000}, "staffs": ["伊藤 翼"]},
    "🦷 歯医者": {"menus": {"検診・クリーニング": 0, "虫歯治療": 0}, "staffs": ["希望なし", "関根 光代"]}
}

st.markdown("---")
st.markdown("### 2. ご希望のサービスまたは商品を選択し、予約を確定してください")
tab_list = st.tabs(list(SERVICES.keys()))

ALL_TIME_SLOTS = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]

for i, (service_name, service_data) in enumerate(SERVICES.items()):
    # システムがカテゴリごとの配色を取得いたします
    colors = CATEGORY_COLORS.get(service_name, {"accent": ACCENT_GOLD, "tab_bg": BASE_BG})
    
    with tab_list[i]:
        # 【解決策1 & 2】タブ内の背景色をカテゴリ色に変更し、通知エリアをカスタムHTMLで色分けいたしました
        st.markdown(f"""
            <style>
            /* このタブ内のCSS */
            [data-testid="stForm"] {{ background-color: {colors['tab_bg']} !important; border-radius: 10px; padding: 25px; color: #333; }}
            /* フォーム内のラベル・テキスト色を調整 (タブ背景色に合わせる) */
            [data-testid="stForm"] .stText, [data-testid="stForm"] .stMarkdown p, [data-testid="stForm"] label, [data-testid="stForm"] div[data-baseweb="radio"] label {{ color: #333 !important; font-weight: bold; }}
            [data-testid="stForm"] input, [data-testid="stForm"] select, [data-testid="stForm"] .stDateInput div, [data-testid="stForm"] .stTimeInput div {{ color: #333 !important; border-color: {colors['accent']}; background-color: rgba(255,255,255,0.5); }}
            </style>
            
            <div style="background-color: {colors['accent']}; color: white; padding: 12px; border-radius: 8px; margin-bottom: 25px; font-weight: bold; font-size: 1.1em; text-align: center;">
                🟢 現在 **【 {service_name} 】** の予約画面を開いています
            </div>
        """, unsafe_allow_html=True)
        
        with st.form(key=f"form_{i}"):
            sel_menu = st.selectbox(f"{service_name} のメニューを選択", list(service_data["menus"].keys()))
            sel_staff = st.selectbox("ご希望の担当者", service_data["staffs"])
            
            d = st.date_input("ご希望の予約日（受取日）", key=f"date_{i}")
            
            # 空き時間計算
            booked_times = []
            if sel_staff not in ["指名なし", "希望なし", "担当者不要（店舗受け取り）"]:
                for record in st.session_state.history_list:
                    if str(d) in record and sel_staff in record and "テスト自動生成" not in record:
                        for slot in ALL_TIME_SLOTS:
                            if slot in record: booked_times.append(slot)
            
            available_times = [slot for slot in ALL_TIME_SLOTS if slot not in booked_times]
            
            if not available_times:
                st.write(f"⚠️ **申し訳ございません。{d} は担当者の予約が埋まっております。**")
                t = None
            else:
                t = st.selectbox("空いている時間を選択してください", available_times, key=f"time_{i}")
            
            dentist_info = ""
            if service_name == "🦷 歯医者":
                st.markdown("#### 📝 事前WEB問診票（必須）")
                q_symptom = st.text_area("1. 具体的な症状をご記入ください（いつから、どのように痛むか等）")
                dentist_info = f"\n症状: {q_symptom}"
            
            st.markdown("---")
            confirm_check = st.checkbox("上記の内容（お名前・フリガナ・日時など）に間違いがないか確認しました")
            submit_btn = st.form_submit_button(f"この内容で {service_name} の予約を確定する")
            
            if submit_btn:
                current_booking_signature = f"{name}_{sel_menu}_{d}_{t}"
                
                if not name or not furigana or len(phone) < 10:
                    st.write("🔴 **エラー: お名前（フルネーム）、フリガナ、正しい電話番号を入力してください。**")
                elif not confirm_check:
                    st.write("⚠️ **システムからの案内: 「確認しました」のチェックボックスをマウスでクリックしてください。**")
                elif service_name == "🦷 歯医者" and not q_symptom:
                    st.write("⚠️ **システムからの案内: 歯科予約の場合は、問診票の「症状」を必ず入力してください。**")
                elif current_booking_signature == st.session_state.last_booking_signature:
                    st.write("ℹ️ **案内: 既に同じ内容での予約が完了しています（二重送信防止）。**")
                else:
                    st.session_state.last_booking_signature = current_booking_signature
                    price = service_data["menus"][sel_menu]
                    price_str = f"{price}円" if price > 0 else "窓口でご相談"
                    
                    st.balloons()
                    st.write("### 🎉 予約が正常にシステムへ確定されました！")
                    
                    final_data = f"【予約完了】\nお名前: {name}（{furigana}）様\n電話: {phone}\n来店歴: {history}\n\nカテゴリ: {service_name}\nメニュー: {sel_menu}\n担当: {sel_staff}\n日時: {d} {t}\n目安金額: {price_str}{dentist_info}"
                    st.code(final_data)
                    
                    # 管理者カードの視覚化に合わせた形式で記録
                    new_history_line = f"📅 {d} ⏰ {t} | {name}（{furigana}）様 | 担当: {sel_staff} | {service_name}: {sel_menu} | {price_str}"
                    st.session_state.history_list.append(new_history_line)

# --- 3. 簡易履歴表示 ---
if st.session_state.history_list:
    st.divider()
    st.write("#### 【システムが本日受付した予約一覧】（※テストデータは非表示）")
    for item in st.session_state.history_list:
        if "テスト自動生成" not in item:
            st.code(item)

st.markdown("---")
with st.expander("🛠 開発者専用メニュー（動作テスト用のダミーデータ自動生成）"):
    if st.button("システムにダミー予約を30日分（計300件）自動で追加する"):
        dummy_data = [
            ("佐藤 健太", "サトウ ケンタ"), ("鈴木 美咲", "スズキ ミサキ"), ("高橋 翔太", "タカハシ ショウタ"), 
            ("田中 花子", "タナカ ハナコ"), ("伊藤 翼", "イトウ ツバサ"), ("渡辺 陽子", "ワタナベ ヨウコ"), 
            ("山本 大地", "ヤマモト ダイチ"), ("中村 さくら", "ナカムラ サクラ")
        ]
        dummy_staff_list = ["関根 光代", "田中 健太", "佐藤 美咲", "鈴木 翔太", "山田 花子", "高橋 陽子", "伊藤 翼"]
        dummy_services = list(SERVICES.keys())
        today = datetime.today().date()
        added_count = 0
        
        for day_offset in range(30):
            target_date = today + timedelta(days=day_offset)
            used_time_staff, used_names = set(), set()
            daily_count, attempts = 0, 0
            
            while daily_count < 10 and attempts < 100:
                attempts += 1
                r_time = random.choice(ALL_TIME_SLOTS)
                r_staff = random.choice(dummy_staff_list)
                r_person = random.choice(dummy_data)
                r_name, r_furi = r_person[0], r_person[1]
                r_service = random.choice(dummy_services)
                
                if (r_time, r_staff) not in used_time_staff and r_name not in used_names:
                    used_time_staff.add((r_time, r_staff))
                    used_names.add(r_name)
                    
                    # 記録形式も最新に同期いたします
                    dummy_record = f"📅 {target_date} ⏰ {r_time} | {r_name}（{r_furi}）様 | 担当: {r_staff} | {r_service} | テスト自動生成"
                    st.session_state.history_list.append(dummy_record)
                    daily_count += 1
                    added_count += 1
                    
        st.success(f"システムが30日分、合計{added_count}件の重複しないダミー予約を生成し、リストに追加いたしました。")
