"""
캐릭터 정의 모듈
각 캐릭터의 타입, 우선순위, 특수 능력을 정의합니다.
"""

from enum import Enum
from typing import Optional


class CharacterType(Enum):
    """캐릭터 타입"""
    # 일반 캐릭터 (우선순위 1-14)
    GENERAL_5 = ("원수", 1, False)      # 원수
    GENERAL_4 = ("대장", 2, False)      # 대장
    GENERAL_3 = ("중장", 3, False)      # 중장
    GENERAL_2 = ("소장", 4, False)      # 소장
    GENERAL_1 = ("준장", 5, False)      # 준장
    COLONEL = ("대령", 6, False)        # 대령
    LT_COLONEL = ("중령", 7, False)     # 중령
    MAJOR = ("소령", 8, False)          # 소령
    CAPTAIN = ("대위", 9, False)        # 대위
    FIRST_LT = ("중위", 10, False)      # 중위
    SECOND_LT = ("소위", 11, False)     # 소위
    MASTER_SGT = ("상사", 12, False)    # 상사
    SGT = ("중사", 13, False)           # 중사
    CORPORAL = ("하사", 14, False)      # 하사

    # 특수 캐릭터
    BOMB_1 = ("폭탄1", 0, True)         # 폭탄1 - 공병에게 지고 모두를 이김
    BOMB_2 = ("폭탄2", 0, True)         # 폭탄2 - 공병에게 지고 모두를 이김
    ENGINEER = ("공병", 16, True)       # 공병 - 폭탄을 이김
    WUKONG_1 = ("손오공1", 17, True)    # 손오공1 - 오더 1~5를 이김
    WUKONG_2 = ("손오공2", 17, True)    # 손오공2 - 오더 1~5를 이김
    FLAG = ("국기", 19, True)           # 국기 - 모두에게 지고, 움직일 수 없음
    MP = ("헌병", 18, True)             # 헌병 - 상대방 정보 공개

    def __init__(self, display_name: str, priority: int, is_special: bool):
        self.display_name = display_name
        self.priority = priority
        self.is_special = is_special


class Character:
    """게임 캐릭터 클래스"""

    def __init__(self, char_type: CharacterType, player_id: int):
        """
        Args:
            char_type: 캐릭터 타입
            player_id: 플레이어 ID (0: AI, 1: Player)
        """
        self.type = char_type
        self.player_id = player_id
        self.is_alive = True
        self.is_revealed = False  # 상대방에게 공개되었는지 여부

    @property
    def name(self) -> str:
        """캐릭터 이름"""
        return self.type.display_name

    @property
    def priority(self) -> int:
        """우선순위"""
        return self.type.priority

    @property
    def is_special(self) -> bool:
        """특수 캐릭터 여부"""
        return self.type.is_special

    @property
    def can_move(self) -> bool:
        """이동 가능 여부"""
        # 국기와 폭탄은 움직일 수 없음
        return self.type not in [
            CharacterType.FLAG,
            CharacterType.BOMB_1,
            CharacterType.BOMB_2,
        ]

    def reveal(self):
        """캐릭터 정보 공개"""
        self.is_revealed = True

    def __repr__(self):
        return f"{self.name}(P{self.player_id})"


def create_full_team(player_id: int) -> list[Character]:
    """
    한 플레이어의 전체 캐릭터 21개를 생성합니다.

    Args:
        player_id: 플레이어 ID (0: AI, 1: Player)

    Returns:
        21개의 캐릭터 리스트
    """
    team = [
        # 일반 캐릭터 (1-14)
        Character(CharacterType.GENERAL_5, player_id),
        Character(CharacterType.GENERAL_4, player_id),
        Character(CharacterType.GENERAL_3, player_id),
        Character(CharacterType.GENERAL_2, player_id),
        Character(CharacterType.GENERAL_1, player_id),
        Character(CharacterType.COLONEL, player_id),
        Character(CharacterType.LT_COLONEL, player_id),
        Character(CharacterType.MAJOR, player_id),
        Character(CharacterType.CAPTAIN, player_id),
        Character(CharacterType.FIRST_LT, player_id),
        Character(CharacterType.SECOND_LT, player_id),
        Character(CharacterType.MASTER_SGT, player_id),
        Character(CharacterType.SGT, player_id),
        Character(CharacterType.CORPORAL, player_id),

        # 특수 캐릭터
        Character(CharacterType.BOMB_1, player_id),
        Character(CharacterType.BOMB_2, player_id),
        Character(CharacterType.ENGINEER, player_id),
        Character(CharacterType.WUKONG_1, player_id),
        Character(CharacterType.WUKONG_2, player_id),
        Character(CharacterType.FLAG, player_id),
        Character(CharacterType.MP, player_id),
    ]

    return team
