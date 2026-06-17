import pygame
import random
import time


class Carta:
    def __init__(self, x, y, w, h, imagem, path):
        self.rect       = pygame.Rect(x, y, w, h)
        self.w          = w
        self.h          = h
        self.imagem     = imagem
        self.path       = path
        self.virada     = False
        self.encontrada = False

    def desenhar(self, surface, fonte, cor_back, cor_borda, cor_acertou):
        x, y = self.rect.x, self.rect.y
        if self.encontrada:
            pygame.draw.rect(surface, cor_acertou, self.rect, border_radius=12)
            surface.blit(self.imagem, (x + 5, y + 5))
        elif self.virada:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=12)
            pygame.draw.rect(surface, cor_borda, self.rect, 2, border_radius=12)
            surface.blit(self.imagem, (x + 5, y + 5))
        else:
            # Verso da carta com a cor do botão e uma bordinha branca interna para dar charme
            pygame.draw.rect(surface, cor_back, self.rect, border_radius=12)
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 1, border_radius=12)
            txt = fonte.render("?", True, (255, 255, 255))
            surface.blit(txt, (x + self.w//2 - txt.get_width()//2,
                               y + self.h//2 - txt.get_height()//2))

    def clicado(self, pos):
        return self.rect.collidepoint(pos)


class BotaoNivel:
    def __init__(self, x, y, largura, altura, texto):
        self.rect_original = pygame.Rect(x, y, largura, altura)
        # Rect dinâmico para o efeito de "afundar"
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto

    def desenhar(self, tela, fonte, cor_base, cor_hover, cor_sombra):
        mouse = pygame.mouse.get_pos()
        
        # Efeito hover: afunda 3 pixels
        if self.rect_original.collidepoint(mouse):
            cor_atual = cor_hover
            self.rect.y = self.rect_original.y + 3
        else:
            cor_atual = cor_base
            self.rect.y = self.rect_original.y

        # 1. Sombra do Botão
        sombra_rect = pygame.Rect(self.rect_original.x, self.rect_original.y + 5, self.rect_original.width, self.rect_original.height)
        pygame.draw.rect(tela, cor_sombra, sombra_rect, border_radius=14)

        # 2. Botão Principal
        pygame.draw.rect(tela, cor_atual, self.rect, border_radius=14)
        
        # 3. Borda interna
        pygame.draw.rect(tela, (255, 255, 255), self.rect, width=1, border_radius=14)

        # 4. Texto
        texto_surface = fonte.render(self.texto, True, (255, 255, 255))
        tela.blit(texto_surface, texto_surface.get_rect(center=self.rect.center))

    def clicou(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.rect_original.collidepoint(evento.pos)
        return False


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

    # --- CORES IDÊNTICAS ÀS DO MENU ---
    COR_FUNDO         = (240, 242, 235)  # Bege claro natural
    COR_TEXTO         = (44, 53, 57)     # Cinza/Verde musgo para títulos
    COR_SUBTITULO     = (76, 133, 119)   # Verde intermediário
    COR_BOTAO         = (67, 143, 114)   # Verde folha vivo
    COR_HOVER         = (82, 171, 137)   # Verde brilhante hover
    COR_SOMBRA        = (41, 92, 73)     # Sombra
    COR_BORDA_MOLDURA = (210, 218, 201)  # Borda suave

    def __init__(self, tela):
        self.tela    = tela
        self.LARGURA, self.ALTURA = tela.get_size()
        self.relogio = pygame.time.Clock()

        # --- FONTES IDÊNTICAS ÀS DO MENU ---
        self.fonte_titulo    = pygame.font.SysFont("cambria", 42, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("calibri", 24, italic=True)
        self.fonte_botao     = pygame.font.SysFont("segoe ui", 22, bold=True)
        self.fonte_interroga = pygame.font.SysFont("segoe ui", 36, bold=True)
        self.fonte_pequena   = pygame.font.SysFont("segoe ui", 16, bold=True)

        # Botões centralizados conforme a largura da tela
        largura_btn = 320
        altura_btn = 60
        x_btn = (self.LARGURA // 2) - (largura_btn // 2)

        self.btns_nivel = [
            BotaoNivel(x_btn, 170, largura_btn, altura_btn, "Fácil - 4 pares"),
            BotaoNivel(x_btn, 250, largura_btn, altura_btn, "Médio - 6 pares"),
            BotaoNivel(x_btn, 330, largura_btn, altura_btn, "Difícil - 8 pares"),
            BotaoNivel(x_btn, 410, largura_btn, altura_btn, "Impossível - 15 pares"),
        ]
        self.pares_por_nivel = [4, 6, 8, 15]

        self.num_pares      = None
        self.cartas         = []
        self.selecionadas   = []
        self.tentativas     = 0
        self.pares_achados  = 0
        self.bloqueado      = False
        self.tempo_bloqueio = 0
        self.estado         = "SELECAO"

    def _carregar_cartas(self):
        num = self.num_pares
        
        # Ajuste dinâmico de tamanhos para evitar que vazem a tela
        if num <= 4:
            carta_w, carta_h, colunas = 120, 100, 4
        elif num <= 6:
            carta_w, carta_h, colunas = 100, 95, 4
        elif num <= 8:
            carta_w, carta_h, colunas = 90, 85, 4
        else:
            carta_w, carta_h, colunas = 70, 70, 6

        imagens_escolhidas = random.sample(self.IMAGENS, num)
        paths = imagens_escolhidas * 2
        random.shuffle(paths)

        total    = len(paths)
        linhas   = total // colunas
        
        # Margens protegidas
        offset_y_titulo = 125  # Espaço para título e subtítulo em cima
        margem_fundo = 40      # Espaço garantido na parte de baixo da tela
        
        espaco_x = (self.LARGURA - colunas * carta_w) // (colunas + 1)
        espaco_y = (self.ALTURA - offset_y_titulo - margem_fundo - linhas * carta_h) // (linhas + 1)

        self.cartas = []
        for i, path in enumerate(paths):
            col = i % colunas
            lin = i // colunas
            x   = espaco_x + col * (carta_w + espaco_x)
            y   = offset_y_titulo + espaco_y + lin * (carta_h + espaco_y)
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
                    if btn.clicou(evento):
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
        
        # Moldura externa elegante (Igual ao menu)
        pygame.draw.rect(self.tela, self.COR_BORDA_MOLDURA,
                         (20, 20, self.LARGURA - 40, self.ALTURA - 40), 3, border_radius=25)

        if self.estado == "SELECAO":
            # Título e Subtítulo
            titulo = self.fonte_titulo.render("Jogo da Memória", True, self.COR_TEXTO)
            subtitulo = self.fonte_subtitulo.render("Escolha o nível de dificuldade", True, self.COR_SUBTITULO)
            
            self.tela.blit(titulo, (self.LARGURA//2 - titulo.get_width()//2, 60))
            self.tela.blit(subtitulo, (self.LARGURA//2 - subtitulo.get_width()//2, 110))

            # Desenha os Botões 3D
            for btn in self.btns_nivel:
                btn.desenhar(self.tela, self.fonte_botao, self.COR_BOTAO, self.COR_HOVER, self.COR_SOMBRA)
                
            esc = self.fonte_pequena.render("Pressione ESC para voltar ao menu", True, self.COR_SUBTITULO)
            self.tela.blit(esc, (self.LARGURA//2 - esc.get_width()//2, self.ALTURA - 60))

        elif self.estado in ("JOGANDO", "VITORIA"):
            # Cabeçalho durante o jogo
            titulo = self.fonte_titulo.render("Memória Botânica", True, self.COR_TEXTO)
            self.tela.blit(titulo, (self.LARGURA//2 - titulo.get_width()//2, 35))

            info = self.fonte_subtitulo.render(
                f"Pares Encontrados: {self.pares_achados}/{self.num_pares}   |   Tentativas: {self.tentativas}",
                True, self.COR_SUBTITULO)
            self.tela.blit(info, (self.LARGURA//2 - info.get_width()//2, 85))

            for carta in self.cartas:
                carta.desenhar(self.tela, self.fonte_interroga,
                               self.COR_BOTAO, self.COR_TEXTO, self.COR_HOVER)

            if self.estado == "VITORIA":
                # Fundo da caixa de vitória
                caixa_rect = pygame.Rect(150, 220, 500, 160)
                pygame.draw.rect(self.tela, self.COR_FUNDO, caixa_rect, border_radius=16)
                pygame.draw.rect(self.tela, self.COR_BOTAO, caixa_rect, 4, border_radius=16)
                
                v1 = self.fonte_titulo.render("Você Venceu!", True, self.COR_TEXTO)
                v2 = self.fonte_botao.render(f"Finalizado em {self.tentativas} tentativas", True, self.COR_SUBTITULO)
                v3 = self.fonte_pequena.render("Clique em qualquer lugar para voltar ao menu", True, self.COR_SOMBRA)
                
                self.tela.blit(v1, (self.LARGURA//2 - v1.get_width()//2, 240))
                self.tela.blit(v2, (self.LARGURA//2 - v2.get_width()//2, 300))
                self.tela.blit(v3, (self.LARGURA//2 - v3.get_width()//2, 345))

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