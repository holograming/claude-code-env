# Notion 데이터베이스 스키마

## 메인 속성 (5개 - 리스트뷰 표시)

### 1. 문제명 (Title)
- **타입**: Title (프로퍼티 이름 필수)
- **설명**: 코딩테스트 문제 이름
- **예시**: "올바른 괄호", "짝지어 제거하기"

### 2. 플랫폼 (Select)
- **타입**: Select
- **옵션**:
  - 프로그래머스
  - 백준
  - LeetCode
  - 기타

### 3. 난이도 (Select)
- **타입**: Select
- **옵션**:
  - Lv.1
  - Lv.2
  - Lv.3
  - Lv.4
  - Lv.5

### 4. 풀이 날짜 (Date)
- **타입**: Date
- **설명**: 문제 풀이 완료 날짜
- **자동 설정**: 페이지 생성 시 현재 날짜

### 5. 상태 (Status)
- **타입**: Status
- **옵션**:
  - 완료 ✅
  - 재시도 🔄
  - 진행중 🚀

## 추가 속성

### 문제 번호 (Number)
- **타입**: Number
- **설명**: 프로그래머스 등의 문제 ID
- **예시**: 12909, 12973

### 알고리즘 (Multi-Select)
- **타입**: Multi-Select
- **옵션**:
  - 스택/큐
  - DFS/BFS
  - DP
  - 그리디
  - 해시
  - 정렬
  - 완전탐색
  - 이분탐색
  - 그래프
  - 힙
  - (추가 가능)

### 문제 링크 (URL)
- **타입**: URL
- **설명**: 프로그래머스 문제 페이지 링크
- **예시**: https://school.programmers.co.kr/learn/courses/30/lessons/12909

### 언어 (Select)
- **타입**: Select
- **옵션**:
  - Python
  - Java
  - C++
  - JavaScript
  - Kotlin
  - Swift
  - Go
  - Rust

## 생성 권장 순서

1. 문제명 (Title) - **필수**
2. 플랫폼 (Select)
3. 난이도 (Select)
4. 풀이 날짜 (Date)
5. 상태 (Status)
6. 문제 번호 (Number)
7. 알고리즘 (Multi-Select)
8. 문제 링크 (URL)
9. 언어 (Select)

## 페이지 본문 구조

자동 생성되는 내용:

```
## 📝 문제 설명
README에서 추출된 문제 설명

---

## 📋 제한 사항
입력/출력 제약 조건

---

## 💻 풀이 코드
GitHub 링크 (Bookmark 블록)

---

## 📒 풀이 메모
사용자가 추가하는 접근 방법, 회고, 주의사항 (Callout)
```
