/**
 * 기본 AI (규칙 기반 + 휴리스틱)
 *
 * 전략:
 * 1. 국기 방어 우선
 * 2. 상대방 국기 공격 시도
 * 3. 유리한 전투 선택
 * 4. 안전한 이동 선호
 */

import { CharacterType } from '../character.js'
import { Position } from '../board.js'
import { resolveBattle } from '../rules.js'

export class BasicAI {
  constructor(playerId = 0) {
    this.playerId = playerId
  }

  getName() {
    return '기본 AI'
  }

  getMove(board) {
    const allMoves = board.getAllValidMoves(this.playerId)

    if (allMoves.length === 0) {
      return null
    }

    // 1. 상대방 국기 공격 (즉시 승리)
    const flagCaptureMoves = this.findFlagCaptureMoves(board, allMoves)
    if (flagCaptureMoves.length > 0) {
      return this.randomChoice(flagCaptureMoves)
    }

    // 2. 확실히 이길 수 있는 전투
    const winningBattles = this.findWinningBattles(board, allMoves)
    if (winningBattles.length > 0) {
      // 우선순위가 높은 상대를 잡는 것 우선
      winningBattles.sort((a, b) => b.priority - a.priority)
      return winningBattles[0].move
    }

    // 3. 국기 방어
    const defensiveMoves = this.findDefensiveMoves(board, allMoves)
    if (defensiveMoves.length > 0) {
      return this.randomChoice(defensiveMoves)
    }

    // 4. 안전한 공격
    const safeAttacks = this.findSafeAttacks(board, allMoves)
    if (safeAttacks.length > 0) {
      return this.randomChoice(safeAttacks)
    }

    // 5. 전진
    const forwardMoves = this.findForwardMoves(board, allMoves)
    if (forwardMoves.length > 0) {
      return this.randomChoice(forwardMoves)
    }

    // 6. 랜덤 이동
    return this.randomChoice(allMoves.map((item) => item.move))
  }

  findFlagCaptureMoves(board, allMoves) {
    const flagMoves = []

    for (const { pos, move } of allMoves) {
      const target = board.getCharacter(move.toPos)
      if (target && target.type === CharacterType.FLAG) {
        flagMoves.push(move)
      }
    }

    return flagMoves
  }

  findWinningBattles(board, allMoves) {
    const winningMoves = []

    for (const { pos, move } of allMoves) {
      const attacker = board.getCharacter(pos)
      const target = board.getCharacter(move.toPos)

      if (!target) {
        continue
      }

      // 전투 시뮬레이션
      const result = resolveBattle(attacker, target)

      // 공격자가 확실히 이기는 경우
      if (result.attackerWins) {
        const targetPriority = target.isRevealed ? target.priority : 10
        winningMoves.push({ move, priority: targetPriority })
      }
    }

    return winningMoves
  }

  findDefensiveMoves(board, allMoves) {
    const defensiveMoves = []

    // 국기 위치 찾기
    const flagPos = this.findMyFlag(board)
    if (!flagPos) {
      return []
    }

    // 국기 주변을 방어
    for (const { pos, move } of allMoves) {
      // 국기 주변으로 이동하는 수
      if (this.isAdjacent(move.toPos, flagPos)) {
        defensiveMoves.push(move)
      }
    }

    return defensiveMoves
  }

  findSafeAttacks(board, allMoves) {
    const safeMoves = []

    for (const { pos, move } of allMoves) {
      const attacker = board.getCharacter(pos)
      const target = board.getCharacter(move.toPos)

      if (!target) {
        continue
      }

      // 상대가 공개되지 않았으면 조심스럽게 공격
      if (!target.isRevealed) {
        // 강한 유닛으로만 공격
        if (attacker.priority <= 8) {
          // 소령 이상
          safeMoves.push(move)
        }
      } else {
        // 공개된 상대면 확률적으로 괜찮은 전투
        const result = resolveBattle(attacker, target)
        if (!result.defenderWins) {
          // 비기거나 이기는 경우
          safeMoves.push(move)
        }
      }
    }

    return safeMoves
  }

  findForwardMoves(board, allMoves) {
    const forwardMoves = []

    // AI가 playerId=0이면 아래로 전진 (row 증가)
    // AI가 playerId=1이면 위로 전진 (row 감소)
    const direction = this.playerId === 0 ? 1 : -1

    for (const { pos, move } of allMoves) {
      // 빈 칸으로만 이동 (공격 제외)
      const target = board.getCharacter(move.toPos)
      if (target !== null) {
        continue
      }

      // 전진하는 방향인지 확인
      if ((move.toPos.row - move.fromPos.row) * direction > 0) {
        forwardMoves.push(move)
      }
    }

    return forwardMoves
  }

  findMyFlag(board) {
    for (let row = 0; row < board.constructor.ROWS; row++) {
      for (let col = 0; col < board.constructor.COLS; col++) {
        const pos = new Position(row, col)
        const char = board.getCharacter(pos)
        if (char && char.playerId === this.playerId && char.type === CharacterType.FLAG) {
          return pos
        }
      }
    }
    return null
  }

  isAdjacent(pos1, pos2) {
    return Math.abs(pos1.row - pos2.row) + Math.abs(pos1.col - pos2.col) === 1
  }

  randomChoice(array) {
    return array[Math.floor(Math.random() * array.length)]
  }
}
