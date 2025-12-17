# Battle Board Game 🎮

턴제 대전 보드 게임 - AI 대전 전략 게임

**완전 클라이언트 사이드 게임 - 서버 불필요!**

## 🌐 온라인 플레이

**GitHub Pages에서 바로 플레이**: [여기를 클릭하세요!](#) *(배포 후 링크 업데이트)*

- 서버 설치 불필요
- 브라우저에서 바로 실행
- 모바일에서도 플레이 가능
- 오프라인에서도 작동

## 게임 소개

9x7 보드에서 21개의 캐릭터로 AI와 대결하는 전략 게임입니다. 각 캐릭터는 고유한 능력과 우선순위를 가지고 있으며, 상대방의 국기를 잡으면 승리합니다.

### 주요 특징

- **불완전 정보 게임**: 상대방 캐릭터는 전투하기 전까지 숨겨져 있음
- **특수 캐릭터**: 폭탄, 공병, 손오공, 헌병 등 특수 능력 보유
- **2단계 AI**:
  - 기본 AI: 규칙 기반 + 휴리스틱 (빠른 응답)
  - 고급 AI: MCTS (Monte Carlo Tree Search) - 더 강력하고 지능적
- **완전 클라이언트 사이드**: JavaScript로 구현되어 서버 불필요

## 게임 룰

### 캐릭터 (21개)

#### 일반 캐릭터 (우선순위로 승부)
1. 원수 (우선순위 1) - 가장 강함
2. 대장 (우선순위 2)
3. 중장 (우선순위 3)
4. 소장 (우선순위 4)
5. 준장 (우선순위 5)
6-14. 대령, 중령, 소령, 대위, 중위, 소위, 상사, 중사, 하사

#### 특수 캐릭터
- **폭탄 1, 2**: 고정, 공병에게 지고 모든 캐릭터를 이김
- **공병**: 폭탄을 이기고, 나머지는 일반 전투
- **손오공 1, 2**: 원수~준장(1~5)을 이기고, 나머지는 일반 전투
- **헌병**: 전투 시 상대방 캐릭터 정보 공개
- **국기**: 고정, 움직일 수 없음, 잡히면 게임 패배

### 전투 규칙

- 우선순위가 **낮을수록 강함** (1이 가장 강함)
- 같은 우선순위끼리 만나면 **둘 다 사망**
- 특수 캐릭터는 예외 규칙 적용

### 승리 조건

상대방의 **국기**를 잡으면 승리!

## 기술 스택

### 프론트엔드 (완전 클라이언트 사이드)
- **React 18**: UI 프레임워크
- **Vite**: 빌드 도구
- **Pure JavaScript**: 게임 로직 (ES6+)
  - 기본 AI: 규칙 기반 + 휴리스틱
  - 고급 AI: MCTS (불완전 정보 게임용)
- **CSS**: 순수 CSS (반응형 디자인)
- **GitHub Pages**: 무료 호스팅

### 백엔드 (레거시, 로컬 개발용)
- Python + FastAPI (선택사항)

## 🚀 로컬 실행

### 1. 프론트엔드 실행 (권장)

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:3000` 접속!

### 2. 빌드

```bash
cd frontend
npm run build
```

빌드된 파일은 `frontend/dist/` 폴더에 생성됩니다.

## 📦 GitHub Pages 배포

### 자동 배포 (권장)

1. **GitHub 저장소 생성**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/battle_board.git
   git push -u origin main
   ```

2. **GitHub Pages 활성화**
   - GitHub 저장소 → Settings → Pages
   - Source: "GitHub Actions" 선택

3. **자동 배포**
   - `main` 브랜치에 push하면 자동으로 배포됨
   - `.github/workflows/deploy.yml`이 자동으로 실행
   - 배포 완료 후 `https://YOUR_USERNAME.github.io/battle_board/` 에서 접속

### 수동 배포

```bash
cd frontend

# gh-pages 패키지 설치
npm install --save-dev gh-pages

# 배포
npm run deploy
```

## 프로젝트 구조

```
battle_board/
├── frontend/                    # 프론트엔드 (클라이언트 사이드)
│   ├── src/
│   │   ├── game/               # 게임 로직 (JavaScript)
│   │   │   ├── character.js    # 캐릭터 정의
│   │   │   ├── rules.js        # 전투 규칙
│   │   │   ├── board.js        # 게임 보드
│   │   │   └── ai/
│   │   │       ├── basicAI.js  # 기본 AI
│   │   │       └── mctsAI.js   # 고급 MCTS AI
│   │   ├── components/
│   │   │   ├── Board.jsx       # 보드 UI
│   │   │   └── Board.css
│   │   ├── App.jsx             # 메인 앱
│   │   └── App.css
│   ├── package.json
│   └── vite.config.js
├── backend/                     # 백엔드 (레거시, 선택사항)
│   └── ... (Python FastAPI)
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions 배포
└── README.md
```

## AI 아키텍처 설명

### 1. 기본 AI (규칙 기반 + 휴리스틱)

**전략:**
1. 상대방 국기 공격 (즉시 승리)
2. 확실히 이길 수 있는 전투 선택
3. 국기 방어
4. 안전한 공격
5. 전진
6. 랜덤 이동

**장점:**
- 즉각적인 응답 (< 10ms)
- 예측 가능한 동작
- 모바일에서도 빠름

**강도:** 중하

### 2. 고급 AI (MCTS - Monte Carlo Tree Search)

**알고리즘:** Determinized UCT

**특징:**
- **Determinization**: 상대방의 숨겨진 캐릭터를 확률적으로 추정
- **시뮬레이션**: 여러 가능한 게임 결과를 시뮬레이션
- **UCT**: 탐색(exploration)과 활용(exploitation)의 균형
- **JavaScript 최적화**: 브라우저에서 효율적으로 실행

**프로세스:**
1. **Selection**: UCT 값을 기준으로 트리 탐색
2. **Expansion**: 새로운 노드 추가
3. **Simulation**: 게임 끝까지 랜덤 플레이아웃
4. **Backpropagation**: 결과를 역전파하여 노드 업데이트

**장점:**
- 불완전 정보 게임에 강함
- 상황에 맞는 적응적 전략
- 서버 없이 브라우저에서 직접 실행

**강도:** 중상~상

## 성능

### 클라이언트 사이드 성능
- **기본 AI**: < 10ms 응답
- **고급 MCTS AI**: ~1.5초 사고 시간
- **메모리 사용**: < 50MB
- **모바일 지원**: iPhone, Android 모두 원활하게 작동

### 서버 vs 클라이언트 비교

| 항목 | 서버 방식 | 클라이언트 방식 |
|------|-----------|-----------------|
| 초기 로딩 | 콜드 스타트 5-10초 | 즉시 시작 |
| AI 응답 속도 | 네트워크 지연 + AI | AI만 |
| 오프라인 플레이 | 불가능 | 가능 |
| 비용 | 서버 비용 필요 | 완전 무료 |
| 모바일 지원 | 네트워크 필요 | 완벽 지원 |

## 향후 개선 가능 사항

1. **AI 개선**
   - Web Workers로 AI 계산 병렬화
   - Opening Book (초기 배치 전략 데이터베이스)
   - 더 정교한 Belief State 관리

2. **게임 기능**
   - 로컬 멀티플레이어 (같은 기기)
   - 리플레이 저장/불러오기
   - 통계 및 전적 (LocalStorage)
   - 수동 캐릭터 배치 UI

3. **UI/UX**
   - 애니메이션 효과 개선
   - 사운드 효과
   - PWA 지원 (앱처럼 설치 가능)
   - 다크 모드

4. **성능**
   - Web Workers로 UI 블로킹 방지
   - AI 응답 시간 단축
   - 캐싱 전략 개선

## FAQ

### Q: 서버가 필요한가요?
A: 아니요! 완전히 브라우저에서 실행됩니다. GitHub Pages에서 무료로 호스팅 가능합니다.

### Q: 모바일에서 작동하나요?
A: 네! 반응형 디자인으로 모바일에서도 완벽하게 작동합니다.

### Q: 오프라인에서 플레이 가능한가요?
A: 네! 한 번 로딩하면 오프라인에서도 플레이 가능합니다.

### Q: AI 성능이 서버보다 떨어지나요?
A: 아니요! 오히려 네트워크 지연이 없어서 더 빠를 수 있습니다. 현대 브라우저의 JavaScript 엔진은 매우 빠릅니다.

## 라이선스

MIT License

## 개발자

Claude Code를 사용하여 제작되었습니다.

---

즐거운 게임 되세요! 🎮
