import sys
import math
import random
import pygame

from settings import *
from utils import add, neg, in_bounds, cell_rect
from particles import Particle, ExpandingRing
from bike import Bike
from ai import flood_fill_free_space, count_safe_neighbors

class TronGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tron Light Cycle — AI Lab")
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("consolas", 22)
        self.font_big = pygame.font.SysFont("consolas", 42, bold=True)
        self.font_mid = pygame.font.SysFont("consolas", 28, bold=True)

        self.player_score = 0
        self.ai_score = 0
        self.match_winner = None
        
        self.state = "MENU"
        self.menu_options = ["Play", "Difficulty", "Trail Mode", "Quit"]
        self.menu_idx = 0
        self.difficulty = "Medium"
        self.difficulties = ["Easy", "Medium", "Hard"]
        self.trail_mode = "Finite"
        self.trail_modes = ["Finite", "Infinite"]
        self.particles = []
        self.overlay_alpha = 0.0
        
        self.menu_bike_img = None
        try:
            img = pygame.image.load("/Users/nick/.gemini/antigravity/brain/dafd4e00-511d-4d34-87f3-2e218c3d39fd/futuristic_tron_bike_1778613577387.png").convert_alpha()
            target_h = 200
            aspect = img.get_width() / img.get_height()
            self.menu_bike_img = pygame.transform.smoothscale(img, (int(target_h * aspect), target_h))
        except:
            pass
        
        self.reset_match()
        self.state = "MENU"

    def reset_match(self):
        self.player_score = 0
        self.ai_score = 0
        self.match_winner = None
        self.reset_round()

    def reset_round(self):
        self.state = "RUNNING"
        self.winner = None
        self.round_start_ms = pygame.time.get_ticks()
        self.round_end_ms = None
        self.round_over_time = None
        self.last_move_time = pygame.time.get_ticks()
        self.move_delay = MEDIUM_DELAY
        self.particles = []
        self.overlay_alpha = 0.0

        self.player = Bike(
            name="Player",
            pos=(5, GRID_H // 2),
            direction=DIRS["RIGHT"],
            color=PLAYER_COLOR,
            glow_color=PLAYER_GLOW,
            head_color=PLAYER_HEAD,
        )
        self.ai = Bike(
            name="AI",
            pos=(GRID_W - 6, GRID_H // 2),
            direction=DIRS["LEFT"],
            color=AI_COLOR,
            glow_color=AI_GLOW,
            head_color=AI_HEAD,
        )

    def occupied_cells(self):
        return set(self.player.trail) | set(self.ai.trail)

    def ai_choose_direction(self):
        occupied = self.occupied_cells()

        candidates = []
        for d in DIR_LIST:
            if d == neg(self.ai.direction):
                continue
            nxt = add(self.ai.pos, d)
            if not in_bounds(nxt):
                continue
            if nxt in occupied:
                continue
            candidates.append(d)

        if not candidates:
            return self.ai.direction

        best_score = None
        best_dirs = []
        for d in candidates:
            nxt = add(self.ai.pos, d)

            space = flood_fill_free_space(nxt, occupied)
            degree = count_safe_neighbors(nxt, occupied)

            # Basic dead-end avoidance
            dead_end_penalty = 0
            if degree == 0:
                dead_end_penalty = 10_000
            elif degree == 1:
                dead_end_penalty = 250

            if self.difficulty == "Easy":
                score = (space * 5) + (degree * 5)
            elif self.difficulty == "Medium":
                score = (space * 10) + (degree * 15) - dead_end_penalty
            else: # Hard
                score = (space * 20) + (degree * 25) - (dead_end_penalty * 2)

            score += random.randint(0, 7)

            if best_score is None or score > best_score:
                best_score = score
                best_dirs = [d]
            elif score == best_score:
                best_dirs.append(d)

        return random.choice(best_dirs)

    def end_round(self, winner):
        self.winner = winner
        self.round_end_ms = pygame.time.get_ticks()
        self.round_over_time = pygame.time.get_ticks()
        
        if winner == "Player":
            self.player_score += 1
        elif winner == "AI":
            self.ai_score += 1
            
        if self.player_score >= 3:
            self.match_winner = "Player"
            self.state = "MATCH_OVER"
        elif self.ai_score >= 3:
            self.match_winner = "AI"
            self.state = "MATCH_OVER"
        else:
            self.state = "ROUND_OVER"

    def survival_time_s(self):
        end_ms = self.round_end_ms if self.round_end_ms is not None else pygame.time.get_ticks()
        return max(0.0, (end_ms - self.round_start_ms) / 1000.0)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)

                if self.state == "MENU":
                    if event.key == pygame.K_UP:
                        self.menu_idx = (self.menu_idx - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_idx = (self.menu_idx + 1) % len(self.menu_options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        opt = self.menu_options[self.menu_idx]
                        if opt == "Play":
                            self.reset_match()
                        elif opt == "Difficulty":
                            d_idx = self.difficulties.index(self.difficulty)
                            self.difficulty = self.difficulties[(d_idx + 1) % len(self.difficulties)]
                        elif opt == "Trail Mode":
                            t_idx = self.trail_modes.index(self.trail_mode)
                            self.trail_mode = self.trail_modes[(t_idx + 1) % len(self.trail_modes)]
                        elif opt == "Quit":
                            pygame.quit()
                            sys.exit(0)
                elif self.state == "RUNNING":
                    if event.key == pygame.K_UP:
                        self.player.set_direction(DIRS["UP"])
                    elif event.key == pygame.K_DOWN:
                        self.player.set_direction(DIRS["DOWN"])
                    elif event.key == pygame.K_LEFT:
                        self.player.set_direction(DIRS["LEFT"])
                    elif event.key == pygame.K_RIGHT:
                        self.player.set_direction(DIRS["RIGHT"])
                elif self.state == "MATCH_OVER":
                    if event.key in (pygame.K_r, pygame.K_SPACE):
                        self.reset_match()
                    elif event.key == pygame.K_m:
                        self.state = "MENU"

    def spawn_particles(self, pos, color):
        cx, cy = pos[0] * CELL_SIZE + CELL_SIZE // 2, PANEL_H + pos[1] * CELL_SIZE + CELL_SIZE // 2
        for _ in range(25):
            self.particles.append(Particle((cx, cy), color))
        self.particles.append(ExpandingRing((cx, cy), color))
        self.particles.append(ExpandingRing((cx, cy), (255, 255, 255)))

    def step(self):
        if self.state != "MENU":
            for p in self.particles[:]:
                p.update()
                if p.lifetime <= 0:
                    self.particles.remove(p)

        if self.state == "ROUND_OVER":
            if pygame.time.get_ticks() - self.round_over_time > 2500:
                self.reset_round()
            return

        if self.state != "RUNNING":
            return

        current_time = pygame.time.get_ticks()
        
        time_s = self.survival_time_s()
        
        if self.difficulty == "Easy":
            base_delay = EASY_DELAY
        elif self.difficulty == "Medium":
            base_delay = MEDIUM_DELAY
        else:
            base_delay = HARD_DELAY
            
        self.move_delay = max(50, base_delay - int(time_s * 2.5))

        if current_time - self.last_move_time < self.move_delay:
            return
            
        self.last_move_time = current_time

        self.ai.set_direction(self.ai_choose_direction())

        occupied = self.occupied_cells()

        p_next = self.player.next_cell()
        a_next = self.ai.next_cell()

        p_crash = (not in_bounds(p_next)) or (p_next in occupied)
        a_crash = (not in_bounds(a_next)) or (a_next in occupied)

        if p_next == a_next:
            p_crash = True
            a_crash = True
        if p_next == self.ai.pos and a_next == self.player.pos:
            p_crash = True
            a_crash = True

        if p_crash and a_crash:
            self.spawn_particles(self.player.pos, PLAYER_HEAD)
            self.spawn_particles(self.ai.pos, AI_HEAD)
            self.end_round("Tie")
            return
        if p_crash:
            self.spawn_particles(self.player.pos, PLAYER_HEAD)
            self.end_round("AI")
            return
        if a_crash:
            self.spawn_particles(self.ai.pos, AI_HEAD)
            self.end_round("Player")
            return

        self.player.commit_move(p_next)
        self.ai.commit_move(a_next)
        
        if self.trail_mode == "Finite":
            if len(self.player.trail) > MAX_TRAIL_LEN:
                self.player.trail.pop(0)
            if len(self.ai.trail) > MAX_TRAIL_LEN:
                self.ai.trail.pop(0)

    def draw_neon_text(self, text, font, color, pos, center=False):
        surf_glow = font.render(text, True, color)
        surf_solid = font.render(text, True, (255, 255, 255))
        
        rect = surf_glow.get_rect(center=pos) if center else surf_glow.get_rect(topleft=pos)
        
        s = pygame.Surface(surf_glow.get_size(), pygame.SRCALPHA)
        s.fill((0,0,0,0))
        s.blit(surf_glow, (0,0))
        s.set_alpha(100)
        
        for dx, dy in [(-2, -2), (2, 2), (-2, 2), (2, -2), (0, 0)]:
            self.screen.blit(s, (rect.x + dx, rect.y + dy))
            
        self.screen.blit(surf_solid, rect)

    def draw_background(self):
        self.screen.fill(BG)
        time_ms = pygame.time.get_ticks()
        
        y_offset = (time_ms * 0.02) % 15
        s = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        for y in range(int(y_offset), WIN_H, 15):
            pygame.draw.line(s, (10, 10, 20, 100), (0, y), (WIN_W, y))
        self.screen.blit(s, (0, 0))

    def draw_trails(self, bike):
        trail_len = len(bike.trail)
        if trail_len < 2:
            self.draw_bike(bike)
            return

        points = []
        for cell in bike.trail[:-1]:
            cx = cell[0] * CELL_SIZE + CELL_SIZE // 2
            cy = PANEL_H + cell[1] * CELL_SIZE + CELL_SIZE // 2
            points.append((cx, cy))
            
        hx = bike.trail[-1][0] * CELL_SIZE + CELL_SIZE // 2
        hy = PANEL_H + bike.trail[-1][1] * CELL_SIZE + CELL_SIZE // 2
        points.append((hx, hy))

        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]
            
            if self.trail_mode == "Finite":
                age_factor = 0.3 + 0.7 * ((i + 1) / trail_len)
            else:
                age_factor = 1.0
            
            r = int(BG[0] + (bike.color[0] - BG[0]) * age_factor)
            g = int(BG[1] + (bike.color[1] - BG[1]) * age_factor)
            b = int(BG[2] + (bike.color[2] - BG[2]) * age_factor)
            faded_color = (r, g, b)

            gr = int(BG[0] + (bike.glow_color[0] - BG[0]) * age_factor)
            gg = int(BG[1] + (bike.glow_color[1] - BG[1]) * age_factor)
            gb = int(BG[2] + (bike.glow_color[2] - BG[2]) * age_factor)
            glow_color = (gr, gg, gb)
            
            if age_factor > 0.4:
                pygame.draw.line(self.screen, glow_color, p1, p2, 10)
            pygame.draw.line(self.screen, faded_color, p1, p2, 5)
            
            if age_factor > 0.6:
                pygame.draw.line(self.screen, (255, 255, 255), p1, p2, 2)
                
            pygame.draw.circle(self.screen, faded_color, p2, 2)

        self.draw_bike(bike)

    def draw_bike(self, bike):
        cell = bike.trail[-1]
        cx = cell[0] * CELL_SIZE + CELL_SIZE // 2
        cy = PANEL_H + cell[1] * CELL_SIZE + CELL_SIZE // 2
        
        dx, dy = bike.direction
        length = CELL_SIZE * 0.9
        width = CELL_SIZE * 0.6
        
        angle = math.atan2(dy, dx)
        
        p_nose = (cx + math.cos(angle) * (length/2), cy + math.sin(angle) * (length/2))
        p_back = (cx - math.cos(angle) * (length/2), cy - math.sin(angle) * (length/2))
        
        angle_left = angle - math.pi/2
        p_left = (cx - math.cos(angle)*length*0.2 + math.cos(angle_left) * (width/2), 
                  cy - math.sin(angle)*length*0.2 + math.sin(angle_left) * (width/2))
                  
        angle_right = angle + math.pi/2
        p_right = (cx - math.cos(angle)*length*0.2 + math.cos(angle_right) * (width/2), 
                   cy - math.sin(angle)*length*0.2 + math.sin(angle_right) * (width/2))

        chassis_pts = [p_nose, p_right, p_back, p_left]
        
        s = pygame.Surface((CELL_SIZE*2, CELL_SIZE*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*bike.glow_color, 80), (CELL_SIZE, CELL_SIZE), CELL_SIZE*0.8)
        self.screen.blit(s, (cx - CELL_SIZE, cy - CELL_SIZE))

        pygame.draw.polygon(self.screen, bike.color, chassis_pts)
        pygame.draw.line(self.screen, (255, 255, 255), p_back, p_nose, 2)
        
        wheel_r = width * 0.35
        fw_x = cx + math.cos(angle) * (length*0.25)
        fw_y = cy + math.sin(angle) * (length*0.25)
        pygame.draw.circle(self.screen, bike.head_color, (int(fw_x), int(fw_y)), int(wheel_r))
        pygame.draw.circle(self.screen, (255,255,255), (int(fw_x), int(fw_y)), int(wheel_r*0.4))
        
        rw_x = cx - math.cos(angle) * (length*0.35)
        rw_y = cy - math.sin(angle) * (length*0.35)
        pygame.draw.circle(self.screen, bike.head_color, (int(rw_x), int(rw_y)), int(wheel_r*1.1))

    def draw_holographic_panel(self, rect, color, label_text, value_text):
        time_ms = pygame.time.get_ticks()
        pulse = (math.sin(time_ms * 0.003) + 1) / 2
        
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (10, 10, 25, 200), s.get_rect(), border_radius=10)
        
        border_alpha = int(80 + 120 * pulse)
        border_color = (*color, border_alpha)
        pygame.draw.rect(s, border_color, s.get_rect(), width=2, border_radius=10)
        
        self.screen.blit(s, rect.topleft)
        
        cx = rect.centerx
        self.draw_neon_text(label_text, self.font, color, (cx, rect.y + 15), center=True)
        self.draw_neon_text(value_text, self.font_big, (255, 255, 255), (cx, rect.y + 45), center=True)

    def draw_panel(self):
        panel_w = 140
        panel_h = 75
        gap = 25
        
        center_x = WIN_W // 2
        
        p_rect = pygame.Rect(center_x - panel_w - panel_w//2 - gap, 12, panel_w, panel_h)
        t_rect = pygame.Rect(center_x - panel_w//2, 12, panel_w, panel_h)
        a_rect = pygame.Rect(center_x + panel_w//2 + gap, 12, panel_w, panel_h)

        self.draw_holographic_panel(p_rect, PLAYER_COLOR, "PLAYER", str(self.player_score))
        
        time_s = self.survival_time_s()
        self.draw_holographic_panel(t_rect, (180, 220, 255), "TIME", f"{time_s:0.1f}s")
        
        self.draw_holographic_panel(a_rect, AI_COLOR, "AI", str(self.ai_score))

    def draw_round_over(self):
        self.overlay_alpha = min(150.0, self.overlay_alpha + 4.0)
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.overlay_alpha)))
        self.screen.blit(overlay, (0, 0))

        if self.winner == "Tie":
            title = "TIE!"
            title_color = (220, 220, 235)
        elif self.winner == "Player":
            title = "PLAYER SCORES"
            title_color = PLAYER_COLOR
        else:
            title = "AI SCORES"
            title_color = AI_COLOR

        self.draw_neon_text(title, self.font_big, title_color, (WIN_W // 2, WIN_H // 2), center=True)

    def draw_match_over(self):
        self.overlay_alpha = min(220.0, self.overlay_alpha + 5.0)
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.overlay_alpha)))
        self.screen.blit(overlay, (0, 0))

        if self.match_winner == "Player":
            title = "PLAYER WINS THE MATCH"
            title_color = PLAYER_COLOR
        else:
            title = "AI WINS THE MATCH"
            title_color = AI_COLOR

        self.draw_neon_text(title, self.font_big, title_color, (WIN_W // 2, WIN_H // 2 - 20), center=True)
        hint = self.font.render("Press R / Space to Play Again  •  M for Menu", True, TEXT)
        self.screen.blit(hint, hint.get_rect(center=(WIN_W // 2, WIN_H // 2 + 40)))

    def draw_menu(self):
        self.draw_background()
        
        time_ms = pygame.time.get_ticks()
        pulse = (math.sin(time_ms * 0.005) + 1) / 2
        
        # Decorative Neon Border
        border_rect = pygame.Rect(15, 15, WIN_W - 30, WIN_H - 30)
        border_alpha = int(80 + 80 * pulse)
        border_surface = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, (*PLAYER_COLOR, border_alpha), border_rect, width=3, border_radius=15)
        pygame.draw.rect(border_surface, (255, 255, 255, int(border_alpha * 0.5)), border_rect, width=1, border_radius=15)
        self.screen.blit(border_surface, (0, 0))
        
        title_y = WIN_H // 2 - 20 + int(pulse * 5)
        self.draw_neon_text("TRON LIGHT CYCLE", self.font_big, PLAYER_COLOR, (WIN_W // 2, title_y), center=True)

        if self.menu_bike_img:
            rect = self.menu_bike_img.get_rect(midbottom=(WIN_W // 2, title_y - 20))
            self.screen.blit(self.menu_bike_img, rect)

        for i, opt in enumerate(self.menu_options):
            is_sel = (i == self.menu_idx)
            color = PLAYER_COLOR if is_sel else MUTED
            
            text = opt
            if opt == "Difficulty":
                text = f"Difficulty: {self.difficulty}"
            elif opt == "Trail Mode":
                text = f"Trail Mode: {self.trail_mode}"
                
            if is_sel:
                text = f"> {text} <"
                
            y_pos = WIN_H // 2 + 45 + i * 65
            if is_sel:
                r = int(PLAYER_COLOR[0] * pulse)
                g = int(PLAYER_COLOR[1] * pulse)
                b = int(PLAYER_COLOR[2] * pulse)
                pulse_color = (max(r, 100), max(g, 100), max(b, 100))
                self.draw_neon_text(text, self.font_mid, pulse_color, (WIN_W // 2, y_pos), center=True)
                
                desc = ""
                if opt == "Trail Mode":
                    if self.trail_mode == "Finite":
                        desc = "Trails fade over time"
                    else:
                        desc = "Trails remain permanently"
                
                if desc:
                    desc_surf = self.font.render(desc, True, MUTED)
                    self.screen.blit(desc_surf, desc_surf.get_rect(center=(WIN_W // 2, y_pos + 30)))
            else:
                surf = self.font_mid.render(text, True, color)
                self.screen.blit(surf, surf.get_rect(center=(WIN_W // 2, y_pos)))

    def draw(self):
        if self.state == "MENU":
            self.draw_menu()
            pygame.display.flip()
            return
            
        self.draw_background()
        self.draw_trails(self.player)
        self.draw_trails(self.ai)
        
        for p in self.particles:
            p.draw(self.screen)
            
        self.draw_panel()

        play_rect = pygame.Rect(0, PANEL_H, WIN_W, WIN_H - PANEL_H)
        pygame.draw.rect(self.screen, (255, 255, 255), play_rect, width=2)

        if self.state == "ROUND_OVER":
            self.draw_round_over()
        elif self.state == "MATCH_OVER":
            self.draw_match_over()

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.step()
            self.draw()
            self.clock.tick(FPS)
