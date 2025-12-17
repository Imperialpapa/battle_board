"""
AI 베이스 클래스
모든 AI가 상속받는 추상 클래스
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..board import GameBoard, Move


class BaseAI(ABC):
    """AI 베이스 클래스"""

    def __init__(self, player_id: int):
        """
        Args:
            player_id: AI의 플레이어 ID (보통 0)
        """
        self.player_id = player_id

    @abstractmethod
    def get_move(self, board: GameBoard) -> Optional[Move]:
        """
        현재 보드 상태에서 최선의 수를 반환

        Args:
            board: 현재 게임 보드

        Returns:
            Move 또는 None (가능한 수가 없는 경우)
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """AI 이름 반환"""
        pass
