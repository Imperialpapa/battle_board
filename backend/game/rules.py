"""
전투 규칙 모듈
캐릭터 간 전투 결과를 결정하는 로직을 구현합니다.
"""

from typing import Optional, Tuple
from .character import Character, CharacterType


class BattleResult:
    """전투 결과"""

    def __init__(
        self,
        attacker_survives: bool,
        defender_survives: bool,
        attacker_revealed: bool = True,
        defender_revealed: bool = True,
    ):
        """
        Args:
            attacker_survives: 공격자 생존 여부
            defender_survives: 방어자 생존 여부
            attacker_revealed: 공격자 정보 공개 여부
            defender_revealed: 방어자 정보 공개 여부
        """
        self.attacker_survives = attacker_survives
        self.defender_survives = defender_survives
        self.attacker_revealed = attacker_revealed
        self.defender_revealed = defender_revealed

    @property
    def both_die(self) -> bool:
        """둘 다 사망"""
        return not self.attacker_survives and not self.defender_survives

    @property
    def attacker_wins(self) -> bool:
        """공격자 승리"""
        return self.attacker_survives and not self.defender_survives

    @property
    def defender_wins(self) -> bool:
        """방어자 승리"""
        return not self.attacker_survives and self.defender_survives


def resolve_battle(attacker: Character, defender: Character) -> BattleResult:
    """
    두 캐릭터 간의 전투 결과를 결정합니다.

    Args:
        attacker: 공격하는 캐릭터 (이동한 캐릭터)
        defender: 방어하는 캐릭터 (원래 있던 캐릭터)

    Returns:
        BattleResult: 전투 결과
    """

    # 헌병 특수 처리: 전투 시 상대방만 공개
    if attacker.type == CharacterType.MP:
        defender.reveal()
        # 헌병은 우선순위 18로 전투
        return _resolve_general_battle(attacker, defender)

    if defender.type == CharacterType.MP:
        attacker.reveal()
        # 헌병은 우선순위 18로 전투
        return _resolve_general_battle(attacker, defender)

    # 특수 캐릭터 전투 처리
    result = _resolve_special_battle(attacker, defender)
    if result is not None:
        return result

    # 일반 전투 (우선순위 비교)
    return _resolve_general_battle(attacker, defender)


def _resolve_special_battle(
    attacker: Character, defender: Character
) -> Optional[BattleResult]:
    """
    특수 캐릭터 간의 전투를 처리합니다.

    Returns:
        BattleResult 또는 None (일반 전투로 처리해야 하는 경우)
    """

    # 국기는 모든 캐릭터에게 패배
    if defender.type == CharacterType.FLAG:
        return BattleResult(attacker_survives=True, defender_survives=False)

    # 폭탄 vs 공병
    if attacker.type == CharacterType.ENGINEER and defender.type in [
        CharacterType.BOMB_1,
        CharacterType.BOMB_2,
    ]:
        # 공병이 폭탄을 이김
        return BattleResult(attacker_survives=True, defender_survives=False)

    if defender.type == CharacterType.ENGINEER and attacker.type in [
        CharacterType.BOMB_1,
        CharacterType.BOMB_2,
    ]:
        # 공병이 폭탄을 이김
        return BattleResult(attacker_survives=False, defender_survives=True)

    # 폭탄 vs 일반 캐릭터 (폭탄이 이김)
    if attacker.type in [CharacterType.BOMB_1, CharacterType.BOMB_2]:
        if defender.type not in [
            CharacterType.BOMB_1,
            CharacterType.BOMB_2,
            CharacterType.ENGINEER,
        ]:
            return BattleResult(attacker_survives=True, defender_survives=False)

    if defender.type in [CharacterType.BOMB_1, CharacterType.BOMB_2]:
        if attacker.type not in [
            CharacterType.BOMB_1,
            CharacterType.BOMB_2,
            CharacterType.ENGINEER,
        ]:
            return BattleResult(attacker_survives=False, defender_survives=True)

    # 손오공 vs 우선순위 1~5 (원수~준장)
    top_ranks = [
        CharacterType.GENERAL_5,
        CharacterType.GENERAL_4,
        CharacterType.GENERAL_3,
        CharacterType.GENERAL_2,
        CharacterType.GENERAL_1,
    ]

    if attacker.type in [CharacterType.WUKONG_1, CharacterType.WUKONG_2]:
        if defender.type in top_ranks:
            # 손오공이 상위 장군들을 이김
            return BattleResult(attacker_survives=True, defender_survives=False)

    if defender.type in [CharacterType.WUKONG_1, CharacterType.WUKONG_2]:
        if attacker.type in top_ranks:
            # 손오공이 상위 장군들을 이김
            return BattleResult(attacker_survives=False, defender_survives=True)

    # 특수 전투가 아니면 None 반환 (일반 전투로 처리)
    return None


def _resolve_general_battle(attacker: Character, defender: Character) -> BattleResult:
    """
    일반 전투 (우선순위 비교)

    Args:
        attacker: 공격자
        defender: 방어자

    Returns:
        BattleResult: 전투 결과
    """

    attacker_priority = attacker.priority
    defender_priority = defender.priority

    if attacker_priority < defender_priority:
        # 우선순위가 낮을수록 강함 (1이 가장 강함)
        return BattleResult(attacker_survives=True, defender_survives=False)
    elif attacker_priority > defender_priority:
        return BattleResult(attacker_survives=False, defender_survives=True)
    else:
        # 같은 우선순위 -> 둘 다 사망
        return BattleResult(attacker_survives=False, defender_survives=False)
