import pygame
from jogo_planta import rodar_quiz
from jogo_memoria import rodar_memoria
from jogo_zombies import rodar_pvz
from jogo_defesa import rodar_proteja_planta

pygame.init()

class Botao:
    """
    Botão genérico com efeito visual 3D usado no menu principal.

    Ao passar o mouse por cima, o botão muda de cor e desce 3 pixels,
    simulando um clique. A hitbox usa sempre a posição original para
    não escapar do cursor durante a animação.
    """

    def __init__(self, x, y, largura, altura, texto):
        """
        Cria o botão.

        Args:
            x (int): Posição horizontal.
            y (int): Posição vertical.
            largura (int): Largura em pixels.
            altura (int): Altura em pixels.
            texto (str): Texto exibido no centro do botão.
        """
        self.rect_original = pygame.Rect(x, y, largura, altura)
        # Criamos um rect dinâmico para o efeito de "afundar" ao passar o mouse
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto

    def desenhar(self, tela, fonte, cor_base, cor_hover, cor_sombra):
        """
        Desenha o botão na tela com efeito de hover e sombra 3D.

        Args:
            tela (pygame.Surface): Superfície onde o botão será desenhado.
            fonte (pygame.font.Font): Fonte usada para renderizar o texto.
            cor_base (tuple): Cor RGB padrão do botão.
            cor_hover (tuple): Cor RGB quando o mouse está em cima.
            cor_sombra (tuple): Cor RGB da sombra (efeito 3D).
        """
        mouse = pygame.mouse.get_pos()
        
        # Se o mouse estiver em cima, o botão muda de cor e "desce" 3 pixels
        if self.rect_original.collidepoint(mouse):
            cor_atual = cor_hover
            self.rect.y = self.rect_original.y + 3
        else:
            cor_atual = cor_base
            self.rect.y = self.rect_original.y

        # 1. Desenha a Sombra do Botão (simula efeito 3D)
        sombra_rect = pygame.Rect(self.rect_original.x, self.rect_original.y + 5, self.rect_original.width, self.rect_original.height)
        pygame.draw.rect(tela, cor_sombra, sombra_rect, border_radius=14)

        # 2. Desenha o Botão Principal por cima
        pygame.draw.rect(tela, cor_atual, self.rect, border_radius=14)
        
        # 3. Borda interna sutil para dar acabamento
        pygame.draw.rect(tela, (255, 255, 255), self.rect, width=1, border_radius=14)

        # 4. Desenha o Texto
        texto_surface = fonte.render(self.texto, True, (255, 255, 255))
        tela.blit(texto_surface, texto_surface.get_rect(center=self.rect.center))

    def clicou(self, evento):
        """
        Verifica se o botão foi clicado com o botão esquerdo do mouse.

        Usa a posição original do botão como hitbox para garantir que
        o clique seja detectado mesmo durante a animação de afundar.
        True se o botão foi clicado, False caso contrário.
        """
        # Usamos o rect_original para garantir que o clique registre mesmo se o botão se mover no hover
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.rect_original.collidepoint(evento.pos)
        return False

class MenuJogos:
    """
    Menu principal do PLINFO Games.

    Inicializa a janela do pygame, define a paleta de cores e as fontes
    do projeto, e exibe quatro botões que direcionam para cada minigame.
    """

    def __init__(self):
        """
        Configura a janela (800x600), carrega fontes do sistema e
        chama criar_botoes() para posicioná-los na tela.
        """
        self.LARGURA = 800
        self.ALTURA = 600

        self.tela = pygame.display.set_mode((self.LARGURA, self.ALTURA))
        pygame.display.set_caption("Jogos Botanicos - PLINFO")

        # --- NOVA PALETA DE CORES (Mais viva e contrastante) ---
        self.COR_FUNDO = (240, 242, 235)       # Bege claro bem natural
        self.COR_TEXTO = (44, 53, 57)          # Cinza escuro/Verde musgo profundo para leitura clara
        self.COR_SUBTITULO = (76, 133, 119)    # Verde intermediário elegante
        self.COR_BOTAO = (67, 143, 114)        # Verde folha mais vivo e nítido
        self.COR_HOVER = (82, 171, 137)        # Verde brilhante para o feedback visual
        self.COR_SOMBRA = (41, 92, 73)         # Tom escuro para profundidade dos botões
        self.COR_BORDA_MOLDURA = (210, 218, 201) # Borda do menu suave

        # Tentando carregar fontes do sistema que costumam ser mais bonitas (alternativas para Arial)
        self.fonte_titulo = pygame.font.SysFont("cambria", 54, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("calibri", 24, italic=True)
        self.fonte_botao = pygame.font.SysFont("segoe ui", 22, bold=True)

        self.criar_botoes()

        self.rodando = True
        self.relogio = pygame.time.Clock()

    def criar_botoes(self):
        """
        Instancia os quatro botões do menu e os agrupa em uma lista.

        Os botões são centralizados horizontalmente com base na largura
        da janela. A lista self.botoes facilita o loop de desenho.
        """
        # Centralizando horizontalmente perfeitamente dinâmico (Largura 320 para mais espaço interno)
        largura_btn = 320
        altura_btn = 65
        x_centralizado = (self.LARGURA // 2) - (largura_btn // 2)
        
        self.btn_quiz = Botao(x_centralizado, 200, largura_btn, altura_btn, "Quiz Botânico")
        self.btn_memoria = Botao(x_centralizado, 290, largura_btn, altura_btn, "Jogo da Memória")
        self.btn_proteger = Botao(x_centralizado, 380, largura_btn, altura_btn, "Proteja a Planta")
        self.btn_zombie = Botao(x_centralizado, 470, largura_btn, altura_btn, "Plants vs Pests")

        self.botoes = [
            self.btn_quiz,
            self.btn_memoria,
            self.btn_proteger,
            self.btn_zombie
        ]

    def eventos(self):
        """
        Processa os eventos do pygame a cada frame.

        Verifica o clique em cada botão e chama a função de entrada
        do jogo correspondente. O jogo roda de forma bloqueante: o
        menu fica pausado até que o jogador pressione ESC e volte.
        """
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
        """
        Renderiza o fundo, a moldura, o título com sombra, o subtítulo
        e todos os botões do menu.
        """
        self.tela.fill(self.COR_FUNDO)
        
        # Moldura externa elegante
        pygame.draw.rect(
            self.tela,
            self.COR_BORDA_MOLDURA,
            (20, 20, self.LARGURA - 40, self.ALTURA - 40),
            3,
            border_radius=25
        )
        
        # Renderizando Textos
        titulo_sombra = self.fonte_titulo.render("PLINFO Games", True, (200, 205, 195))
        titulo = self.fonte_titulo.render("PLINFO Games", True, self.COR_TEXTO)
        subtitulo = self.fonte_subtitulo.render("Escolha um jogo para jogar!", True, self.COR_SUBTITULO)
        
        # Posições dos textos
        x_titulo = self.LARGURA // 2 - titulo.get_width() // 2
        
        # Desenha sombra do título levemente deslocada e depois o principal por cima
        self.tela.blit(titulo_sombra, (x_titulo + 3, 73))
        self.tela.blit(titulo, (x_titulo, 70))
        
        self.tela.blit(
            subtitulo,
            (self.LARGURA // 2 - subtitulo.get_width() // 2, 140)
        )
        
        # Desenha os botões modificados
        for botao in self.botoes:
            botao.desenhar(
                self.tela,
                self.fonte_botao,
                self.COR_BOTAO,
                self.COR_HOVER,
                self.COR_SOMBRA
            )

    def rodar(self):
        """
        Loop principal do menu. Processa eventos, desenha a tela e
        limita a taxa de quadros a 60 FPS até o jogador fechar a janela.
        """
        while self.rodando:
            self.eventos()
            self.desenhar()

            pygame.display.flip()
            self.relogio.tick(60)

        pygame.quit()

if __name__ == "__main__":
    menu = MenuJogos()
    menu.rodar()
