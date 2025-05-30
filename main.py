import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 32
GRID_X_OFFSET = 60
GRID_Y_OFFSET = 60

WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE + 2 * GRID_X_OFFSET + 280
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 2 * GRID_Y_OFFSET + 40

# Modern color palette
BACKGROUND = (15, 15, 23)
GRID_BG = (25, 25, 35)
GRID_LINE = (45, 45, 60)
UI_BG = (30, 30, 40)
UI_BORDER = (60, 60, 80)
TEXT_PRIMARY = (220, 220, 230)
TEXT_SECONDARY = (160, 160, 180)
ACCENT = (100, 200, 255)
SUCCESS = (80, 200, 120)
WARNING = (255, 180, 80)
DANGER = (255, 100, 100)

# Enhanced Tetromino colors with gradients
TETROMINO_COLORS = {
    'I': (0, 240, 255),      # Bright cyan
    'O': (255, 220, 0),      # Golden yellow
    'T': (160, 80, 255),     # Purple
    'S': (80, 255, 80),      # Bright green
    'Z': (255, 80, 80),      # Bright red
    'J': (80, 120, 255),     # Blue
    'L': (255, 160, 0)       # Orange
}

# Shadow colors (darker versions)
SHADOW_COLORS = {
    'I': (0, 180, 200),
    'O': (200, 170, 0),
    'T': (120, 60, 200),
    'S': (60, 200, 60),
    'Z': (200, 60, 60),
    'J': (60, 90, 200),
    'L': (200, 120, 0)
}

# Tetromino shapes (same as before)
TETROMINOES = {
    'I': [['.....',
           '..#..',
           '..#..',
           '..#..',
           '..#..'],
          ['.....',
           '.....',
           '####.',
           '.....',
           '.....']],
    
    'O': [['.....',
           '.....',
           '.##..',
           '.##..',
           '.....']],
    
    'T': [['.....',
           '.....',
           '.#...',
           '###..',
           '.....'],
          ['.....',
           '.....',
           '.#...',
           '.##..',
           '.#...'],
          ['.....',
           '.....',
           '.....',
           '###..',
           '.#...'],
          ['.....',
           '.....',
           '.#...',
           '##...',
           '.#...']],
    
    'S': [['.....',
           '.....',
           '.##..',
           '##...',
           '.....'],
          ['.....',
           '.#...',
           '.##..',
           '..#..',
           '.....']],
    
    'Z': [['.....',
           '.....',
           '##...',
           '.##..',
           '.....'],
          ['.....',
           '..#..',
           '.##..',
           '.#...',
           '.....']],
    
    'J': [['.....',
           '.#...',
           '.#...',
           '##...',
           '.....'],
          ['.....',
           '.....',
           '#....',
           '###..',
           '.....'],
          ['.....',
           '.##..',
           '.#...',
           '.#...',
           '.....'],
          ['.....',
           '.....',
           '###..',
           '..#..',
           '.....']],
    
    'L': [['.....',
           '..#..',
           '..#..',
           '.##..',
           '.....'],
          ['.....',
           '.....',
           '###..',
           '#....',
           '.....'],
          ['.....',
           '##...',
           '.#...',
           '.#...',
           '.....'],
          ['.....',
           '.....',
           '..#..',
           '###..',
           '.....']]
}

class ParticleEffect:
    def __init__(self, x, y, color):
        self.particles = []
        for _ in range(8):
            self.particles.append({
                'x': x,
                'y': y,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-5, -1),
                'life': 30,
                'color': color
            })
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # gravity
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        for particle in self.particles:
            alpha = particle['life'] / 30.0
            size = max(1, int(3 * alpha))
            pygame.draw.circle(screen, particle['color'], 
                             (int(particle['x']), int(particle['y'])), size)

class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.shadow_color = SHADOW_COLORS[shape]
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0
        self.rotation = 0
        self.animation_offset = 0
        self.pulse = 0
    
    def get_rotated_shape(self):
        return TETROMINOES[self.shape][self.rotation]
    
    def get_cells(self):
        cells = []
        shape = self.get_rotated_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == '#':
                    cells.append((self.x + j, self.y + i))
        return cells

class TetrisGame:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500
        self.particles = []
        self.line_clear_animation = []
        self.animation_time = 0
        
    def get_new_piece(self):
        shape = random.choice(list(TETROMINOES.keys()))
        return Tetromino(shape, TETROMINO_COLORS[shape])
    
    def is_valid_position(self, piece, dx=0, dy=0, rotation=None):
        if rotation is None:
            rotation = piece.rotation
        
        old_rotation = piece.rotation
        piece.rotation = rotation
        
        for x, y in piece.get_cells():
            x += dx
            y += dy
            
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                piece.rotation = old_rotation
                return False
            
            if y >= 0 and self.grid[y][x] is not None:
                piece.rotation = old_rotation
                return False
        
        piece.rotation = old_rotation
        return True
    
    def place_piece(self, piece):
        for x, y in piece.get_cells():
            if y >= 0:
                self.grid[y][x] = piece.color
        
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(cell is not None for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        # Add line clear animation
        if lines_to_clear:
            self.line_clear_animation = lines_to_clear[:]
            # Add particles for line clear effect
            for y in lines_to_clear:
                for x in range(GRID_WIDTH):
                    px = GRID_X_OFFSET + x * CELL_SIZE + CELL_SIZE // 2
                    py = GRID_Y_OFFSET + y * CELL_SIZE + CELL_SIZE // 2
                    self.particles.append(ParticleEffect(px, py, self.grid[y][x]))
        
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
        
        lines_cleared = len(lines_to_clear)
        self.lines_cleared += lines_cleared
        
        # Enhanced scoring system
        score_values = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
        self.score += score_values.get(lines_cleared, 0) * self.level
        
        # Level progression
        self.level = self.lines_cleared // 10 + 1
        self.fall_speed = max(50, 500 - (self.level - 1) * 50)
    
    def move_piece(self, dx, dy):
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
    
    def rotate_piece(self):
        rotations = len(TETROMINOES[self.current_piece.shape])
        new_rotation = (self.current_piece.rotation + 1) % rotations
        
        if self.is_valid_position(self.current_piece, 0, 0, new_rotation):
            self.current_piece.rotation = new_rotation
            return True
        return False
    
    def update(self, dt):
        self.animation_time += dt
        
        # Update particles
        for particle_effect in self.particles[:]:
            particle_effect.update()
            if not particle_effect.particles:
                self.particles.remove(particle_effect)
        
        # Clear line clear animation after some time
        if self.line_clear_animation and self.animation_time > 300:
            self.line_clear_animation = []
            self.animation_time = 0
        
        # Update current piece animation
        if self.current_piece:
            self.current_piece.pulse += 0.1
        
        self.fall_time += dt
        
        if self.fall_time >= self.fall_speed:
            if not self.move_piece(0, 1):
                self.place_piece(self.current_piece)
                self.current_piece = self.next_piece
                self.next_piece = self.get_new_piece()
                
                # Check game over
                if not self.is_valid_position(self.current_piece):
                    return False  # Game over
            
            self.fall_time = 0
        
        return True  # Game continues
    
    def hard_drop(self):
        drop_distance = 0
        while self.move_piece(0, 1):
            drop_distance += 1
            self.score += 2
        
        # Add drop effect
        if drop_distance > 0:
            for x, y in self.current_piece.get_cells():
                px = GRID_X_OFFSET + x * CELL_SIZE + CELL_SIZE // 2
                py = GRID_Y_OFFSET + y * CELL_SIZE + CELL_SIZE // 2
                self.particles.append(ParticleEffect(px, py, self.current_piece.color))
    
    def draw_rounded_rect(self, screen, color, rect, radius=4):
        """Draw a rounded rectangle"""
        pygame.draw.rect(screen, color, rect, border_radius=radius)
    
    def draw_cell_with_gradient(self, screen, x, y, color, shadow_color, highlight=False):
        """Draw a cell with gradient effect"""
        rect = pygame.Rect(
            GRID_X_OFFSET + x * CELL_SIZE + 1,
            GRID_Y_OFFSET + y * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2
        )
        
        # Main color
        self.draw_rounded_rect(screen, color, rect, 3)
        
        # Highlight effect
        if highlight:
            pulse = abs(math.sin(self.animation_time * 0.01)) * 0.3 + 0.7
            highlight_color = tuple(min(255, max(0, int(c * pulse))) for c in color)
            self.draw_rounded_rect(screen, highlight_color, rect, 3)
        
        # Inner highlight
        inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 8, 4)
        highlight_color = tuple(min(255, max(0, c + 40)) for c in color)
        self.draw_rounded_rect(screen, highlight_color, inner_rect, 2)
        
        # Shadow - ensure no negative values
        shadow_rect = pygame.Rect(rect.x + 2, rect.bottom - 6, rect.width - 4, 4)
        safe_shadow_color = tuple(max(0, min(255, c)) for c in shadow_color)
        self.draw_rounded_rect(screen, safe_shadow_color, shadow_rect, 2)
    
    def draw_grid(self, screen):
        # Draw background
        grid_bg_rect = pygame.Rect(
            GRID_X_OFFSET - 5, GRID_Y_OFFSET - 5,
            GRID_WIDTH * CELL_SIZE + 10, GRID_HEIGHT * CELL_SIZE + 10
        )
        self.draw_rounded_rect(screen, GRID_BG, grid_bg_rect, 8)
        
        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            start_pos = (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET)
            end_pos = (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET + GRID_HEIGHT * CELL_SIZE)
            pygame.draw.line(screen, GRID_LINE, start_pos, end_pos, 1)
        
        for y in range(GRID_HEIGHT + 1):
            start_pos = (GRID_X_OFFSET, GRID_Y_OFFSET + y * CELL_SIZE)
            end_pos = (GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE, GRID_Y_OFFSET + y * CELL_SIZE)
            pygame.draw.line(screen, GRID_LINE, start_pos, end_pos, 1)
        
        # Draw placed pieces
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] is not None:
                    # Check if this line is being cleared
                    highlight = y in self.line_clear_animation
                    shadow_color = tuple(max(0, c - 60) for c in self.grid[y][x])
                    self.draw_cell_with_gradient(screen, x, y, self.grid[y][x], shadow_color, highlight)
    
    def draw_piece(self, screen, piece, ghost=False):
        alpha = 0.3 if ghost else 1.0
        
        for x, y in piece.get_cells():
            if y >= 0:
                if ghost:
                    # Draw ghost piece
                    rect = pygame.Rect(
                        GRID_X_OFFSET + x * CELL_SIZE + 1,
                        GRID_Y_OFFSET + y * CELL_SIZE + 1,
                        CELL_SIZE - 2,
                        CELL_SIZE - 2
                    )
                    ghost_color = tuple(max(0, c // 3) for c in piece.color)
                    pygame.draw.rect(screen, ghost_color, rect, 2, border_radius=3)
                else:
                    self.draw_cell_with_gradient(screen, x, y, piece.color, piece.shadow_color, True)
    
    def draw_ghost_piece(self, screen):
        """Draw the ghost piece showing where the current piece will land"""
        ghost_piece = Tetromino(self.current_piece.shape, self.current_piece.color)
        ghost_piece.x = self.current_piece.x
        ghost_piece.y = self.current_piece.y
        ghost_piece.rotation = self.current_piece.rotation
        
        # Move ghost piece down until it can't move anymore
        while self.is_valid_position(ghost_piece, 0, 1):
            ghost_piece.y += 1
        
        # Only draw if ghost is below current piece
        if ghost_piece.y > self.current_piece.y:
            self.draw_piece(screen, ghost_piece, ghost=True)
    
    def draw_ui_panel(self, screen, x, y, width, height, title):
        """Draw a styled UI panel"""
        panel_rect = pygame.Rect(x, y, width, height)
        self.draw_rounded_rect(screen, UI_BG, panel_rect, 8)
        pygame.draw.rect(screen, UI_BORDER, panel_rect, 2, border_radius=8)
        
        if title:
            font = pygame.font.Font(None, 24)
            title_text = font.render(title, True, TEXT_PRIMARY)
            screen.blit(title_text, (x + 10, y + 8))
        
        return panel_rect
    
    def draw_next_piece(self, screen):
        ui_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
        ui_y = GRID_Y_OFFSET
        
        panel = self.draw_ui_panel(screen, ui_x, ui_y, 120, 100, "Next")
        
        # Draw next piece
        shape = TETROMINOES[self.next_piece.shape][0]
        start_x = ui_x + 30
        start_y = ui_y + 15
        
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == '#':
                    mini_rect = pygame.Rect(
                        start_x + j * 16,
                        start_y + i * 16,
                        14,
                        14
                    )
                    self.draw_rounded_rect(screen, self.next_piece.color, mini_rect, 2)
                    # Mini highlight
                    highlight_rect = pygame.Rect(mini_rect.x + 1, mini_rect.y + 1, mini_rect.width - 4, 3)
                    highlight_color = tuple(min(255, c + 40) for c in self.next_piece.color)
                    self.draw_rounded_rect(screen, highlight_color, highlight_rect, 1)
    
    def draw_stats(self, screen):
        ui_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
        ui_y = GRID_Y_OFFSET + 120
        
        panel = self.draw_ui_panel(screen, ui_x, ui_y, 120, 140, "Stats")
        
        font = pygame.font.Font(None, 20)
        
        stats = [
            ("Score", str(self.score), SUCCESS),
            ("Level", str(self.level), ACCENT),
            ("Lines", str(self.lines_cleared), WARNING)
        ]
        
        for i, (label, value, color) in enumerate(stats):
            y_pos = ui_y + 35 + i * 35
            
            label_text = font.render(label, True, TEXT_SECONDARY)
            value_text = font.render(value, True, color)
            
            screen.blit(label_text, (ui_x + 10, y_pos))
            screen.blit(value_text, (ui_x + 10, y_pos + 15))
    
    def draw_controls(self, screen):
        ui_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
        ui_y = GRID_Y_OFFSET + 280
        
        panel = self.draw_ui_panel(screen, ui_x, ui_y, 120, 200, "Controls")
        
        font = pygame.font.Font(None, 16)
        
        controls = [
            "← → Move",
            "↓ Soft Drop",
            "↑ Rotate",
            "Space Hard Drop",
            "",
            "R Restart",
            "ESC Quit"
        ]
        
        for i, control in enumerate(controls):
            if control:
                color = TEXT_SECONDARY if control else TEXT_PRIMARY
                text = font.render(control, True, color)
                screen.blit(text, (ui_x + 10, ui_y + 30 + i * 18))

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Modern Tetris")
    clock = pygame.time.Clock()
    
    # Load fonts
    try:
        title_font = pygame.font.Font(None, 48)
        ui_font = pygame.font.Font(None, 24)
    except:
        title_font = pygame.font.Font(None, 48)
        ui_font = pygame.font.Font(None, 24)
    
    game = TetrisGame()
    game_over = False
    
    while True:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game = TetrisGame()
                    game_over = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                elif not game_over:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        game.move_piece(-1, 0)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        game.move_piece(1, 0)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        if game.move_piece(0, 1):
                            game.score += 1
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()
        
        if not game_over:
            game_over = not game.update(dt)
        
        # Drawing
        screen.fill(BACKGROUND)
        
        # Draw game elements
        game.draw_grid(screen)
        if not game_over and game.current_piece:
            game.draw_ghost_piece(screen)
            game.draw_piece(screen, game.current_piece)
        
        # Draw UI
        game.draw_next_piece(screen)
        game.draw_stats(screen)
        game.draw_controls(screen)
        
        # Draw particles
        for particle_effect in game.particles:
            particle_effect.draw(screen)
        
        # Game over overlay
        if game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BACKGROUND)
            screen.blit(overlay, (0, 0))
            
            # Game over panel
            panel_width, panel_height = 300, 150
            panel_x = (WINDOW_WIDTH - panel_width) // 2
            panel_y = (WINDOW_HEIGHT - panel_height) // 2
            
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            game.draw_rounded_rect(screen, UI_BG, panel_rect, 12)
            pygame.draw.rect(screen, DANGER, panel_rect, 3, border_radius=12)
            
            game_over_text = title_font.render("GAME OVER", True, DANGER)
            score_text = ui_font.render(f"Final Score: {game.score}", True, TEXT_PRIMARY)
            restart_text = ui_font.render("Press R to restart", True, TEXT_SECONDARY)
            
            screen.blit(game_over_text, 
                       (panel_x + (panel_width - game_over_text.get_width()) // 2, panel_y + 20))
            screen.blit(score_text, 
                       (panel_x + (panel_width - score_text.get_width()) // 2, panel_y + 70))
            screen.blit(restart_text, 
                       (panel_x + (panel_width - restart_text.get_width()) // 2, panel_y + 100))
        
        pygame.display.flip()

if __name__ == "__main__":
    main()