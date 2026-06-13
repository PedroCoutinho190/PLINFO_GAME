import pygame
import random
import os


def load_image(path, size, fallback_color):
    try:
        img = pygame.image.load(os.path.join("imagens", path)).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill(fallback_color)
        return surf


# ============================================================
# CLASSES DE ENTIDADES
# ============================================================

class Planta:
    CORES = {
        "camomila": (255, 215, 0),
        "babosa":   (50, 200, 50),
        "espada":   (100, 100, 100),
    }

    def __init__(self, x, y, tipo, assets):
        self.x      = x
        self.y      = y
        self.tipo   = tipo
        self.timer  = 0
        self.assets = assets

        if tipo == "camomila":
            self.hp   = 100
            self.custo = 50
        elif tipo == "babosa":
            self.hp   = 100
            self.custo = 100
        elif tipo == "espada":
            self.hp   = 300
            self.custo = 50

        self.image = assets[tipo]

    def desenhar(self, surface, font_mini):
        surface.blit(self.image, (self.x, self.y))

        if self.tipo == "camomila":
            pygame.draw.circle(surface, (255, 215, 0), (self.x + 55, self.y + 10), 10)
            txt = font_mini.render("$", True, (0, 0, 0))
            surface.blit(txt, (self.x + 51, self.y + 4))
        elif self.tipo == "babosa":
            pygame.draw.circle(surface, (50, 200, 50), (self.x + 55, self.y + 10), 6)
            pygame.draw.circle(surface, (0, 0, 0),     (self.x + 55, self.y + 10), 6, 1)
        elif self.tipo == "espada":
            pts = [
                (self.x + 48, self.y + 2),
                (self.x + 62, self.y + 2),
                (self.x + 55, self.y + 16)
            ]
            pygame.draw.polygon(surface, (100, 150, 255), pts)
            pygame.draw.polygon(surface, (0, 0, 0), pts, 1)


class Praga:
    def __init__(self, lane, img, onda, grid_offset_y, cell_size, width):
        self.x     = width
        self.y     = grid_offset_y + lane * cell_size + 10
        self.speed = 0.4 + (onda * 0.08)
        self.hp    = 80 + (onda * 40)
        self.lane  = lane
        self.rect  = pygame.Rect(self.x, self.y, 60, 60)
        self.img   = img

    def atualizar(self):
        self.x     -= self.speed
        self.rect.x = self.x

    def desenhar(self, surface):
        surface.blit(self.img, (self.x, self.y))


class Boss:
    def __init__(self, lane, img, grid_offset_y, cell_size, width):
        self.x      = width
        self.y      = grid_offset_y + lane * cell_size - 10
        self.speed  = 0.3
        self.hp     = 1000
        self.hp_max = 1000
        self.lane   = lane
        self.rect   = pygame.Rect(self.x, self.y, 90, 90)
        self.img    = img

    def atualizar(self):
        self.x     -= self.speed
        self.rect.x = self.x

    def desenhar(self, surface, font_small):
        surface.blit(self.img, (self.x, self.y))
        barra_w = 90
        vida_w  = int(barra_w * self.hp / self.hp_max)
        pygame.draw.rect(surface, (200, 50, 50),  (self.x, self.y - 12, barra_w, 8))
        pygame.draw.rect(surface, (50, 200, 50),  (self.x, self.y - 12, vida_w,  8))
        txt = font_small.render("BOSS", True, (200, 50, 50))
        surface.blit(txt, (self.x + 30, self.y - 25))


class Projétil:
    def __init__(self, x, y, lane):
        self.x    = x
        self.y    = y
        self.speed = 5
        self.lane  = lane
        self.rect  = pygame.Rect(x, y, 15, 15)

    def atualizar(self):
        self.x    += self.speed
        self.rect.x = self.x

    def desenhar(self, surface):
        pygame.draw.circle(surface, (50, 200, 50),
                           (int(self.x + 7), int(self.y + 7)), 8)


# ============================================================
# CLASSE PRINCIPAL DO JOGO
# ============================================================

class JogoZombies:
    ROWS, COLS    = 5, 9
    CELL_SIZE     = 80
    GRID_OFFSET_X = 50
    GRID_OFFSET_Y = 150
    WIDTH, HEIGHT = 800, 600
    MAX_ONDAS     = 5

    COR = {
        "white":  (255, 255, 255),
        "green":  (50, 200, 50),
        "brown":  (139, 69, 19),
        "red":    (200, 50, 50),
        "yellow": (255, 215, 0),
        "gray":   (100, 100, 100),
        "black":  (0, 0, 0),
        "blue":   (100, 150, 255),
        "wood":   (210, 180, 140),
        "orange": (255, 140, 0),
    }

    def __init__(self, tela):
        self.tela    = tela
        self.relogio = pygame.time.Clock()

        self.font_ui    = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 20)
        self.font_mini  = pygame.font.SysFont(None, 16)
        self.font_large = pygame.font.SysFont(None, 72)

        self.pragas_imgs = {
            1: load_image("praga1.png", (60, 60), (255, 100, 100)),
            2: load_image("praga2.png", (60, 60), (220, 80,  80)),
            3: load_image("praga3.png", (60, 60), (180, 60,  60)),
            4: load_image("praga4.png", (60, 60), (140, 40,  40)),
        }
        self.boss_img = load_image("acaro.png", (90, 90), (200, 50, 50))

        self.plant_assets = {
            "camomila": load_image("camomila_estacao_dos_graos.jpg", (60, 60), (255, 215, 0)),
            "babosa":   load_image("babosa.jpg",                     (60, 60), (50, 200, 50)),
            "espada":   load_image("espada_de_sao_jorge.jpg",        (60, 60), (100, 100, 100)),
        }

        self._resetar()

    def _resetar(self):
        self.plantas          = []
        self.pragas           = []
        self.projeteis        = []
        self.planta_selecionada = None
        self.spawn_timer      = 0
        self.sun_timer        = 0
        self.spawned          = 0
        self.onda             = 1
        self.boss_spawnado    = False
        self.dinheiro         = 150
        self.estado           = "PLAYING"

    def _spawnar_praga(self):
        lane = random.randint(0, self.ROWS - 1)
        img  = self.pragas_imgs[self.onda]
        self.pragas.append(Praga(
            lane, img, self.onda,
            self.GRID_OFFSET_Y, self.CELL_SIZE, self.WIDTH
        ))
        self.spawned += 1
        self.spawn_timer = 0

    def _spawnar_boss(self):
        lane = random.randint(0, self.ROWS - 1)
        self.pragas.append(Boss(
            lane, self.boss_img,
            self.GRID_OFFSET_Y, self.CELL_SIZE, self.WIDTH
        ))
        self.boss_spawnado = True

    def _planta_em(self, px, py):
        for p in self.plantas:
            if p.x == px and p.y == py:
                return p
        return None

    def processar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and self.estado != "PLAYING":
                    self._resetar()

            if self.estado == "PLAYING" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Menu superior
                if 10 <= mouse_pos[1] <= 70:
                    if   20  <= mouse_pos[0] <= 80:  self.planta_selecionada = "camomila"
                    elif 120 <= mouse_pos[0] <= 180: self.planta_selecionada = "babosa"
                    elif 220 <= mouse_pos[0] <= 280: self.planta_selecionada = "espada"
                    elif 320 <= mouse_pos[0] <= 380: self.planta_selecionada = "pa"

                # Grid
                gx_max = self.GRID_OFFSET_X + self.COLS * self.CELL_SIZE
                gy_max = self.GRID_OFFSET_Y + self.ROWS * self.CELL_SIZE
                if (self.GRID_OFFSET_X <= mouse_pos[0] <= gx_max and
                        self.GRID_OFFSET_Y <= mouse_pos[1] <= gy_max):

                    col = (mouse_pos[0] - self.GRID_OFFSET_X) // self.CELL_SIZE
                    row = (mouse_pos[1] - self.GRID_OFFSET_Y) // self.CELL_SIZE
                    px  = self.GRID_OFFSET_X + col * self.CELL_SIZE + 10
                    py  = self.GRID_OFFSET_Y + row * self.CELL_SIZE + 10

                    existente = self._planta_em(px, py)

                    if self.planta_selecionada == "pa":
                        if existente:
                            self.plantas.remove(existente)
                            self.planta_selecionada = None

                    elif not existente and self.planta_selecionada:
                        custo = 50 if self.planta_selecionada in ["camomila", "espada"] else 100
                        if self.dinheiro >= custo:
                            self.plantas.append(
                                Planta(px, py, self.planta_selecionada, self.plant_assets)
                            )
                            self.dinheiro          -= custo
                            self.planta_selecionada = None

        return True

    def atualizar(self):
        if self.estado != "PLAYING":
            return

        # Camomila gera dinheiro
        self.sun_timer += 1
        if self.sun_timer >= 300:
            for p in self.plantas:
                if p.tipo == "camomila":
                    self.dinheiro += 20
            self.sun_timer = 0

        # Babosa atira
        for p in self.plantas:
            if p.tipo == "babosa":
                p.timer += 1
                if p.timer >= 90:
                    lane = (p.y - self.GRID_OFFSET_Y) // self.CELL_SIZE
                    self.projeteis.append(Projétil(p.x + 50, p.y + 20, lane))
                    p.timer = 0

        # Sistema de ondas
        limite = 2 + (self.onda * 3)
        tempo  = max(60, 600 - (self.onda * 100) - (self.spawned * 3))

        if self.onda < self.MAX_ONDAS and self.spawned < limite:
            self.spawn_timer += 1
            if self.spawn_timer >= tempo:
                self._spawnar_praga()

        elif self.onda < self.MAX_ONDAS and len(self.pragas) == 0:
            self.onda    += 1
            self.spawned  = 0
            self.spawn_timer = 0

        elif self.onda == self.MAX_ONDAS and not self.boss_spawnado:
            self._spawnar_boss()

        elif self.onda == self.MAX_ONDAS and self.boss_spawnado and len(self.pragas) == 0:
            self.estado = "VICTORY"

        # Atualiza pragas
        for z in self.pragas[:]:
            z.atualizar()
            if z.x < 0:
                self.estado = "GAME_OVER"
                return

            for p in self.plantas[:]:
                lane_p = (p.y - self.GRID_OFFSET_Y) // self.CELL_SIZE
                if lane_p == z.lane and z.rect.colliderect(pygame.Rect(p.x, p.y, 60, 60)):
                    z.speed = 0
                    p.hp   -= 1 + (self.onda // 2)
                    if p.hp <= 0:
                        self.plantas.remove(p)
                        z.speed = 0.3 if isinstance(z, Boss) else 0.4 + (self.onda * 0.08)
                    break

        # Atualiza projeteis
        for b in self.projeteis[:]:
            b.atualizar()
            hit = False
            for z in self.pragas[:]:
                if b.lane == z.lane and b.rect.colliderect(z.rect):
                    z.hp -= 20
                    if z.hp <= 0 and z in self.pragas:
                        self.pragas.remove(z)
                    hit = True
                    break
            if hit or b.x > self.WIDTH:
                if b in self.projeteis:
                    self.projeteis.remove(b)

    def desenhar(self):
        self.tela.fill(self.COR["brown"])

        # Grid
        for row in range(self.ROWS):
            for col in range(self.COLS):
                rect  = pygame.Rect(
                    self.GRID_OFFSET_X + col * self.CELL_SIZE,
                    self.GRID_OFFSET_Y + row * self.CELL_SIZE,
                    self.CELL_SIZE, self.CELL_SIZE
                )
                color = (60, 180, 60) if (row + col) % 2 == 0 else (50, 160, 50)
                pygame.draw.rect(self.tela, color, rect)

        # Entidades
        for p in self.plantas:
            p.desenhar(self.tela, self.font_mini)
        for z in self.pragas:
            if isinstance(z, Boss):
                z.desenhar(self.tela, self.font_small)
            else:
                z.desenhar(self.tela)
        for b in self.projeteis:
            b.desenhar(self.tela)

        # UI superior
        pygame.draw.rect(self.tela, self.COR["black"], (0, 0, self.WIDTH, 100))

        self.tela.blit(self.font_ui.render(f"Energia: {self.dinheiro}", True, self.COR["yellow"]), (630, 15))
        self.tela.blit(self.font_ui.render(f"Onda: {self.onda}/{self.MAX_ONDAS}", True, self.COR["white"]), (630, 50))

        self.tela.blit(self.plant_assets["camomila"], (20,  10))
        self.tela.blit(self.font_small.render("$50 (Gera)",   True, self.COR["white"]), (15,  75))
        self.tela.blit(self.plant_assets["babosa"],   (120, 10))
        self.tela.blit(self.font_small.render("$100 (Atira)", True, self.COR["white"]), (115, 75))
        self.tela.blit(self.plant_assets["espada"],   (220, 10))
        self.tela.blit(self.font_small.render("$50 (Escudo)", True, self.COR["white"]), (210, 75))

        pygame.draw.rect(self.tela, self.COR["brown"], (320, 10, 60, 60))
        pygame.draw.rect(self.tela, self.COR["gray"],  (340, 20, 20, 25))
        pygame.draw.rect(self.tela, self.COR["wood"],  (347, 45,  6, 20))
        self.tela.blit(self.font_small.render("Pa (Excluir)", True, self.COR["white"]), (315, 75))

        sel = self.planta_selecionada
        if sel == "camomila": pygame.draw.rect(self.tela, self.COR["white"], (20,  10, 60, 60), 3)
        elif sel == "babosa": pygame.draw.rect(self.tela, self.COR["white"], (120, 10, 60, 60), 3)
        elif sel == "espada": pygame.draw.rect(self.tela, self.COR["white"], (220, 10, 60, 60), 3)
        elif sel == "pa":     pygame.draw.rect(self.tela, self.COR["white"], (320, 10, 60, 60), 3)

        esc = self.font_small.render("ESC para voltar ao menu", True, self.COR["gray"])
        self.tela.blit(esc, (20, 108))

        if self.onda == self.MAX_ONDAS and not self.boss_spawnado:
            aviso = self.font_ui.render("BOSS CHEGANDO!", True, self.COR["red"])
            self.tela.blit(aviso, (self.WIDTH//2 - aviso.get_width()//2, 120))

        # Tela de fim
        if self.estado in ("GAME_OVER", "VICTORY"):
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(self.COR["black"])
            self.tela.blit(overlay, (0, 0))

            cor  = self.COR["red"] if self.estado == "GAME_OVER" else self.COR["green"]
            txt1 = self.font_large.render(
                "VOCE PERDEU!" if self.estado == "GAME_OVER" else "VITORIA!", True, cor)
            txt2 = self.font_ui.render("R para reiniciar | ESC para voltar", True, self.COR["white"])
            self.tela.blit(txt1, (self.WIDTH//2 - txt1.get_width()//2, self.HEIGHT//2 - 50))
            self.tela.blit(txt2, (self.WIDTH//2 - txt2.get_width()//2, self.HEIGHT//2 + 30))

    def executar(self):
        while True:
            if not self.processar_eventos():
                self._resetar()
                return
            self.atualizar()
            self.desenhar()
            pygame.display.flip()
            self.relogio.tick(60)


def rodar_pvz(tela):
    jogo = JogoZombies(tela)
    jogo.executar()