import pygame
import random
import time

LARGURA, ALTURA = 800, 600

COR_FUNDO       = (244, 241, 222)
COR_TEXTO       = (61, 64, 91)
COR_BOTAO       = (129, 178, 154)
COR_BOTAO_HOVER = (156, 197, 178)
COR_CARTA_BACK  = (129, 178, 154)
COR_CARTA_BORDA = (61, 64, 91)
COR_ACERTOU     = (82, 183, 136)
COR_ERROU       = (224, 122, 95)
COR_BORDA       = (190, 200, 175)

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


def rodar_memoria(tela):

    fonte_titulo  = pygame.font.SysFont("arial", 32, bold=True)
    fonte_info    = pygame.font.SysFont("arial", 20)
    fonte_pequena = pygame.font.SysFont("arial", 15)
    fonte_vitoria = pygame.font.SysFont("arial", 36, bold=True)

    class BotaoNivel:
        def __init__(self, x, y, w, h, texto):
            self.rect  = pygame.Rect(x, y, w, h)
            self.texto = texto

        def desenhar(self, surface):
            pos_mouse = pygame.mouse.get_pos()
            cor = COR_BOTAO_HOVER if self.rect.collidepoint(pos_mouse) else COR_BOTAO
            pygame.draw.rect(surface, cor, self.rect, border_radius=12)
            txt = fonte_info.render(self.texto, True, (255, 255, 255))
            surface.blit(txt, (self.rect.centerx - txt.get_width()//2,
                               self.rect.centery - txt.get_height()//2))

        def clicado(self, evento):
            return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(evento.pos)

    btn_facil      = BotaoNivel(250, 140, 300, 60, "Facil - 4 pares")
    btn_medio      = BotaoNivel(250, 220, 300, 60, "Medio - 6 pares")
    btn_dificil    = BotaoNivel(250, 300, 300, 60, "Dificil - 8 pares")
    btn_impossivel = BotaoNivel(250, 380, 300, 60, f"Impossivel - {len(IMAGENS)} pares")

    num_pares = None
    relogio   = pygame.time.Clock()

    while num_pares is None:
        tela.fill(COR_FUNDO)
        pygame.draw.rect(tela, COR_BORDA, (15, 15, LARGURA-30, ALTURA-30), 4, border_radius=20)

        titulo = fonte_titulo.render("Jogo da Memoria - Escolha o Nivel", True, COR_TEXTO)
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 60))

        btn_facil.desenhar(tela)
        btn_medio.desenhar(tela)
        btn_dificil.desenhar(tela)
        btn_impossivel.desenhar(tela)

        esc = fonte_pequena.render("ESC para voltar", True, COR_BOTAO)
        tela.blit(esc, (LARGURA//2 - esc.get_width()//2, ALTURA - 40))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return
            if btn_facil.clicado(evento):
                num_pares = 4
            elif btn_medio.clicado(evento):
                num_pares = 6
            elif btn_dificil.clicado(evento):
                num_pares = 8
            elif btn_impossivel.clicado(evento):
                num_pares = len(IMAGENS)

        pygame.display.flip()
        relogio.tick(60)

    # =====================
    # TAMANHO DAS CARTAS
    # =====================
    if num_pares <= 8:
        carta_w = 120
        carta_h = 100
        colunas = 4
    else:
        carta_w = 85
        carta_h = 75
        colunas = 6

    # =====================
    # PREPARAR CARTAS
    # =====================
    imagens_escolhidas = random.sample(IMAGENS, num_pares)

    imagens_carregadas = {}
    for path in imagens_escolhidas:
        try:
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (carta_w - 10, carta_h - 10))
            imagens_carregadas[path] = img
        except:
            surf = pygame.Surface((carta_w - 10, carta_h - 10))
            surf.fill((200, 200, 200))
            imagens_carregadas[path] = surf

    cartas = imagens_escolhidas * 2
    random.shuffle(cartas)

    total    = len(cartas)
    linhas   = total // colunas
    espaco_x = (LARGURA - colunas * carta_w) // (colunas + 1)
    espaco_y = (ALTURA - 80 - linhas * carta_h) // (linhas + 1)

    posicoes = []
    for i in range(total):
        col = i % colunas
        lin = i // colunas
        x   = espaco_x + col * (carta_w + espaco_x)
        y   = 80 + espaco_y + lin * (carta_h + espaco_y)
        posicoes.append((x, y))

    viradas        = [False] * total
    encontradas    = [False] * total
    selecionadas   = []
    tentativas     = 0
    pares_achados  = 0
    bloqueado      = False
    tempo_bloqueio = 0

    def desenhar_carta(i):
        x, y = posicoes[i]
        if encontradas[i]:
            pygame.draw.rect(tela, COR_ACERTOU, (x, y, carta_w, carta_h), border_radius=8)
            tela.blit(imagens_carregadas[cartas[i]], (x + 5, y + 5))
        elif viradas[i]:
            pygame.draw.rect(tela, (255, 255, 255), (x, y, carta_w, carta_h), border_radius=8)
            pygame.draw.rect(tela, COR_CARTA_BORDA, (x, y, carta_w, carta_h), 2, border_radius=8)
            tela.blit(imagens_carregadas[cartas[i]], (x + 5, y + 5))
        else:
            pygame.draw.rect(tela, COR_CARTA_BACK, (x, y, carta_w, carta_h), border_radius=8)
            pygame.draw.rect(tela, COR_CARTA_BORDA, (x, y, carta_w, carta_h), 2, border_radius=8)
            txt = fonte_info.render("?", True, (255, 255, 255))
            tela.blit(txt, (x + carta_w//2 - txt.get_width()//2,
                            y + carta_h//2 - txt.get_height()//2))

    # =====================
    # LOOP DO JOGO
    # =====================
    while True:
        tela.fill(COR_FUNDO)
        pygame.draw.rect(tela, COR_BORDA, (15, 15, LARGURA-30, ALTURA-30), 4, border_radius=20)

        if bloqueado and time.time() - tempo_bloqueio > 1.0:
            for i in selecionadas:
                viradas[i] = False
            selecionadas = []
            bloqueado    = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and not bloqueado:
                mx, my = evento.pos
                for i, (x, y) in enumerate(posicoes):
                    if x <= mx <= x + carta_w and y <= my <= y + carta_h:
                        if not viradas[i] and not encontradas[i] and i not in selecionadas:
                            viradas[i] = True
                            selecionadas.append(i)

                            if len(selecionadas) == 2:
                                tentativas += 1
                                i1, i2 = selecionadas
                                if cartas[i1] == cartas[i2]:
                                    encontradas[i1] = True
                                    encontradas[i2] = True
                                    pares_achados   += 1
                                    selecionadas     = []
                                else:
                                    bloqueado      = True
                                    tempo_bloqueio = time.time()
                        break

        titulo = fonte_titulo.render("Jogo da Memoria Botanico", True, COR_TEXTO)
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 15))

        info = fonte_info.render(f"Pares: {pares_achados}/{num_pares}   Tentativas: {tentativas}", True, COR_BOTAO)
        tela.blit(info, (LARGURA//2 - info.get_width()//2, 52))

        for i in range(total):
            desenhar_carta(i)

        if pares_achados == num_pares:
            pygame.draw.rect(tela, (255, 255, 255), (150, 220, 500, 140), border_radius=16)
            v1 = fonte_vitoria.render("Parabens! Completou o jogo!", True, COR_ACERTOU)
            v2 = fonte_info.render(f"Tentativas: {tentativas}", True, COR_TEXTO)
            v3 = fonte_pequena.render("Clique ESC para voltar ao menu", True, COR_BOTAO)
            tela.blit(v1, (LARGURA//2 - v1.get_width()//2, 235))
            tela.blit(v2, (LARGURA//2 - v2.get_width()//2, 295))
            tela.blit(v3, (LARGURA//2 - v3.get_width()//2, 330))

            for ev in pygame.event.get():
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    return

        esc = fonte_pequena.render("ESC para voltar", True, COR_BOTAO)
        tela.blit(esc, (20, ALTURA - 25))

        pygame.display.flip()
        relogio.tick(60)