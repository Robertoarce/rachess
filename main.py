from fasthtml.common import *
from fasthtml.js import *

# Tailwind CSS
tailwind_css = "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"

app, route = fast_app(
    hdrs=(
        Link(rel="stylesheet", href=tailwind_css),
        Style("""
            .chessboard {
                display: grid;
                grid-template-columns: repeat(8, 1fr);
                grid-template-rows: repeat(8, 1fr);
                width: 400px;
                height: 400px;
            }
            .square {
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 2rem;
            }
        """)
    ),
    pico=False  # We're using Tailwind instead of Pico CSS
)

# Chess pieces Unicode characters
pieces = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
}

# Initial board setup
initial_board = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
]

@route('/')
def index():
    return PageX(
        "Chess Game",
        Div(
            # Chessboard
            Div(
                *[Div(
                    pieces.get(initial_board[row][col], ''),
                    cls=f"square {'bg-gray-200' if (row + col) % 2 == 0 else 'bg-gray-600'} text-black",
                    id=f"square-{row}-{col}",
                    hx_post=f"/move",
                    hx_trigger="click",
                    hx_vals=f'{{"row": {row}, "col": {col}}}'
                ) for row in range(8) for col in range(8)],
                cls="chessboard border border-gray-800"
            ),
            # Controls
            Div(
                Button("New Game", cls="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded",
                       hx_post="/new-game", hx_target="#game-container"),
                Button("Undo Move", cls="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded ml-2",
                       hx_post="/undo-move", hx_target="#game-container"),
                cls="mt-4"
            ),
            # Move list
            Div(
                H3("Moves", cls="text-xl font-bold mb-2"),
                Ul(id="move-list", cls="list-decimal list-inside"),
                cls="mt-4"
            ),
            id="game-container",
            cls="container mx-auto mt-8 flex flex-col items-center"
        )
    )

# Game state (you might want to use a database for persistence in a real application)
game_state = {
    'board': initial_board,
    'moves': [],
    'selected_piece': None,
    'current_player': 'white'
}

@route('/move', methods=['POST'])
async def move(request):
    data = await request.form()
    row, col = int(data['row']), int(data['col'])
    
    if game_state['selected_piece'] is None:
        # Select the piece if it belongs to the current player
        piece = game_state['board'][row][col]
        if (piece.isupper() and game_state['current_player'] == 'white') or \
           (piece.islower() and game_state['current_player'] == 'black'):
            game_state['selected_piece'] = (row, col)
    else:
        # Move the selected piece
        from_row, from_col = game_state['selected_piece']
        game_state['board'][row][col] = game_state['board'][from_row][from_col]
        game_state['board'][from_row][from_col] = ' '
        
        # Record the move
        move = f"{chr(from_col + 97)}{8-from_row} to {chr(col + 97)}{8-row}"
        game_state['moves'].append(move)
        
        # Switch players
        game_state['current_player'] = 'black' if game_state['current_player'] == 'white' else 'white'
        game_state['selected_piece'] = None

    return render_board()

@route('/new-game', methods=['POST'])
def new_game():
    game_state['board'] = [row[:] for row in initial_board]
    game_state['moves'] = []
    game_state['selected_piece'] = None
    game_state['current_player'] = 'white'
    return render_board()

@route('/undo-move', methods=['POST'])
def undo_move():
    if game_state['moves']:
        game_state['moves'].pop()
        # In a real application, you'd restore the previous board state here
        game_state['current_player'] = 'black' if game_state['current_player'] == 'white' else 'white'
    return render_board()

def render_board():
    return Div(
        # Chessboard
        Div(
            *[Div(
                pieces.get(game_state['board'][row][col], ''),
                cls=f"square {'bg-gray-200' if (row + col) % 2 == 0 else 'bg-gray-600'} text-black",
                id=f"square-{row}-{col}",
                hx_post=f"/move",
                hx_trigger="click",
                hx_vals=f'{{"row": {row}, "col": {col}}}'
            ) for row in range(8) for col in range(8)],
            cls="chessboard border border-gray-800"
        ),
        # Controls
        Div(
            Button("New Game", cls="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded",
                   hx_post="/new-game", hx_target="#game-container"),
            Button("Undo Move", cls="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded ml-2",
                   hx_post="/undo-move", hx_target="#game-container"),
            cls="mt-4"
        ),
        # Move list
        Div(
            H3("Moves", cls="text-xl font-bold mb-2"),
            Ul(*[Li(move, cls="mb-1") for move in game_state['moves']], id="move-list", cls="list-decimal list-inside"),
            cls="mt-4"
        ),
        id="game-container",
        cls="container mx-auto mt-8 flex flex-col items-center"
    )

if __name__ == "__main__":
    serve()