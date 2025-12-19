# 단어 카드 선정 알고리즘

> 새 카드를 학습할 때 어떤 순서로 제시할지 결정하는 알고리즘 가이드

---

## 📌 핵심 문제

**FSRS는 복습 간격만 최적화**하고, **새 카드 도입 순서는 결정하지 않음**.

| FSRS가 하는 것 ✅ | FSRS가 안 하는 것 ❌ |
|------------------|---------------------|
| 복습 간격 조절 (언제 다시 볼지) | 새 카드 순서 결정 (어떤 카드를 먼저 볼지) |
| 개인별 카드 난이도 추적 | 단어 자체의 언어적 난이도 평가 |
| 망각 곡선 기반 최적화 | 새 단어 도입 전략 |

---

## 🎯 알고리즘 옵션 비교

### 1. 빈도 기반 정렬 (Frequency-based) ⭐ **추천**

**원리:** 실제 언어 사용에서 자주 등장하는 단어부터 학습

**장점:**
- ✅ 실용성 최고 (상위 1000단어 = 일상 언어의 ~80%)
- ✅ 연구로 검증됨 (Nation, 2006)
- ✅ 구현 간단
- ✅ 초보자에게 효과적

**단점:**
- ❌ 개인의 목표/흥미 반영 안 됨
- ❌ 특수 목적 학습에는 부적합 (예: 의학, 법률)

**데이터 소스:**
- **COCA (Corpus of Contemporary American English)**: 60,000단어 빈도 리스트
- **Oxford 3000/5000**: 학습용으로 선별된 단어 + CEFR 매핑
- **Google Books Ngram**: 웹 기반 빈도
- **Wiktionary Frequency Lists**: 오픈 소스

**구현:**
```python
# frequency_rank가 낮을수록 자주 쓰이는 단어
ORDER BY frequency_rank ASC
LIMIT 10
```

**예시:**
```
Rank 1: the
Rank 2: be
Rank 3: to
Rank 4: of
Rank 5: and
...
```

---

### 2. 난이도 기반 정렬 (Difficulty-based)

**원리:** 쉬운 단어 → 어려운 단어 순으로 점진적 학습

**난이도 평가 기준:**
- 단어 길이 (짧을수록 쉬움)
- 음절 수
- 의미의 추상성 (concrete vs abstract)
- 형태소 복잡도 (morphological complexity)

**장점:**
- ✅ 학습자 부담 감소
- ✅ 초기 성공 경험 → 동기 부여
- ✅ 점진적 난이도 상승

**단점:**
- ❌ 난이도 평가 주관적
- ❌ 쉬운 단어 ≠ 유용한 단어
- ❌ 학습 속도 느릴 수 있음

**구현:**
```python
ORDER BY difficulty_level ASC, word_length ASC
```

---

### 3. i+1 / Zone of Proximal Development (ZPD) 🔬 **연구 기반**

**원리:** 현재 레벨보다 "살짝" 어려운 것만 학습

**제안자:**
- **Stephen Krashen** (i+1 가설, 1982): i = 현재 수준, +1 = 약간 더 어려운 수준
- **Lev Vygotsky** (ZPD): 혼자는 못하지만 도움 받으면 할 수 있는 영역

**장점:**
- ✅ 이론적 근거 탄탄
- ✅ 적절한 도전 = 최적 학습
- ✅ 개인화된 학습 경로
- ✅ 좌절감 방지

**단점:**
- ❌ 사용자 레벨 정확히 측정 필요
- ❌ 구현 복잡
- ❌ 초기 데이터 부족 시 부정확

**레벨 계산 방법:**
```python
def calculate_user_level(user_id: int, n_recent: int = 50) -> float:
    """최근 N개 리뷰의 정답률로 사용자 레벨 추정"""

    recent_reviews = get_recent_reviews(user_id, limit=n_recent)

    if not recent_reviews:
        return 1.0  # 초보자 기본값

    accuracy = sum(r.is_correct for r in recent_reviews) / len(recent_reviews)
    avg_difficulty = sum(r.card.difficulty_level for r in recent_reviews) / len(recent_reviews)

    # 정답률 기반 조정
    if accuracy > 0.9:
        return avg_difficulty + 0.5  # 레벨 올리기
    elif accuracy < 0.7:
        return max(1.0, avg_difficulty - 0.5)  # 레벨 낮추기
    else:
        return avg_difficulty  # 현재 레벨 유지
```

**필터링:**
```python
user_level = calculate_user_level(user_id)

query = query.where(
    VocabularyCard.difficulty_level >= user_level - 0.5,
    VocabularyCard.difficulty_level <= user_level + 1.5
)
```

---

### 4. Semantic Clustering (의미 군집화)

**원리:** 관련 단어를 함께 학습 → 연상 기억 강화

**이론적 근거:**
- **Semantic Network Theory**: 단어는 네트워크로 연결됨
- **Dual Coding Theory** (Paivio): 언어적 + 시각적 연상

**장점:**
- ✅ 장기 기억 강화
- ✅ 맥락 이해 향상
- ✅ 연상 학습 효과

**단점:**
- ❌ 너무 비슷한 단어는 혼란 초래
- ❌ 간섭 효과 (interference)
- ❌ 카테고리 설정 필요

**구현:**
```python
# 카테고리별 그룹핑
# "음식": apple, banana, bread, butter, ...
# "여행": airport, hotel, ticket, passport, ...

ORDER BY category, frequency_rank
```

**주의사항:**
```python
# BAD: 동의어를 연속으로 학습 (혼란)
# big, large, huge, enormous, gigantic

# GOOD: 카테고리는 같지만 성질이 다른 단어들
# big, small, medium, tiny, huge
```

---

### 5. Interleaving (섞기) 🔄

**원리:** 비슷한 것만 연속 학습 X, 다양한 것 섞어서 학습

**연구 근거:**
- **Rohrer & Taylor (2007)**: Interleaving이 blocked practice보다 효과적
- **Kornell & Bjork (2008)**: 다양한 맥락 → 더 robust한 학습

**Blocked vs Interleaved:**
```
Blocked (나쁨):
A A A A B B B B C C C C

Interleaved (좋음):
A B C A B C A B C A B C
```

**장점:**
- ✅ 장기 기억 효과
- ✅ 변별력 향상 (discrimination)
- ✅ 전이 학습 (transfer)

**단점:**
- ❌ 단기적으로 어렵게 느껴짐
- ❌ 학습자가 혼란스러워할 수 있음

**구현:**
```python
def interleave_by_category(cards: list) -> list:
    """카테고리별로 섞기"""
    from itertools import cycle
    from collections import defaultdict

    by_category = defaultdict(list)
    for card in cards:
        by_category[card.category].append(card)

    # Round-robin으로 섞기
    result = []
    iterators = [iter(cards) for cards in by_category.values()]

    while iterators:
        for it in iterators[:]:
            try:
                result.append(next(it))
            except StopIteration:
                iterators.remove(it)

    return result
```

---

### 6. Prerequisite Graph (선수 학습 그래프)

**원리:** A를 알아야 B를 이해할 수 있는 의존 관계 반영

**예시:**
```
Level 1: eat (먹다)
  ↓
Level 2: ate (먹었다) - 과거형
  ↓
Level 3: have eaten (먹어버렸다) - 현재완료
```

**장점:**
- ✅ 논리적 학습 순서
- ✅ 문법적 체계성
- ✅ 혼란 방지

**단점:**
- ❌ 그래프 구축 비용 큼
- ❌ 모든 단어에 적용 불가
- ❌ 유연성 낮음

**구현:**
```sql
-- prerequisite_ids 필드 추가
ALTER TABLE vocabulary_cards ADD COLUMN prerequisite_ids JSONB;

-- 예: "eating" 카드는 "eat"를 먼저 알아야 함
UPDATE vocabulary_cards
SET prerequisite_ids = '[123]'  -- "eat"의 card_id
WHERE english_word = 'eating';
```

```python
def topological_sort_cards(cards: list) -> list:
    """선수 조건에 따라 정렬"""
    from collections import defaultdict, deque

    graph = defaultdict(list)
    in_degree = defaultdict(int)

    for card in cards:
        for prereq_id in (card.prerequisite_ids or []):
            graph[prereq_id].append(card.id)
            in_degree[card.id] += 1

    # Kahn's algorithm
    queue = deque([c for c in cards if in_degree[c.id] == 0])
    result = []

    while queue:
        card = queue.popleft()
        result.append(card)

        for next_id in graph[card.id]:
            in_degree[next_id] -= 1
            if in_degree[next_id] == 0:
                next_card = next(c for c in cards if c.id == next_id)
                queue.append(next_card)

    return result
```

---

### 7. 랜덤 (Random) 🎲

**원리:** 무작위 순서로 제시

**장점:**
- ✅ 구현 초간단
- ✅ 편향 없음
- ✅ 다양성 보장

**단점:**
- ❌ 비효율적
- ❌ 동기 부여 부족
- ❌ 연구 근거 없음

**사용 케이스:**
- 테스트/실험용
- 복습 시 (새 단어 X)

**구현:**
```python
ORDER BY RANDOM()
```

---

## 🏆 추천 전략: 하이브리드 접근법

### MVP 구현 (단계 1) ⭐

**전략:** 빈도 기반 + 선택된 덱 필터

```python
async def get_new_cards_mvp(
    session: AsyncSession,
    user_id: int,
    selected_deck_ids: list[int] | None,
    limit: int = 10
) -> list[VocabularyCard]:
    """MVP: 빈도 기반 간단 구현"""

    # 이미 본 카드 제외
    seen_subquery = select(UserCardProgress.card_id).where(
        UserCardProgress.user_id == user_id
    )

    query = select(VocabularyCard).where(
        VocabularyCard.id.not_in(seen_subquery)
    )

    # 선택된 덱 필터
    if selected_deck_ids:
        query = query.where(VocabularyCard.deck_id.in_(selected_deck_ids))

    # 빈도순 정렬
    query = query.order_by(VocabularyCard.frequency_rank.asc())

    result = await session.exec(query.limit(limit))
    return list(result.all())
```

**장점:**
- 간단하고 빠름
- 80% 케이스 커버
- 즉시 배포 가능

---

### V2 구현 (단계 2) 🚀

**전략:** 빈도 기반 + i+1 필터링 + Interleaving

```python
async def get_new_cards_v2(
    session: AsyncSession,
    user_id: int,
    selected_deck_ids: list[int] | None,
    limit: int = 10
) -> list[VocabularyCard]:
    """V2: i+1 필터링 추가"""

    # 1. 사용자 레벨 계산
    user_level = await calculate_user_level(session, user_id)

    # 2. 이미 본 카드 제외
    seen_subquery = select(UserCardProgress.card_id).where(
        UserCardProgress.user_id == user_id
    )

    query = select(VocabularyCard).where(
        VocabularyCard.id.not_in(seen_subquery)
    )

    # 3. 선택된 덱 필터
    if selected_deck_ids:
        query = query.where(VocabularyCard.deck_id.in_(selected_deck_ids))

    # 4. i+1 필터링 (레벨 ± 1 범위)
    query = query.where(
        VocabularyCard.difficulty_level >= user_level - 0.5,
        VocabularyCard.difficulty_level <= user_level + 1.5
    )

    # 5. 빈도순 정렬
    query = query.order_by(VocabularyCard.frequency_rank.asc())

    # 6. 후보 가져오기 (limit의 2배)
    result = await session.exec(query.limit(limit * 2))
    candidates = list(result.all())

    # 7. Interleaving (카테고리 섞기)
    interleaved = interleave_by_category(candidates)

    return interleaved[:limit]


def interleave_by_category(cards: list) -> list:
    """카테고리가 연속되지 않도록 섞기"""
    from collections import defaultdict

    by_category = defaultdict(list)
    for card in cards:
        category = card.category or "uncategorized"
        by_category[category].append(card)

    result = []
    categories = list(by_category.keys())
    indices = {cat: 0 for cat in categories}

    while len(result) < len(cards):
        for cat in categories:
            if indices[cat] < len(by_category[cat]):
                result.append(by_category[cat][indices[cat]])
                indices[cat] += 1

    return result
```

**장점:**
- 개인화된 학습
- 적절한 난이도 유지
- 카테고리 간섭 방지

---

### V3 구현 (장기) 🎯

**전략:** V2 + 머신러닝 기반 예측

```python
async def get_new_cards_v3(
    session: AsyncSession,
    user_id: int,
    selected_deck_ids: list[int] | None,
    limit: int = 10
) -> list[VocabularyCard]:
    """V3: ML 기반 최적화"""

    # 1. 사용자 프로필 분석
    user_profile = await analyze_user_profile(session, user_id)
    # - 학습 속도
    # - 선호 카테고리
    # - 약점 영역

    # 2. 후보 선정 (V2 로직)
    candidates = await get_new_cards_v2(session, user_id, selected_deck_ids, limit * 3)

    # 3. ML 모델로 각 카드 점수 계산
    scored = []
    for card in candidates:
        score = ml_model.predict_success_rate(user_profile, card)
        scored.append((card, score))

    # 4. 최적 점수 범위 (너무 쉽지도 어렵지도 않게)
    sorted_cards = sorted(scored, key=lambda x: x[1], reverse=True)
    optimal = [card for card, score in sorted_cards if 0.6 <= score <= 0.8]

    return optimal[:limit]
```

---

## 📊 실제 앱들의 전략

| 앱 | 새 카드 순서 전략 | 특징 |
|---|------------------|------|
| **Duolingo** | Skill Tree (Prerequisite) + 빈도 | 게이미피케이션 강함 |
| **Anki** | 덱 순서 그대로 (사용자 재량) | 유연성 최고 |
| **Memrise** | 빈도 기반 + 레벨별 | 초보자 친화적 |
| **Drops** | 테마별 → 테마 내 랜덤 | 시각적 학습 중심 |
| **Lingvist** | AI 기반 adaptive | 정답률 실시간 분석 |
| **Busuu** | CEFR 레벨 + 주제별 | 공식 인증 중심 |

---

## 🎓 연구 기반 권장사항

### Nation (2006) - "How Large a Vocabulary is Needed?"

> "The 2,000 most frequent word families of English provide around 80% coverage of informal spoken English, about 80% coverage of formal spoken English, and about 79% coverage of written texts."

**결론:** 초기에는 고빈도 단어 집중

### Krashen (1982) - "Principles and Practice in Second Language Acquisition"

> "Comprehensible input (i+1) is the crucial and necessary ingredient for language acquisition."

**결론:** 현재 수준 + 1 단계 유지

### Rohrer & Taylor (2007) - "The Shuffling of Mathematics Problems"

> "Interleaved practice led to better performance than blocked practice."

**결론:** 섞어서 학습하는 것이 효과적

### Kornell & Bjork (2008) - "Learning Concepts and Categories"

> "Interleaving different categories produced much better learning than studying examples from each category in blocks."

**결론:** 카테고리 간 섞기 중요

---

## 🛠️ 구현 체크리스트

### MVP (Sprint 1)
- [ ] VocabularyCard에 `frequency_rank` 필드 추가
- [ ] 영어 빈도 데이터 수집 및 매핑
- [ ] 빈도 기반 정렬 구현
- [ ] 선택된 덱 필터링 구현
- [ ] `GET /study/session/start` API 구현

### V2 (Sprint 2-3)
- [ ] 사용자 레벨 계산 로직 구현
- [ ] i+1 필터링 추가
- [ ] VocabularyCard에 `category` 필드 추가
- [ ] Interleaving 로직 구현
- [ ] A/B 테스트 설정

### V3 (장기)
- [ ] 사용자 학습 패턴 데이터 수집
- [ ] ML 모델 학습 인프라 구축
- [ ] 예측 모델 구현
- [ ] 실시간 적응형 알고리즘
- [ ] 성능 모니터링 대시보드

---

## 🧪 A/B 테스트 제안

### 가설 1: 빈도 vs 난이도
- **A그룹**: 빈도 기반만
- **B그룹**: 난이도 기반만
- **측정**: 30일 후 retention, 정답률

### 가설 2: i+1 필터 효과
- **A그룹**: 빈도만
- **B그룹**: 빈도 + i+1 필터
- **측정**: 학습 속도, 만족도

### 가설 3: Interleaving 효과
- **A그룹**: Blocked (카테고리별 묶음)
- **B그룹**: Interleaved (섞기)
- **측정**: 장기 기억 (7일 후 복습 정답률)

---

## 📚 참고 문헌

1. Nation, I.S.P. (2006). *How Large a Vocabulary is Needed for Reading and Listening?* The Canadian Modern Language Review.

2. Krashen, S. (1982). *Principles and Practice in Second Language Acquisition*. Pergamon Press.

3. Rohrer, D., & Taylor, K. (2007). The shuffling of mathematics problems improves learning. *Instructional Science*, 35(6), 481-498.

4. Kornell, N., & Bjork, R. A. (2008). Learning concepts and categories: Is spacing the "enemy of induction"? *Psychological Science*, 19(6), 585-592.

5. Paivio, A. (1986). *Mental Representations: A Dual Coding Approach*. Oxford University Press.

---

## 🔗 데이터 소스

- **COCA Frequency List**: https://www.wordfrequency.info/samples.asp
- **Oxford 3000/5000**: https://www.oxfordlearnersdictionaries.com/wordlists/oxford3000-5000
- **Google Books Ngram**: https://books.google.com/ngrams
- **Wiktionary Frequency Lists**: https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists
