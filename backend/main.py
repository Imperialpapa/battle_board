"""
FastAPI 서버
게임 로직을 웹 API로 제공
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid

from game.board import GameBoard, Position, Move
from game.ai.basic_ai import BasicAI
from game.ai.mcts_ai import MCTSAI

app = FastAPI(title="Battle Board Game API")

# CORS 설정 (React 앱과 통신하기 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 게임 세션 저장소
game_sessions = {}


class NewGameRequest(BaseModel):
    """새 게임 생성 요청"""

    ai_difficulty: str = "basic"  # "basic" 또는 "advanced"
    player_positions: Optional[List[int]] = None  # 수동 배치용


class MoveRequest(BaseModel):
    """이동 요청"""

    from_row: int
    from_col: int
    to_row: int
    to_col: int


class GameResponse(BaseModel):
    """게임 상태 응답"""

    game_id: str
    board: List[List[Optional[dict]]]
    current_player: int
    game_over: bool
    winner: Optional[int]
    last_battle: Optional[dict]
    valid_moves: List[dict]


@app.get("/")
async def root():
    """API 정보"""
    return {
        "name": "Battle Board Game API",
        "version": "1.0.0",
        "endpoints": [
            "/game/new",
            "/game/{game_id}",
            "/game/{game_id}/move",
            "/game/{game_id}/ai-move",
        ],
    }


@app.post("/game/new")
async def create_new_game(request: NewGameRequest):
    """
    새 게임 생성

    Args:
        request: 게임 설정 (AI 난이도, 배치)

    Returns:
        게임 ID와 초기 보드 상태
    """
    # 게임 ID 생성
    game_id = str(uuid.uuid4())

    # 게임 보드 생성
    board = GameBoard()
    board.setup_board(request.player_positions)

    # AI 생성
    if request.ai_difficulty == "advanced":
        ai = MCTSAI(player_id=0, simulation_time=1.5)
    else:
        ai = BasicAI(player_id=0)

    # 세션 저장
    game_sessions[game_id] = {"board": board, "ai": ai}

    # 현재 상태 반환
    return await get_game_state(game_id)


@app.get("/game/{game_id}")
async def get_game_state(game_id: str):
    """
    게임 상태 조회

    Args:
        game_id: 게임 ID

    Returns:
        현재 게임 상태
    """
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")

    session = game_sessions[game_id]
    board = session["board"]

    # 플레이어 시점에서 보드 상태 (player_id=1)
    board_state = board.get_board_state(for_player=1)

    # 현재 플레이어의 유효한 이동 가져오기
    valid_moves = []
    if board.current_player == 1 and not board.game_over:
        all_moves = board.get_all_valid_moves(1)
        for pos, move in all_moves:
            valid_moves.append(
                {
                    "from_row": move.from_pos.row,
                    "from_col": move.from_pos.col,
                    "to_row": move.to_pos.row,
                    "to_col": move.to_pos.col,
                }
            )

    return {
        "game_id": game_id,
        "board": board_state,
        "current_player": board.current_player,
        "game_over": board.game_over,
        "winner": board.winner,
        "last_battle": board.last_battle,
        "valid_moves": valid_moves,
    }


@app.post("/game/{game_id}/move")
async def make_player_move(game_id: str, move_request: MoveRequest):
    """
    플레이어 이동 실행

    Args:
        game_id: 게임 ID
        move_request: 이동 정보

    Returns:
        업데이트된 게임 상태
    """
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")

    session = game_sessions[game_id]
    board = session["board"]

    # 현재 플레이어가 맞는지 확인
    if board.current_player != 1:
        raise HTTPException(status_code=400, detail="Not player's turn")

    # 게임이 끝났는지 확인
    if board.game_over:
        raise HTTPException(status_code=400, detail="Game is over")

    # 이동 실행
    from_pos = Position(move_request.from_row, move_request.from_col)
    to_pos = Position(move_request.to_row, move_request.to_col)
    move = Move(from_pos, to_pos)

    success = board.make_move(move)

    if not success:
        raise HTTPException(status_code=400, detail="Invalid move")

    return await get_game_state(game_id)


@app.post("/game/{game_id}/ai-move")
async def make_ai_move(game_id: str):
    """
    AI 이동 실행

    Args:
        game_id: 게임 ID

    Returns:
        업데이트된 게임 상태
    """
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")

    session = game_sessions[game_id]
    board = session["board"]
    ai = session["ai"]

    # 현재 플레이어가 AI인지 확인
    if board.current_player != 0:
        raise HTTPException(status_code=400, detail="Not AI's turn")

    # 게임이 끝났는지 확인
    if board.game_over:
        raise HTTPException(status_code=400, detail="Game is over")

    # AI 이동 실행
    ai_move = ai.get_move(board)

    if ai_move is None:
        raise HTTPException(status_code=500, detail="AI couldn't find a move")

    board.make_move(ai_move)

    return await get_game_state(game_id)


@app.delete("/game/{game_id}")
async def delete_game(game_id: str):
    """
    게임 삭제

    Args:
        game_id: 게임 ID

    Returns:
        삭제 확인
    """
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")

    del game_sessions[game_id]

    return {"message": "Game deleted successfully"}


@app.get("/game/{game_id}/moves")
async def get_valid_moves(game_id: str, row: int, col: int):
    """
    특정 캐릭터의 유효한 이동 가져오기

    Args:
        game_id: 게임 ID
        row: 캐릭터 행
        col: 캐릭터 열

    Returns:
        유효한 이동 목록
    """
    if game_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game not found")

    session = game_sessions[game_id]
    board = session["board"]

    pos = Position(row, col)
    valid_moves = board.get_valid_moves(pos)

    return {
        "valid_moves": [
            {"to_row": move.to_pos.row, "to_col": move.to_pos.col}
            for move in valid_moves
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
