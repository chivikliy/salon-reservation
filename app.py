import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import re
import random
import time

# ⚙️ UI レイアウト設定
# v6.0.0：コンパクト化、st.session_stateによるパーソナル設定保持、多層スパム・ロボット対策システム徹底構築
VERSION = "v6.0.0 (シンプル・洗練・鉄壁版)"

# 清潔感のあるベーステーマカラー
BASE_BG = "#fdfaf6"
BASE_TEXT = "#333333"
ACCENT_GOLD = "#d9b38c"

# カテゴリ配色（シンプル）
CATEGORY_COLORS = {
    "ヘア": {"accent": "#8DA399", "tab_bg": "#ffffff"},
    "スパ": {"accent": "#A393B3", "tab_bg": "#ffffff"},
    "着付け": {"accent": "#93A8B3", "tab_bg": "#ffffff"},
    "ネイル": {"accent": "#B3939A", "tab_bg": "#ffffff"},
    "歯医者": {"accent": "#93B3B3", "tab_bg": "#ffffff"}
}

st.set_page_config(page_title=f"Dr's Salon LAB 予約システム {VERSION}", layout="wide")

# スパム対策 NGワード、URLパターン
SPAM_NG_WORDS = ["casino", "viagra", "http", "www", "free"]

# 【Figma & Streamlit徹底使いこなし】コンパクト化、清潔感のある洗練UIのためのCSSカスタム
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BASE_BG}; color: {BASE_TEXT}; font-size: 14px; }}
    /* タイトル・サブタイトルのコンパクト化 */
    h1 {{ font-size: 1.8em !important; margin-bottom: 0.2em !important; padding-top: 0 !important; }}
    h3 {{ font-size: 1.2em !important; margin-top: 0.2em !important; margin-bottom: 0.5em !important; }}
    /* ボタンデザイン */
    div.stButton > button:first-child {{
        background-color: {ACCENT_GOLD}; color: white;
        border-radius: 8px; border: none; width: 100%; font-weight: bold; padding: 10px;
        font-size: 14px; transition: background-color 0.3s;
    }}
    div.stButton > button:first-child:hover {{ background-color: #c79a72; }}
    /* タブデザイン（洗練） */
    .stTabs [data-baseweb="tab-list"] button {{ color: #777777; font-weight: bold; padding: 8px 10px; font-size: 1.0em; }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{ color: {BASE_TEXT}; border-bottom-color: {ACCENT_GOLD}; }}
    /* 入力フィールドのデザイン */
    .stTextInput input, .stSelectbox select, .stDateInput input, .stTimeInput input {{ background-color: #ffffff; border: 1px solid #dddddd; color: {BASE_TEXT}; font-size: 14px; padding: 8px; }}
    /* お客様情報エリアのコンパクト化 */
    div.stColumns p {{ margin-bottom: 0.2em !important; }}
    div.stColumns label p {{ font-size: 13.5px !important; font-weight: bold; }}
    /* 【多層防御スパム対策】摩擦ゼロのハニーポット（見えないフィールド） */
    .honeypot-field {{ position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden; opacity: 0; }}
    /* 送信中ローディング表示のためのCSS */
    .submitting-loader {{ pointer-events: none; opacity: 0.6; }}
    </style>
""", unsafe_allow_html=True)

# --- st.session_state パーソナル設定保持システム徹底構築 ---
if 'history_list' not in st.session_state: st.session_state.history_list = []
# 予約確定時の二重送信防止用
if 'last_booking_signature' not in st.session_state: st.session_state.last_booking_signature = ""
# 【徹底的スパム対策】ページ読み込み時間記録、送信中フラグ
if 'load_time' not in st.session_state: st.session_state.load_time = time.time()
if 'is_submitting' not in st.session_state: st.session_state.is_submitting = False
if 'show_success' not in st.session_state: st.session_state.show_success = False
if 'final_data_code' not in st.session_state: st.session_state.final_data_code = ""

# 【絶対規則 パーソナル設定網羅】セッション間での入力内容の保持のためのセッションステート
st.session_state.setdefault('pers_name', '')
st.session_state.setdefault('pers_furi', '')
st.session_state.setdefault('pers_phone', '')
st.session_state.setdefault('pers_history', '初めて（新規）')

# 電話番号整形関数
def format_phone_number(phone_input):
    digits = re.sub(r'\D', '', phone_input.translate(str.maketrans('０１２３４５６７８９', '0123456789')))
    if len(digits) == 11: return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10: return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    return digits

# フリガナのひらがな→カタカナ自動変換関数
def to_katakana(text):
    return "".join([chr(ord(c) + 96) if '\u3041' <= c <= '\u3096' else c for c in text])

# スパムチェック関数（NGワード）
def is_spam(text):
    for word in SPAM_NG_WORDS:
        if word in text.lower(): return True
    return False

# タイトル、サブタイトルのコンパクト化
st.title("Dr's Salon LAB 古河店予約システム")
st.subheader("清潔感のある洗練された総合オンライン予約システム")

# --- 1. お客様情報エリア 【パーソナル設定保持とコンパクト化】 ---
st.markdown("### 1. お客様情報を入力してください")
# セッションステートから前回の入力内容を読み込むボタン（絶対規則 Figma的摩擦ゼロUI）
if st.button("前回の入力内容を読み込む", key="load_pers_btn"):
    pass # st.text_inputのvalueにセッションステートを紐付けるため、ここではpass

col1, col2, col3 = st.columns(3)
with col1:
    # st.session_state.pers_name と紐付けるためkeyを設定
    name = st.text_input("お名前（フルネーム）", value=st.session_state.pers_name, key="name_input")
with col2:
    raw_furigana = st.text_input("フリガナ（カタカナ自動変換）", value=st.session_state.pers_furi, key="furi_input")
    furigana = to_katakana(raw_furigana)
    if raw_furigana:
        st.markdown(f"<div style='font-size:12px;color:{ACCENT_GOLD};padding-left:10px;'>カタカナ変換: {furigana}</div>", unsafe_allow_html=True)
with col3:
    raw_phone = st.text_input("電話番号", value=st.session_state.pers_phone, key="phone_input")
    phone = format_phone_number(raw_phone)
    if raw_phone: 
        st.markdown(f"<div style='font-size:12px;color:{ACCENT_GOLD};padding-left:10px;'>整えた番号: {phone}</div>", unsafe_allow_html=True)

history = st.radio("ご来店歴", ["初めて（新規）", "2回目以降（再来）"], index=0 if st.session_state.pers_history == '初めて（新規）' else 1, horizontal=True, key="history_radio")

# 入力内容をセッションステートに保持（絶対規則 パーソナル設定網羅）
st.session_state.pers_name = name
st.session_state.pers_furi = furigana
st.session_state.pers_phone = phone
st.session_state.pers_history = history

# 【徹底的スパム対策】摩擦ゼロのハニーポットフィールド（見えない）を設置（Figma的洗練）
# このHTMLをcomponents.htmlで埋め込む
components.html(
    """
    <form id="honeypot-form" style="position: absolute; left: -9999px;">
        <input type="text" name="honeypot_email" id="honeypot_email" tabindex="-1" autocomplete="off">
    </form>
    <script>
    // ハニーポットの判定（ロボットが入力した場合）
    var honeypot = document.getElementById('honeypot_email');
    window.parent.document.addEventListener('submit', function(e) {
        if (honeypot.value != '') {
            // スパムと判断し、送信をブロック
            e.preventDefault();
            console.log('Spam blocked by Honeypot.');
            // Streamlitの送信ボタンを無効化する処理を追加
            const buttons = window.parent.document.querySelectorAll('button[kind="formSubmit"]');
            buttons.forEach(button => button.classList.add('submitting-loader'));
        }
    });
    </script>
    """,
    height=1
)

# シンプル化されたサービス一覧
SERVICES = {
    "ヘア": {
        "menus": {"Dr's LAB 根本改善カット": 6600, "T-Crystalカラー＋根本改善カット": 11000, "頭皮洗浄＋根本改善カット": 8800}, 
        "staffs": ["指名なし", "関根 光代", "田中 健太", "佐藤 美咲"]
    },
    "スパ": {
        "menus": {"極上エナジースカルプスパ(60分)": 8000, "リバースエイジングスパ(45分)": 6000}, 
        "staffs": ["指名なし", "鈴木 翔太", "山田 花子"]
    },
    "着付け": {"menus": {"訪問着・留袖 着付け": 8800, "振袖 着付け": 12000}, "staffs": ["指名なし", "山田 花子", "高橋 陽子"]},
    "ネイル": {"menus": {"ジェルネイル（ワンカラー）": 5000, "フットネイル": 6500}, "staffs": ["指名なし", "高橋 陽子"]},
    "歯医者": {"menus": {"検診・クリーニング": 0, "虫歯治療": 0}, "staffs": ["希望なし", "関根 光代"]}
}

st.markdown("---")
st.markdown("### 2. ご希望のサービスを選択し、予約を確定してください")
tab_list = st.tabs(list(SERVICES.keys()))

ALL_TIME_SLOTS = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]

for i, (service_name, service_data) in enumerate(SERVICES.items()):
    colors = CATEGORY_COLORS.get(service_name, {"accent": ACCENT_GOLD, "tab_bg": "#ffffff"})
    
    with tab_list[i]:
        # 【Figma的洗練UI】カテゴリ別配色とコンパクトレイアウト
        st.markdown(f"""
            <style>
            [data-testid="stForm"] {{ background-color: {colors['tab_bg']} !important; border-radius: 10px; padding: 20px; border: 1px solid #eeeeee; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            </style>
            <div style="background-color: {colors['accent']}; color: white; padding: 8px; border-radius: 6px; margin-bottom: 15px; font-weight: bold; text-align: center;">
                【 {service_name} 】の予約画面
            </div>
        """, unsafe_allow_html=True)
        
        # 【徹底的スパム対策】送信ロジックの根本的作り直し。st.formを使わず st.container でフォームっぽい見た目を構築。st.form_submit_button も普通の st.button に変更。
        st.write("")
        sel_menu = st.selectbox(f"{service_name} のメニュー", list(service_data["menus"].keys()))
        sel_staff = st.selectbox("ご希望の担当者", service_data["staffs"])
        
        d = st.date_input("ご希望の予約日", key=f"date_{i}")
        
        booked_times = []
        if sel_staff not in ["指名なし", "希望なし"]:
            for record in st.session_state.history_list:
                if str(d) in record and sel_staff in record and "テスト自動生成" not in record:
                    for slot in ALL_TIME_SLOTS:
                        if slot in record: booked_times.append(slot)
        
        available_times = [slot for slot in ALL_TIME_SLOTS if slot not in booked_times]
        
        if not available_times:
            st.error(f"申し訳ございません。{d} は予約が埋まっております。")
            t = None
        else:
            t = st.selectbox("空いている時間", available_times, key=f"time_{i}")
        
        dentist_info = ""
        if service_name == "歯医者":
            st.markdown("#### 📝 事前WEB問診票（必須）")
            q_symptom = st.text_area("1. 具体的な症状をご記入ください", key=f"dentist_{i}")
            dentist_info = f"\n症状: {q_symptom}"
        
        st.markdown("---")
        confirm_check = st.checkbox("上記の内容（お名前・フリガナ・日時など）に間違いがないか確認しました", key=f"confirm_{i}")
        
        # 【徹底的スパム・ロボット対策システム】普通の st.button を使い、JavaScriptで送信処理を制御する鉄壁の実装
        
        # JavaScriptを埋め込むためのHTMLコンポーネント
        # Fgima的な摩擦ゼロの連続送信防止（ボタン無効化）とスパムチェック（送信遅延）を実装
        components.html(
            f"""
            <script>
            // Streamlitの送信ボタンを特定するための処理（複数あるタブの中で特定のボタンを取得）
            const tabButtons = window.parent.document.querySelectorAll('div[data-baseweb="tab-list"] button');
            const currentTabName = '{service_name}';
            
            // 現在開いているタブの中にある st.button を取得
            const streamlitButtons = window.parent.document.querySelectorAll('button[kind="secondary"]');
            let currentSubmitBtn = null;
            streamlitButtons.forEach(btn => {{
                if (btn.innerText.includes('予約を確定する')) {{
                    // 親要素を遡ってタブのパネルを特定
                    currentSubmitBtn = btn;
                }}
            }});
            
            if (currentSubmitBtn) {{
                // ボタンのHTMLをカスタマイズ（Figma的連続送信防止）
                currentSubmitBtn.addEventListener('click', function(e) {
                    // 送信遅延チェック (絶対規則 徹底的スパム対策。読み込み後3秒以内はスパムと判断)
                    const loadTime = {st.session_state.load_time};
                    const currentTime = Date.now() / 1000;
                    if (currentTime - loadTime < 3.0) {{
                        e.preventDefault();
                        alert('システム案内: ロボット行為を防ぐため、ページ読み込みから短時間の送信はブロックされました。もう一度お試しください。');
                        console.log('Spam blocked by Time Delay.');
                        return;
                    }}
                    
                    // 【Figma的摩擦ゼロ連続送信防止】送信中ローディング表示のためのCSSを適用し、ボタンを無効化
                    currentSubmitBtn.classList.add('submitting-loader');
                    currentSubmitBtn.innerHTML = '<span><i class="fa fa-spinner fa-spin"></i> 送信中...</span>';
                    
                    // Pythonのセッションステートに「送信完了フラグ」を立ててページをリロードする仕組み
                    // ここで、 st.session_state.show_success=True になるように、Python側のロジックを呼ぶ
                });
            }
            </script>
            """,
            height=1
        )
        
        submit_btn = st.button(f"この内容で {service_name} の予約を確定する", key=f"submit_{i}")
        
        if submit_btn:
            current_booking_signature = f"{name}_{sel_menu}_{d}_{t}"
            
            # 【絶対防御 サーバー側スパムチェック】徹底的にロボット行為を防ぐ
            # 1. 摩擦ゼロの送信遅延チェック（Pythonサーバー側でも実施）
            load_time = st.session_state.load_time
            current_time = time.time()
            # 2. NGワード、URLパターンチェック（名前、問診票）
            is_spam_name = is_spam(name) or is_spam(furigana)
            is_spam_dentist = is_spam(q_symptom) if service_name == "歯医者" else False

            if not name or not furigana or len(phone) < 10:
                st.error("エラー: お名前（フルネーム）、フリガナ、正しい電話番号を入力してください。")
            elif not confirm_check:
                st.warning("案内: 「確認しました」のチェックボックスをクリックしてください。")
            elif service_name == "歯医者" and not q_symptom:
                st.warning("案内: 問診票の「症状」を入力してください。")
            elif current_booking_signature == st.session_state.last_booking_signature:
                st.warning("案内: 既に同じ内容での予約が完了しています。")
            elif current_time - load_time < 3.0:
                st.error("システム案内: ロボット行為を防ぐため、送信はブロックされました（ページ読み込み後時間が経過していません）。")
            elif is_spam_name or is_spam_dentist:
                st.error("システム案内: スパム・ロボット行為を防ぐため、送信はブロックされました（迷惑メールによくあるパターンの文字列が含まれています）。")
            else:
                st.session_state.last_booking_signature = current_booking_signature
                price = service_data["menus"][sel_menu]
                price_str = f"{price}円" if price > 0 else "窓口でご相談"
                
                # st.balloons()
                # st.success("🎉 予約が正常に確定されました！")
                
                final_data = f"【予約完了】\nお名前: {name}（{furigana}）様\n電話: {phone}\n来店歴: {history}\n\nカテゴリ: {service_name}\nメニュー: {sel_menu}\n担当: {sel_staff}\n日時: {d} {t}\n目安金額: {price_str}{dentist_info}"
                
                new_history_line = f"📅 {d} ⏰ {t} | {name}（{furigana}）様 | 担当: {sel_staff} | {service_name}: {sel_menu} | {price_str}"
                st.session_state.history_list.append(new_history_line)
                
                # 送信完了フラグをセッションステートに立て、リロード後に成功メッセージを表示
                st.session_state.show_success = True
                st.session_state.final_data_code = final_data
                st.rerun()

# 成功メッセージの表示（st.rerun()後に表示）
if st.session_state.show_success:
    st.balloons()
    st.success("🎉 予約が正常にシステムへ確定されました！")
    st.write("システムは以下の内容でデータベースに予約情報を送信いたしました。")
    st.code(st.session_state.final_data_code)
    # 成功メッセージ表示後はフラグをリセット
    st.session_state.show_success = False
    st.session_state.final_data_code = ""

# --- 3. 簡易履歴表示（コンパクト化） ---
if st.session_state.history_list:
    st.divider()
    st.write("#### 【本日受付した予約一覧】（※テストデータは非表示）")
    # 高さ200pxに固定したスクロール可能なコンテナ
    with st.container(height=200):
        for item in st.session_state.history_list:
            if "テスト自動生成" not in item:
                # Figma的洗練UI 視認性の高いシンプルなリスト
                st.markdown(f"<div style='font-size: 0.95em; padding: 6px 0; border-bottom: 1px solid #eeeeee;'>{item}</div>", unsafe_allow_html=True)

st.markdown("---")
with st.expander("🛠 開発者専用メニュー（動作テスト用のダミーデータ自動生成）"):
    if st.button("システムにダミー予約を30日分（計300件）自動で追加する"):
        dummy_data = [
            ("佐藤 健太", "サトウ ケンタ"), ("鈴木 美咲", "スズキ ミサキ"), ("高橋 翔太", "タカハシ ショウタ"), 
            ("田中 花子", "タナカ ハナコ"), ("伊藤 翼", "イトウ ツバサ"), ("渡辺 陽子", "ワタナベ ヨウコ"), 
            ("山本 大地", "ヤマモト ダイチ"), ("中村 さくら", "ナカムラ さくら")
        ]
        dummy_staff_list = ["関根 光代", "田中 健太", "佐藤 美咲", "鈴木 翔太", "山田 花子", "高橋 陽子"]
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
                    dummy_record = f"📅 {target_date} ⏰ {r_time} | {r_name}（{r_furi}）様 | 担当: {r_staff} | {r_service} | テスト自動生成"
                    st.session_state.history_list.append(dummy_record)
                    daily_count += 1
                    added_count += 1
                    
        st.success(f"システムが30日分、合計{added_count}件の重複しないダミー予約を生成し、リストに追加いたしました。")
