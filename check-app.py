import streamlit as st
import pandas as pd
import datetime

# ページの初期設定
st.set_page_config(page_title="おうち学習サポーター", page_icon="📝", layout="wide")
st.title("📝 おうち学習サポーター（きょうだい対応版）")

# 正しいパスワードの設定（自由に変更してください）
PARENT_PASSWORD = "pass"

# 全体で共有するデータ（簡易的な保存メモリ）
if "grading_history" not in st.session_state:
    st.session_state["grading_history"] = []
if "score_history" not in st.session_state:
    st.session_state["score_history"] = []

# 科目の選択肢
SUBJECTS = ["国語", "算数・数学", "理科", "社会", "英語", "その他"]

# --- 👥 左側のサイドバーで「誰のページか」と「モード」を選ぶ ---
with st.sidebar:
    st.header("👥 ユーザー選択")
    # 1. お子さん（自分 or 弟）を選ぶ
    current_student = st.radio("誰の記録を見ますか？", ["そうし", "保留"])
    
    st.write("---")
    # 2. 保護者モードへの切り替え
    st.header("⚙️ モード切替")
    app_mode = st.radio("モードを選択", ["🙋 子ども用ページ", "🔒 保護者用ページ"])
    
    # 保護者モードの時だけパスワード入力を求める
    is_parent_authenticated = False
    if app_mode == "🔒 保護者用ページ":
        password_input = st.text_input("保護者用パスワードを入力してください", type="password")
        if password_input == PARENT_PASSWORD:
            st.success("認証成功！保護者メニューを表示します。")
            is_parent_authenticated = True
        elif password_input != "":
            st.error("パスワードが違います")

# --- 🔄 メイン画面の表示制御 ---

# 🛑 【ケースA】保護者モードだけどパスワードが違う（または未入力）の場合
if app_mode == "🔒 保護者用ページ" and not is_parent_authenticated:
    st.warning("🔒 このページは保護者専用です。左側のサイドバーでパスワードを入力してください。")
    st.stop() # ここでプログラムの描画をストップする

# 🟢 【ケースB】保護者モード 且つ パスワードが合っている場合
elif app_mode == "🔒 保護者用ページ" and is_parent_authenticated:
    st.header(f"🛠️ 保護者専用メニュー（対象: {current_student}）")
    
    tab1, tab2 = st.tabs(["🔍 記述問題の採点・添削", "📊 科目ごとの正答率記録（入力・確認）"])
    
    # 記述問題の採点
    with tab1:
        st.subheader(f"🔍 {current_student} の記述採点とフィードバック")
        col1, col2 = st.columns(2)
        
        with col1:
            sub_tab1 = st.selectbox("科目を選択", SUBJECTS, key="tab1_subject")
            uploaded_q = st.file_uploader("1. 【問題】の写真をアップロード", type=["png", "jpg", "jpeg"], key="upload_q")
            if uploaded_q is not None: st.image(uploaded_q, caption="📷 問題", use_container_width=True)
                
            uploaded_a = st.file_uploader("2. 【模範解答】の写真をアップロード", type=["png", "jpg", "jpeg"], key="upload_a")
            if uploaded_a is not None: st.image(uploaded_a, caption="📷 模範解答", use_container_width=True)
                
            uploaded_child = st.file_uploader("3. 【子どものノート】の写真をアップロード", type=["png", "jpg", "jpeg"], key="upload_child")
            if uploaded_child is not None: st.image(uploaded_child, caption="📷 解答", use_container_width=True)

        with col2:
            st.info("💡 【AI助手エリア】\n将来的にここに、AIからのアドバイスが表示されるようになります！")
            st.write("---")
            score_status = st.radio("採点結果", ["⭕ 正解", "🔺 惜しい！部分点", "❌ 不正解"], horizontal=True)
            parent_comment = st.text_area("保護者からのひとことフィードバック", placeholder="例：よく書けてるよ！", height=150)
            
            if st.button("採点結果を保存する", type="primary"):
                st.session_state["grading_history"].append({
                    "日付": datetime.date.today(), "生徒名": current_student, "科目": sub_tab1, "判定": score_status, "フィードバック": parent_comment
                })
                st.success("🎉 採点結果を保存しました！")
                st.rerun()

    # 正答率の記録
    with tab2:
        st.subheader(f"📊 {current_student} のテスト結果の入力と記録")
        col3, col4 = st.columns([1, 2])
        with col3:
            sub_tab2 = st.selectbox("科目を選択", SUBJECTS, key="tab2_subject")
            test_date = st.date_input("テスト日", datetime.date.today())
            total_questions = st.number_input("全体の問題数", min_value=1, value=10, step=1)
            correct_questions = st.number_input("合っていた問題数", min_value=0, max_value=int(total_questions), value=7, step=1)
            accuracy_rate = round((correct_questions / total_questions) * 100, 1)
            st.metric(label="今回の正答率", value=f"{accuracy_rate} %")
            
            if st.button("結果を記録する"):
                st.session_state["score_history"].append({
                    "日付": test_date, "生徒名": current_student, "科目": sub_tab2, "総問題数": total_questions, "正解数": correct_questions, "正答率(%)": accuracy_rate
                })
                st.success("📈 結果を記録しました！")
                st.rerun()
                
        with col4:
            # 選択中の子どものデータだけを絞り込んで表示
            df_score = pd.DataFrame(st.session_state["score_history"])
            if not df_score.empty and current_student in df_score["生徒名"].values:
                df_student_score = df_score[df_score["生徒名"] == current_student]
                st.dataframe(df_student_score, use_container_width=True)
                st.line_chart(data=df_student_score, x="日付", y="正答率(%)")
            else:
                st.write(f"まだ {current_student} の記録データがありません。")

# 🔵 【ケースC】子ども用ページ（確認だけができるモード・パスワード不要）
else:
    st.header(f"🎒 {current_student} のお勉強確認ページ")
    st.write("保護者の方がつけてくれた採点結果や、これまでのグラフを確認しよう！")
    
    view_tab1, view_tab2 = st.tabs(["📋 記述問題の採点結果", "📈 テストの正答率グラフ"])
    
    with view_tab1:
        st.subheader("📬 保護者からのフィードバック履歴")
        df_grading = pd.DataFrame(st.session_state["grading_history"])
        if not df_grading.empty and current_student in df_grading["生徒名"].values:
            df_student_grad = df_grading[df_grading["生徒名"] == current_student]
            st.dataframe(df_student_grad[["日付", "科目", "判定", "フィードバック"]], use_container_width=True)
        else:
            st.write("まだ採点の履歴はありません。")
            
    with view_tab2:
        st.subheader("📊 これまでの正答率の推移")
        df_score = pd.DataFrame(st.session_state["score_history"])
        if not df_score.empty and current_student in df_score["生徒名"].values:
            df_student_score = df_score[df_score["score_history" == "生徒名"] == current_student] if False else df_score[df_score["生徒名"] == current_student]
            st.line_chart(data=df_student_score, x="日付", y="正答率(%)")
            st.dataframe(df_student_score[["日付", "科目", "総問題数", "正解数", "正答率(%)"]], use_container_width=True)
        else:
            st.write("まだテスト結果の記録はありません。")

