import streamlit as st
import pandas as pd
import datetime

# --- 1. アプリの初期設定 ---
# --- 1. アプリの初期設定 ---
if 'study_data' not in st.session_state:
    # 中身を空っぽの表にする
    st.session_state.study_data = pd.DataFrame(columns=["日付", "科目", "時間(分)"])
    ])

if 'handwriting_status' not in st.session_state:
    st.session_state.handwriting_status = "未提出"

if 'quiz_list' not in st.session_state:
    st.session_state.quiz_list = [
        {"日付": "7/13", "問題": "太陽はどっちからのぼる？", "答え": "東"}
    ]

# --- 2. 共通タイトル ---
st.title("⚽ 受験＆サッカー 応援アプリ 📝")
st.write("弟くんの勉強とスポーツの両立をサポートするアプリです。")

st.sidebar.header("ユーザー切り替え")
user_mode = st.sidebar.radio("だれが使っていますか？", ["弟くん（学習モード）", "家族（保護者・サポーターモード）"])

# --- 3. ロードマップ ---
st.markdown("---")
exam_date = datetime.date(2026, 11, 1)  # 目標日
today = datetime.date.today()
days_left = (exam_date - today).days

st.subheader("🏁 11月の目標まであと何日？")
if days_left > 0:
    st.info(f"11月1日の本番まで あと **{days_left}日**！ 一歩ずつ進もう！")
else:
    st.success("目標の日になりました！全力を出し切ろう！")
st.markdown("---")

# --- 4. 弟くんモード ---
if user_mode == "弟くん（学習モード）":
    menu = st.tabs(["⏱️ 勉強タイマー＆記録", "🔍 ていねい文字チェック", "💡 今日のクイズ＆メモ", "📈 ぼくの成長グラフ"])
    
    with menu[0]:
        st.subheader("今日の勉強を記録しよう")
        subject = st.selectbox("科目を選んでね", ["算数", "国語", "理科", "社会", "サッカー練習"])
        minutes = st.number_input("何分がんばった？（分）", min_value=5, max_value=300, step=5, value=30)
        
        if st.button("記録を保存する"):
            new_data = pd.DataFrame([{"日付": today.strftime("%m/%d"), "科目": subject, "時間(分)": minutes}])
            st.session_state.study_data = pd.concat([st.session_state.study_data, new_data], ignore_index=True)
            st.success(f"「{subject}」を {minutes}分 記録したよ！えらいっ！")
            
    with menu[1]:
        st.subheader("ノートていねいさチェック")
        st.write(f"いまの状態： **{st.session_state.handwriting_status}**")
        uploaded_file = st.file_uploader("写真をアップロードしてね", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            st.image(uploaded_file, caption='アップロードしたノート', use_column_width=True)
            if st.button("家族にチェックをおねがいする"):
                st.session_state.handwriting_status = "判定待ち"
                st.info("家族にお願いしたよ！判定をまとう。")

    with menu[2]:
        st.subheader("小3の弟くんへのクイズを作ろう！")
        q_text = st.text_input("問題（例：日本で一番高い山は？）")
        a_text = st.text_input("答え（例：富士山）")
        if st.button("クイズを登録する"):
            if q_text and a_text:
                st.session_state.quiz_list.append({"日付": today.strftime("%m/%d"), "問題": q_text, "答え": a_text})
                st.success("クイズを登録したよ！")

    with menu[3]:
        st.subheader("これまでの勉強時間の合計")
        df = st.session_state.study_data
        df_grouped = df.groupby("日付")["時間(分)"].sum().reset_index()
        st.bar_chart(df_grouped.set_index("日付"))
        st.write("▼ これまでの細かい記録一覧")
        st.dataframe(df)

# --- 5. 家族モード ---
else:
    st.subheader("👨‍👩‍👦 保護者・サポーター管理画面")
    password = st.text_input("サポーター用パスワードを入力してください", type="password")
    
    if password == "1234":
        st.success("認証成功！いつもサポートお疲れ様です！")
        parent_menu = st.tabs(["🔍 ノートの文字判定", "📋 クイズの確認", "📊 全体の進捗確認"])
        
        with parent_menu[0]:
            st.write(f"現在のステータス: **{st.session_state.handwriting_status}**")
            if st.session_state.handwriting_status == "判定待ち":
                st.info("弟くんからノートが届いています！")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 はなまる！（合格）"):
                        st.session_state.handwriting_status = "合格！はなまる！💮"
                        st.balloons()
                with col2:
                    if st.button("✍️ もうすこし！（お直し）"):
                        st.session_state.handwriting_status = "もう一息！次がんばろう！"
            else:
                st.write("新しく届いているノートはありません。")
                
        with parent_menu[1]:
            st.table(st.session_state.quiz_list)
            
        with parent_menu[2]:
            st.dataframe(st.session_state.study_data)
    elif password != "":
        st.error("パスワードが違います。")