import pygame
import random
import os

# ============================================================
# PALETA DE CORES GLOBAL PADRONIZADA
# ============================================================
COR_FUNDO         = (0, 0, 0) # Fundo preto solicitado
COR_TEXTO         = (44, 53, 57)
COR_SUBTITULO     = (76, 133, 119)
COR_BOTAO         = (67, 143, 114)
COR_BORDA_MOLDURA = (210, 218, 201)
COR_CERTO         = (82, 183, 136)
COR_ERRADO        = (200, 80, 80)
COR_PAINEL        = (225, 232, 215)


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
    def __init__(self, x, y, tipo, assets):
        self.x      = x
        self.y      = y
        self.tipo   = tipo
        self.timer  = 0
        self.assets = assets

        if tipo == "camomila":
            self.hp    = 100
            self.custo = 50
        elif tipo == "babosa":
            self.hp    = 100
            self.custo = 100
        elif tipo == "espada":
            self.hp    = 300
            self.custo = 50

        self.image = assets[tipo]

    def desenhar(self, surface, font_mini):
        surface.blit(self.image, (self.x, self.y))

        sombra = pygame.Surface((60, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 50), (0, 0, 60, 20))
        surface.blit(sombra, (self.x, self.y + 45))

        if self.tipo == "camomila":
            pygame.draw.circle(surface, (255, 215, 0), (self.x + 55, self.y + 10), 10)
            txt = font_mini.render("$", True, (0, 0, 0))
            surface.blit(txt, (self.x + 52, self.y + 2))
        elif self.tipo == "babosa":
            pygame.draw.circle(surface, COR_CERTO, (self.x + 55, self.y + 10), 6)
            pygame.draw.circle(surface, (0, 0, 0), (self.x + 55, self.y + 10), 6, 1)
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
        pygame.draw.rect(surface, COR_ERRADO,  (self.x, self.y - 12, barra_w, 8), border_radius=4)
        pygame.draw.rect(surface, COR_CERTO,   (self.x, self.y - 12, vida_w,  8), border_radius=4)
        txt = font_small.render("BOSS", True, COR_ERRADO)
        surface.blit(txt, (self.x + 25, self.y - 30))


class Projétil:
    def __init__(self, x, y, lane):
        self.x     = x
        self.y     = y
        self.speed = 5
        self.lane  = lane
        self.rect  = pygame.Rect(x, y, 15, 15)

    def atualizar(self):
        self.x     += self.speed
        self.rect.x = self.x

    def desenhar(self, surface):
        pygame.draw.circle(surface, COR_CERTO, (int(self.x + 7), int(self.y + 7)), 8)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 7), int(self.y + 7)), 8, 2)


# ============================================================
# CLASSE PRINCIPAL DO JOGO
# ============================================================

class JogoZombies:
    ROWS, COLS    = 5, 9
    CELL_SIZE     = 80
    GRID_OFFSET_X = 40
    GRID_OFFSET_Y = 160
    WIDTH, HEIGHT = 800, 600
    MAX_ONDAS     = 5

    def __init__(self, tela):
        self.tela    = tela
        self.relogio = pygame.time.Clock()

        self.font_ui    = pygame.font.SysFont("segoe ui", 28, bold=True)
        self.font_small = pygame.font.SysFont("segoe ui", 16, bold=True)
        self.font_mini  = pygame.font.SysFont("segoe ui", 14, bold=True)
        self.font_large = pygame.font.SysFont("cambria", 72, bold=True)

        self.pragas_imgs = {
            1: load_image("praga1.png", (60, 60), (255, 100, 100)),
            2: load_image("praga2.png", (60, 60), (220, 80,  80)),
            3: load_image("praga3.png", (60, 60), (180, 60,  60)),
            4: load_image("praga4.png", (60, 60), (140, 40,  40)),
        }
        self.boss_img = load_image("acaro.png", (90, 90), COR_ERRADO)

        self.plant_assets = {
            "camomila": load_image("camomila_estacao_dos_graos.jpg", (60, 60), (255, 215, 0)),
            "babosa":   load_image("babosa.jpg",                     (60, 60), COR_CERTO),
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
        img  = self.pragas_imgs[self.onda] if self.onda <= 4 else self.pragas_imgs[4]
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
                if 40 <= mouse_pos[1] <= 100:
                    if   50  <= mouse_pos[0] <= 110: self.planta_selecionada = "camomila"
                    elif 150 <= mouse_pos[0] <= 210: self.planta_selecionada = "babosa"
                    elif 250 <= mouse_pos[0] <= 310: self.planta_selecionada = "espada"
                    elif 350 <= mouse_pos[0] <= 410: self.planta_selecionada = "pa"

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
                            self.dinheiro -= custo
                            self.planta_selecionada = None

        return True

    def atualizar(self):
        if self.estado != "PLAYING":
            return

        self.sun_timer += 1
        if self.sun_timer >= 300:
            for p in self.plantas:
                if p.tipo == "camomila":
                    self.dinheiro += 20
            self.sun_timer = 0

        for p in self.plantas:
            if p.tipo == "babosa":
                p.timer += 1
                if p.timer >= 90:
                    lane_planta = (p.y - self.GRID_OFFSET_Y) // self.CELL_SIZE
                    tem_inimigo_na_lane = any(z.lane == lane_planta for z in self.pragas)
                    if tem_inimigo_na_lane:
                        self.projeteis.append(Projétil(p.x + 50, p.y + 20, lane_planta))
                    p.timer = 0

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
        # 1. Fundo Preto
        self.tela.fill(COR_FUNDO)

        # 2. Base de grama contínua preenchendo as laterais ("Mais grama")
        for row in range(self.ROWS):
            faixa_rect = pygame.Rect(
                10, # Inicia logo após a moldura
                self.GRID_OFFSET_Y + row * self.CELL_SIZE, 
                self.WIDTH - 20, # Vai até o outro lado
                self.CELL_SIZE
            )
            cor_faixa = (65, 145, 55) if row % 2 == 0 else (55, 135, 50)
            pygame.draw.rect(self.tela, cor_faixa, faixa_rect)

        # 3. Desenhar quadrados do Grid onde você pode plantar
        for row in range(self.ROWS):
            for col in range(self.COLS):
                rect  = pygame.Rect(
                    self.GRID_OFFSET_X + col * self.CELL_SIZE,
                    self.GRID_OFFSET_Y + row * self.CELL_SIZE,
                    self.CELL_SIZE, self.CELL_SIZE
                )
                # Tons de grama ligeiramente diferentes para destacar a área plantável
                color = (82, 175, 70) if (row + col) % 2 == 0 else (72, 160, 60)
                pygame.draw.rect(self.tela, color, rect)
                pygame.draw.rect(self.tela, (45, 125, 40), rect, 1) # Borda suave

        # 4. Entidades
        for p in self.plantas:
            p.desenhar(self.tela, self.font_mini)
        for z in self.pragas:
            if isinstance(z, Boss):
                z.desenhar(self.tela, self.font_small)
            else:
                z.desenhar(self.tela)
        for b in self.projeteis:
            b.desenhar(self.tela)

        # 5. Painel Superior
        painel_rect = pygame.Rect(30, 25, self.WIDTH - 60, 110)
        pygame.draw.rect(self.tela, COR_PAINEL, painel_rect, border_radius=15)
        pygame.draw.rect(self.tela, COR_BORDA_MOLDURA, painel_rect, 3, border_radius=15)

        self.tela.blit(self.font_ui.render(f"Energia: ${self.dinheiro}", True, (200, 150, 20)), (550, 40))
        self.tela.blit(self.font_ui.render(f"Onda: {self.onda}/{self.MAX_ONDAS}", True, COR_TEXTO), (550, 80))
        self.tela.blit(self.plant_assets["camomila"], (50,  40))
        self.tela.blit(self.font_small.render("Gera ($50)",   True, COR_TEXTO), (45,  105))
        self.tela.blit(self.plant_assets["babosa"],   (150, 40))
        self.tela.blit(self.font_small.render("Atira ($100)", True, COR_TEXTO), (145, 105))
        self.tela.blit(self.plant_assets["espada"],   (250, 40))
        self.tela.blit(self.font_small.render("Escudo ($50)", True, COR_TEXTO), (240, 105))

        pygame.draw.rect(self.tela, (182, 143, 105), (350, 40, 60, 60), border_radius=8)
        pygame.draw.rect(self.tela, (130, 130, 130), (370, 50, 20, 25))
        pygame.draw.rect(self.tela, (210, 180, 140), (377, 75, 6, 20))
        self.tela.blit(self.font_small.render("Pá (Vender)", True, COR_TEXTO), (345, 105))

        sel = self.planta_selecionada
        if sel == "camomila": pygame.draw.rect(self.tela, COR_BOTAO, (50,  40, 60, 60), 4, border_radius=4)
        elif sel == "babosa": pygame.draw.rect(self.tela, COR_BOTAO, (150, 40, 60, 60), 4, border_radius=4)
        elif sel == "espada": pygame.draw.rect(self.tela, COR_BOTAO, (250, 40, 60, 60), 4, border_radius=4)
        elif sel == "pa":     pygame.draw.rect(self.tela, COR_ERRADO, (350, 40, 60, 60), 4, border_radius=4)

        if self.onda == self.MAX_ONDAS and not self.boss_spawnado:
            aviso = self.font_large.render("BOSS CHEGANDO!", True, COR_ERRADO)
            self.tela.blit(aviso, (self.WIDTH//2 - aviso.get_width()//2, self.HEIGHT//2 - 50))

        # 6. Moldura Externa Unificada
        pygame.draw.rect(
            self.tela, COR_BORDA_MOLDURA,
            (10, 10, self.WIDTH - 20, self.HEIGHT - 20), 4, border_radius=25
        )

        # 7. Telas de Fim de Jogo
        if self.estado in ("GAME_OVER", "VICTORY"):
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
            overlay.set_alpha(190)
            overlay.fill((20, 25, 20))
            self.tela.blit(overlay, (0, 0))

            cor  = COR_ERRADO if self.estado == "GAME_OVER" else COR_CERTO
            txt1 = self.font_large.render(
                "VOCÊ PERDEU!" if self.estado == "GAME_OVER" else "VITÓRIA!", True, cor)
            txt2 = self.font_ui.render("R para reiniciar | ESC para voltar", True, (255, 255, 255))
            self.tela.blit(txt1, (self.WIDTH//2 - txt1.get_width()//2, self.HEIGHT//2 - 60))
            self.tela.blit(txt2, (self.WIDTH//2 - txt2.get_width()//2, self.HEIGHT//2 + 40))

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

if __name__ == "__main__":
    pygame.init()
    tela = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Defesa Botânica PLINFO")
    rodar_pvz(tela)
    pygame.quit()