import pygame
from jogo_planta import rodar_quiz
from jogo_memoria import rodar_memoria
from jogo_zombies import rodar_pvz
from jogo_defesa import rodar_proteja_planta

pygame.init()
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogos Botanicos - PLINFO")

# Paleta de Cores
COR_FUNDO       = (244, 241, 222)
COR_TEXTO       = (61, 64, 91)
COR_BOTAO       = (129, 178, 154)
COR_BOTAO_HOVER = (156, 197, 178)
COR_BORDA       = (190, 200, 175) 

fonte_titulo    = pygame.font.SysFont("arial", 48, bold=True)
fonte_subtitulo = pygame.font.SysFont("arial", 24)
fonte_botao     = pygame.font.SysFont("arial", 22, bold=True)


class Botao:
    def __init__(self, x, y, largura, altura, texto):
        self.rect  = pygame.Rect(x, y, largura, altura)
        self.texto = texto

    def desenhar(self, surface):
        pos_mouse = pygame.mouse.get_pos()
        cor = COR_BOTAO_HOVER if self.rect.collidepoint(pos_mouse) else COR_BOTAO
        pygame.draw.rect(surface, cor, self.rect, border_radius=12)
        texto_surface = fonte_botao.render(self.texto, True, (255, 255, 255))
        texto_rect    = texto_surface.get_rect(center=self.rect.center)
        surface.blit(texto_surface, texto_rect)

    def verificar_clique(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                return True
        return False


btn_quiz      = Botao(250, 180, 300, 70, "Quiz Botanico")
btn_memoria   = Botao(250, 270, 300, 70, "Jogo da Memoria")
btn_regar     = Botao(250, 360, 300, 70, "Proteja a Planta")
btn_adivinhar = Botao(250, 450, 300, 70, "Defenda a Torre")

estado  = "MENU_JOGOS"
relogio = pygame.time.Clock()
rodando = True


while rodando:
    tela.fill(COR_FUNDO)

    # --- DESENHO DA BORDA ---
    pygame.draw.rect(tela, COR_BORDA, (15, 15, LARGURA-30, ALTURA-30), 4, border_radius=20)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if estado == "MENU_JOGOS":
            if btn_quiz.verificar_clique(evento):
                rodar_quiz(tela)
            elif btn_memoria.verificar_clique(evento):
                rodar_memoria(tela)
            elif btn_regar.verificar_clique(evento):
                rodar_proteja_planta(tela)
            elif btn_adivinhar.verificar_clique(evento):
                rodar_pvz(tela)

        elif estado == "REGAR":
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                estado = "MENU_JOGOS"

        elif estado == "ADIVINHAR":
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                estado = "MENU_JOGOS"

    if estado == "MENU_JOGOS":
        titulo = fonte_titulo.render("PLINFO Games", True, COR_TEXTO)
        sub    = fonte_subtitulo.render("Escolha um jogo para jogar!", True, COR_BOTAO)
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 80))
        tela.blit(sub,    (LARGURA//2 - sub.get_width()//2,    140))
        btn_quiz.desenhar(tela)
        btn_memoria.desenhar(tela)
        btn_regar.desenhar(tela)
        btn_adivinhar.desenhar(tela)

    elif estado == "REGAR":
        msg = fonte_subtitulo.render("Em desenvolvimento! ESC para voltar", True, COR_TEXTO)
        tela.blit(msg, (LARGURA//2 - msg.get_width()//2, 280))

    elif estado == "ADIVINHAR":
        msg = fonte_subtitulo.render("Em desenvolvimento! ESC para voltar", True, COR_TEXTO)
        tela.blit(msg, (LARGURA//2 - msg.get_width()//2, 280))

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()