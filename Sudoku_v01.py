# ---/ Program to solve a Sudoku puzzle 9x9 \---
"""
Board source -> external file "sudoku.txt"
1 row -> 1 row in Sudoku without commas and other characters
'0' -> empty cell
with error managment
"""

# ---/ Create a board \---
def print_board(board):
    for i in range(9):
        for j in range(9):
            print(board[i][j], end=" ")
            if (j + 1) % 3 == 0 and j != 8:
                print("|", end=" ")
        print()
        if (i + 1) % 3 == 0 and i != 8:
            print("- - - + - - - + - - -")

# ---/ Find empty cell \---
def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

# ---/ Checks if 'num' can be inserted into 'pos' position \---
def is_valid(board, num, pos): 
    row, col = pos

    if num in board[row]: #//Checks if 'num' is already in 'row'
        return False

    for i in range(9): #//Checks if 'num' is already in 'col'
        if board[i][col] == num:
            return False

    box_x = col // 3 #// Which box of Sudoku 0 / 1 / 2
    box_y = row // 3

    for i in range(box_y * 3, box_y * 3 + 3): #// Checks all the boxes if 'num' exist 
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num:
                return False

    return True

# ---/ Solve the Sudoku puzzle by backtracking \---
def solve(board):
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

# ---/ Solve the Sudoku puzzle by backtracking + Error managment \---
def read_board_from_file(filename): 
    board = []
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            if len(lines) != 9:
                raise ValueError("The file should contain exactly 9 rows. || Plik powinien zawierać dokładnie 9 wierszy.")
            for i, line in enumerate(lines):
                line = line.strip()
                if len(line) != 9 or not line.isdigit():
                    raise ValueError(f"Error in line {i + 1}: '{line}' is not correct. || Błąd w wierszu {i + 1}: '{line}' nie jest prawidłowy.")
                board.append([int(ch) for ch in line])
    except Exception as e:
        print(f"Error while loading the board: {e} || Błąd podczas wczytywania planszy: {e}")
        exit(1)
    return board


# ---/ Main Program \---
filename = "sudoku.txt" # if needed filename = "C:\\Users\\...\\sudoku.txt"

board = read_board_from_file(filename)

print("\n","-_" * 20)
print("\nSudoku before solving: || Sudoku przed rozwiązaniem:\n")
print_board(board)

if solve(board):
    print("\n", "-_" * 20)
    print("\nSudoku solved: || Sudoku po rozwiązaniu:\n")
    print_board(board)
else:
    print("\nFailed to solve Sudoku. Check the correctness of the board.\nNie udało się rozwiązać Sudoku. Sprawdź poprawność planszy.")

print("\n", "-_" * 20, "\n")