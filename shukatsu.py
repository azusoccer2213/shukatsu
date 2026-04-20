import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- ページ設定 ---
st.set_page_config(page_title="就活総合管理アプリ", layout="wide", page_icon="💼")

# --- データ管理設定 ---
FILES = {
    "企業分析": "company_analysis.csv",
    "ES": "es_data.csv",
    "自己分析": "self_analysis.csv",
    "メモ": "recruit_memo.csv"
}

# 企業分析に「内容（メモ）」を追加
COLUMNS = {
    "企業分析": ["更新日", "企業名", "業界", "志望度", "強み", "弱み・課題", "機会・チャンス", "ライバル・競合", "選考状況", "ID_メールアドレス", "パスワード", "内容"],
    "ES": ["更新日", "企業名", "設問", "文字数制限", "回答案", "現在文字数", "提出期限"],
    "自己分析": ["更新日", "項目", "具体的なエピソード", "面接でのアピール方法"],
    "メモ": ["日付", "カテゴリ", "タイトル", "ID_メールアドレス", "パスワード", "内容"]
}

def load_data(key):
    filename = FILES[key]
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            for col in COLUMNS[key]:
                if col not in df.columns:
                    df[col] = ""
            df = df[COLUMNS[key]]
            df = df.fillna("")
            return df
        except Exception as e:
            st.error(f"データの読み込みエラー: {e}")
            return pd.DataFrame(columns=COLUMNS[key])
    else:
        return pd.DataFrame(columns=COLUMNS[key])

def save_data(key, df):
    df.to_csv(FILES[key], index=False)

# --- サイドバー ---
with st.sidebar:
    st.title("💼 就活マネジメント")
    st.markdown("---")
    menu = st.radio(
        "メニューを選択",
        ["① ホーム", "② 企業分析", "③ ESページ", "④ 自己分析", "⑤ リクルート情報メモ"],
        key="main_menu"
    )

# ==========================================
# ① ホーム
# ==========================================
if menu == "① ホーム":
    st.title("🏠 ホーム・ダッシュボード")
    df_es = load_data("ES")
    df_memo = load_data("メモ")
    df_company = load_data("企業分析")
    today = datetime.now().date()

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("登録企業数", f"{len(df_company)} 社")
    with col2:
        if not df_es.empty:
            df_es['提出期限'] = pd.to_datetime(df_es['提出期限'], errors='coerce').dt.date
            active_es = len(df_es[df_es['提出期限'] >= today])
            st.metric("進行中のES", f"{active_es} 件")
        else: st.metric("進行中のES", "0 件")
    with col3:
        if not df_memo.empty:
            df_memo['日付'] = pd.to_datetime(df_memo['日付'], errors='coerce').dt.date
            upcoming_events = len(df_memo[df_memo['日付'] >= today])
            st.metric("今後の予定", f"{upcoming_events} 件")
        else: st.metric("今後の予定", "0 件")

# ==========================================
# ② 企業分析 (ID・パスワード・メモ欄を追加)
# ==========================================
elif menu == "② 企業分析":
    st.title("🏢 企業分析")
    df_company = load_data("企業分析")
    
    with st.expander("➕ 新規企業の登録", expanded=False):
        with st.form("company_form", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                company = st.text_input("企業名*")
                industry = st.selectbox("業界", ["メーカー", "IT・通信", "商社", "金融", "コンサル", "インフラ", "サービス", "その他"])
                c_id = st.text_input("ログインID / メールアドレス")
            with col_f2:
                status = st.selectbox("選考状況", ["興味あり", "説明会待ち", "ES提出済", "面接(1次)", "面接(2次)", "最終面接", "内定", "お見送り"])
                rank = st.slider("志望度", 1, 5, 3)
                c_pw = st.text_input("パスワード", type="password")
            
            st.markdown("##### 企業メモ")
            c_memo = st.text_area("備考・メモ (社風や選考の注意点など)")

            st.markdown("##### SWOT分析")
            c_sw1, c_sw2 = st.columns(2)
            with c_sw1:
                strength = st.text_area("強み")
                opportunity = st.text_area("機会")
            with c_sw2:
                weakness = st.text_area("弱み")
                rival = st.text_area("競合")

            if st.form_submit_button("登録"):
                if company:
                    new_data = [
                        datetime.now().strftime("%Y-%m-%d"), 
                        company, industry, rank, strength, weakness, 
                        opportunity, rival, status, c_id, c_pw, c_memo
                    ]
                    new_row = pd.DataFrame([new_data], columns=COLUMNS["企業分析"])
                    df_company = pd.concat([df_company, new_row], ignore_index=True)
                    save_data("企業分析", df_company)
                    st.rerun()

    for i, row in df_company.iterrows():
        with st.expander(f"🏢 {row['企業名']} | {row['選考状況']}"):
            edit_mode = st.checkbox("編集する", key=f"edit_co_check_{i}")
            if edit_mode:
                with st.form(f"edit_form_co_{i}"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        e_status = st.selectbox("選考状況", ["興味あり", "説明会待ち", "ES提出済", "面接(1次)", "面接(2次)", "最終面接", "内定", "お見送り"], index=["興味あり", "説明会待ち", "ES提出済", "面接(1次)", "面接(2次)", "最終面接", "内定", "お見送り"].index(row['選考状況']))
                        e_id = st.text_input("ログインID / メールアドレス", value=row['ID_メールアドレス'])
                    with col_e2:
                        e_rank = st.slider("志望度", 1, 5, int(row['志望度']))
                        e_pw = st.text_input("パスワード", value=row['パスワード'])
                    
                    e_memo = st.text_area("備考・メモ", value=row['内容'])
                    e_strength = st.text_area("強み", value=row['強み'])
                    e_weakness = st.text_area("弱み", value=row['弱み・課題'])

                    if st.form_submit_button("更新"):
                        df_company.at[i, '選考状況'] = e_status
                        df_company.at[i, '志望度'] = e_rank
                        df_company.at[i, 'ID_メールアドレス'] = e_id
                        df_company.at[i, 'パスワード'] = e_pw
                        df_company.at[i, '内容'] = e_memo
                        df_company.at[i, '強み'] = e_strength
                        df_company.at[i, '弱み・課題'] = e_weakness
                        df_company.at[i, '更新日'] = datetime.now().strftime("%Y-%m-%d")
                        save_data("企業分析", df_company)
                        st.rerun()
            else:
                st.write(f"志望度: {'⭐' * int(row['志望度'])}")
                
                c_acc1, c_acc2 = st.columns(2)
                with c_acc1:
                    st.code(f"ID: {row['ID_メールアドレス']}", language="text")
                with c_acc2:
                    st.code(f"PW: {row['パスワード']}", language="text")
                
                if row['内容']:
                    st.info(f"📝 企業メモ:\n{row['内容']}")
                
                st.write(f"💪 強み: {row['強み']}")
                
                if st.button("削除", key=f"del_co_{i}"):
                    df_company = df_company.drop(i).reset_index(drop=True)
                    save_data("企業分析", df_company)
                    st.rerun()

# ==========================================
# ③ ESページ 
# ==========================================
elif menu == "③ ESページ":
    st.title("📝 ES管理")
    df_es = load_data("ES")
    with st.expander("➕ 新規ES登録"):
        with st.form("es_form", clear_on_submit=True):
            co = st.text_input("企業名*")
            q = st.text_area("設問*")
            dl = st.date_input("提出期限")
            ans = st.text_area("回答案")
            if st.form_submit_button("保存"):
                new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), co, q, 400, ans, len(ans), dl]], columns=COLUMNS["ES"])
                df_es = pd.concat([df_es, new_row], ignore_index=True)
                save_data("ES", df_es)
                st.rerun()
    
    for i, row in df_es.iterrows():
        with st.expander(f"{row['企業名']} | {row['提出期限']}"):
            edit_mode = st.checkbox("編集する", key=f"edit_es_check_{i}")
            if edit_mode:
                with st.form(f"edit_form_es_{i}"):
                    e_q = st.text_area("設問", value=row['設問'])
                    e_ans = st.text_area("回答案", value=row['回答案'])
                    if st.form_submit_button("更新"):
                        df_es.at[i, '設問'] = e_q
                        df_es.at[i, '回答案'] = e_ans
                        df_es.at[i, '現在文字数'] = len(e_ans)
                        df_es.at[i, '更新日'] = datetime.now().strftime("%Y-%m-%d")
                        save_data("ES", df_es)
                        st.rerun()
            else:
                st.write(f"設問: {row['設問']}")
                st.info(row['回答案'])
                st.caption(f"文字数: {len(row['回答案'])}")
                if st.button("削除", key=f"del_es_{i}"):
                    df_es = df_es.drop(i).reset_index(drop=True)
                    save_data("ES", df_es)
                    st.rerun()

# ==========================================
# ④ 自己分析
# ==========================================
elif menu == "④ 自己分析":
    st.title("🔍 自己分析")
    df_self = load_data("自己分析")
    with st.expander("➕ 新規追加"):
        with st.form("self_form", clear_on_submit=True):
            cat = st.selectbox("項目", ["強み", "研究内容", "ガクチカ", "志望動機(軸)", "自己PR"])
            epi = st.text_area("内容")
            method = st.text_area("アピール方法")
            if st.form_submit_button("保存"):
                new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), cat, epi, method]], columns=COLUMNS["自己分析"])
                df_self = pd.concat([df_self, new_row], ignore_index=True)
                save_data("自己分析", df_self)
                st.rerun()

    for i, row in df_self.iterrows():
        with st.expander(f"📌 {row['項目']}"):
            edit_mode = st.checkbox("編集する", key=f"edit_self_check_{i}")
            if edit_mode:
                with st.form(f"edit_form_self_{i}"):
                    e_epi = st.text_area("内容", value=row['具体的なエピソード'])
                    e_method = st.text_area("アピール方法", value=row['面接でのアピール方法'])
                    if st.form_submit_button("更新"):
                        df_self.at[i, '具体的なエピソード'] = e_epi
                        df_self.at[i, '面接でのアピール方法'] = e_method
                        save_data("自己分析", df_self)
                        st.rerun()
            else:
                st.write(row['具体的なエピソード'])
                st.subheader("💡 アピール方法")
                st.write(row['面接でのアピール方法'])
                if st.button("削除", key=f"del_self_{i}"):
                    df_self = df_self.drop(i).reset_index(drop=True)
                    save_data("自己分析", df_self)
                    st.rerun()

# ==========================================
# ⑤ リクルート情報メモ
# ==========================================
elif menu == "⑤ リクルート情報メモ":
    st.title("📓 メモ")
    df_memo = load_data("メモ")
    with st.expander("➕ 追加"):
        with st.form("memo_form", clear_on_submit=True):
            d = st.date_input("日付")
            c = st.selectbox("カテゴリ", ["面接", "説明会", "その他"])
            t = st.text_input("タイトル*")
            cnt = st.text_area("内容")
            if st.form_submit_button("保存"):
                new_row = pd.DataFrame([[d, c, t, "", "", cnt]], columns=COLUMNS["メモ"])
                df_memo = pd.concat([df_memo, new_row], ignore_index=True)
                save_data("メモ", df_memo)
                st.rerun()

    for i, row in df_memo.iterrows():
        with st.expander(f"{row['日付']} | {row['タイトル']}"):
            edit_mode = st.checkbox("編集する", key=f"edit_memo_check_{i}")
            if edit_mode:
                with st.form(f"edit_form_memo_{i}"):
                    e_t = st.text_input("タイトル", value=row['タイトル'])
                    e_cnt = st.text_area("内容", value=row['内容'])
                    if st.form_submit_button("更新"):
                        df_memo.at[i, 'タイトル'] = e_t
                        df_memo.at[i, '内容'] = e_cnt
                        save_data("メモ", df_memo)
                        st.rerun()
            else:
                st.write(row['内容'])
                if st.button("削除", key=f"del_memo_{i}"):
                    df_memo = df_memo.drop(i).reset_index(drop=True)
                    save_data("メモ", df_memo)
                    st.rerun()