import pygame
import time
import random
from perguntas_quiz import perguntas

# Paleta de Cores
COR_FUNDO = (244, 241, 222)
COR_TEXTO = (61, 64, 91)
COR_BOTAO = (129, 178, 154)
COR_BOTAO_HOVER = (156, 197, 178)
COR_CERTO = (82, 183, 136)
COR_ERRADO = (224, 122, 95)
COR_MADEIRA = (212, 163, 115)
COR_BORDA = (190, 200, 175)

LARGURA, ALTURA = 800, 600

# --- Funções de Desenho para UI Temática ---
def desenhar_folha(surface, x, y, cor):
    """Desenha uma folhinha simples usando polígonos para representar as vidas"""
    pontos = [(x, y - 10), (x + 8, y), (x, y + 10), (x - 8, y)]
    pygame.draw.polygon(surface, cor, pontos)

def desenhar_mascote(surface, x, y, estado_resposta=None):
    """Desenha um vasinho de planta mascote no centro da tela"""
    # Vasinho
    pygame.draw.polygon(surface, COR_MADEIRA, [(x-30, y+30), (x+30, y+30), (x+20, y+70), (x-20, y+70)])
    pygame.draw.line(surface, (180, 130, 90), (x-30, y+30), (x+30, y+30), 6)
    
    # Folhas da planta (Círculos)
    cor_planta = COR_CERTO if estado_resposta is not False else (180, 190, 180) # Fica cinza se errar
    pygame.draw.circle(surface, cor_planta, (x, y), 25)
    pygame.draw.circle(surface, cor_planta, (x-20, y-5), 20)
    pygame.draw.circle(surface, cor_planta, (x+20, y-5), 20)
    
    if estado_resposta is None or estado_resposta is True:
        # Acertou
        pygame.draw.circle(surface, (0, 0, 0), (x-8, y-5), 3)
        pygame.draw.circle(surface, (0, 0, 0), (x+8, y-5), 3)
        pygame.draw.arc(surface, (0, 0, 0), (x-8, y-5, 16, 15), 3.14, 0, 3) 
    else:
        # Errou 
        pygame.draw.line(surface, (0,0,0), (x-12, y-8), (x-4, y), 3)
        pygame.draw.line(surface, (0,0,0), (x-4, y-8), (x-12, y), 3)
        pygame.draw.line(surface, (0,0,0), (x+4, y-8), (x+12, y), 3)
        pygame.draw.line(surface, (0,0,0), (x+12, y-8), (x+4, y), 3)


# Classe do Botão 
class Botao:
    def __init__(self, x, y, largura, altura, texto, imagem_path=None):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor_atual = COR_BOTAO
        self.imagem = None
        if imagem_path:
            try:
                img = pygame.image.load(imagem_path)
                self.imagem = pygame.transform.scale(img, (55, 55))
            except:
                self.imagem = None

    def desenhar(self, surface, fonte):
        pos_mouse = pygame.mouse.get_pos()
        cor = COR_BOTAO_HOVER if self.rect.collidepoint(pos_mouse) and self.cor_atual == COR_BOTAO else self.cor_atual
        pygame.draw.rect(surface, cor, self.rect, border_radius=12)

        if self.imagem:
            surface.blit(self.imagem, (self.rect.x + 8, self.rect.y + 7))
            texto_surface = fonte.render(self.texto, True, (255, 255, 255))
            texto_rect = texto_surface.get_rect(midleft=(self.rect.x + 72, self.rect.centery))
        else:
            texto_surface = fonte.render(self.texto, True, (255, 255, 255))
            texto_rect = texto_surface.get_rect(center=self.rect.center)

        surface.blit(texto_surface, texto_rect)

    def verificar_clique(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                return True
        return False


# Função principal do quiz
def rodar_quiz(tela):

    fonte_titulo   = pygame.font.SysFont("arial", 48, bold=True)
    fonte_pergunta = pygame.font.SysFont("arial", 24, bold=True)
    fonte_botao    = pygame.font.SysFont("arial", 20)

    estado = "MENU"
    indice_pergunta = 0
    pontos = 0
    vidas = 3
    botoes_opcoes = []
    perguntas_selecionadas = []
    
    # Variáveis de tempo
    tempo_maximo = 15.0 # 15 Segundos por pergunta
    tempo_atual = tempo_maximo
    estado_resposta_mascote = None # None, True, ou False

    def criar_botoes_pergunta():
        botoes_opcoes.clear()
        opcoes = perguntas_selecionadas[indice_pergunta]["opcoes"]
        imagens = perguntas_selecionadas[indice_pergunta].get("imagens_opcoes", [None] * 4)
        posicoes = [(80, 400), (420, 400), (80, 490), (420, 490)] 
        for i in range(4):
            btn = Botao(posicoes[i][0], posicoes[i][1], 300, 72, opcoes[i], imagens[i])
            botoes_opcoes.append(btn)

    relogio = pygame.time.Clock()

    while True:
        dt = relogio.tick(60)
        tela.fill(COR_FUNDO)
        
        # Desenha a moldura de "Trepadeira"
        pygame.draw.rect(tela, COR_BORDA, (15, 15, LARGURA-30, ALTURA-30), 4, border_radius=20)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return

            if estado == "MENU":
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    estado = "JOGANDO"
                    indice_pergunta = 0
                    pontos = 0
                    vidas = 3
                    tempo_atual = tempo_maximo
                    estado_resposta_mascote = None
                    
                    # Sorteia 15 perguntas aleatórias da lista original (ou todas, se tiver menos de 15)
                    qtd_perguntas = min(15, len(perguntas))
                    perguntas_selecionadas = random.sample(perguntas, qtd_perguntas)
                    
                    criar_botoes_pergunta()

            elif estado == "JOGANDO":
                for btn in botoes_opcoes:
                    if btn.verificar_clique(evento):
                        resposta_correta = perguntas_selecionadas[indice_pergunta]["resposta"]
                        if btn.texto == resposta_correta:
                            btn.cor_atual = COR_CERTO
                            pontos += 1
                            estado_resposta_mascote = True
                        else:
                            btn.cor_atual = COR_ERRADO
                            vidas -= 1
                            estado_resposta_mascote = False
                            for b in botoes_opcoes:
                                if b.texto == resposta_correta:
                                    b.cor_atual = COR_CERTO

                        # Desenha tudo uma última vez para mostrar o botão colorido e a carinha do mascote
                        tela.fill(COR_FUNDO)
                        pygame.draw.rect(tela, COR_BORDA, (15, 15, LARGURA-30, ALTURA-30), 4, border_radius=20)
                        desenhar_mascote(tela, LARGURA // 2, 170, estado_resposta_mascote)
                        for b in botoes_opcoes: b.desenhar(tela, fonte_botao)
                        pygame.display.flip()
                        
                        time.sleep(1.5) # Pausa para ver a resposta

                        indice_pergunta += 1
                        tempo_atual = tempo_maximo # Reseta o tempo
                        estado_resposta_mascote = None # Reseta o mascote
                        
                        if vidas <= 0:
                            estado = "RESULTADO"
                        elif indice_pergunta < len(perguntas_selecionadas):
                            criar_botoes_pergunta()
                        else:
                            estado = "RESULTADO"

            elif estado == "RESULTADO":
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    estado = "MENU" # Volta para o menu em vez de fechar

        # Lógica de Tempo e UI se estiver Jogando
        if estado == "JOGANDO":
            # Diminui o tempo
            tempo_atual -= dt / 1000 
            if tempo_atual <= 0:
                vidas -= 1
                indice_pergunta += 1
                tempo_atual = tempo_maximo
                if vidas <= 0 or indice_pergunta >= len(perguntas_selecionadas):
                    estado = "RESULTADO"
                else:
                    criar_botoes_pergunta()

            # Textos Superiores
            texto_progresso = fonte_botao.render(f"Pergunta {indice_pergunta + 1} de {len(perguntas_selecionadas)}", True, COR_TEXTO)
            texto_pontos = fonte_botao.render(f"Pontos: {pontos}", True, COR_TEXTO)
            tela.blit(texto_progresso, (30, 30))
            tela.blit(texto_pontos, (LARGURA - 140, 30))

            # Desenhando Vidas (Folhas)
            for i in range(vidas):
                desenhar_folha(tela, 40 + (i * 25), 70, COR_CERTO)

            # Barra de Tempo Centralizada no Topo
            largura_barra_max = 300
            largura_barra_atual = largura_barra_max * (max(0, tempo_atual) / tempo_maximo)
            x_barra = LARGURA//2 - largura_barra_max//2
            pygame.draw.rect(tela, (210, 210, 200), (x_barra, 35, largura_barra_max, 12), border_radius=6) # Fundo Cinza
            pygame.draw.rect(tela, COR_BOTAO, (x_barra, 35, largura_barra_atual, 12), border_radius=6)     # Tempo Verde

            # Mascote
            desenhar_mascote(tela, LARGURA // 2, 170, estado_resposta_mascote)

            # Pergunta 
            pergunta_atual = perguntas_selecionadas[indice_pergunta]["pergunta"]
            palavras = pergunta_atual.split(" ")
            linha1, linha2 = "", ""
            for palavra in palavras:
                if len(linha1) < 45:
                    linha1 += palavra + " "
                else:
                    linha2 += palavra + " "

            texto_l1 = fonte_pergunta.render(linha1.strip(), True, COR_TEXTO)
            texto_l2 = fonte_pergunta.render(linha2.strip(), True, COR_TEXTO)
            tela.blit(texto_l1, (LARGURA // 2 - texto_l1.get_width() // 2, 290))
            tela.blit(texto_l2, (LARGURA // 2 - texto_l2.get_width() // 2, 330))

            for btn in botoes_opcoes:
                btn.desenhar(tela, fonte_botao)

        elif estado == "MENU":
            titulo = fonte_titulo.render("Quiz Botânico", True, COR_TEXTO)
            sub = fonte_pergunta.render("Clique para começar | ESC para voltar", True, COR_BOTAO)
            desenhar_mascote(tela, LARGURA // 2, 220) # Mascote no menu também!
            tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 120))
            tela.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 320))

        elif estado == "RESULTADO":
            if vidas <= 0:
                titulo = fonte_titulo.render("Game Over!", True, COR_ERRADO)
                resultado = fonte_pergunta.render(f"Você perdeu suas vidas. Acertou {pontos}!", True, COR_TEXTO)
            else:
                titulo = fonte_titulo.render("Fim do Quiz!", True, COR_TEXTO)
                resultado = fonte_titulo.render(f"Você acertou {pontos} de {len(perguntas_selecionadas)}!", True, COR_CERTO)
                
            reiniciar = fonte_pergunta.render("Clique para voltar ao menu.", True, COR_BOTAO)
            tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 150))
            tela.blit(resultado, (LARGURA // 2 - resultado.get_width() // 2, 250))
            tela.blit(reiniciar, (LARGURA // 2 - reiniciar.get_width() // 2, 400))

        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Quiz Botânico PLINFO")
    rodar_quiz(tela)
    pygame.quit()