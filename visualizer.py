import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from matplotlib import patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties

# for font in fonts:
#     if 'WenQuanYi Micro Hei' in font or 'Symbola' in font:
#         print(f"Found font: {font}")
plt.rcParams['font.family'] = ['WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问

plt.style.use('ggplot')
# ==============================================
# 天梯图可视化模块
# ==============================================
def draw_ladder(players):
    """生成带段位标识的渐变风格天梯图"""
    fig = plt.figure(figsize=(14, 10), facecolor='#2E2E2E')
    ax = fig.add_subplot(facecolor='#2E2E2E')

    # 段位配置系统
    RANK_CONFIG = {
        '青铜': {'color': '#CD7F32', 'threshold': 1000},
        '白银': {'color': '#C0C0C0', 'threshold': 1500},
        '黄金': {'color': '#FFD700', 'threshold': 2000},
        '白金': {'color': '#00CED1', 'threshold': 2500},
        '钻石': {'color': '#B9F2FF', 'threshold': 3000}
    }

    sorted_players = players.sort_values('Rating', ascending=False)

    for idx, (_, row) in enumerate(sorted_players.iterrows()):
        # 动态计算段位
        current_rank = next(
            (k for k, v in RANK_CONFIG.items() if row['Rating'] >= v['threshold']),
            '青铜'
        )
        rank_color = RANK_CONFIG[current_rank]['color']

        total_height = len(sorted_players)*4.5

        y_pos = total_height - (idx+1) * 4.5  # 纵向间距

        # ===== 卡片主体 =====
        # 渐变背景
        gradient = np.linspace(0, 1, 100).reshape(1, -1)
        ax.imshow(
            gradient, aspect='auto',
            cmap=LinearSegmentedColormap.from_list('grad', ['#FFFFFF00', rank_color]),
            extent=(0, 14, y_pos, y_pos + 4),
            alpha=0.2
        )

        # 主卡片
        card = plt.Rectangle(
            (0, y_pos), 14, 4,
            facecolor=rank_color + 'CC',
            edgecolor='gold' if current_rank == '钻石' else 'white',
            linewidth=2,
            linestyle='--' if row['Streak'] >= 3 else '-',
            zorder=2
        )
        ax.add_patch(card)

        # ===== 核心信息 =====
        # 段位徽章
        ax.text(
            1, y_pos + 2,
            f"{current_rank} {roman_numeral(row['Rating'] // 500)}",
            fontsize=16, weight='bold', color='white',
            path_effects=[pe.withStroke(linewidth=3, foreground="black")]
        )
        sum1 = row['Wins'] + row['Losses']
        if row['Wins'] + row['Losses'] == 0:
            sum1 = 1
        # 玩家数据
        info_text = (
                f"#{idx + 1} {row['Name']}\n"
                f"{row['Wins']}胜 {row['Losses']}负 | "
                f"胜率 {row['Wins'] / (sum1):.0%}\n"
                f"Rating: {row['Rating']}\n"
                f"{'连胜' if row['Streak'] > 0 else '连败'} {abs(row['Streak'])} "
                + ("▲" * min(3, row['Streak']) if row['Streak'] > 0 else "▼" * min(3, abs(row['Streak'])))
        )
        ax.text(3, y_pos + 3.71, info_text,
            fontsize=15, color='white', va='top',
            path_effects=[pe.withStroke(linewidth=2, foreground="black")]
        )

        # ===== 装饰元素 =====
        # 历史战绩块
        for i, res in enumerate(str(row['History'])[-6:]):
            ax.add_patch(plt.Rectangle(
                (11 + i * 0.7, y_pos + 0.5), 0.6, 0.6,
                facecolor='#4CAF50' if res == 'W' else '#FF5252',
                edgecolor='white'
            ))

        # 头像占位符
        ax.add_patch(plt.Circle(
            (12.5, y_pos + 2), 1.2,
            facecolor='#FFFFFF80', edgecolor='white'
        ))
        ax.text(12.8, y_pos + 2, "TOP1" if idx == 0 else "TOP"+str(idx+1),
                fontsize=24, ha='center', va='center')

        # 全局装饰
        ax.set_title('==============荣耀天梯==============',
                     fontsize=28, color='white', pad=20,
                      weight='bold')
        ax.set_xlim(0, 14)
        ax.set_ylim(0, len(players) * 4.5)
        ax.axis('off')
        plt.tight_layout()
    return fig

def draw_force_directed_graph(matches):
    """力导向对战关系图"""
    # 初始化画布
    fig, ax = plt.subplots(figsize=(12, 9), facecolor='#F5F5F5')

    # 创建有向图
    G = nx.DiGraph()

    # 构建边权重数据
    edge_weights = {}
    for _, row in matches.iterrows():
        winner = row['Winner']
        loser = row['Player1'] if winner != row['Player1'] else row['Player2']
        edge = (winner, loser)
        edge_weights[edge] = edge_weights.get(edge, 0) + 1

    # 添加节点和边
    for (winner, loser), weight in edge_weights.items():
        G.add_edge(winner, loser, weight=weight)

    # 计算力导向布局
    pos = nx.spring_layout(
        G,
        k=0.8 / np.sqrt(len(G.nodes())),  # 节点间距系数
        iterations=100,  # 布局迭代次数
        seed=42,  # 固定随机种子
        weight='weight'  # 边权重影响布局
    )

    # 可视化参数
    node_size = [800 + 300 * G.degree(n) for n in G.nodes()]  # 节点大小反映活跃度
    edge_width = [0.5 + 1.5 * G[u][v]['weight'] for u, v in G.edges()]  # 边宽反映对战次数

    # 绘制节点
    nx.draw_networkx_nodes(
        G, pos,
        node_size=node_size,
        node_color='#4CAF50',  # 主题绿色
        alpha=0.9,
        edgecolors='#2E7D32',  # 深绿边框
        linewidths=1.5,
        ax=ax
    )

    # 绘制边
    edges = nx.draw_networkx_edges(
        G, pos,
        edge_color='#757575',  # 高级灰
        width=edge_width,
        arrowsize=15,
        arrowstyle='->,head_width=0.4,head_length=0.6',
        connectionstyle='arc3,rad=0.2',
        ax=ax
    )

    # 绘制标签
    nx.draw_networkx_labels(
        G, pos,
        font_size=12,
        font_color='white',
        bbox=dict(
            facecolor='#2E7D32',
            alpha=0.8,
            boxstyle='round,pad=0.3'
        ),
        ax=ax
    )

    # 添加统计信息
    ax.text(
        0.95, 0.95,
        f"总对战次数: {sum(edge_weights.values())}\n玩家数量: {len(G.nodes())}",
        transform=ax.transAxes,
        ha='right',
        va='top',
        bbox=dict(facecolor='white', alpha=0.8)
    )

    # 隐藏边框
    ax.axis('off')
    plt.tight_layout()
    return fig
def roman_numeral(val):
    """将数字转为罗马数字"""
    return ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'][val % 7]
