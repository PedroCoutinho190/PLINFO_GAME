import pygame
import random
import time


class Carta:
    def __init__(self, x, y, w, h, imagem, path):
        self.rect      = pygame.Rect(x, y, w, h)
        self.w         = w
        self.h         = h
        self.imagem    = imagem
        self.path      = path
        self.virada    = False
        self.encontrada = False

    def desenhar(self, surface, fonte, cor_back, cor_borda, cor_acertou):
        x, y = self.rect.x, self.rect.y
        if self.encontrada:
            pygame.draw.rect(surface, cor_acertou, self.rect, border_radius=8)
            surface.blit(self.imagem, (x + 5, y + 5))
        elif self.virada:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=8)
            pygame.draw.rect(surface, cor_borda, self.rect, 2, border_radius=8)
            surface.blit(self.imagem, (x + 5, y + 5))
        else:
            pygame.draw.rect(surface, cor_back, self.rect, border_radius=8)
            pygame.draw.rect(surface, cor_borda, self.rect, 2, border_radius=8)
            txt = fonte.render("?", True, (255, 255, 255))
            surface.blit(txt, (x + self.w//2 - txt.get_width()//2,
                               y + self.h//2 - txt.get_height()//2))

    def clicado(self, pos):
        return self.rect.collidepoint(pos)


class BotaoNivel:
    def __init__(self, x, y, w, h, texto):
        self.rect  = pygame.Rect(x, y, w, h)
        self.texto = texto

    def desenhar(self, surface, fonte, cor_botao, cor_hover):
        pos_mouse = pygame.mouse.get_pos()
        cor = cor_hover if self.rect.collidepoint(pos_mouse) else cor_botao
        pygame.draw.rect(surface, cor, self.rect, border_radius=12)
        txt = fonte.render(self.texto, True, (255, 255, 255))
        surface.blit(txt, (self.rect.centerx - txt.get_width()//2,
                           self.rect.centery - txt.get_height()//2))

    def clicado(self, evento):
        return (evento.type == pygame.MOUSEBUTTONDOWN and
                evento.button == 1 and
                self.rect.collidepoint(evento.pos))


class JogoMemoria:

    IMAGENS = [
        "imagens/alecrim.png",
        "imagens/babosa.jpg",
        "imagens/boldo.png",
        "imagens/camomila_estacao_dos_graos.jpg",
        "imagens/cidreira.png",
        "imagens/coentro.png",
        "imagens/comigo_ninguem_pode.jpg",
        "imagens/espada_de_sao_jorge.jpg",
        "imagens/guaco.png",
        "imagens/hortela.jpg",
        "imagens/lotus.jpg",
        "imagens/louro.jpg",
        "imagens/mamona.jpg",
        "imagens/manjericao.png",
        "imagens/oregano.png",
        "imagens/salsa.png",
        "imagens/tomilho.png",
        "imagens/vitoria_regia.jpg",
    ]

    COR_FUNDO       = (244, 241, 222)
    COR_TEXTO       = (61, 64, 91)
    COR_BOTAO       = (129, 178, 154)
    COR_BOTAO_HOVER = (156, 197, 178)
    COR_CARTA_BACK  = (129, 178, 154)
    COR_CARTA_BORDA = (61, 64, 91)
    COR_ACERTOU     = (82, 183, 136)
    COR_BORDA       = (190, 200, 175)

    def __init__(self, tela):
        self.tela    = tela
        self.LARGURA, self.ALTURA = tela.get_size()
        self.relogio = pygame.time.Clock()

        self.fonte_titulo  = pygame.font.SysFont("arial", 32, bold=True)
        self.fonte_info    = pygame.font.SysFont("arial", 20)
        self.fonte_pequena = pygame.font.SysFont("arial", 15)
        self.fonte_vitoria = pygame.font.SysFont("arial", 36, bold=True)

        self.btns_nivel = [
            BotaoNivel(250, 140, 300, 60, "Facil - 4 pares"),
            BotaoNivel(250, 220, 300, 60, "Medio - 6 pares"),
            BotaoNivel(250, 300, 300, 60, "Dificil - 8 pares"),
            BotaoNivel(250, 380, 300, 60, "Impossivel - 16 pares"),
        ]
        self.pares_por_nivel = [4, 6, 8, 16]

        self.num_pares     = None
        self.cartas        = []
        self.selecionadas  = []
        self.tentativas    = 0
        self.pares_achados = 0
        self.bloqueado     = False
        self.tempo_bloqueio = 0
        self.estado        = "SELECAO"

    def _carregar_cartas(self):
        num = self.num_pares
        if num <= 8:
            carta_w, carta_h, colunas = 120, 100, 4
        else:
            carta_w, carta_h, colunas = 85, 75, 6

        imagens_escolhidas = random.sample(self.IMAGENS, num)
        paths = imagens_escolhidas * 2
        random.shuffle(paths)

        total    = len(paths)
        linhas   = total // colunas
        espaco_x = (self.LARGURA - colunas * carta_w) // (colunas + 1)
        espaco_y = (self.ALTURA - 80 - linhas * carta_h) // (linhas + 1)

        self.cartas = []
        for i, path in enumerate(paths):
            col = i % colunas
            lin = i // colunas
            x   = espaco_x + col * (carta_w + espaco_x)
            y   = 80 + espaco_y + lin * (carta_h + espaco_y)
            try:
                img = pygame.image.load(path)
                img = pygame.transform.scale(img, (carta_w - 10, carta_h - 10))
            except:
                img = pygame.Surface((carta_w - 10, carta_h - 10))
                img.fill((200, 200, 200))
            self.cartas.append(Carta(x, y, carta_w, carta_h, img, path))

    def _resetar(self):
        self.selecionadas   = []
        self.tentativas     = 0
        self.pares_achados  = 0
        self.bloqueado      = False
        self.tempo_bloqueio = 0
        self.num_pares      = None
        self.cartas         = []
        self.estado         = "SELECAO"

    def processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return False

            if self.estado == "SELECAO":
                for i, btn in enumerate(self.btns_nivel):
                    if btn.clicado(evento):
                        self.num_pares = self.pares_por_nivel[i]
                        self._carregar_cartas()
                        self.estado = "JOGANDO"

            elif self.estado == "JOGANDO" and not self.bloqueado:
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for carta in self.cartas:
                        if (carta.clicado(evento.pos) and
                                not carta.virada and
                                not carta.encontrada and
                                carta not in self.selecionadas):
                            carta.virada = True
                            self.selecionadas.append(carta)
                            if len(self.selecionadas) == 2:
                                self.tentativas += 1
                                c1, c2 = self.selecionadas
                                if c1.path == c2.path:
                                    c1.encontrada = True
                                    c2.encontrada = True
                                    self.pares_achados += 1
                                    self.selecionadas   = []
                                else:
                                    self.bloqueado      = True
                                    self.tempo_bloqueio = time.time()
                            break

            elif self.estado == "VITORIA":
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    return False

        return True

    def atualizar(self):
        if self.bloqueado and time.time() - self.tempo_bloqueio > 1.0:
            for carta in self.selecionadas:
                carta.virada = False
            self.selecionadas = []
            self.bloqueado    = False

        if self.estado == "JOGANDO" and self.pares_achados == self.num_pares:
            self.estado = "VITORIA"

    def desenhar(self):
        self.tela.fill(self.COR_FUNDO)
        pygame.draw.rect(self.tela, self.COR_BORDA,
                         (15, 15, self.LARGURA-30, self.ALTURA-30), 4, border_radius=20)

        if self.estado == "SELECAO":
            titulo = self.fonte_titulo.render("Jogo da Memoria - Escolha o Nivel", True, self.COR_TEXTO)
            self.tela.blit(titulo, (self.LARGURA//2 - titulo.get_width()//2, 60))
            for btn in self.btns_nivel:
                btn.desenhar(self.tela, self.fonte_info, self.COR_BOTAO, self.COR_BOTAO_HOVER)
            esc = self.fonte_pequena.render("ESC para voltar", True, self.COR_BOTAO)
            self.tela.blit(esc, (self.LARGURA//2 - esc.get_width()//2, self.ALTURA - 40))

        elif self.estado in ("JOGANDO", "VITORIA"):
            titulo = self.fonte_titulo.render("Jogo da Memoria Botanico", True, self.COR_TEXTO)
            self.tela.blit(titulo, (self.LARGURA//2 - titulo.get_width()//2, 15))

            info = self.fonte_info.render(
                f"Pares: {self.pares_achados}/{self.num_pares}   Tentativas: {self.tentativas}",
                True, self.COR_BOTAO)
            self.tela.blit(info, (self.LARGURA//2 - info.get_width()//2, 52))

            for carta in self.cartas:
                carta.desenhar(self.tela, self.fonte_info,
                               self.COR_CARTA_BACK, self.COR_CARTA_BORDA, self.COR_ACERTOU)


            if self.estado == "VITORIA":
                pygame.draw.rect(self.tela, (255, 255, 255), (150, 220, 500, 140), border_radius=16)
                v1 = self.fonte_vitoria.render("Parabens, Completou o jogo!", True, self.COR_ACERTOU)
                v2 = self.fonte_info.render(f"Tentativas: {self.tentativas}", True, self.COR_TEXTO)
                v3 = self.fonte_pequena.render("Clique para voltar ao menu", True, self.COR_BOTAO)
                self.tela.blit(v1, (self.LARGURA//2 - v1.get_width()//2, 235))
                self.tela.blit(v2, (self.LARGURA//2 - v2.get_width()//2, 295))
                self.tela.blit(v3, (self.LARGURA//2 - v3.get_width()//2, 330))

    def executar(self):
        while True:
            if not self.processar_eventos():
                self._resetar()
                return
            self.atualizar()
            self.desenhar()
            pygame.display.flip()
            self.relogio.tick(60)


def rodar_memoria(tela):
    jogo = JogoMemoria(tela)
    jogo.executar()