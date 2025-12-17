/**
 * 게임 보드 모듈
 * 보드 상태 관리, 캐릭터 이동, 게임 로직을 구현합니다.
 */

import { Character, CharacterType, createFullTeam } from './character.js'
import { resolveBattle } from './rules.js'

export class Position {
  constructor(row, col) {
    this.row = row
    this.col = col
  }

  equals(other) {
    return this.row === other.row && this.col === other.col
  }
}

export class Move {
  constructor(fromPos, toPos) {
    this.fromPos = fromPos
    this.toPos = toPos
  }
}

export class GameBoard {
  static ROWS = 9
  static COLS = 7

  constructor() {
    // 보드: 2D 배열 (null 또는 Character)
    this.board = Array(GameBoard.ROWS)
      .fill(null)
      .map(() => Array(GameBoard.COLS).fill(null))

    // 플레이어 팀
    this.aiTeam = createFullTeam(0)
    this.playerTeam = createFullTeam(1)

    // 게임 상태
    this.currentPlayer = 1 // 1: Player, 0: AI
    this.gameOver = false
    this.winner = null

    // 전투 로그
    this.lastBattle = null
  }

  setupBoard(playerPositions = null) {
    // AI 캐릭터 배치 (상단 3x7 = 21칸)
    const aiPositions = Array.from({ length: 21 }, (_, i) => i)
    this.shuffle(aiPositions)

    let idx = 0
    for (let row = 0; row < 3; row++) {
      for (let col = 0; col < GameBoard.COLS; col++) {
        const charIdx = aiPositions[idx]
        this.board[row][col] = this.aiTeam[charIdx]
        idx++
      }
    }

    // Player 캐릭터 배치 (하단 3x7 = 21칸)
    if (!playerPositions) {
      playerPositions = Array.from({ length: 21 }, (_, i) => i)
      this.shuffle(playerPositions)
    }

    idx = 0
    for (let row = GameBoard.ROWS - 3; row < GameBoard.ROWS; row++) {
      for (let col = 0; col < GameBoard.COLS; col++) {
        const charIdx = playerPositions[idx]
        this.board[row][col] = this.playerTeam[charIdx]
        idx++
      }
    }
  }

  shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[array[i], array[j]] = [array[j], array[i]]
    }
  }

  getCharacter(pos) {
    if (!this.isValidPosition(pos)) {
      return null
    }
    return this.board[pos.row][pos.col]
  }

  isValidPosition(pos) {
    return pos.row >= 0 && pos.row < GameBoard.ROWS && pos.col >= 0 && pos.col < GameBoard.COLS
  }

  getValidMoves(pos) {
    const character = this.getCharacter(pos)
    if (!character || !character.isAlive) {
      return []
    }

    if (!character.canMove) {
      return []
    }

    if (character.playerId !== this.currentPlayer) {
      return []
    }

    const validMoves = []
    const directions = [
      [-1, 0],
      [1, 0],
      [0, -1],
      [0, 1],
    ]

    for (const [dr, dc] of directions) {
      const newPos = new Position(pos.row + dr, pos.col + dc)

      if (!this.isValidPosition(newPos)) {
        continue
      }

      const target = this.getCharacter(newPos)

      // 빈 칸이거나, 상대방 캐릭터가 있는 경우만 이동 가능
      if (target === null || target.playerId !== character.playerId) {
        validMoves.push(new Move(pos, newPos))
      }
    }

    return validMoves
  }

  makeMove(move) {
    const character = this.getCharacter(move.fromPos)
    if (!character) {
      return false
    }

    // 유효한 이동인지 확인
    const validMoves = this.getValidMoves(move.fromPos)
    const isValid = validMoves.some(
      (m) => m.fromPos.equals(move.fromPos) && m.toPos.equals(move.toPos)
    )

    if (!isValid) {
      return false
    }

    const target = this.getCharacter(move.toPos)

    // 빈 칸으로 이동
    if (target === null) {
      this.board[move.toPos.row][move.toPos.col] = character
      this.board[move.fromPos.row][move.fromPos.col] = null
      this.lastBattle = null
    } else {
      // 전투 발생
      const battleResult = resolveBattle(character, target)

      // 전투 로그 저장
      this.lastBattle = {
        attacker: character.name,
        defender: target.name,
        attackerSurvives: battleResult.attackerSurvives,
        defenderSurvives: battleResult.defenderSurvives,
        attackerRevealed: battleResult.attackerRevealed,
        defenderRevealed: battleResult.defenderRevealed,
      }

      // 전투 결과 반영
      if (!battleResult.attackerSurvives) {
        character.isAlive = false
        this.board[move.fromPos.row][move.fromPos.col] = null
      }

      if (!battleResult.defenderSurvives) {
        target.isAlive = false
        this.board[move.toPos.row][move.toPos.col] = null
      }

      // 공격자가 승리하면 이동
      if (battleResult.attackerSurvives) {
        this.board[move.toPos.row][move.toPos.col] = character
        if (!move.fromPos.equals(move.toPos)) {
          this.board[move.fromPos.row][move.fromPos.col] = null
        }
      }

      // 캐릭터 공개 처리
      if (battleResult.attackerRevealed) {
        character.reveal()
      }
      if (battleResult.defenderRevealed) {
        target.reveal()
      }

      // 국기를 잡았는지 확인
      if (target.type === CharacterType.FLAG && !target.isAlive) {
        this.gameOver = true
        this.winner = character.playerId
      }
    }

    // 턴 변경
    this.currentPlayer = 1 - this.currentPlayer

    return true
  }

  getAllValidMoves(playerId) {
    const allMoves = []

    for (let row = 0; row < GameBoard.ROWS; row++) {
      for (let col = 0; col < GameBoard.COLS; col++) {
        const pos = new Position(row, col)
        const character = this.getCharacter(pos)

        if (character && character.isAlive && character.playerId === playerId) {
          const moves = this.getValidMoves(pos)
          for (const move of moves) {
            allMoves.push({ pos, move })
          }
        }
      }
    }

    return allMoves
  }

  clone() {
    const newBoard = new GameBoard()

    // 보드 복사
    newBoard.board = this.board.map((row) => [...row])

    // 팀 복사
    newBoard.aiTeam = [...this.aiTeam]
    newBoard.playerTeam = [...this.playerTeam]

    // 게임 상태 복사
    newBoard.currentPlayer = this.currentPlayer
    newBoard.gameOver = this.gameOver
    newBoard.winner = this.winner
    newBoard.lastBattle = this.lastBattle ? { ...this.lastBattle } : null

    return newBoard
  }

  getBoardState(forPlayer) {
    const state = []

    for (let row = 0; row < GameBoard.ROWS; row++) {
      const rowState = []
      for (let col = 0; col < GameBoard.COLS; col++) {
        const character = this.board[row][col]

        if (character === null) {
          rowState.push(null)
        } else {
          // 자기 편 캐릭터 또는 공개된 캐릭터는 정보 표시
          if (character.playerId === forPlayer || character.isRevealed) {
            rowState.push({
              name: character.name,
              type: character.typeName,
              player_id: character.playerId,
              is_alive: character.isAlive,
              is_revealed: character.isRevealed,
              priority: character.priority,
            })
          } else {
            // 상대방 캐릭터는 숨김
            rowState.push({
              name: '???',
              type: 'HIDDEN',
              player_id: character.playerId,
              is_alive: character.isAlive,
              is_revealed: false,
              priority: null,
            })
          }
        }
      }
      state.push(rowState)
    }

    return state
  }

  isGameOver() {
    return this.gameOver
  }

  getWinner() {
    return this.winner
  }
}
