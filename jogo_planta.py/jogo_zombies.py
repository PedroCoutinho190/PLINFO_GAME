import pygame
import random
import os

WHITE  = (255, 255, 255)
GREEN  = (50, 200, 50)
BROWN  = (139, 69, 19)
RED    = (200, 50, 50)
YELLOW = (255, 215, 0)
GRAY   = (100, 100, 100)
BLACK  = (0, 0, 0)
BLUE   = (100, 150, 255)
WOOD   = (210, 180, 140)
ORANGE = (255, 140, 0)

ROWS, COLS    = 5, 9
CELL_SIZE     = 80
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 150
WIDTH, HEIGHT = 800, 600


def load_image(path, size, fallback_color):
    try:
        img = pygame.image.load(os.path.join("imagens", path)).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill(fallback_color)
        return surf


def reset_game():
    return {
        "money": 150,
        "plants": [],
        "zombies": [],
        "bullets": [],
        "selected_plant": None,
        "zombie_spawn_timer": 0,
        "sun_timer": 0,
        "zombies_spawned": 0,
        "onda": 1,
        "boss_spawnado": False,
        "state": "PLAYING"
    }


class Plant:
    def __init__(self, x, y, p_type, assets):
        self.x      = x
        self.y      = y
        self.type   = p_type
        self.hp     = 100
        self.timer  = 0
        self.assets = assets

        if self.type == "camomila":
            self.image = assets["camomila"]
            self.cost  = 50
        elif self.type == "babosa":
            self.image = assets["babosa"]
            self.cost  = 100
        elif self.type == "espada":
            self.image = assets["espada"]
            self.hp    = 300
            self.cost  = 50

    def draw(self, surface, font_mini):
        surface.blit(self.image, (self.x, self.y))

        if self.type == "camomila":
            pygame.draw.circle(surface, YELLOW, (self.x + 55, self.y + 10), 10)
            txt = font_mini.render("$", True, BLACK)
            surface.blit(txt, (self.x + 51, self.y + 4))

        elif self.type == "babosa":
            pygame.draw.circle(surface, GREEN, (self.x + 55, self.y + 10), 6)
            pygame.draw.circle(surface, BLACK, (self.x + 55, self.y + 10), 6, 1)

        elif self.type == "espada":
            pts = [
                (self.x + 48, self.y + 2),
                (self.x + 62, self.y + 2),
                (self.x + 55, self.y + 16)
            ]
            pygame.draw.polygon(surface, BLUE, pts)
            pygame.draw.polygon(surface, BLACK, pts, 1)


class Zombie:
    def __init__(self, lane, img, onda):
        self.x     = WIDTH
        self.y     = GRID_OFFSET_Y + lane * CELL_SIZE + 10
        self.speed = 0.4 + (onda * 0.08)   # ← cresce mais devagar
        self.hp    = 80 + (onda * 40)       # ← mais balanceado
        self.lane  = lane
        self.rect  = pygame.Rect(self.x, self.y, 60, 60)
        self.img   = img

    def update(self):
        self.x     -= self.speed
        self.rect.x = self.x

    def draw(self, surface):
        surface.blit(self.img, (self.x, self.y))


class Boss:
    def __init__(self, lane, boss_img):
        self.x      = WIDTH
        self.y      = GRID_OFFSET_Y + lane * CELL_SIZE - 10
        self.speed  = 0.3
        self.hp     = 1000
        self.hp_max = 1000
        self.lane   = lane
        self.rect   = pygame.Rect(self.x, self.y, 90, 90)
        self.img    = boss_img

    def update(self):
        self.x     -= self.speed
        self.rect.x = self.x

    def draw(self, surface, font_small):
        surface.blit(self.img, (self.x, self.y))
        barra_w = 90
        vida_w  = int(barra_w * self.hp / self.hp_max)
        pygame.draw.rect(surface, RED,   (self.x, self.y - 12, barra_w, 8))
        pygame.draw.rect(surface, GREEN, (self.x, self.y - 12, vida_w,  8))
        txt = font_small.render("BOSS", True, RED)
        surface.blit(txt, (self.x + 30, self.y - 25))


class Bullet:
    def __init__(self, x, y, lane):
        self.x     = x
        self.y     = y
        self.speed = 5
        self.lane  = lane
        self.rect  = pygame.Rect(self.x, self.y, 15, 15)

    def update(self):
        self.x    += self.speed
        self.rect.x = self.x

    def draw(self, surface):
        pygame.draw.circle(surface, GREEN, (int(self.x + 7), int(self.y + 7)), 8)


def rodar_pvz(tela):

    clock      = pygame.time.Clock()
    font_ui    = pygame.font.SysFont(None, 36)
    font_small = pygame.font.SysFont(None, 20)
    font_mini  = pygame.font.SysFont(None, 16)
    font_large = pygame.font.SysFont(None, 72)

    # ← imagem diferente por onda
    pragas_imgs = {
        1: load_image("praga1.png", (60, 60), (255, 100, 100)),
        2: load_image("praga2.png", (60, 60), (220, 80,  80)),
        3: load_image("praga3.png", (60, 60), (180, 60,  60)),
        4: load_image("praga4.png", (60, 60), (140, 40,  40)),
    }
    boss_img = load_image("acaro.png", (90, 90), RED)

    plant_assets = {
        "camomila": load_image("camomila_estacao_dos_graos.jpg", (60, 60), YELLOW),
        "babosa":   load_image("babosa.jpg",                     (60, 60), GREEN),
        "espada":   load_image("espada_de_sao_jorge.jpg",        (60, 60), GRAY)
    }

    game_data = reset_game()
    running   = True

    while running:
        tela.fill(BROWN)

        for row in range(ROWS):
            for col in range(COLS):
                rect  = pygame.Rect(
                    GRID_OFFSET_X + col * CELL_SIZE,
                    GRID_OFFSET_Y + row * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                color = (60, 180, 60) if (row + col) % 2 == 0 else (50, 160, 50)
                pygame.draw.rect(tela, color, rect)

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

            if game_data["state"] == "PLAYING":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    if 10 <= mouse_pos[1] <= 70:
                        if   20  <= mouse_pos[0] <= 80:  game_data["selected_plant"] = "camomila"
                        elif 120 <= mouse_pos[0] <= 180: game_data["selected_plant"] = "babosa"
                        elif 220 <= mouse_pos[0] <= 280: game_data["selected_plant"] = "espada"
                        elif 320 <= mouse_pos[0] <= 380: game_data["selected_plant"] = "pa"

                    if (GRID_OFFSET_X <= mouse_pos[0] <= GRID_OFFSET_X + COLS * CELL_SIZE and
                            GRID_OFFSET_Y <= mouse_pos[1] <= GRID_OFFSET_Y + ROWS * CELL_SIZE):

                        col = (mouse_pos[0] - GRID_OFFSET_X) // CELL_SIZE
                        row = (mouse_pos[1] - GRID_OFFSET_Y) // CELL_SIZE
                        px  = GRID_OFFSET_X + col * CELL_SIZE + 10
                        py  = GRID_OFFSET_Y + row * CELL_SIZE + 10

                        plant_exists = None
                        for p in game_data["plants"]:
                            if p.x == px and p.y == py:
                                plant_exists = p
                                break

                        if game_data["selected_plant"] == "pa":
                            if plant_exists:
                                game_data["plants"].remove(plant_exists)
                                game_data["selected_plant"] = None

                        elif not plant_exists and game_data["selected_plant"]:
                            cost = 50 if game_data["selected_plant"] in ["camomila", "espada"] else 100
                            if game_data["money"] >= cost:
                                game_data["plants"].append(
                                    Plant(px, py, game_data["selected_plant"], plant_assets)
                                )
                                game_data["money"]         -= cost
                                game_data["selected_plant"] = None

            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    game_data = reset_game()

        if game_data["state"] == "PLAYING":

            # Camomila gera dinheiro
            game_data["sun_timer"] += 1
            if game_data["sun_timer"] >= 300:
                for p in game_data["plants"]:
                    if p.type == "camomila":
                        game_data["money"] += 20
                game_data["sun_timer"] = 0

            # Babosa atira
            for p in game_data["plants"]:
                if p.type == "babosa":
                    p.timer += 1
                    if p.timer >= 90:
                        lane = (p.y - GRID_OFFSET_Y) // CELL_SIZE
                        game_data["bullets"].append(Bullet(p.x + 50, p.y + 20, lane))
                        p.timer = 0

            onda        = game_data["onda"]
            limite_onda = 2 + (onda * 3)
            tempo_spawn = max(60, 600 - (onda * 100) - (game_data["zombies_spawned"] * 3))

            if onda < 5 and game_data["zombies_spawned"] < limite_onda:
                game_data["zombie_spawn_timer"] += 1
                if game_data["zombie_spawn_timer"] >= tempo_spawn:
                    lane     = random.randint(0, ROWS - 1)
                    img_praga = pragas_imgs[onda]  # ← imagem da onda atual
                    game_data["zombies"].append(Zombie(lane, img_praga, onda))
                    game_data["zombies_spawned"] += 1
                    game_data["zombie_spawn_timer"] = 0

            elif onda < 5 and len(game_data["zombies"]) == 0:
                game_data["onda"]               += 1
                game_data["zombies_spawned"]      = 0
                game_data["zombie_spawn_timer"]   = 0

            elif onda == 5 and not game_data["boss_spawnado"]:
                lane = random.randint(0, ROWS - 1)
                game_data["zombies"].append(Boss(lane, boss_img))
                game_data["boss_spawnado"] = True

            elif onda == 5 and game_data["boss_spawnado"] and len(game_data["zombies"]) == 0:
                game_data["state"] = "VICTORY"

            for z in game_data["zombies"][:]:
                z.update()
                if z.x < 0:
                    game_data["state"] = "GAME_OVER"

                for p in game_data["plants"][:]:
                    lane_p = (p.y - GRID_OFFSET_Y) // CELL_SIZE
                    if lane_p == z.lane and z.rect.colliderect(pygame.Rect(p.x, p.y, 60, 60)):
                        z.speed  = 0
                        p.hp    -= 1 + (onda // 2)  # ← dano aumenta por onda
                        if p.hp <= 0:
                            game_data["plants"].remove(p)
                            z.speed = 0.3 if isinstance(z, Boss) else 0.4 + (onda * 0.08)
                        break

            for b in game_data["bullets"][:]:
                b.update()
                hit = False
                for z in game_data["zombies"][:]:
                    if b.lane == z.lane and b.rect.colliderect(z.rect):
                        z.hp -= 20
                        if z.hp <= 0 and z in game_data["zombies"]:
                            game_data["zombies"].remove(z)
                        hit = True
                        break
                if hit or b.x > WIDTH:
                    if b in game_data["bullets"]:
                        game_data["bullets"].remove(b)

        for p in game_data["plants"]:
            p.draw(tela, font_mini)
        for z in game_data["zombies"]:
            if isinstance(z, Boss):
                z.draw(tela, font_small)
            else:
                z.draw(tela)
        for b in game_data["bullets"]:
            b.draw(tela)

        pygame.draw.rect(tela, BLACK, (0, 0, WIDTH, 100))

        money_text = font_ui.render(f"Energia: {game_data['money']}", True, YELLOW)
        horda_text = font_ui.render(f"Onda: {game_data['onda']}/5",   True, WHITE)
        tela.blit(money_text, (630, 15))
        tela.blit(horda_text, (630, 50))

        tela.blit(plant_assets["camomila"], (20,  10))
        tela.blit(font_small.render("$50 (Gera)",   True, WHITE), (15,  75))
        tela.blit(plant_assets["babosa"],   (120, 10))
        tela.blit(font_small.render("$100 (Atira)", True, WHITE), (115, 75))
        tela.blit(plant_assets["espada"],   (220, 10))
        tela.blit(font_small.render("$50 (Escudo)", True, WHITE), (210, 75))

        pygame.draw.rect(tela, BROWN, (320, 10, 60, 60))
        pygame.draw.rect(tela, GRAY,  (340, 20, 20, 25))
        pygame.draw.rect(tela, WOOD,  (347, 45,  6, 20))
        tela.blit(font_small.render("Pa (Excluir)", True, WHITE), (315, 75))

        sel = game_data["selected_plant"]
        if sel == "camomila": pygame.draw.rect(tela, WHITE, (20,  10, 60, 60), 3)
        elif sel == "babosa": pygame.draw.rect(tela, WHITE, (120, 10, 60, 60), 3)
        elif sel == "espada": pygame.draw.rect(tela, WHITE, (220, 10, 60, 60), 3)
        elif sel == "pa":     pygame.draw.rect(tela, WHITE, (320, 10, 60, 60), 3)

        esc = font_small.render("ESC para voltar ao menu", True, GRAY)
        tela.blit(esc, (20, 108))

        if game_data["onda"] == 5 and not game_data["boss_spawnado"]:
            aviso = font_ui.render("BOSS CHEGANDO!", True, RED)
            tela.blit(aviso, (WIDTH//2 - aviso.get_width()//2, 120))

        if game_data["state"] in ("GAME_OVER", "VICTORY"):
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            tela.blit(overlay, (0, 0))

            txt1 = font_large.render("VOCE PERDEU!", True, RED) if game_data["state"] == "GAME_OVER" else font_large.render("VITORIA!", True, GREEN)
            txt2 = font_ui.render("Pressione R para reiniciar | ESC para voltar", True, WHITE)
            tela.blit(txt1, (WIDTH//2 - txt1.get_width()//2, HEIGHT//2 - 50))
            tela.blit(txt2, (WIDTH//2 - txt2.get_width()//2, HEIGHT//2 + 30))

        pygame.display.flip()
        clock.tick(60)