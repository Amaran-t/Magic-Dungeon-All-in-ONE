import pygame
import sys
import re

pygame.init()

# --- Константы ---
WIDTH, HEIGHT = 800, 600
FONT = pygame.font.SysFont("consolas", 20)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (30, 30, 30)
BLUE = (0, 100, 255)

# --- Окно ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Magic Dungeon MVP")

# --- Игровой мир ---
world = {
    '/start': {
        'files': {'readme.txt': 'Добро пожаловать в подземелье!'},
        'dirs': ['hall']
    },
    '/start/hall': {
        'files': {'hint.code': 'Собери заклинание для прохода.'},
        'dirs': ['core'],
        'locked': True
    },
    '/start/hall/core': {
        'files': {'final.txt': 'Ты прошел MVP-игру! Поздравляю!'},
        'dirs': []
    }
}

# --- Состояние ---
current_path = '/start'
command_history = []
input_text = ''
magic_blocks = [
    'if', 'input()', '==', '"abracadabra"', 'print("Success")'
]
assembled_code = []
game_unlocked = False

# --- Вспомогательные функции ---
def draw_text(text, x, y, color=WHITE):
    surface = FONT.render(text, True, color)
    screen.blit(surface, (x, y))

def execute_command(cmd):
    global current_path, game_unlocked
    parts = cmd.strip().split()
    if not parts:
        return
    base = parts[0]

    if base == 'pwd':
        command_history.append(current_path)
    elif base == 'ls':
        room = world.get(current_path, {})
        files = ' '.join(room.get('files', {}).keys())
        dirs = ' '.join(room.get('dirs', []))
        command_history.append(f"{files} {dirs}")
    elif base == 'cd':
        if len(parts) < 2:
            command_history.append("cd: укажите путь")
            return
        target = parts[1]
        new_path = current_path + '/' + target if not current_path.endswith('/') else current_path + target
        if new_path in world:
            if world[new_path].get('locked') and not game_unlocked:
                command_history.append("Дверь закрыта. Требуется заклинание.")
            else:
                current_path = new_path
                command_history.append(f"Вы перешли в {new_path}")
        else:
            command_history.append("Нет такой директории")
    elif base == 'cat':
        if len(parts) < 2:
            command_history.append("cat: укажите файл")
            return
        filename = parts[1]
        room = world.get(current_path, {})
        content = room.get('files', {}).get(filename)
        if content:
            command_history.append(content)
        else:
            command_history.append("Файл не найден")
    else:
        command_history.append(f"Неизвестная команда: {base}")

def try_unlock():
    global game_unlocked
    code = ' '.join(assembled_code)
    pattern = r'if input\(\) == \"abracadabra\": print\(\"Success\"\)'
    if re.fullmatch(pattern, code.replace(' ', '')):
        game_unlocked = True
        command_history.append("Заклинание сработало! Путь открыт.")
    else:
        command_history.append("Неверное заклинание")

# --- Основной цикл ---
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BLACK)

    # Ввод
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if input_text.startswith("spell:"):
                    block = input_text[6:].strip()
                    if block in magic_blocks:
                        assembled_code.append(block)
                        command_history.append(f"Добавлено: {block}")
                    elif block == 'cast':
                        try_unlock()
                        assembled_code = []
                    else:
                        command_history.append("Неизвестный блок")
                else:
                    execute_command(input_text)
                input_text = ''
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode

    # Отображение истории
    y = 10
    for line in command_history[-20:]:
        draw_text(line, 10, y)
        y += 22

    # Отображение поля ввода
    pygame.draw.rect(screen, GRAY, (10, HEIGHT - 40, WIDTH - 20, 30))
    draw_text(input_text, 15, HEIGHT - 35)

    # Панель блоков
    draw_text("Блоки заклинаний:", WIDTH - 260, 10, BLUE)
    for i, block in enumerate(magic_blocks):
        draw_text(block, WIDTH - 260, 40 + i * 25)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
