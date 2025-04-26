import streamlit as st
from data_manager import RankingSystem
from visualizer import draw_ladder, draw_force_directed_graph

# 初始化系统
if 'system' not in st.session_state:
    st.session_state.system = RankingSystem()
st.markdown("""
<style>
    body {
        font-family: "WenQuanYi Micro Hei", "Noto Color Emoji", "Segoe UI Emoji", sans-serif;
    }
</style>
""", unsafe_allow_html=True)
# 侧边栏 - 数据输入
with st.sidebar:
    st.header("⚔️ 添加对战记录")
    player1 = st.text_input("玩家1")
    player2 = st.text_input("玩家2")
    winner = st.radio("胜利者", [player1, player2])

    if st.button("提交比赛结果"):
        st.session_state.system.add_match(player1, player2, winner)
        st.success("数据已更新！")

# 主界面布局
tab1, tab2 = st.tabs(["天梯排名", "胜负关系"])

with tab1:
    st.header("🏆 天梯排行榜")
    players = st.session_state.system.players
    st.pyplot(draw_ladder(players))

with tab2:
    st.header("🗺️ 对战关系网络")
    matches = st.session_state.system.matches
    st.pyplot(draw_force_directed_graph(matches))

# 在数据编辑部分下方添加保存按钮
st.header("📊 原始数据")
col1, col2 = st.columns(2)
with col1:
    st.subheader("玩家数据")
    edited_players = st.data_editor(st.session_state.system.players)

with col2:
    st.subheader("对战记录")
    st.dataframe(st.session_state.system.matches)

# 新增保存按钮
if st.button("💾 手动保存所有数据"):
    st.session_state.system.players = edited_players  # 同步编辑后的数据
    st.session_state.system.save_data()
    st.toast("数据已成功保存！", icon="✅")
