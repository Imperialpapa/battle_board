"""
기본 AI (규칙 기반 + 휴리스틱)

전략:
1. 국기 방어 우선
2. 상대방 국기 공격 시도
3. 유리한 전투 선택
4. 안전한 이동 선호
"""

import random
from typing import Optional, List, Tuple
from .base_ai import BaseAI
from ..board import GameBoard, Move, Position
from ..character import CharacterType
from ..rules import resolve_battle


class BasicAI(BaseAI):
    """기본 AI (규칙 기반 + 휴리스틱)"""

    def __init__(self, player_id: int = 0):
        super().__init__(player_id)

    def get_name(self) -> str:
        return "기본 AI"

    def get_move(self, board: GameBoard) -> Optional[Move]:
        """
        현재 보드 상태에서 최선의 수를 반환

        우선순위:
        1. 상대방 국기 공격 (승리)
        2. 확실히 이길 수 있는 전투
        3. 국기 방어
        4. 안전한 공격
        5. 전진
        6. 랜덤 이동
        """

        all_moves = board.get_all_valid_moves(self.player_id)

        if not all_moves:
            return None

        # 1. 상대방 국기 공격 (즉시 승리)
        flag_capture_moves = self._find_flag_capture_moves(board, all_moves)
        if flag_capture_moves:
            return random.choice(flag_capture_moves)

        # 2. 확실히 이길 수 있는 전투
        winning_battles = self._find_winning_battles(board, all_moves)
        if winning_battles:
            # 우선순위가 높은 상대를 잡는 것 우선
            winning_battles.sort(key=lambda x: x[1], reverse=True)
            return winning_battles[0][0]

        # 3. 국기 방어
        defensive_moves = self._find_defensive_moves(board, all_moves)
        if defensive_moves:
            return random.choice(defensive_moves)

        # 4. 안전한 공격 (비길 수 있거나 약간 위험한 전투)
        safe_attacks = self._find_safe_attacks(board, all_moves)
        if safe_attacks:
            return random.choice(safe_attacks)

        # 5. 전진 (적진으로 이동)
        forward_moves = self._find_forward_moves(board, all_moves)
        if forward_moves:
            return random.choice(forward_moves)

        # 6. 랜덤 이동
        return random.choice([move for _, move in all_moves])

    def _find_flag_capture_moves(
        self, board: GameBoard, all_moves: List[Tuple[Position, Move]]
    ) -> List[Move]:
        """상대방 국기를 잡을 수 있는 수 찾기"""
        flag_moves = []

        for pos, move in all_moves:
            target = board.get_character(move.to_pos)
            if target and target.type == CharacterType.FLAG:
                flag_moves.append(move)

        return flag_moves

    def _find_winning_battles(
        self, board: GameBoard, all_moves: List[Tuple[Position, Move]]
    ) -> List[Tuple[Move, int]]:
        """확실히 이길 수 있는 전투 찾기 (상대 우선순위와 함께 반환)"""
        winning_moves = []

        for pos, move in all_moves:
            attacker = board.get_character(pos)
            target = board.get_character(move.to_pos)

            if target is None:
                continue

            # 전투 시뮬레이션
            result = resolve_battle(attacker, target)

            # 공격자가 확실히 이기는 경우
            if result.attacker_wins:
                target_priority = target.priority if target.is_revealed else 10
                winning_moves.append((move, target_priority))

        return winning_moves

    def _find_defensive_moves(
        self, board: GameBoard, all_moves: List[Tuple[Position, Move]]
    ) -> List[Move]:
        """국기 방어를 위한 수 찾기"""
        defensive_moves = []

        # 국기 위치 찾기
        flag_pos = self._find_my_flag(board)
        if flag_pos is None:
            return []

        # 국기 주변을 방어
        for pos, move in all_moves:
            # 국기 주변으로 이동하는 수
            if self._is_adjacent(move.to_pos, flag_pos):
                defensive_moves.append(move)

        return defensive_moves

    def _find_safe_attacks(
        self, board: GameBoard, all_moves: List[Tuple[Position, Move]]
    ) -> List[Move]:
        """안전한 공격 찾기"""
        safe_moves = []

        for pos, move in all_moves:
            attacker = board.get_character(pos)
            target = board.get_character(move.to_pos)

            if target is None:
                continue

            # 상대가 공개되지 않았으면 조심스럽게 공격
            if not target.is_revealed:
                # 강한 유닛으로만 공격
                if attacker.priority <= 8:  # 소령 이상
                    safe_moves.append(move)
            else:
                # 공개된 상대면 확률적으로 괜찮은 전투
                result = resolve_battle(attacker, target)
                if not result.defender_wins:  # 비기거나 이기는 경우
                    safe_moves.append(move)

        return safe_moves

    def _find_forward_moves(
        self, board: GameBoard, all_moves: List[Tuple[Position, Move]]
    ) -> List[Move]:
        """전진하는 수 찾기"""
        forward_moves = []

        # AI가 player_id=0이면 아래로 전진 (row 증가)
        # AI가 player_id=1이면 위로 전진 (row 감소)
        direction = 1 if self.player_id == 0 else -1

        for pos, move in all_moves:
            # 빈 칸으로만 이동 (공격 제외)
            target = board.get_character(move.to_pos)
            if target is not None:
                continue

            # 전진하는 방향인지 확인
            if (move.to_pos.row - move.from_pos.row) * direction > 0:
                forward_moves.append(move)

        return forward_moves

    def _find_my_flag(self, board: GameBoard) -> Optional[Position]:
        """내 국기 위치 찾기"""
        for row in range(board.ROWS):
            for col in range(board.COLS):
                pos = Position(row, col)
                char = board.get_character(pos)
                if (
                    char
                    and char.player_id == self.player_id
                    and char.type == CharacterType.FLAG
                ):
                    return pos
        return None

    def _is_adjacent(self, pos1: Position, pos2: Position) -> bool:
        """두 위치가 인접한지 확인"""
        return abs(pos1.row - pos2.row) + abs(pos1.col - pos2.col) == 1
