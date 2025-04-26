import pandas as pd
import os


class RankingSystem:
    def __init__(self):
        # 创建数据存储目录
        os.makedirs('data', exist_ok=True)

        # 初始化或加载玩家数据
        self.players_path = 'data/players.csv'
        if os.path.exists(self.players_path):
            self.players = pd.read_csv(self.players_path, encoding='utf-8')
        else:
            self.players = pd.DataFrame(columns=[
                'ID', 'Name', 'Rating', 'Wins', 'Losses', 'Streak', 'History'
            ])

        # 初始化或加载对战记录
        self.matches_path = 'data/matches.csv'
        if os.path.exists(self.matches_path):
            self.matches = pd.read_csv(self.matches_path, parse_dates=['Timestamp'], encoding='utf-8')
        else:
            self.matches = pd.DataFrame(columns=[
                'Player1', 'Player2', 'Winner', 'Timestamp'
            ])

    def _update_ratings(self, player1, player2, winner):
        """更新玩家评分、胜负记录和连胜状态"""
        # 确定胜利方和失败方
        loser = player2 if winner == player1 else player1

        # 获取玩家索引
        winner_idx = self.players.index[self.players['Name'] == winner].tolist()[0]
        loser_idx = self.players.index[self.players['Name'] == loser].tolist()[0]

        # ======================
        # 1. Elo 评分系统计算
        # ======================
        K = 32  # 调整系数（新手建议40，高手建议16-24）

        # 获取当前评分
        R_winner = self.players.at[winner_idx, 'Rating']
        R_loser = self.players.at[loser_idx, 'Rating']

        # 计算期望胜率
        E_winner = 1 / (1 + 10 ** ((R_loser - R_winner) / 400))
        E_loser = 1 - E_winner

        # 更新评分
        self.players.at[winner_idx, 'Rating'] = round(R_winner + K * (1 - E_winner))
        self.players.at[loser_idx, 'Rating'] = round(R_loser + K * (0 - E_loser))

        # ======================
        # 2. 胜负记录更新
        # ======================
        self.players.at[winner_idx, 'Wins'] += 1
        self.players.at[loser_idx, 'Losses'] += 1

        # ======================
        # 3. 连胜状态计算
        # ======================
        # 胜利者连胜处理
        if self.players.at[winner_idx, 'Streak'] >= 0:
            self.players.at[winner_idx, 'Streak'] += 1
        else:
            self.players.at[winner_idx, 'Streak'] = 1  # 终止连败开始连胜

        # 失败者连败处理
        if self.players.at[loser_idx, 'Streak'] <= 0:
            self.players.at[loser_idx, 'Streak'] -= 1
        else:
            self.players.at[loser_idx, 'Streak'] = -1  # 终止连胜开始连败

        # ======================
        # 4. 历史战绩更新
        # ======================
        # 胜利者记录W（保留最后5场）
        winner_history = str(self.players.at[winner_idx, 'History'])
        self.players.at[winner_idx, 'History'] = (winner_history + "W")[-5:]

        # 失败者记录L（保留最后5场）
        loser_history = str(self.players.at[loser_idx, 'History'])
        self.players.at[loser_idx, 'History'] = (loser_history + "L")[-5:]

        # ======================
        # 5. 数据范围保护
        # ======================
        # 确保评分不低于最小值
        self.players.at[winner_idx, 'Rating'] = max(self.players.at[winner_idx, 'Rating'], 500)
        self.players.at[loser_idx, 'Rating'] = max(self.players.at[loser_idx, 'Rating'], 500)
    def save_data(self):
        """保存数据到CSV文件"""
        self.players.to_csv(self.players_path, index=False, encoding='utf-8')
        self.matches.to_csv(self.matches_path, index=False, encoding='utf-8')

    def add_match(self, player1, player2, winner):
        # 更新对战记录
        new_match = {
            'Player1': player1,
            'Player2': player2,
            'Winner': winner,
            'Timestamp': pd.Timestamp.now()
        }
        self.matches = pd.concat([self.matches, pd.DataFrame([new_match])], ignore_index=True)

        # 更新玩家数据（原逻辑）
        for player in [player1, player2]:
            if player not in self.players['Name'].values:
                self._add_new_player(player)

        self._update_ratings(player1, player2, winner)

        # 新增保存操作
        self.save_data()  # 每次添加比赛后自动保存

    def _add_new_player(self, name):
        new_player = {
            'ID': len(self.players) + 1,
            'Name': name,
            'Rating': 1000,
            'Wins': 0,
            'Losses': 0,
            'Streak': 0,
            'History': ''
        }
        self.players = pd.concat([self.players, pd.DataFrame([new_player])], ignore_index=True)
        self.save_data()  # 添加新玩家后保存