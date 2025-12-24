import streamlit as st
import random
import time
import json
import os

# ------------------ 설정 ------------------
DIFFICULTY = {
    "Easy": (8, 10),
    "Normal": (12, 25),
    "Hard": (16, 50)
}

SCORE_FILE = "best_score.json"

# ------------------ 점수 저장 ------------------
def load_scores():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_scores(scores):
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f)

# ------------------ 게임 초기화 ------------------
def init_game(size, mines):
    st.session_state.size = size
    st.session_state.mines = mines
    st.session_state.start_time = time.time()
    st.session_state.game_over = False
    st.session_state.win = False

    st.session_state.board = [[0]*size for _ in range(size)]
    st.session_state.visible = [[False]*size for _ in range(size)]
    st.session_state.flagged = [[False]*size for _ in range(size)]

    positions = random.sample(range(size*size), mines)
    for p in positions:
        r, c = divmod(p, size)
        st.session_state.board[r][c] = -1

    for r in range(size):
        for c in range(size):
            if st.session_state.board[r][c] == -1:
                continue
            count = 0
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < size and 0 <= nc < size:
                        if st.session_state.board[nr][nc] == -1:
                            count += 1
            st.session_state.board[r][c] = count

# ------------------ 빈칸 확장 ------------------
def flood_fill(r, c):
    stack = [(r, c)]
    while stack:
        x, y = stack.pop()
        if st.session_state.visible[x][y]:
            continue
        st.session_state.visible[x][y] = True
        if st.session_state.board[x][y] == 0:
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    nx, ny = x+dr, y+dc
                    if 0 <= nx < st.session_state.size and 0 <= ny < st.session_state.size:
                        if not st.session_state.visible[nx][ny]:
                            stack.append((nx, ny))

# ------------------ 전체 공개 ------------------
def reveal_all():
    for r in range(st.session_state.size):
        for c in range(st.session_state.size):
            st.session_state.visible[r][c] = True

# ------------------ 클릭 처리 ------------------
def click_cell(r, c):
    if st.session_state.game_over or st.session_state.flagged[r][c]:
        return

    if st.session_state.board[r][c] == -1:
        st.session_state.game_over = True
        reveal_all()
        st.audio("https://www.soundjay.com/explosion/sounds/explosion-01.mp3")
    else:
        flood_fill(r, c)
        check_win()

def toggle_flag(r, c):
    if not st.session_state.visible[r][c]:
        st.session_state.flagged[r][c] = not st.session_state.flagged[r][c]

# ------------------ 승리 체크 ------------------
def check_win():
    for r in range(st.session_state.size):
        for c in range(st.session_state.size):
            if st.session_state.board[r][c] != -1 and not st.session_state.visible[r][c]:
                return
    st.session_state.win = True
    st.session_state.game_over = True

    elapsed = int(time.time() - st.session_state.start_time)
    scores = load_scores()
    key = st.session_state.difficulty
    if key not in scores or elapsed < scores[key]:
        scores[key] = elapsed
        save_scores(scores)

# ------------------ UI ------------------
st.set_page_config(layout="wide")
st.title("💣 Minesweeper")

difficulty = st.selectbox("난이도", list(DIFFICULTY.keys()))
size, mines = DIFFICULTY[difficulty]
st.session_state.difficulty = difficulty

if "board" not in st.session_state or st.button("🔄 새 게임"):
    init_game(size, mines)

scores = load_scores()
if difficulty in scores:
    st.info(f"🏆 최고기록: {scores[difficulty]}초")

# ------------------ 보드 출력 ------------------
for r in range(size):
    cols = st.columns(size)
    for c in range(size):
        with cols[c]:
            if st.session_state.visible[r][c]:
                v = st.session_state.board[r][c]
                if v == -1:
                    st.markdown("<div style='font-size:32px;'>💣</div>", unsafe_allow_html=True)
                elif v == 0:
                    st.markdown("<div style='font-size:28px;'>&nbsp;</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='font-size:32px; font-weight:bold;'>{v}</div>", unsafe_allow_html=True)
            else:
                if st.session_state.flagged[r][c]:
                    st.button("🚩", key=f"f{r}{c}", on_click=toggle_flag, args=(r,c))
                else:
                    st.button(" ", key=f"b{r}{c}", on_click=click_cell, args=(r,c))

# ------------------ 결과 ------------------
if st.session_state.game_over:
    if st.session_state.win:
        st.markdown("<h2 style='text-align:center;color:green;'>🎉 YOU SURVIVED 🎉</h2>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:red;'>☠️ YOU DEAD ☠️</h2>", unsafe_allow_html=True)

