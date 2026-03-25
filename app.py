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
            
            # システムが管理する1日の営業時間リスト（10:00〜18:00）
            ALL_TIME_SLOTS = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
            
            # お客様が選んだ「日付」と「担当者」の、すでに埋まっている時間をシステムが探し出します
            booked_times = []
            if sel_staff != "指名なし" and sel_staff != "希望なし":
                for record in st.session_state.history_list:
                    if str(d) in record and sel_staff in record:
                        for slot in ALL_TIME_SLOTS:
                            if slot in record:
                                booked_times.append(slot)
            
            # 全ての時間から、すでに埋まっている時間を引き算して「空き時間」を作ります
            available_times = [slot for slot in ALL_TIME_SLOTS if slot not in booked_times]
            
            # 空き時間の有無によって、画面の表示を切り替えます
            if not available_times:
                st.error("システムからのご案内：申し訳ございません。この日は担当者の予約がすべて埋まっております。カレンダーから別の日付を選択してください。")
                t = None
            else:
                t = st.selectbox("空いている時間を選択してください（予約済みの時間は自動で非表示になります）", available_times, key=f"time_{i}")
            
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
                    
                    # システムが空き時間を担当者ごとに判別するため、担当者名を記録に必ず追加いたします
                    new_history_line = f"{d} {t} | {name} 様 | 担当: {sel_staff} | {service_name}: {sel_menu} | {price_str}"
                    st.session_state.history_list.append(new_history_line)

# --- 3. 簡易履歴表示 ---
if st.session_state.history_list:
    st.divider()
    st.write("#### 【システムが本日受付した予約一覧】")
    for item in st.session_state.history_list:
        st.code(item)

# --- 🛠 開発者専用メニュー（テスト用自動予約システム） ---
st.markdown("---")
with st.expander("🛠 開発者専用メニュー（動作テスト用のダミーデータ自動生成）"):
    st.write("システムがランダムな予約データを自動で生成し、リストに追加いたします。")
    if st.button("システムにダミー予約を30日分（計300件）自動で追加する"):
        import random
        from datetime import timedelta
        
        dummy_names = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村", "小林", "加藤"]
        staff_list = ["田中", "佐藤", "鈴木", "専属着付師 山田", "高橋", "インストラクター 伊藤", "院長希望"]
        services = ["✂️ ヘア", "💆‍♀️ スパ", "👘 着付け", "💅 ネイル", "🧘 瞑想教室", "🦷 歯医者"]
        times = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        
        today = datetime.today().date()
        added_count = 0
        
        # システムは本日から30日間、1日ずつ順番に処理を進めます
        for day_offset in range(30):
            target_date = today + timedelta(days=day_offset)
            
            # その日の「すでに予約された時間と担当者のペア」と「予約したお客様の名前」を記録する入れ物を用意します
            used_time_staff = set()
            used_names = set()
            
            daily_count = 0
            attempts = 0 # 無限ループを防止するための安全装置です
            
            # システムは、重複がない10件の予約を1日ごとに生成いたします
            while daily_count < 10 and attempts < 100:
                attempts += 1
                r_time = random.choice(times)
                r_staff = random.choice(staff_list)
                r_name = random.choice(dummy_names)
                r_service = random.choice(services)
                
                # 同時刻・同担当者の重複、および同日の同じお客様の重複をシステムが厳密に弾きます
                if (r_time, r_staff) not in used_time_staff and r_name not in used_names:
                    used_time_staff.add((r_time, r_staff))
                    used_names.add(r_name)
                    
                    dummy_record = f"{target_date} {r_time} | {r_name} 様 | 担当: {r_staff} | {r_service} | テスト自動生成"
                    st.session_state.history_list.append(dummy_record)
                    daily_count += 1
                    added_count += 1
                    
        st.success(f"システムが30日分、合計{added_count}件の重複しないダミー予約を生成し、リストに追加いたしました。読者はブラウザの更新ボタンを押して、カレンダーの空き時間を確認してください。")
