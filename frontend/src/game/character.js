/**
 * 캐릭터 정의 모듈
 * 각 캐릭터의 타입, 우선순위, 특수 능력을 정의합니다.
 */

export const CharacterType = {
  // 일반 캐릭터 (우선순위 1-14)
  GENERAL_5: { name: '원수', priority: 1, isSpecial: false },
  GENERAL_4: { name: '대장', priority: 2, isSpecial: false },
  GENERAL_3: { name: '중장', priority: 3, isSpecial: false },
  GENERAL_2: { name: '소장', priority: 4, isSpecial: false },
  GENERAL_1: { name: '준장', priority: 5, isSpecial: false },
  COLONEL: { name: '대령', priority: 6, isSpecial: false },
  LT_COLONEL: { name: '중령', priority: 7, isSpecial: false },
  MAJOR: { name: '소령', priority: 8, isSpecial: false },
  CAPTAIN: { name: '대위', priority: 9, isSpecial: false },
  FIRST_LT: { name: '중위', priority: 10, isSpecial: false },
  SECOND_LT: { name: '소위', priority: 11, isSpecial: false },
  MASTER_SGT: { name: '상사', priority: 12, isSpecial: false },
  SGT: { name: '중사', priority: 13, isSpecial: false },
  CORPORAL: { name: '하사', priority: 14, isSpecial: false },

  // 특수 캐릭터
  BOMB_1: { name: '폭탄1', priority: 0, isSpecial: true },
  BOMB_2: { name: '폭탄2', priority: 0, isSpecial: true },
  ENGINEER: { name: '공병', priority: 16, isSpecial: true },
  WUKONG_1: { name: '손오공1', priority: 17, isSpecial: true },
  WUKONG_2: { name: '손오공2', priority: 17, isSpecial: true },
  FLAG: { name: '국기', priority: 19, isSpecial: true },
  MP: { name: '헌병', priority: 18, isSpecial: true },
}

export class Character {
  constructor(type, playerId) {
    this.type = type
    this.typeName = Object.keys(CharacterType).find(
      (key) => CharacterType[key] === type
    )
    this.playerId = playerId
    this.isAlive = true
    this.isRevealed = false
  }

  get name() {
    return this.type.name
  }

  get priority() {
    return this.type.priority
  }

  get isSpecial() {
    return this.type.isSpecial
  }

  get canMove() {
    // 국기와 폭탄은 움직일 수 없음
    return (
      this.type !== CharacterType.FLAG &&
      this.type !== CharacterType.BOMB_1 &&
      this.type !== CharacterType.BOMB_2
    )
  }

  reveal() {
    this.isRevealed = true
  }
}

export function createFullTeam(playerId) {
  return [
    // 일반 캐릭터 (1-14)
    new Character(CharacterType.GENERAL_5, playerId),
    new Character(CharacterType.GENERAL_4, playerId),
    new Character(CharacterType.GENERAL_3, playerId),
    new Character(CharacterType.GENERAL_2, playerId),
    new Character(CharacterType.GENERAL_1, playerId),
    new Character(CharacterType.COLONEL, playerId),
    new Character(CharacterType.LT_COLONEL, playerId),
    new Character(CharacterType.MAJOR, playerId),
    new Character(CharacterType.CAPTAIN, playerId),
    new Character(CharacterType.FIRST_LT, playerId),
    new Character(CharacterType.SECOND_LT, playerId),
    new Character(CharacterType.MASTER_SGT, playerId),
    new Character(CharacterType.SGT, playerId),
    new Character(CharacterType.CORPORAL, playerId),

    // 특수 캐릭터
    new Character(CharacterType.BOMB_1, playerId),
    new Character(CharacterType.BOMB_2, playerId),
    new Character(CharacterType.ENGINEER, playerId),
    new Character(CharacterType.WUKONG_1, playerId),
    new Character(CharacterType.WUKONG_2, playerId),
    new Character(CharacterType.FLAG, playerId),
    new Character(CharacterType.MP, playerId),
  ]
}
