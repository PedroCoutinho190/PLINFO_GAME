import pygame
import time
import random
from perguntas_quiz import perguntas


# ============================================================
# FUNÇÕES DE DESENHO TEMÁTICO
# ============================================================

def desenhar_folha(surface, x, y, cor):
    pontos = [(x, y - 10), (x + 8, y), (x, y + 10), (x - 8, y)]
    pygame.draw.polygon(surface, cor, pontos)


def desenhar_mascote(surface, x, y, estado_resposta=None):
    COR_MADEIRA = (212, 163, 115)
    COR_CERTO   = (82, 183, 136)

    pygame.draw.polygon(surface, COR_MADEIRA,
                        [(x-30, y+30), (x+30, y+30), (x+20, y+70), (x-20, y+70)])
    pygame.draw.line(surface, (180, 130, 90), (x-30, y+30), (x+30, y+30), 6)

    cor_planta = COR_CERTO if estado_resposta is not False else (180, 190, 180)
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


# ============================================================
# CLASSE BOTAO
# ============================================================

class BotaoOpcao:
    COR_BOTAO       = (129, 178, 154)
    COR_BOTAO_HOVER = (156, 197, 178)
    COR_CERTO       = (82, 183, 136)
    COR_ERRADO      = (224, 122, 95)

    def __init__(self, x, y, largura, altura, texto, imagem_path=None):
        self.rect      = pygame.Rect(x, y, largura, altura)
        self.texto     = texto
        self.cor_atual = self.COR_BOTAO
        self.imagem    = None
        if imagem_path:
            try:
                img        = pygame.image.load(imagem_path)
                self.imagem = pygame.transform.scale(img, (55, 55))
            except:
                self.imagem = None

    def desenhar(self, surface, fonte):
        pos_mouse = pygame.mouse.get_pos()
        cor = (self.COR_BOTAO_HOVER
               if self.rect.collidepoint(pos_mouse) and self.cor_atual == self.COR_BOTAO
               else self.cor_atual)
        pygame.draw.rect(surface, cor, self.rect, border_radius=12)

        if self.imagem:
            surface.blit(self.imagem, (self.rect.x + 8, self.rect.y + 7))
            txt   = fonte.render(self.texto, True, (255, 255, 255))
            trect = txt.get_rect(midleft=(self.rect.x + 72, self.rect.centery))
        else:
            txt   = fonte.render(self.texto, True, (255, 255, 255))
            trect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, trect)

    def verificar_clique(self, evento):
        return (evento.type == pygame.MOUSEBUTTONDOWN and
                evento.button == 1 and
                self.rect.collidepoint(evento.pos))

    def marcar_certo(self):
        self.cor_atual = self.COR_CERTO

    def marcar_errado(self):
        self.cor_atual = self.COR_ERRADO

    def resetar_cor(self):
        self.cor_atual = self.COR_BOTAO


# ============================================================
# CLASSE PRINCIPAL DO QUIZ
# ============================================================

class JogoQuiz:
    LARGURA, ALTURA = 800, 600
    COR_FUNDO   = (244, 241, 222)
    COR_TEXTO   = (61, 64, 91)
    COR_BOTAO   = (129, 178, 154)
    COR_BORDA   = (190, 200, 175)
    COR_CERTO   = (82, 183, 136)
    COR_ERRADO  = (224, 122, 95)
    TEMPO_MAX   = 15.0
    POSICOES    = [(80, 400), (420, 400), (80, 490), (420, 490)]

    def __init__(self, tela):
        self.tela   = tela
        self.relogio = pygame.time.Clock()

        self.fonte_titulo   = pygame.font.SysFont("arial", 48, bold=True)
        self.fonte_pergunta = pygame.font.SysFont("arial", 24, bold=True)
        self.fonte_botao    = pygame.font.SysFont("arial", 20)

        self._resetar()

    def _resetar(self):
        self.estado                 = "MENU"
        self.indice_pergunta        = 0
        self.pontos                 = 0
        self.vidas                  = 3
        self.tempo_atual            = self.TEMPO_MAX
        self.estado_resposta_mascote = None
        self.botoes_opcoes          = []
        self.perguntas_selecionadas = []
        self.tempo_espera           = 0  # Cronômetro para não usar o time.sleep()

    def _criar_botoes(self):
        self.botoes_opcoes = []
        p    = self.perguntas_selecionadas[self.indice_pergunta]
        opcoes = p["opcoes"]
        imgs   = p.get("imagens_opcoes", [None] * 4)
        for i in range(4):
            x, y = self.POSICOES[i]
            self.botoes_opcoes.append(BotaoOpcao(x, y, 300, 72, opcoes[i], imgs[i]))

    def _iniciar_jogo(self):
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

        # Ao invés de dormir o código, mudamos o estado. Isso trava os cliques naturalmente!
        self.estado = "ESPERANDO_RESPOSTA"
        self.tempo_espera = 1.5  # 1.5 segundos de espera

    def processar_eventos(self):
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
                # Como o clique só funciona no estado "JOGANDO", o estado de espera fica blindado
                for btn in self.botoes_opcoes:
                    if btn.verificar_clique(evento):
                        self._responder(btn)
                        break

            elif self.estado == "RESULTADO":
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    self._resetar()

        return True

    def atualizar(self, dt):
        # 1. Se estiver esperando o feedback do acerto/erro acabar
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
                    self.estado = "JOGANDO"  # Volta para o jogo normal
                else:
                    self.estado = "RESULTADO"
            return  # Retorna para não decrementar o tempo da pergunta

        # 2. Se estiver no jogo rolando normal
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
        self.tela.fill(self.COR_FUNDO)
        pygame.draw.rect(self.tela, self.COR_BORDA, (15, 15, self.LARGURA-30, self.ALTURA-30), 4, border_radius=20)

        if self.estado == "MENU":
            titulo = self.fonte_titulo.render("Quiz Botanico", True, self.COR_TEXTO)
            sub    = self.fonte_pergunta.render("Clique para comecar | ESC para voltar", True, self.COR_BOTAO)
            desenhar_mascote(self.tela, self.LARGURA//2, 220)
            self.tela.blit(titulo, (self.LARGURA//2 - titulo.get_width()//2, 120))
            self.tela.blit(sub,    (self.LARGURA//2 - sub.get_width()//2,    320))

        # Agora desenha os componentes gráficos tanto no jogo rolando quanto na tela de espera!
        elif self.estado in ["JOGANDO", "ESPERANDO_RESPOSTA"]:
            prog   = self.fonte_botao.render(f"Pergunta {self.indice_pergunta + 1} de {len(self.perguntas_selecionadas)}", True, self.COR_TEXTO)
            pontos = self.fonte_botao.render(f"Pontos: {self.pontos}", True, self.COR_TEXTO)
            self.tela.blit(prog, (30, 30))
            self.tela.blit(pontos, (self.LARGURA - 140, 30))

            for i in range(self.vidas):
                desenhar_folha(self.tela, 40 + (i * 25), 70, self.COR_CERTO)

            barra_max  = 300
            barra_atual = barra_max * (max(0, self.tempo_atual) / self.TEMPO_MAX)
            x_barra    = self.LARGURA//2 - barra_max//2
            pygame.draw.rect(self.tela, (210, 210, 200), (x_barra, 35, barra_max, 12), border_radius=6)
            pygame.draw.rect(self.tela, self.COR_BOTAO,  (x_barra, 35, barra_atual, 12), border_radius=6)

            desenhar_mascote(self.tela, self.LARGURA//2, 170, self.estado_resposta_mascote)

            pergunta_atual = self.perguntas_selecionadas[self.indice_pergunta]["pergunta"]
            palavras = pergunta_atual.split(" ")
            linha1, linha2 = "", ""
            for palavra in palavras:
                if len(linha1) < 45: linha1 += palavra + " "
                else: linha2 += palavra + " "

            l1 = self.fonte_pergunta.render(linha1.strip(), True, self.COR_TEXTO)
            l2 = self.fonte_pergunta.render(linha2.strip(), True, self.COR_TEXTO)
            self.tela.blit(l1, (self.LARGURA//2 - l1.get_width()//2, 290))
            self.tela.blit(l2, (self.LARGURA//2 - l2.get_width()//2, 330))

            for btn in self.botoes_opcoes:
                btn.desenhar(self.tela, self.fonte_botao)

        elif self.estado == "RESULTADO":
            if self.vidas <= 0:
                titulo = self.fonte_titulo.render("Game Over!", True, self.COR_ERRADO)
                resultado = self.fonte_pergunta.render(f"Voce perdeu suas vidas. Acertou {self.pontos}!", True, self.COR_TEXTO)
            else:
                titulo = self.fonte_titulo.render("Fim do Quiz!", True, self.COR_TEXTO)
                resultado = self.fonte_titulo.render(f"Voce acertou {self.pontos} de {len(self.perguntas_selecionadas)}!", True, self.COR_CERTO)

            reiniciar = self.fonte_pergunta.render("Clique para voltar ao menu.", True, self.COR_BOTAO)
            self.tela.blit(titulo, (self.LARGURA//2 - titulo.get_width()//2, 150))
            self.tela.blit(resultado, (self.LARGURA//2 - resultado.get_width()//2, 250))
            self.tela.blit(reiniciar, (self.LARGURA//2 - reiniciar.get_width()//2, 400))

    def executar(self):
        while True:
            dt = self.relogio.tick(60)
            if not self.processar_eventos():
                self._resetar()
                return
            self.atualizar(dt)
            self.desenhar()
            pygame.display.flip()


def rodar_quiz(tela):
    jogo = JogoQuiz(tela)
    jogo.executar()


if __name__ == "__main__":
    pygame.init()
    tela = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Quiz Botanico PLINFO")
    rodar_quiz(tela)
    pygame.quit()