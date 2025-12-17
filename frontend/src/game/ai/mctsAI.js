/**
 * 고급 AI (Monte Carlo Tree Search with Determinization)
 *
 * 불완전 정보 게임을 위한 MCTS:
 * - Determinization: 상대방 캐릭터 배치를 확률적으로 추정
 * - UCT (Upper Confidence bounds applied to Trees): 탐색과 활용의 균형
 * - 시뮬레이션을 통한 평가
 */

import { CharacterType } from '../character.js'

class MCTSNode {
  constructor(board, move = null, parent = null) {
    this.board = board.clone()
    this.move = move
    this.parent = parent
    this.children = []
    this.wins = 0
    this.visits = 0
    this.untriedMoves = []

    // 가능한 수 초기화
    if (!this.board.isGameOver()) {
      const allMoves = this.board.getAllValidMoves(this.board.currentPlayer)
      this.untriedMoves = allMoves.map((item) => item.move)
    }
  }

  uctValue(explorationWeight = 1.41) {
    if (this.visits === 0) {
      return Infinity
    }

    const exploit = this.wins / this.visits
    const explore = explorationWeight * Math.sqrt(Math.log(this.parent.visits) / this.visits)

    return exploit + explore
  }

  bestChild(explorationWeight = 1.41) {
    return this.children.reduce((best, child) => {
      return child.uctValue(explorationWeight) > best.uctValue(explorationWeight) ? child : best
    })
  }

  mostVisitedChild() {
    return this.children.reduce((best, child) => {
      return child.visits > best.visits ? child : best
    })
  }
}

export class MCTSAI {
  constructor(playerId = 0, simulationTime = 2.0, determinizations = 3) {
    this.playerId = playerId
    this.simulationTime = simulationTime
    this.determinizations = determinizations
  }

  getName() {
    return '고급 AI (MCTS)'
  }

  getMove(board) {
    // 가능한 수가 없으면 null 반환
    const allMoves = board.getAllValidMoves(this.playerId)
    if (allMoves.length === 0) {
      return null
    }

    // Determinization: 여러 가능한 상대방 배치를 시뮬레이션
    const moveScores = {}

    for (let i = 0; i < this.determinizations; i++) {
      // 상대방 캐릭터 배치 추정
      const determinizedBoard = this.determinizeBoard(board)

      // 이 배치에 대해 MCTS 실행
      const bestMove = this.mctsSearch(determinizedBoard)

      if (bestMove) {
        const moveKey = `${bestMove.fromPos.row},${bestMove.fromPos.col}->${bestMove.toPos.row},${bestMove.toPos.col}`
        moveScores[moveKey] = (moveScores[moveKey] || 0) + 1
      }
    }

    // 가장 많이 선택된 수 반환
    if (Object.keys(moveScores).length === 0) {
      return this.randomChoice(allMoves.map((item) => item.move))
    }

    const bestMoveKey = Object.keys(moveScores).reduce((a, b) => {
      return moveScores[a] > moveScores[b] ? a : b
    })

    const parts = bestMoveKey.split('->')
    const fromParts = parts[0].split(',')
    const toParts = parts[1].split(',')

    const fromPos = { row: parseInt(fromParts[0]), col: parseInt(fromParts[1]) }
    const toPos = { row: parseInt(toParts[0]), col: parseInt(toParts[1]) }

    return { fromPos, toPos }
  }

  determinizeBoard(board) {
    // 간단한 구현: 그냥 보드를 복제
    // 실제로는 더 정교한 확률 모델 사용 가능
    return board.clone()
  }

  mctsSearch(board) {
    const root = new MCTSNode(board)
    const endTime = Date.now() + this.simulationTime * 1000

    let iterations = 0
    while (Date.now() < endTime) {
      let node = root

      // 1. Selection: UCT를 사용하여 리프 노드까지 이동
      while (node.untriedMoves.length === 0 && node.children.length > 0) {
        node = node.bestChild()
      }

      // 2. Expansion: 새로운 노드 추가
      if (node.untriedMoves.length > 0) {
        const move = this.randomChoice(node.untriedMoves)
        node.untriedMoves = node.untriedMoves.filter((m) => m !== move)

        // 새 보드 생성
        const newBoard = node.board.clone()
        newBoard.makeMove(move)

        const childNode = new MCTSNode(newBoard, move, node)
        node.children.push(childNode)
        node = childNode
      }

      // 3. Simulation: 랜덤 플레이아웃
      const result = this.simulate(node.board)

      // 4. Backpropagation: 결과를 역전파
      while (node !== null) {
        node.visits++
        if (result === this.playerId) {
          node.wins++
        } else if (result === -1) {
          // 무승부
          node.wins += 0.5
        }
        node = node.parent
      }

      iterations++
    }

    // 가장 많이 방문된 자식의 수 반환
    if (root.children.length > 0) {
      const bestChild = root.mostVisitedChild()
      return bestChild.move
    }

    return null
  }

  simulate(board, maxMoves = 100) {
    const simBoard = board.clone()
    let moves = 0

    while (!simBoard.isGameOver() && moves < maxMoves) {
      const allMoves = simBoard.getAllValidMoves(simBoard.currentPlayer)

      if (allMoves.length === 0) {
        break
      }

      // 랜덤 수 선택 (기본 휴리스틱 적용 가능)
      const move = this.selectSimulationMove(simBoard, allMoves)

      if (move) {
        simBoard.makeMove(move)
      }

      moves++
    }

    // 게임 결과 반환
    if (simBoard.isGameOver()) {
      return simBoard.getWinner()
    }

    // 무승부 또는 최대 이동 수 도달
    return -1
  }

  selectSimulationMove(board, allMoves) {
    // 국기를 잡을 수 있으면 우선
    for (const { pos, move } of allMoves) {
      const target = board.getCharacter(move.toPos)
      if (target && target.type === CharacterType.FLAG) {
        return move
      }
    }

    // 그 외에는 랜덤
    if (allMoves.length > 0) {
      return this.randomChoice(allMoves.map((item) => item.move))
    }

    return null
  }

  randomChoice(array) {
    return array[Math.floor(Math.random() * array.length)]
  }
}
