import pygame
import random
import winsound
import os

pygame.init()

WIDTH = 800
HEIGHT = 600

GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_SIZE = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (255, 0, 0),  # Красный
    (0, 255, 0),  # Зеленый
    (0, 0, 255),  # Синий
    (255, 255, 0),  # Желтый
    (255, 0, 255),  # Фиолетовый
    (0, 255, 255)  # Голубой
]

# Тетрамино
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 0],
     [0, 1, 1]],  # Z
    [[0, 1, 1],
     [1, 1, 0]],  # S
    [[1, 1, 1],
     [0, 1, 0]],  # T
    [[1, 1, 0],
     [1, 1, 0]],  # O
    [[1, 0, 0],
     [1, 1, 1]],  # L
    [[0, 0, 1],
     [1, 1, 1]],  # J
    [[1, 0],
     [0, 1]]  # Test
]

try:
    def play_beep():
        winsound.Beep(500, 100)
except Exception:
    def play_beep():
        print('Звук только для пользователей Windows, извините')


class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.color = random.choice(COLORS)
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        rotated_shape = []
        rows = len(self.shape)
        cols = len(self.shape[0])

        for col in range(cols):
            new_row = []
            for row in range(rows - 1, -1, -1):
                new_row.append(self.shape[row][col])
            rotated_shape.append(new_row)

        self.shape = rotated_shape


class Game:
    def __init__(self):

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in
                     range(GRID_HEIGHT)]  # права команда слева что она выполyняеет
        self.current_tetromino = self.new_tetromino()
        self.next_tetromino = self.new_tetromino()
        self.game_over = False
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.base_fall_speed = 500
        self.fall_speed = self.base_fall_speed
        self.level = 1
        self.high_score = self.load_high_score()
        # Звуковая кнопка
        self.is_sound = True
        self.sound_button_x = WIDTH - 160
        self.sound_button_y = HEIGHT - 100
        self.sound_button_width = 150
        self.sound_button_height = 80

    def new_tetromino(self):
        return Tetromino(random.choice(SHAPES))  # выбирается случайная тертромино

    def draw_grid(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                pygame.draw.rect(
                    self.screen,
                    GRAY if cell == 0 else COLORS[cell - 1], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE),
                    1 if cell == 0 else 0
                )

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as file:
            file.write(str(self.high_score))

    def draw_tetromino(self):
        if self.current_tetromino:
            for y, row in enumerate(self.current_tetromino.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            self.screen,
                            self.current_tetromino.color,
                            ((self.current_tetromino.x + x) * GRID_SIZE,
                             (self.current_tetromino.y + y) * GRID_SIZE,
                             GRID_SIZE, GRID_SIZE)
                        )

    def valid_move(self, shape, x_offset, y_offset):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_tetromino.x + x + x_offset
                    new_y = self.current_tetromino.y + y + y_offset
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x] != 0:
                        return False

        return True

    def place_tetromino(self):
        for y, row in enumerate(self.current_tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_tetromino.y + y][self.current_tetromino.x + x] = COLORS.index(
                        self.current_tetromino.color) + 1

        self.check_lines()
        self.current_tetromino = self.next_tetromino  # теперь записывает инфу
        self.next_tetromino = self.new_tetromino()  # и заменяет ее чтобы выглядело нормально
        if not self.valid_move(self.current_tetromino.shape, 0, 0):
            self.game_over = True

    def draw_next_tetormino(self):
        if self.next_tetromino:
            #  по сути просто рисование без движения
            start_x = (GRID_WIDTH + 2)
            start_y = 5

            text_next = self.font.render("Следующая фигура", True, WHITE)
            self.screen.blit(text_next, (320, 100))

            #  Размеры обводки
            border_x = start_x * GRID_SIZE - 15
            border_y = (start_y - 0.5) * GRID_SIZE
            border_width = 5 * GRID_SIZE
            border_height = 5 * GRID_SIZE - 58
            pygame.draw.rect(self.screen, WHITE, (border_x, border_y, border_width, border_height), 2)

            for y, row in enumerate(self.next_tetromino.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            self.screen,
                            self.next_tetromino.color,
                            ((start_x + x) * GRID_SIZE,
                             (start_y + y) * GRID_SIZE,
                             GRID_SIZE, GRID_SIZE)
                        )

    def check_lines(self):
        full_lines = []
        for y, row in enumerate(self.grid):
            if all(cell != 0 for cell in row):
                full_lines.append(y)

        if full_lines:
            self.score += len(full_lines) * 100
            for line in sorted(full_lines, reverse=True):
                del self.grid[line]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])

    def draw_score(self):
        score_text = self.font.render(f"Получено очков: {self.score}", True, WHITE)
        self.screen.blit(score_text, (320, 10))

        high_score_text = self.font.render(f"Лучший резульат: {self.high_score}", True, WHITE)
        self.screen.blit(high_score_text, (320, 400))

    def draw_game_over(self):
        game_over_text = self.font.render("Вы погибли!", True, (255, 0, 0))
        self.screen.blit(game_over_text,
                         (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))

    def draw_level(self):
        level_text = self.font.render(f"Уровень сложности: {self.level}", True, WHITE)
        self.screen.blit(level_text, (320, 40))

    def draw_sound_button(self):
        button_color = (0, 255, 0) if self.is_sound else (255, 0, 0)
        pygame.draw.rect(
            self.screen,
            button_color,
            (self.sound_button_x, self.sound_button_y, self.sound_button_width, self.sound_button_height)
        )

        text_dd = self.font.render("Бипанье", True, WHITE)
        text_rect = text_dd.get_rect(center=(
            self.sound_button_x + self.sound_button_width // 2, self.sound_button_y + self.sound_button_height // 2))
        self.screen.blit(text_dd, text_rect)

    def main(self):
        fall_time = 0
        fall_speed = 500

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.valid_move(self.current_tetromino.shape, -1, 0):
                            self.current_tetromino.x -= 1
                            if self.is_sound:
                                play_beep()
                    elif event.key == pygame.K_RIGHT:
                        if self.valid_move(self.current_tetromino.shape, 1, 0):
                            self.current_tetromino.x += 1
                            if self.is_sound:
                                play_beep()
                    elif event.key == pygame.K_DOWN:
                        if self.valid_move(self.current_tetromino.shape, 0, 1):
                            self.current_tetromino.y += 1
                            if self.is_sound:
                                play_beep()
                    elif event.key == pygame.K_UP:
                        rotated_shape = self.current_tetromino.shape
                        self.current_tetromino.rotate()
                        if not self.valid_move(self.current_tetromino.shape, 0, 0):
                            self.current_tetromino.shape = rotated_shape
                        else:
                            if self.is_sound:
                                play_beep()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    #  Проверяем нажатие внутри кнопки
                    if self.sound_button_x <= mouse_x <= self.sound_button_x + self.sound_button_width and \
                            self.sound_button_y <= mouse_y <= self.sound_button_y + self.sound_button_height:
                        self.is_sound = not self.is_sound

            if not self.game_over:
                fall_time += self.clock.get_rawtime()
                self.clock.tick()

                #  Увеличение сложности
                if self.score >= 1000 and self.fall_speed == self.base_fall_speed:
                    self.fall_speed = self.base_fall_speed * 0.8
                    self.level = 2
                elif self.score >= 2000 and self.fall_speed == self.base_fall_speed * 0.8:
                    self.fall_speed = self.base_fall_speed * 0.6
                    self.level = 3
                elif self.score >= 3000 and self.fall_speed == self.base_fall_speed * 0.6:
                    self.fall_speed = self.base_fall_speed * 0.4
                    self.level = 4
                elif self.score >= 4000 and self.fall_speed == self.base_fall_speed * 0.4:
                    self.fall_speed = self.base_fall_speed * 0.2
                    self.level = 5  # по идее если поле не пустое то тут уже невозможно

                if fall_time > self.fall_speed:
                    fall_time = 0
                    if self.valid_move(self.current_tetromino.shape, 0, 1):
                        self.current_tetromino.y += 1
                    else:
                        self.place_tetromino()

            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_tetromino()
            self.draw_score()
            self.draw_next_tetormino()
            self.draw_level()
            self.draw_sound_button()
            if self.game_over:
                self.draw_game_over()
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
            pygame.display.flip()

        pygame.quit()


game = Game()
game.main()
