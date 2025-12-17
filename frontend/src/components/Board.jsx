import './Board.css'

function Board({ board, selectedCell, validMoves, onCellClick, loading }) {
  const isValidMove = (row, col) => {
    return validMoves.some((m) => m.to_row === row && m.to_col === col)
  }

  const isSelected = (row, col) => {
    return selectedCell && selectedCell.row === row && selectedCell.col === col
  }

  const getCellClass = (row, col, cell) => {
    let className = 'cell'

    if (isSelected(row, col)) {
      className += ' selected'
    } else if (isValidMove(row, col)) {
      className += ' valid-move'
    }

    if (cell) {
      if (cell.player_id === 0) {
        className += ' ai-cell'
      } else if (cell.player_id === 1) {
        className += ' player-cell'
      }
    }

    return className
  }

  const getCharacterDisplay = (cell) => {
    if (!cell) return ''

    if (cell.type === 'HIDDEN') {
      return '???'
    }

    return cell.name
  }

  const getCharacterEmoji = (cell) => {
    if (!cell || cell.type === 'HIDDEN') return '❓'

    const emojiMap = {
      FLAG: '🚩',
      BOMB_1: '💣',
      BOMB_2: '💣',
      ENGINEER: '🔧',
      WUKONG_1: '🐒',
      WUKONG_2: '🐒',
      MP: '👮',
      GENERAL_5: '⭐⭐⭐⭐⭐',
      GENERAL_4: '⭐⭐⭐⭐',
      GENERAL_3: '⭐⭐⭐',
      GENERAL_2: '⭐⭐',
      GENERAL_1: '⭐',
      COLONEL: '🎖️',
      LT_COLONEL: '🎖️',
      MAJOR: '🎖️',
      CAPTAIN: '🎖️',
      FIRST_LT: '🎖️',
      SECOND_LT: '🎖️',
      MASTER_SGT: '🪖',
      SGT: '🪖',
      CORPORAL: '🪖',
    }

    return emojiMap[cell.type] || '👤'
  }

  return (
    <div className={`board-container ${loading ? 'loading' : ''}`}>
      <div className="board">
        {board.map((row, rowIdx) => (
          <div key={rowIdx} className="board-row">
            {row.map((cell, colIdx) => (
              <div
                key={`${rowIdx}-${colIdx}`}
                className={getCellClass(rowIdx, colIdx, cell)}
                onClick={() => !loading && onCellClick(rowIdx, colIdx)}
              >
                {cell && (
                  <div className="character">
                    <div className="character-emoji">
                      {getCharacterEmoji(cell)}
                    </div>
                    <div className="character-name">
                      {getCharacterDisplay(cell)}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>
      {loading && <div className="loading-overlay">처리 중...</div>}
    </div>
  )
}

export default Board
