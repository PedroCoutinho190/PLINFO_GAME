import pygame
from jogo_planta import rodar_quiz
from jogo_memoria import rodar_memoria
from jogo_zombies import rodar_pvz
from jogo_defesa import rodar_proteja_planta

pygame.init()

class Botao:
    def __init__(self, x, y, largura, altura, texto):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto

    def desenhar(self, tela, fonte, cor, hover):
        mouse = pygame.mouse.get_pos()
        cor_atual = hover if self.rect.collidepoint(mouse) else cor

        pygame.draw.rect(tela, cor_atual, self.rect, border_radius=12)

        texto = fonte.render(self.texto, True, (255,255,255))
        tela.blit(texto, texto.get_rect(center=self.rect.center))

    def clicou(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.rect.collidepoint(evento.pos)
        return False

class MenuJogos:
    def __init__(self):
        self.LARGURA = 800
        self.ALTURA = 600

        self.tela = pygame.display.set_mode((self.LARGURA,self.ALTURA))
        pygame.display.set_caption("Jogos Botanicos - PLINFO")

        self.COR_FUNDO = (244,241,222)
        self.COR_TEXTO = (61,64,91)
        self.COR_BOTAO = (129,178,154)
        self.COR_HOVER = (156,197,178)
        self.COR_BORDA = (190,200,175)

        self.fonte_titulo = pygame.font.SysFont("arial",48,bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("arial",24)
        self.fonte_botao = pygame.font.SysFont("arial",22,bold=True)

        self.criar_botoes()

        self.rodando = True
        self.relogio = pygame.time.Clock()

    def criar_botoes(self):
        self.btn_quiz = Botao(250,180,300,70,"Quiz Botanico")
        self.btn_memoria = Botao(250,270,300,70,"Jogo da Memoria")
        self.btn_proteger = Botao(250,360,300,70,"Proteja a Planta")
        self.btn_zombie = Botao(250,450,300,70,"Defenda a Torre")

        self.botoes = [
            self.btn_quiz,
            self.btn_memoria,
            self.btn_proteger,
            self.btn_zombie
        ]

    def eventos(self):
        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                self.rodando = False

            if self.btn_quiz.clicou(evento):
                rodar_quiz(self.tela)

            elif self.btn_memoria.clicou(evento):
                rodar_memoria(self.tela)

            elif self.btn_proteger.clicou(evento):
                rodar_proteja_planta(self.tela)

            elif self.btn_zombie.clicou(evento):
                rodar_pvz(self.tela)

    def desenhar(self):
        self.tela.fill(self.COR_FUNDO)
        pygame.draw.rect(
            self.tela,
            self.COR_BORDA,
            (15,15,self.LARGURA-30,self.ALTURA-30),
            4,
            border_radius=20
        )
        titulo = self.fonte_titulo.render(
            "PLINFO Games",
            True,
            self.COR_TEXTO
        )
        subtitulo = self.fonte_subtitulo.render(
            "Escolha um jogo para jogar!",
            True,
            self.COR_BOTAO
        )
        self.tela.blit(
            titulo,
            (self.LARGURA//2-titulo.get_width()//2,80)
        )
        self.tela.blit(
            subtitulo,
            (self.LARGURA//2-subtitulo.get_width()//2,140)
        )
        for botao in self.botoes:
            botao.desenhar(
                self.tela,
                self.fonte_botao,
                self.COR_BOTAO,
                self.COR_HOVER
            )
    def rodar(self):
        while self.rodando:
            self.eventos()
            self.desenhar()

            pygame.display.flip()
            self.relogio.tick(60)

        pygame.quit()

if __name__ == "__main__":
    menu = MenuJogos()
    menu.rodar()