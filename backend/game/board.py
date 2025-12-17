"""
게임 보드 모듈
보드 상태 관리, 캐릭터 이동, 게임 로직을 구현합니다.
"""

import random
from typing import Optional, Tuple, List, Dict
from copy import deepcopy
from .character import Character, CharacterType, create_full_team
from .rules import resolve_battle, BattleResult


class Position:
    """보드 위치"""

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

    def __repr__(self):
        return f"({self.row},{self.col})"


class Move:
    """이동 정보"""

    def __init__(self, from_pos: Position, to_pos: Position):
        self.from_pos = from_pos
        self.to_pos = to_pos

    def __repr__(self):
        return f"{self.from_pos} -> {self.to_pos}"


class GameBoard:
    """게임 보드"""

    ROWS = 9
    COLS = 7

    def __init__(self):
        """보드 초기화"""
        # 보드: 2D 배열 (None 또는 Character)
        self.board: List[List[Optional[Character]]] = [
            [None for _ in range(self.COLS)] for _ in range(self.ROWS)
        ]

        # 플레이어 팀
        self.ai_team: List[Character] = create_full_team(player_id=0)
        self.player_team: List[Character] = create_full_team(player_id=1)

        # 게임 상태
        self.current_player = 1  # 1: Player, 0: AI
        self.game_over = False
        self.winner: Optional[int] = None

        # 전투 로그
        self.last_battle: Optional[Dict] = None

    def setup_board(self, player_positions: Optional[List[int]] = None):
        """
        보드에 캐릭터 배치

        Args:
            player_positions: 플레이어 캐릭터 배치 순서 (0-20 인덱스 리스트)
                             None이면 자동 배치
        """
        # AI 캐릭터 배치 (상단 3x7 = 21칸)
        ai_positions = list(range(21))
        random.shuffle(ai_positions)

        idx = 0
        for row in range(3):
            for col in range(self.COLS):
                char_idx = ai_positions[idx]
                self.board[row][col] = self.ai_team[char_idx]
                idx += 1

        # Player 캐릭터 배치 (하단 3x7 = 21칸)
        if player_positions is None:
            player_positions = list(range(21))
            random.shuffle(player_positions)

        idx = 0
        for row in range(self.ROWS - 3, self.ROWS):
            for col in range(self.COLS):
                char_idx = player_positions[idx]
                self.board[row][col] = self.player_team[char_idx]
                idx += 1

    def get_character(self, pos: Position) -> Optional[Character]:
        """특정 위치의 캐릭터 가져오기"""
        if not self._is_valid_position(pos):
            return None
        return self.board[pos.row][pos.col]

    def _is_valid_position(self, pos: Position) -> bool:
        """유효한 위치인지 확인"""
        return 0 <= pos.row < self.ROWS and 0 <= pos.col < self.COLS

    def get_valid_moves(self, pos: Position) -> List[Move]:
        """
        특정 위치에서 가능한 모든 이동 반환

        Args:
            pos: 시작 위치

        Returns:
            가능한 Move 리스트
        """
        character = self.get_character(pos)
        if character is None or not character.is_alive:
            return []

        # 캐릭터가 움직일 수 없으면 (국기)
        if not character.can_move:
            return []

        # 현재 플레이어의 캐릭터가 아니면
        if character.player_id != self.current_player:
            return []

        valid_moves = []

        # 상하좌우 4방향
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            new_row = pos.row + dr
            new_col = pos.col + dc
            new_pos = Position(new_row, new_col)

            if not self._is_valid_position(new_pos):
                continue

            target = self.get_character(new_pos)

            # 빈 칸이거나, 상대방 캐릭터가 있는 경우만 이동 가능
            if target is None or target.player_id != character.player_id:
                valid_moves.append(Move(pos, new_pos))

        return valid_moves

    def make_move(self, move: Move) -> bool:
        """
        이동 실행

        Args:
            move: 이동 정보

        Returns:
            이동 성공 여부
        """
        character = self.get_character(move.from_pos)
        if character is None:
            return False

        # 유효한 이동인지 확인
        valid_moves = self.get_valid_moves(move.from_pos)
        is_valid = any(
            m.from_pos == move.from_pos and m.to_pos == move.to_pos
            for m in valid_moves
        )
        if not is_valid:
            return False

        target = self.get_character(move.to_pos)

        # 빈 칸으로 이동
        if target is None:
            self.board[move.to_pos.row][move.to_pos.col] = character
            self.board[move.from_pos.row][move.from_pos.col] = None
            self.last_battle = None
        else:
            # 전투 발생
            battle_result = resolve_battle(character, target)

            # 전투 로그 저장
            self.last_battle = {
                "attacker": character.name,
                "defender": target.name,
                "attacker_survives": battle_result.attacker_survives,
                "defender_survives": battle_result.defender_survives,
                "attacker_revealed": battle_result.attacker_revealed,
                "defender_revealed": battle_result.defender_revealed,
            }

            # 전투 결과 반영
            if not battle_result.attacker_survives:
                character.is_alive = False
                self.board[move.from_pos.row][move.from_pos.col] = None

            if not battle_result.defender_survives:
                target.is_alive = False
                self.board[move.to_pos.row][move.to_pos.col] = None

            # 공격자가 승리하면 이동
            if battle_result.attacker_survives:
                self.board[move.to_pos.row][move.to_pos.col] = character
                if move.from_pos != move.to_pos:
                    self.board[move.from_pos.row][move.from_pos.col] = None

            # 캐릭터 공개 처리
            if battle_result.attacker_revealed:
                character.reveal()
            if battle_result.defender_revealed:
                target.reveal()

            # 국기를 잡았는지 확인
            if target.type == CharacterType.FLAG and not target.is_alive:
                self.game_over = True
                self.winner = character.player_id

        # 턴 변경
        self.current_player = 1 - self.current_player

        return True

    def get_all_valid_moves(self, player_id: int) -> List[Tuple[Position, Move]]:
        """
        특정 플레이어의 모든 가능한 이동 반환

        Args:
            player_id: 플레이어 ID

        Returns:
            (시작 위치, Move) 튜플 리스트
        """
        all_moves = []

        for row in range(self.ROWS):
            for col in range(self.COLS):
                pos = Position(row, col)
                character = self.get_character(pos)

                if (
                    character is not None
                    and character.is_alive
                    and character.player_id == player_id
                ):
                    moves = self.get_valid_moves(pos)
                    for move in moves:
                        all_moves.append((pos, move))

        return all_moves

    def clone(self) -> "GameBoard":
        """보드 복사"""
        return deepcopy(self)

    def get_board_state(self, for_player: int) -> List[List[Optional[Dict]]]:
        """
        플레이어 시점에서 보드 상태 반환

        Args:
            for_player: 플레이어 ID (0: AI, 1: Player)

        Returns:
            2D 배열 (각 셀은 캐릭터 정보 딕셔너리 또는 None)
        """
        state = []

        for row in range(self.ROWS):
            row_state = []
            for col in range(self.COLS):
                character = self.board[row][col]

                if character is None:
                    row_state.append(None)
                else:
                    # 자기 편 캐릭터 또는 공개된 캐릭터는 정보 표시
                    if character.player_id == for_player or character.is_revealed:
                        row_state.append(
                            {
                                "name": character.name,
                                "type": character.type.name,
                                "player_id": character.player_id,
                                "is_alive": character.is_alive,
                                "is_revealed": character.is_revealed,
                                "priority": character.priority,
                            }
                        )
                    else:
                        # 상대방 캐릭터는 숨김
                        row_state.append(
                            {
                                "name": "???",
                                "type": "HIDDEN",
                                "player_id": character.player_id,
                                "is_alive": character.is_alive,
                                "is_revealed": False,
                                "priority": None,
                            }
                        )

            state.append(row_state)

        return state

    def is_game_over(self) -> bool:
        """게임 종료 확인"""
        return self.game_over

    def get_winner(self) -> Optional[int]:
        """승자 반환"""
        return self.winner
