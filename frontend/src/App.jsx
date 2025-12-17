import { useState } from 'react'
import Board from './components/Board'
import { GameBoard, Position } from './game/board.js'
import { BasicAI } from './game/ai/basicAI.js'
import { MCTSAI } from './game/ai/mctsAI.js'
import './App.css'

function App() {
  const [gameBoard, setGameBoard] = useState(null)
  const [ai, setAi] = useState(null)
  const [gameState, setGameState] = useState(null)
  const [selectedCell, setSelectedCell] = useState(null)
  const [validMoves, setValidMoves] = useState([])
  const [aiDifficulty, setAiDifficulty] = useState('basic')
  const [loading, setLoading] = useState(false)

  // 새 게임 시작
  const startNewGame = () => {
    const board = new GameBoard()
    board.setupBoard()

    const newAi = aiDifficulty === 'advanced' ? new MCTSAI(0, 1.5) : new BasicAI(0)

    setGameBoard(board)
    setAi(newAi)
    setSelectedCell(null)
    setValidMoves([])
    updateGameState(board)
  }

  // 게임 상태 업데이트
  const updateGameState = (board) => {
    const boardState = board.getBoardState(1) // 플레이어 시점

    // 현재 플레이어의 유효한 이동 가져오기
    const moves = []
    if (board.currentPlayer === 1 && !board.gameOver) {
      const allMoves = board.getAllValidMoves(1)
      for (const { pos, move } of allMoves) {
        moves.push({
          from_row: move.fromPos.row,
          from_col: move.fromPos.col,
          to_row: move.toPos.row,
          to_col: move.toPos.col,
        })
      }
    }

    setGameState({
      board: boardState,
      current_player: board.currentPlayer,
      game_over: board.gameOver,
      winner: board.winner,
      last_battle: board.lastBattle,
      valid_moves: moves,
    })
  }

  // 셀 클릭 처리
  const handleCellClick = (row, col) => {
    if (!gameBoard || gameState.game_over || gameState.current_player !== 1 || loading) {
      return
    }

    const cell = gameState.board[row][col]

    // 이미 선택된 셀을 다시 클릭한 경우
    if (selectedCell && selectedCell.row === row && selectedCell.col === col) {
      setSelectedCell(null)
      setValidMoves([])
      return
    }

    // 유효한 이동 대상을 클릭한 경우
    if (selectedCell && validMoves.some((m) => m.to_row === row && m.to_col === col)) {
      makeMove(selectedCell.row, selectedCell.col, row, col)
      return
    }

    // 내 캐릭터를 선택한 경우
    if (cell && cell.player_id === 1 && cell.is_alive) {
      setSelectedCell({ row, col })
      fetchValidMoves(row, col)
    } else {
      setSelectedCell(null)
      setValidMoves([])
    }
  }

  // 유효한 이동 가져오기
  const fetchValidMoves = (row, col) => {
    const pos = new Position(row, col)
    const moves = gameBoard.getValidMoves(pos)

    setValidMoves(
      moves.map((move) => ({
        to_row: move.toPos.row,
        to_col: move.toPos.col,
      }))
    )
  }

  // 플레이어 이동 실행
  const makeMove = (fromRow, fromCol, toRow, toCol) => {
    setLoading(true)

    // 약간의 지연을 주어 UI 업데이트 보장
    setTimeout(() => {
      const fromPos = new Position(fromRow, fromCol)
      const toPos = new Position(toRow, toCol)
      const move = { fromPos, toPos }

      const success = gameBoard.makeMove(move)

      if (success) {
        updateGameState(gameBoard)
        setSelectedCell(null)
        setValidMoves([])

        // AI 차례면 자동으로 AI 이동
        if (gameBoard.currentPlayer === 0 && !gameBoard.gameOver) {
          setTimeout(() => makeAIMove(), 500)
        } else {
          setLoading(false)
        }
      } else {
        alert('유효하지 않은 이동입니다.')
        setLoading(false)
      }
    }, 100)
  }

  // AI 이동 실행
  const makeAIMove = () => {
    setLoading(true)

    // AI 계산을 비동기로 실행
    setTimeout(() => {
      const aiMove = ai.getMove(gameBoard)

      if (aiMove) {
        gameBoard.makeMove(aiMove)
        updateGameState(gameBoard)
      }

      setLoading(false)
    }, 100)
  }

  return (
    <div className="app">
      <h1 className="title">Battle Board Game</h1>

      {!gameBoard ? (
        <div className="menu">
          <h2>새 게임 시작</h2>
          <div className="difficulty-selector">
            <label>
              <input
                type="radio"
                value="basic"
                checked={aiDifficulty === 'basic'}
                onChange={(e) => setAiDifficulty(e.target.value)}
              />
              기본 AI (빠름)
            </label>
            <label>
              <input
                type="radio"
                value="advanced"
                checked={aiDifficulty === 'advanced'}
                onChange={(e) => setAiDifficulty(e.target.value)}
              />
              고급 AI (MCTS, 강력)
            </label>
          </div>
          <button onClick={startNewGame} className="btn-primary">
            게임 시작
          </button>
        </div>
      ) : (
        <div className="game-container">
          <div className="board-and-controls">
            <Board
              board={gameState?.board || []}
              selectedCell={selectedCell}
              validMoves={validMoves}
              onCellClick={handleCellClick}
              loading={loading}
            />

            <div className="game-controls">
              <button onClick={startNewGame} className="btn-new-game">
                새 게임
              </button>

              <div className="current-turn">
                <h3>현재 턴</h3>
                <p className={`turn-player ${gameState?.current_player === 1 ? 'player' : 'ai'}`}>
                  {gameState?.current_player === 1 ? '플레이어' : 'AI'}
                </p>
              </div>

              {gameState?.last_battle && (
                <div className="battle-log">
                  <h3>전투 결과</h3>
                  <p>
                    {gameState.last_battle.attacker} vs {gameState.last_battle.defender}
                    {' → '}
                    {gameState.last_battle.attackerSurvives && !gameState.last_battle.defenderSurvives
                      ? `${gameState.last_battle.attacker} 승리!`
                      : !gameState.last_battle.attackerSurvives && gameState.last_battle.defenderSurvives
                      ? `${gameState.last_battle.defender} 승리!`
                      : '무승부 (둘 다 사망)'}
                  </p>
                </div>
              )}

              {gameState?.game_over && (
                <div className="game-over">
                  <h2>게임 종료!</h2>
                  <p>승자: {gameState.winner === 1 ? '플레이어' : 'AI'}</p>
                </div>
              )}
            </div>
          </div>

          <div className="instructions">
            <h3>게임 방법</h3>
            <ul>
              <li>내 캐릭터(파란색)를 클릭하여 선택</li>
              <li>이동 가능한 위치(녹색)를 클릭하여 이동</li>
              <li>상대방 국기를 잡으면 승리!</li>
              <li>??? 표시는 아직 공개되지 않은 상대방 캐릭터</li>
              <li>서버 불필요 - 완전히 브라우저에서 작동</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
