import pygame
import time
import random
from perguntas_quiz import perguntas

# PALETA DE CORES GLOBAL PADRONIZADA
COR_FUNDO         = (240, 242, 235)
COR_TEXTO         = (44, 53, 57)
COR_SUBTITULO     = (76, 133, 119)
COR_BOTAO         = (67, 143, 114)
COR_BOTAO_HOVER   = (82, 171, 137)
COR_SOMBRA        = (41, 92, 73)
COR_BORDA_MOLDURA = (210, 218, 201)
COR_CERTO         = (82, 183, 136)
COR_ERRADO        = (200, 80, 80)


# FUNÇÕES DE DESENHO TEMÁTICO

def desenhar_folha(surface, x, y, cor):
    """
    Desenha uma folha estilizada (losango) em uma posição da tela.

    Usada para representar as vidas restantes do jogador durante o quiz.

    Args:
        surface (pygame.Surface): Onde a folha será desenhada.
        x (int): Centro horizontal da folha.
        y (int): Centro vertical da folha.
        cor (tuple): Cor RGB da folha.
    """
    pontos = [(x, y - 10), (x + 8, y), (x, y + 10), (x - 8, y)]
    pygame.draw.polygon(surface, cor, pontos)


def desenhar_mascote(surface, x, y, estado_resposta=None):
    """
    Desenha o mascote do quiz: um vaso de planta com expressão facial.

    A expressão muda conforme o resultado da última resposta:
    - None ou True → olhos normais e sorriso (neutro/acerto).
    - False → olhos em X e sem sorriso (erro).

    Args:
        surface (pygame.Surface): Onde o mascote será desenhado.
        x (int): Centro horizontal do mascote.
        y (int): Centro vertical do mascote.
        estado_resposta (bool | None): True = acertou, False = errou,
            None = aguardando resposta.
    """
    COR_MADEIRA = (182, 143, 105) # Tom ligeiramente ajustado
    
    pygame.draw.polygon(surface, COR_MADEIRA,
                        [(x-30, y+30), (x+30, y+30), (x+20, y+70), (x-20, y+70)])
    pygame.draw.line(surface, (150, 110, 80), (x-30, y+30), (x+30, y+30), 6)

    cor_planta = COR_CERTO if estado_resposta is not False else (160, 180, 160)
    pygame.draw.circle(surface, cor_planta, (x,     y),      25)
    pygame.draw.circle(surface, cor_planta, (x-20,  y-5),    20)
    pygame.draw.circle(surface, cor_planta, (x+20,  y-5),    20)

    if estado_resposta is None or estado_resposta is True:
        pygame.draw.circle(surface, (0, 0, 0), (x-8, y-5), 3)
        pygame.draw.circle(surface, (0, 0, 0), (x+8, y-5), 3)
        pygame.draw.arc(surface, (0, 0, 0), (x-8, y-5, 16, 15), 3.14, 0, 3)
    else:
        pygame.draw.line(surface, (0,0,0), (x-12, y-8), (x-4,  y),   3)
        pygame.draw.line(surface, (0,0,0), (x-4,  y-8), (x-12, y),   3)
        pygame.draw.line(surface, (0,0,0), (x+4,  y-8), (x+12, y),   3)
        pygame.draw.line(surface, (0,0,0), (x+12, y-8), (x+4,  y),   3)


# CLASSE BOTAO COM EFEITO 3D

class BotaoOpcao:
    """
    Botão de opção do quiz com suporte a imagem, efeito 3D e feedback visual.

    Pode ser marcado como certo (verde) ou errado (vermelho) após o jogador
    responder, e volta à cor padrão quando a próxima pergunta começa.
    A animação de afundar é desativada assim que o botão recebe uma marcação.
    """

    def __init__(self, x, y, largura, altura, texto, imagem_path=None):
        """
        Cria o botão de opção.

        Args:
            x (int): Posição horizontal.
            y (int): Posição vertical.
            largura (int): Largura em pixels.
            altura (int): Altura em pixels.
            texto (str): Texto da opção de resposta.
            imagem_path (str | None): Caminho para a imagem da opção.
                Se fornecido, a imagem aparece à esquerda do texto.
        """
        self.rect_original = pygame.Rect(x, y, largura, altura)
        self.rect          = pygame.Rect(x, y, largura, altura)
        self.texto         = texto
        self.cor_atual     = COR_BOTAO
        self.imagem        = None
        
        if imagem_path:
            try:
                img         = pygame.image.load(imagem_path)
                self.imagem = pygame.transform.scale(img, (55, 55))
            except:
                self.imagem = None

    def desenhar(self, surface, fonte):
        """
        Renderiza o botão com sombra, borda e conteúdo (imagem + texto).

        A animação de afundar só acontece enquanto o botão está na cor
        padrão (ainda não respondido).

        Args:
            surface (pygame.Surface): Onde o botão será desenhado.
            fonte (pygame.font.Font): Fonte para o texto da opção.
        """
        pos_mouse = pygame.mouse.get_pos()
        is_hovered = self.rect_original.collidepoint(pos_mouse)
        
        # Animação de afundar só ocorre se o botão ainda não foi respondido (marcado como certo ou errado)
        if is_hovered and self.cor_atual == COR_BOTAO:
            cor = COR_BOTAO_HOVER
            self.rect.y = self.rect_original.y + 3
        else:
            cor = self.cor_atual
            self.rect.y = self.rect_original.y

        # 1. Sombra do Botão
        sombra_rect = pygame.Rect(self.rect_original.x, self.rect_original.y + 5, self.rect_original.width, self.rect_original.height)
        pygame.draw.rect(surface, COR_SOMBRA, sombra_rect, border_radius=12)

        # 2. Botão Principal
        pygame.draw.rect(surface, cor, self.rect, border_radius=12)
        
        # 3. Borda Interna para dar acabamento
        pygame.draw.rect(surface, (255, 255, 255), self.rect, width=1, border_radius=12)

        # 4. Conteúdo (Imagem e Texto)
        if self.imagem:
            surface.blit(self.imagem, (self.rect.x + 8, self.rect.y + 7))
            txt   = fonte.render(self.texto, True, (255, 255, 255))
            trect = txt.get_rect(midleft=(self.rect.x + 72, self.rect.centery))
        else:
            txt   = fonte.render(self.texto, True, (255, 255, 255))
            trect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, trect)

    def verificar_clique(self, evento):
        """
        Verifica se o botão foi clicado com o botão esquerdo do mouse.

        A hitbox é sempre baseada em rect_original para não escapar do
        cursor durante a animação de afundar.

        Args:
            evento (pygame.event.Event): Evento a ser verificado.

        Returns:
            bool: True se clicado, False caso contrário.
        """
        # A hitbox considera o rect_original para evitar que o botão fuja do mouse
        return (evento.type == pygame.MOUSEBUTTONDOWN and
                evento.button == 1 and
                self.rect_original.collidepoint(evento.pos))

    def marcar_certo(self):
        """Pinta o botão de verde para indicar resposta correta."""
        self.cor_atual = COR_CERTO

    def marcar_errado(self):
        """Pinta o botão de vermelho para indicar resposta errada."""
        self.cor_atual = COR_ERRADO

    def resetar_cor(self):
        """Volta o botão à cor padrão (verde neutro)."""
        self.cor_atual = COR_BOTAO


# CLASSE PRINCIPAL DO QUIZ

class JogoQuiz:
    """
    Gerenciador do Quiz Botânico.

    Controla o fluxo completo: menu de entrada → perguntas com timer →
    feedback visual → tela de resultado. Usa 15 perguntas aleatórias do
    banco em perguntas_quiz.py, com 3 vidas e 15 segundos por pergunta.

    Estados possíveis de self.estado:
        - "MENU": tela inicial, aguardando clique para começar.
        - "JOGANDO": pergunta ativa com contagem regressiva.
        - "ESPERANDO_RESPOSTA": pausado 1,5 s para mostrar o feedback.
        - "RESULTADO": exibe pontuação final e opção de reiniciar.
    """

    LARGURA, ALTURA = 800, 600
    TEMPO_MAX   = 15.0
    POSICOES    = [(80, 400), (420, 400), (80, 490), (420, 490)]

    def __init__(self, tela):
        """
        Inicializa o quiz com a tela recebida e carrega as fontes.

        Args:
            tela (pygame.Surface): Superfície do pygame onde o jogo é renderizado.
        """
        self.tela   = tela
        self.relogio = pygame.time.Clock()

        # Fontes padronizadas com o projeto
        self.fonte_titulo   = pygame.font.SysFont("cambria", 48, bold=True)
        self.fonte_pergunta = pygame.font.SysFont("segoe ui", 24, bold=True)
        self.fonte_botao    = pygame.font.SysFont("segoe ui", 20, bold=True)
        self.fonte_subtit   = pygame.font.SysFont("calibri", 24, italic=True)

        self._resetar()

    def _resetar(self):
        """
        Volta todos os atributos de partida ao estado inicial (menu).

        Chamado na criação do objeto e ao voltar ao menu após uma partida.
        """
        self.estado                 = "MENU"
        self.indice_pergunta        = 0
        self.pontos                 = 0
        self.vidas                  = 3
        self.tempo_atual            = self.TEMPO_MAX
        self.estado_resposta_mascote = None
        self.botoes_opcoes          = []
        self.perguntas_selecionadas = []
        self.tempo_espera           = 0

    def _criar_botoes(self):
        """
        Cria os quatro BotaoOpcao para a pergunta atual.

        Lê as opções e os caminhos de imagem da pergunta corrente e
        posiciona os botões nas coordenadas definidas em POSICOES.
        """
        self.botoes_opcoes = []
        p    = self.perguntas_selecionadas[self.indice_pergunta]
        opcoes = p["opcoes"]
        imgs   = p.get("imagens_opcoes", [None] * 4)
        for i in range(4):
            x, y = self.POSICOES[i]
            self.botoes_opcoes.append(BotaoOpcao(x, y, 300, 72, opcoes[i], imgs[i]))

    def _iniciar_jogo(self):
        """
        Inicia uma nova partida: embaralha até 15 perguntas, zera contadores
        e muda o estado para "JOGANDO".
        """
        self.indice_pergunta        = 0
        self.pontos                 = 0
        self.vidas                  = 3
        self.tempo_atual            = self.TEMPO_MAX
        self.estado_resposta_mascote = None
        self.tempo_espera           = 0
        qtd = min(15, len(perguntas))
        self.perguntas_selecionadas = random.sample(perguntas, qtd)
        self.estado                 = "JOGANDO"
        self._criar_botoes()

    def _responder(self, btn):
        """
        Processa a resposta do jogador ao clicar em um BotaoOpcao.

        - Resposta certa: marca o botão de verde, incrementa pontos e
          sorri o mascote.
        - Resposta errada: marca o botão de vermelho, decrementa vidas,
          revela a opção correta em verde e faz o mascote franzir.

        Em ambos os casos, muda o estado para "ESPERANDO_RESPOSTA" e
        inicia um timer de 1,5 s antes de avançar.

        Args:
            btn (BotaoOpcao): Botão que o jogador clicou.
        """
        resposta_correta = self.perguntas_selecionadas[self.indice_pergunta]["resposta"]

        if btn.texto == resposta_correta:
            btn.marcar_certo()
            self.pontos += 1
            self.estado_resposta_mascote = True
        else:
            btn.marcar_errado()
            self.vidas -= 1
            self.estado_resposta_mascote = False
            for b in self.botoes_opcoes:
                if b.texto == resposta_correta:
                    b.marcar_certo()

        self.estado = "ESPERANDO_RESPOSTA"
        self.tempo_espera = 1.5 

    def processar_eventos(self):
        """
        Lê e trata todos os eventos do pygame no frame atual.

        - QUIT → fecha o jogo.
        - ESC → retorna ao menu (retorna False).
        - Clique no menu → inicia partida.
        - Clique em botão durante "JOGANDO" → chama _responder().
        - Clique em "RESULTADO" → volta ao menu.

        Returns:
            bool: False se o jogador pressionou ESC (sinal para sair do quiz),
                True em todos os outros casos.
        """
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return False

            if self.estado == "MENU":
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    self._iniciar_jogo()

            elif self.estado == "JOGANDO":
                for btn in self.botoes_opcoes:
                    if btn.verificar_clique(evento):
                        self._responder(btn)
                        break

            elif self.estado == "RESULTADO":
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    self._resetar()

        return True

    def atualizar(self, dt):
        """
        Atualiza a lógica do jogo a cada frame.

        Durante "ESPERANDO_RESPOSTA": decrementa o timer de pausa e,
        ao expirar, avança para a próxima pergunta ou vai para "RESULTADO".

        Durante "JOGANDO": decrementa o timer da pergunta. Se o tempo
        acabar, desconta uma vida e avança (ou encerra se acabaram as vidas).

        Args:
            dt (int): Tempo em milissegundos desde o último frame (retorno de Clock.tick).
        """
        if self.estado == "ESPERANDO_RESPOSTA":
            self.tempo_espera -= dt / 1000
            if self.tempo_espera <= 0:
                self.indice_pergunta += 1
                self.tempo_atual = self.TEMPO_MAX
                self.estado_resposta_mascote = None
                
                if self.vidas <= 0:
                    self.estado = "RESULTADO"
                elif self.indice_pergunta < len(self.perguntas_selecionadas):
                    self._criar_botoes()
                    self.estado = "JOGANDO"
                else:
                    self.estado = "RESULTADO"
            return 

        if self.estado != "JOGANDO":
            return

        self.tempo_atual -= dt / 1000
        if self.tempo_atual <= 0:
            self.vidas -= 1
            self.indice_pergunta += 1
            self.tempo_atual = self.TEMPO_MAX
            if self.vidas <= 0 or self.indice_pergunta >= len(self.perguntas_selecionadas):
                self.estado = "RESULTADO"
            else:
                self._criar_botoes()

    def desenhar(self):
        """
        Renderiza a tela completa de acordo com o estado atual.

        - "MENU": título, mascote e instrução de início.
        - "JOGANDO" / "ESPERANDO_RESPOSTA": cabeçalho com progresso,
          vidas (folhas), barra de tempo, mascote, pergunta e botões.
        - "RESULTADO": título de vitória ou game over e pontuação final.
        """
        self.tela.fill(COR_FUNDO)
        
        # Moldura externa idêntica ao Proteja a Planta
        pygame.draw.rect(
            self.tela, COR_BORDA_MOLDURA,
            (20, 20, self.LARGURA - 40, self.ALTURA - 40), 3, border_radius=25
        )

        if self.estado == "MENU":
            titulo = self.fonte_titulo.render("Quiz Botânico", True, COR_TEXTO)
            sub    = self.fonte_subtit.render("Clique para começar | ESC para voltar", True, COR_SUBTITULO)
            desenhar_mascote(self.tela, self.LARGURA//2, 220)
            self.tela.blit(titulo, (self.LARGURA//2 - titulo.get_width()//2, 120))
            self.tela.blit(sub,    (self.LARGURA//2 - sub.get_width()//2,    320))

        elif self.estado in ["JOGANDO", "ESPERANDO_RESPOSTA"]:
            prog   = self.fonte_botao.render(f"Pergunta {self.indice_pergunta + 1} de {len(self.perguntas_selecionadas)}", True, COR_TEXTO)
            pontos = self.fonte_botao.render(f"Pontos: {self.pontos}", True, COR_TEXTO)
            self.tela.blit(prog, (40, 40))
            self.tela.blit(pontos, (self.LARGURA - 140, 40))

            for i in range(self.vidas):
                desenhar_folha(self.tela, 50 + (i * 25), 80, COR_CERTO)

            barra_max  = 300
            barra_atual = barra_max * (max(0, self.tempo_atual) / self.TEMPO_MAX)
            x_barra    = self.LARGURA//2 - barra_max//2
            pygame.draw.rect(self.tela, COR_BORDA_MOLDURA, (x_barra, 45, barra_max, 12), border_radius=6)
            pygame.draw.rect(self.tela, COR_BOTAO,  (x_barra, 45, barra_atual, 12), border_radius=6)

            desenhar_mascote(self.tela, self.LARGURA//2, 170, self.estado_resposta_mascote)

            pergunta_atual = self.perguntas_selecionadas[self.indice_pergunta]["pergunta"]
            palavras = pergunta_atual.split(" ")
            linha1, linha2 = "", ""
            for palavra in palavras:
                if len(linha1) < 45: linha1 += palavra + " "
                else: linha2 += palavra + " "

            l1 = self.fonte_pergunta.render(linha1.strip(), True, COR_TEXTO)
            l2 = self.fonte_pergunta.render(linha2.strip(), True, COR_TEXTO)
            self.tela.blit(l1, (self.LARGURA//2 - l1.get_width()//2, 290))
            self.tela.blit(l2, (self.LARGURA//2 - l2.get_width()//2, 330))

            for btn in self.botoes_opcoes:
                btn.desenhar(self.tela, self.fonte_botao)

        elif self.estado == "RESULTADO":
            if self.vidas <= 0:
                titulo = self.fonte_titulo.render("Game Over!", True, COR_ERRADO)
                resultado = self.fonte_pergunta.render(f"Você perdeu suas vidas. Acertou {self.pontos}!", True, COR_TEXTO)
            else:
                titulo = self.fonte_titulo.render("Fim do Quiz!", True, COR_TEXTO)
                resultado = self.fonte_titulo.render(f"Você acertou {self.pontos} de {len(self.perguntas_selecionadas)}!", True, COR_CERTO)

            reiniciar = self.fonte_subtit.render("Clique para tentar de novo.", True, COR_SUBTITULO)
            self.tela.blit(titulo, (self.LARGURA//2 - titulo.get_width()//2, 180))
            self.tela.blit(resultado, (self.LARGURA//2 - resultado.get_width()//2, 280))
            self.tela.blit(reiniciar, (self.LARGURA//2 - reiniciar.get_width()//2, 400))

    def executar(self):
        """
        Loop principal do quiz. Roda a 60 FPS até o jogador pressionar ESC.

        Ao sair, chama _resetar() para limpar o estado antes de devolver
        o controle ao menu.
        """
        while True:
            dt = self.relogio.tick(60)
            if not self.processar_eventos():
                self._resetar()
                return
            self.atualizar(dt)
            self.desenhar()
            pygame.display.flip()


def rodar_quiz(tela):
    """
    Ponto de entrada do Quiz Botânico chamado pelo menu principal.

    Cria uma instância de JogoQuiz e inicia o loop.

    Args:
        tela (pygame.Surface): Superfície compartilhada com o menu.
    """
    jogo = JogoQuiz(tela)
    jogo.executar()


if __name__ == "__main__":
    pygame.init()
    tela = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Quiz Botânico PLINFO")
    rodar_quiz(tela)
    pygame.quit()
