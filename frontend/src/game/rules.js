/**
 * 전투 규칙 모듈
 * 캐릭터 간 전투 결과를 결정하는 로직을 구현합니다.
 */

import { CharacterType } from './character.js'

export class BattleResult {
  constructor(attackerSurvives, defenderSurvives, attackerRevealed = true, defenderRevealed = true) {
    this.attackerSurvives = attackerSurvives
    this.defenderSurvives = defenderSurvives
    this.attackerRevealed = attackerRevealed
    this.defenderRevealed = defenderRevealed
  }

  get bothDie() {
    return !this.attackerSurvives && !this.defenderSurvives
  }

  get attackerWins() {
    return this.attackerSurvives && !this.defenderSurvives
  }

  get defenderWins() {
    return !this.attackerSurvives && this.defenderSurvives
  }
}

export function resolveBattle(attacker, defender) {
  // 헌병 특수 처리: 전투 시 상대방만 공개
  if (attacker.type === CharacterType.MP) {
    defender.reveal()
    return resolveGeneralBattle(attacker, defender)
  }

  if (defender.type === CharacterType.MP) {
    attacker.reveal()
    return resolveGeneralBattle(attacker, defender)
  }

  // 특수 캐릭터 전투 처리
  const specialResult = resolveSpecialBattle(attacker, defender)
  if (specialResult !== null) {
    return specialResult
  }

  // 일반 전투 (우선순위 비교)
  return resolveGeneralBattle(attacker, defender)
}

function resolveSpecialBattle(attacker, defender) {
  // 국기는 모든 캐릭터에게 패배
  if (defender.type === CharacterType.FLAG) {
    return new BattleResult(true, false)
  }

  // 폭탄 vs 공병
  if (
    attacker.type === CharacterType.ENGINEER &&
    (defender.type === CharacterType.BOMB_1 || defender.type === CharacterType.BOMB_2)
  ) {
    return new BattleResult(true, false)
  }

  if (
    defender.type === CharacterType.ENGINEER &&
    (attacker.type === CharacterType.BOMB_1 || attacker.type === CharacterType.BOMB_2)
  ) {
    return new BattleResult(false, true)
  }

  // 폭탄 vs 일반 캐릭터 (폭탄이 이김)
  if (attacker.type === CharacterType.BOMB_1 || attacker.type === CharacterType.BOMB_2) {
    if (
      defender.type !== CharacterType.BOMB_1 &&
      defender.type !== CharacterType.BOMB_2 &&
      defender.type !== CharacterType.ENGINEER
    ) {
      return new BattleResult(true, false)
    }
  }

  if (defender.type === CharacterType.BOMB_1 || defender.type === CharacterType.BOMB_2) {
    if (
      attacker.type !== CharacterType.BOMB_1 &&
      attacker.type !== CharacterType.BOMB_2 &&
      attacker.type !== CharacterType.ENGINEER
    ) {
      return new BattleResult(false, true)
    }
  }

  // 손오공 vs 우선순위 1~5 (원수~준장)
  const topRanks = [
    CharacterType.GENERAL_5,
    CharacterType.GENERAL_4,
    CharacterType.GENERAL_3,
    CharacterType.GENERAL_2,
    CharacterType.GENERAL_1,
  ]

  if (attacker.type === CharacterType.WUKONG_1 || attacker.type === CharacterType.WUKONG_2) {
    if (topRanks.includes(defender.type)) {
      return new BattleResult(true, false)
    }
  }

  if (defender.type === CharacterType.WUKONG_1 || defender.type === CharacterType.WUKONG_2) {
    if (topRanks.includes(attacker.type)) {
      return new BattleResult(false, true)
    }
  }

  // 특수 전투가 아니면 null 반환
  return null
}

function resolveGeneralBattle(attacker, defender) {
  const attackerPriority = attacker.priority
  const defenderPriority = defender.priority

  if (attackerPriority < defenderPriority) {
    // 우선순위가 낮을수록 강함 (1이 가장 강함)
    return new BattleResult(true, false)
  } else if (attackerPriority > defenderPriority) {
    return new BattleResult(false, true)
  } else {
    // 같은 우선순위 -> 둘 다 사망
    return new BattleResult(false, false)
  }
}
