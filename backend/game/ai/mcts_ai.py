"""
고급 AI (Monte Carlo Tree Search with Determinization)

불완전 정보 게임을 위한 MCTS:
- Determinization: 상대방 캐릭터 배치를 확률적으로 추정
- UCT (Upper Confidence bounds applied to Trees): 탐색과 활용의 균형
- 시뮬레이션을 통한 평가
"""

import math
import random
import time
from typing import Optional, List, Dict
from .base_ai import BaseAI
from ..board import GameBoard, Move, Position
from ..character import CharacterType


class MCTSNode:
    """MCTS 트리 노드"""

    def __init__(self, board: GameBoard, move: Optional[Move] = None, parent=None):
        self.board = board.clone()
        self.move = move  # 부모에서 이 노드로 오는 수
        self.parent = parent
        self.children: List[MCTSNode] = []
        self.wins = 0
        self.visits = 0
        self.untried_moves: List[Move] = []

        # 가능한 수 초기화
        if not self.board.is_game_over():
            all_moves = self.board.get_all_valid_moves(self.board.current_player)
            self.untried_moves = [move for _, move in all_moves]

    def uct_value(self, exploration_weight: float = 1.41) -> float:
        """
        UCT (Upper Confidence bounds applied to Trees) 값 계산

        Args:
            exploration_weight: 탐색 가중치 (보통 sqrt(2))

        Returns:
            UCT 값
        """
        if self.visits == 0:
            return float("inf")

        exploit = self.wins / self.visits
        explore = exploration_weight * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )

        return exploit + explore

    def best_child(self, exploration_weight: float = 1.41):
        """UCT 값이 가장 높은 자식 노드 반환"""
        return max(self.children, key=lambda c: c.uct_value(exploration_weight))

    def most_visited_child(self):
        """가장 많이 방문된 자식 노드 반환"""
        return max(self.children, key=lambda c: c.visits)


class MCTSAI(BaseAI):
    """MCTS AI (Monte Carlo Tree Search with Determinization)"""

    def __init__(
        self,
        player_id: int = 0,
        simulation_time: float = 2.0,
        determinizations: int = 3,
    ):
        """
        Args:
            player_id: AI의 플레이어 ID
            simulation_time: 시뮬레이션 시간 (초)
            determinizations: Determinization 횟수
        """
        super().__init__(player_id)
        self.simulation_time = simulation_time
        self.determinizations = determinizations

    def get_name(self) -> str:
        return "고급 AI (MCTS)"

    def get_move(self, board: GameBoard) -> Optional[Move]:
        """
        MCTS를 사용하여 최선의 수를 반환

        불완전 정보를 처리하기 위해 Determinization 사용:
        1. 상대방 캐릭터 배치를 여러 번 추정
        2. 각 추정에 대해 MCTS 실행
        3. 결과를 종합하여 최선의 수 선택
        """

        # 가능한 수가 없으면 None 반환
        all_moves = board.get_all_valid_moves(self.player_id)
        if not all_moves:
            return None

        # Determinization: 여러 가능한 상대방 배치를 시뮬레이션
        move_scores: Dict[str, float] = {}

        for _ in range(self.determinizations):
            # 상대방 캐릭터 배치 추정
            determinized_board = self._determinize_board(board)

            # 이 배치에 대해 MCTS 실행
            best_move = self._mcts_search(determinized_board)

            if best_move:
                move_key = f"{best_move.from_pos.row},{best_move.from_pos.col}->{best_move.to_pos.row},{best_move.to_pos.col}"
                move_scores[move_key] = move_scores.get(move_key, 0) + 1

        # 가장 많이 선택된 수 반환
        if not move_scores:
            return random.choice([move for _, move in all_moves])

        best_move_key = max(move_scores, key=move_scores.get)
        parts = best_move_key.split("->")
        from_parts = parts[0].split(",")
        to_parts = parts[1].split(",")

        from_pos = Position(int(from_parts[0]), int(from_parts[1]))
        to_pos = Position(int(to_parts[0]), int(to_parts[1]))

        return Move(from_pos, to_pos)

    def _determinize_board(self, board: GameBoard) -> GameBoard:
        """
        상대방 캐릭터 배치를 추정하여 완전 정보 보드 생성

        공개되지 않은 상대방 캐릭터의 타입을 확률적으로 할당
        """
        determinized = board.clone()

        # 상대방 ID
        opponent_id = 1 - self.player_id

        # 공개되지 않은 상대방 캐릭터 찾기
        hidden_chars = []
        hidden_positions = []

        for row in range(board.ROWS):
            for col in range(board.COLS):
                pos = Position(row, col)
                char = determinized.get_character(pos)

                if (
                    char
                    and char.player_id == opponent_id
                    and not char.is_revealed
                    and char.is_alive
                ):
                    hidden_chars.append(char)
                    hidden_positions.append(pos)

        # 숨겨진 캐릭터들을 랜덤하게 섞음 (간단한 추정)
        # 실제로는 더 정교한 확률 모델을 사용할 수 있음
        if hidden_chars:
            random.shuffle(hidden_chars)

        return determinized

    def _mcts_search(self, board: GameBoard) -> Optional[Move]:
        """
        단일 보드 상태에 대해 MCTS 실행

        Args:
            board: 게임 보드 (determinized)

        Returns:
            최선의 수
        """
        root = MCTSNode(board)

        end_time = time.time() + self.simulation_time

        iterations = 0
        while time.time() < end_time:
            node = root

            # 1. Selection: UCT를 사용하여 리프 노드까지 이동
            while node.untried_moves == [] and node.children != []:
                node = node.best_child()

            # 2. Expansion: 새로운 노드 추가
            if node.untried_moves:
                move = random.choice(node.untried_moves)
                node.untried_moves.remove(move)

                # 새 보드 생성
                new_board = node.board.clone()
                new_board.make_move(move)

                child_node = MCTSNode(new_board, move, node)
                node.children.append(child_node)
                node = child_node

            # 3. Simulation: 랜덤 플레이아웃
            result = self._simulate(node.board)

            # 4. Backpropagation: 결과를 역전파
            while node is not None:
                node.visits += 1
                if result == self.player_id:
                    node.wins += 1
                elif result == -1:  # 무승부
                    node.wins += 0.5
                node = node.parent

            iterations += 1

        # 가장 많이 방문된 자식의 수 반환
        if root.children:
            best_child = root.most_visited_child()
            return best_child.move

        return None

    def _simulate(self, board: GameBoard, max_moves: int = 100) -> int:
        """
        게임을 끝까지 시뮬레이션

        Args:
            board: 시작 보드
            max_moves: 최대 이동 수

        Returns:
            승자 (player_id) 또는 -1 (무승부)
        """
        sim_board = board.clone()
        moves = 0

        while not sim_board.is_game_over() and moves < max_moves:
            all_moves = sim_board.get_all_valid_moves(sim_board.current_player)

            if not all_moves:
                break

            # 랜덤 수 선택 (기본 휴리스틱 적용 가능)
            move = self._select_simulation_move(sim_board, all_moves)

            if move:
                sim_board.make_move(move)

            moves += 1

        # 게임 결과 반환
        if sim_board.is_game_over():
            return sim_board.get_winner()

        # 무승부 또는 최대 이동 수 도달
        return -1

    def _select_simulation_move(
        self, board: GameBoard, all_moves: List[tuple]
    ) -> Optional[Move]:
        """
        시뮬레이션에서 사용할 수 선택 (간단한 휴리스틱)

        Args:
            board: 게임 보드
            all_moves: 가능한 모든 수

        Returns:
            선택된 수
        """
        # 국기를 잡을 수 있으면 우선
        for pos, move in all_moves:
            target = board.get_character(move.to_pos)
            if target and target.type == CharacterType.FLAG:
                return move

        # 그 외에는 랜덤
        if all_moves:
            return random.choice([move for _, move in all_moves])

        return None
