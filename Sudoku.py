# --- Program to solve a Sudoku puzzle 9x9 ---
"""
Board source -> external file "sudoku.txt"
1 row = 1 row in Sudoku without commas and other characters
with error managment
"""

# --- Create a board ---
def print_board(board):
    for i in range(9):
        for j in range(9):
            print(board[i][j], end=" ")
            if (j + 1) % 3 == 0 and j != 8:
                print("|", end=" ")
        print()
        if (i + 1) % 3 == 0 and i != 8:
            print("- - - + - - - + - - -")

# --- Find empty cell ---
def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

# --- Checks if 'num' can be inserted into 'pos' position ---
def is_valid(board, num, pos): 
    row, col = pos

    if num in board[row]: # Checks if 'num' is already in 'row'
        return False

    for i in range(9): # Checks if 'num' is already in 'col'
        if board[i][col] == num:
            return False

    box_x = col // 3 # Which box of Sudoku 0 / 1 / 2
    box_y = row // 3

    for i in range(box_y * 3, box_y * 3 + 3): # Checks all the boxes if 'num' exist 
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num:
                return False

    return True


def solve(board): # Solve the Sudoku puzzle by backtracking
    find = find_empty(board)
    if not find:
        return True
    else:
        row, col = find

    for num in range(1, 10):
        if is_valid(board, num, (row, col)):
            board[row][col] = num

            if solve(board):
                return True

            board[row][col] = 0

    return False


def read_board_from_file(filename):
    board = []
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            if len(lines) != 9:
                raise ValueError("Plik powinien zawierać dokładnie 9 wierszy.")
            for i, line in enumerate(lines):
                line = line.strip()
                if len(line) != 9 or not line.isdigit():
                    raise ValueError(f"Błąd w wierszu {i + 1}: '{line}' nie jest prawidłowy.")
                board.append([int(ch) for ch in line])
    except Exception as e:
        print(f"Błąd podczas wczytywania planszy: {e}")
        exit(1)
    return board


# --- Main Program ---
filename = "sudoku.txt" # C:\\Users\\ if needed
board = read_board_from_file(filename)

print("\nSudoku przed rozwiązaniem:\n")
print_board(board)

if solve(board):
    print("\nSudoku po rozwiązaniu:\n")
    print_board(board)
else:
    print("\nNie udało się rozwiązać Sudoku. Sprawdź poprawność planszy.")
