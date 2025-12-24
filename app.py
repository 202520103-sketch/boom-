import streamlit as st
import random
import base64

st.set_page_config(page_title="💣 Minesweeper", layout="centered")

# --------------------
# 난이도 프리셋
# --------------------
DIFFICULTY = {
    "Easy 😊": (8, 8, 10),
    "Normal 😐": (10, 10, 20),
    "Hard 😈": (12, 12, 30),
    "Hell ☠️": (15, 15, 50)
}

st.sidebar.title("🎮 게임 설정")
mode = st.sidebar.radio("난이도 선택", DIFFICULTY.keys())
ROWS, COLS, MINES = DIFFICULTY[mode]

# --------------------
# 폭발 효과음 (짧은 펑 소리, wav)
# --------------------
EXPLOSION_SOUND = """
UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQgAAAAA////
////////////////////////////////////////////
"""

def play_explosion():
    audio_bytes = base64.b64decode(EXPLOSION_SOUND)
    st.audio(audio_bytes, format="audio/wav")

# --------------------
# 게임 초기화
# --------------------
def init_game():
    board = [[0]*COLS for _ in range(ROWS)]
    opened = [[False]*COLS for _ in range(ROWS)]

    positions = [(r, c) for r in range(ROWS) for c in range(COLS)]
    mines = random.sample(positions, MINES)

    for r, c in mines:
        board[r][c] = -1

    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == -1:
                continue
            board[r][c] = sum(
                1 for dr in [-1, 0, 1] for dc in [-1, 0, 1]
                if 0 <= r+dr < ROWS and 0 <= c+dc < COLS
                and board[r+dr][c+dc] == -1
            )

    st.session_state.board = board
    st.session_state.opened = opened
    st.session_state.game_over = False
    st.session_state.win = False
    st.session_state.mode = mode

# 난이도 변경 시 리셋
if "mode" not in st.session_state or st.session_state.mode != mode:
    init_game()

# --------------------
# 스타일
# --------------------
st.markdown("""
<style>
button {
    width: 42px !important;
    height: 42px !important;
    border-radius: 8px !important;
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("💣 Minesweeper")
st.caption(f"난이도: {mode} | 지뢰 {MINES}개")

# --------------------
# 보드 출력
# --------------------
opened_count = 0
for r in range(ROWS):
    cols = st.columns(COLS)
    for c in range(COLS):
        with cols[c]:
            val = st.session_state.board[r][c]
            opened = st.session_state.opened[r][c]

            if opened:
                opened_count += 1
                if val == -1:
                    st.markdown("💥")
                elif val == 0:
                    st.markdown("⬜")
                else:
                    colors = ["blue", "green", "red", "purple", "brown", "black"]
                    st.markdown(
                        f"<b style='color:{colors[val-1]}'>{val}</b>",
                        unsafe_allow_html=True
                    )
            else:
                if st.button(" ", key=f"{r}-{c}", disabled=st.session_state.game_over):
                    st.session_state.opened[r][c] = True
                    if val == -1:
                        st.session_state.game_over = True
                        play_explosion()
                        for i in range(ROWS):
                            for j in range(COLS):
                                st.session_state.opened[i][j] = True

# --------------------
# 승리 조건
# --------------------
if not st.session_state.game_over:
    if opened_count == ROWS * COLS - MINES:
        st.session_state.win = True
        st.session_state.game_over = True

# --------------------
# 결과 화면
# --------------------
if st.session_state.game_over:
    if st.session_state.win:
        st.markdown(
            "<h2 style='color:green; text-align:center;'>🎉 YOU SURVIVED 🎉</h2>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<h2 style='color:red; text-align:center;'>☠️ YOU DEAD ☠️</h2>",
            unsafe_allow_html=True
        )

    if st.button("🔄 다시 시작"):
        init_game()
