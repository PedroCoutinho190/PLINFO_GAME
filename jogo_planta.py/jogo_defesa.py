import pygame
import random
import math

# --- Constantes Globais de Estilo ---
COR_FUNDO = (244, 241, 222)
COR_TEXTO = (61, 64, 91)
COR_BORDA = (190, 200, 175)
COR_BOTAO = (129, 178, 154)
COR_BOTAO_HOVER = (156, 197, 178)
COR_PRAGA  = (224, 122, 95)

class Planta:
    """Representa a planta central que precisa ser defendida."""
    def __init__(self, x, y, imagem):
        self.x = x
        self.y = y
        self.raio = 45
        self.vida_max = 100
        self.vida = self.vida_max
        self.imagem = imagem

    def sofrer_dano(self, dano):
        self.vida -= dano
        if self.vida < 0:
            self.vida = 0

    def esta_viva(self):
        return self.vida > 0

    def desenhar(self, tela):
        diametro = int(self.raio * 2)
        img_jogo = pygame.transform.scale(self.imagem, (diametro, diametro))
        tela.blit(img_jogo, (self.x - self.raio, self.y - self.raio))
        # Círculo sutil indicando a hitbox
        pygame.draw.circle(tela, COR_BORDA, (self.x, self.y), self.raio, 2)

    def desenhar_barra_vida(self, tela):
        largura_barra = 160
        bx = self.x - largura_barra // 2
        by = self.y + self.raio + 20
        
        # Fundo da barra
        pygame.draw.rect(tela, (210, 210, 210), (bx, by, largura_barra, 14), border_radius=4) 
        
        # Vida atual
        largura_vida = int((self.vida / self.vida_max) * largura_barra)
        cor_vida = (100, 180, 100) if self.vida > 35 else (200, 90, 90) 
        pygame.draw.rect(tela, cor_vida, (bx, by, largura_vida, 14), border_radius=4)

class Praga:
    """Representa o inimigo (ácaro) que ataca a planta."""
    def __init__(self, largura_tela, altura_tela, alvo_x, alvo_y, numero_spawn, img_original):
        self.raio = random.randint(16, 24)
        self.img_original = img_original
        
        # Escolhe uma borda aleatória para nascer (0=Cima, 1=Baixo, 2=Esquerda, 3=Direita)
        borda = random.randint(0, 3) 
        if borda == 0:   self.x, self.y = random.randint(40, largura_tela-40), 40
        elif borda == 1: self.x, self.y = random.randint(40, largura_tela-40), altura_tela-40
        elif borda == 2: self.x, self.y = 40, random.randint(40, altura_tela-40)
        else:            self.x, self.y = largura_tela-40, random.randint(40, altura_tela-40)
        
        # Calcula direção rumo à planta
        dx, dy = alvo_x - self.x, alvo_y - self.y
        dist_centro = math.hypot(dx, dy)
        
        # Aumenta a velocidade baseando-se em quantas já nasceram
        # Multiplicador: aumenta 0.05 de velocidade para CADA praga que nasce
        aumento_velocidade = numero_spawn * 0.05 
        velocidade_base = random.uniform(1.8, 3.2) + aumento_velocidade
        
        self.vx = (dx / dist_centro) * velocidade_base
        self.vy = (dy / dist_centro) * velocidade_base

   

    def atualizar(self):
        self.x += self.vx
        self.y += self.vy

    def colide_com_mouse(self, pos_mouse):
        dist = math.hypot(self.x - pos_mouse[0], self.y - pos_mouse[1])
        return dist <= self.raio + 10

    def colide_com_planta(self, planta):
        dist_planta = math.hypot(self.x - planta.x, self.y - planta.y)
        return dist_planta <= (planta.raio + self.raio)

    def desenhar(self, tela):
        if self.img_original:
            diametro = int(self.raio * 2)
            img_escalada = pygame.transform.scale(self.img_original, (diametro, diametro))
            tela.blit(img_escalada, (int(self.x - self.raio), int(self.y - self.raio)))
        else:
            pygame.draw.circle(tela, COR_PRAGA, (int(self.x), int(self.y)), self.raio)


class OpcaoSelecao:
    """Representa um item selecionável na tela de menu inicial."""
    def __init__(self, nome, arquivo_img, rect):
        self.nome = nome
        self.rect = rect
        try:
            self.img = pygame.image.load(arquivo_img).convert_alpha()
        except pygame.error:
            self.img = pygame.Surface((90, 90))
            self.img.fill(COR_BOTAO)

    def desenhar(self, tela, pos_mouse, fonte_pequena):
        # Efeito visual de hover
        if self.rect.collidepoint(pos_mouse):
            pygame.draw.rect(tela, COR_BOTAO_HOVER, self.rect.inflate(10, 10), border_radius=15)
        
        # Imagem e Borda
        img_menu = pygame.transform.scale(self.img, (self.rect.width - 10, self.rect.height - 10))
        tela.blit(img_menu, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(tela, COR_TEXTO, self.rect, 3, border_radius=12)
        
        # Texto
        txt_nome = fonte_pequena.render(self.nome, True, COR_TEXTO)
        tela.blit(txt_nome, (self.rect.centerx - txt_nome.get_width()//2, self.rect.bottom + 10))


class JogoProtejaPlanta:
    """Gerenciador Principal do Minigame."""
    def __init__(self, tela):
        self.tela = tela
        self.LARGURA, self.ALTURA = tela.get_size()
        
        # Fontes
        self.fonte = pygame.font.SysFont("arial", 24, bold=True)
        self.fonte_titulo = pygame.font.SysFont("arial", 36, bold=True)
        self.fonte_grande = pygame.font.SysFont("arial", 52, bold=True)
        self.fonte_pequena = pygame.font.SysFont("arial", 16, bold=True)
        
        self.relogio = pygame.time.Clock()
        self.estado_jogo = "SELECAO"
        
        self.carregar_recursos()
        self.resetar_partida()

    def carregar_recursos(self):
        # Opções de plantas
        dados_plantas = [
            {"nome": "Babosa", "arquivo": "imagens/babosa.jpg"},
            {"nome": "Coentro", "arquivo": "imagens/coentro.png"},
            {"nome": "Hortelã", "arquivo": "imagens/hortela.jpg"},
            {"nome": "Lótus", "arquivo": "imagens/lotus.jpg"},
            {"nome": "C. Ninguém Pode", "arquivo": "imagens/comigo_ninguem_pode.jpg"}
        ]
        
        self.opcoes_plantas = []
        largura_item = 110
        espacamento = 30
        x_inicial = (self.LARGURA - (5 * largura_item + 4 * espacamento)) // 2
        
        for i, dados in enumerate(dados_plantas):
            rect = pygame.Rect(x_inicial + i * (largura_item + espacamento), 250, largura_item, largura_item)
            self.opcoes_plantas.append(OpcaoSelecao(dados["nome"], dados["arquivo"], rect))

        # Imagem da praga
        try:
            self.img_praga = pygame.image.load("imagens/acaro.png").convert_alpha()
        except pygame.error:
            self.img_praga = None

    def resetar_partida(self):
        self.planta = None
        self.pragas = []
        self.tempo_spawn = 0
        self.frequencia_spawn = 70
        self.score = 0
        self.total_pragas_spawnadas = 0

    def processar_eventos(self):
        pos_mouse = pygame.mouse.get_pos()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False # Sinaliza para sair do minigame
                    
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                
                if self.estado_jogo == "SELECAO":
                    for opcao in self.opcoes_plantas:
                        if opcao.rect.collidepoint(evento.pos):
                            # Instancia a planta no centro da tela baseada na escolha
                            self.planta = Planta(self.LARGURA // 2, self.ALTURA // 2, opcao.img)
                            self.estado_jogo = "JOGANDO"
                            
                elif self.estado_jogo == "JOGANDO":
                    # Checa colisão do clique com as pragas (iterando de trás pra frente)
                    for i in range(len(self.pragas) - 1, -1, -1):
                        if self.pragas[i].colide_com_mouse(pos_mouse):
                            self.pragas.pop(i)
                            self.score += 1
                            if self.frequencia_spawn > 25:
                                self.frequencia_spawn -= 1
                            break 
                            
                elif self.estado_jogo == "GAME_OVER":
                    self.resetar_partida()
                    self.estado_jogo = "SELECAO"
        
        return True # Continua no minigame

    def atualizar_jogando(self):
        # Spawna novas pragas
        self.tempo_spawn += 1
        if self.tempo_spawn >= self.frequencia_spawn:
            self.tempo_spawn = 0
            self.total_pragas_spawnadas += 1
            nova_praga = Praga(self.LARGURA, self.ALTURA, self.planta.x, self.planta.y, self.score, self.img_praga)
            self.pragas.append(nova_praga)
        
        # Atualiza posição e checa dano na planta
        for i in range(len(self.pragas) - 1, -1, -1):
            p = self.pragas[i]
            p.atualizar()
            
            if p.colide_com_planta(self.planta):
                self.planta.sofrer_dano(10)
                self.pragas.pop(i)
                
                if not self.planta.esta_viva():
                    self.estado_jogo = "GAME_OVER"

    def desenhar_tela(self):
        self.tela.fill(COR_FUNDO)
        pygame.draw.rect(self.tela, COR_BORDA, (15, 15, self.LARGURA-30, self.ALTURA-30), 4, border_radius=20)
        
        pos_mouse = pygame.mouse.get_pos()

        if self.estado_jogo == "SELECAO":
            txt_sel = self.fonte_titulo.render("Escolha a planta que quer defender:", True, COR_TEXTO)
            self.tela.blit(txt_sel, (self.LARGURA//2 - txt_sel.get_width()//2, 140))
            
            for opcao in self.opcoes_plantas:
                opcao.desenhar(self.tela, pos_mouse, self.fonte_pequena)

            txt_voltar = self.fonte.render("ESC para voltar ao menu principal", True, COR_TEXTO)
            self.tela.blit(txt_voltar, (self.LARGURA//2 - txt_voltar.get_width()//2, self.ALTURA - 80))

        elif self.estado_jogo == "JOGANDO":
            self.planta.desenhar(self.tela)
            
            for p in self.pragas:
                p.desenhar(self.tela)
                
            self.planta.desenhar_barra_vida(self.tela)
            
            txt_score = self.fonte.render(f"Pragas Eliminadas: {self.score}", True, COR_TEXTO)
            self.tela.blit(txt_score, (40, 40))
            
            txt_esc = self.fonte.render("ESC para Voltar", True, COR_TEXTO)
            self.tela.blit(txt_esc, (self.LARGURA - txt_esc.get_width() - 40, 40))

        elif self.estado_jogo == "GAME_OVER":
            txt_go = self.fonte_grande.render("PLANTA DESTRUÍDA!", True, COR_PRAGA)
            txt_ponto = self.fonte.render(f"Você salvou a planta de {self.score} pragas.", True, COR_TEXTO)
            txt_restart = self.fonte.render("Clique na tela para escolher outra planta ou ESC para sair", True, COR_TEXTO)
            
            self.tela.blit(txt_go, (self.LARGURA//2 - txt_go.get_width()//2, self.ALTURA//2 - 60))
            self.tela.blit(txt_ponto, (self.LARGURA//2 - txt_ponto.get_width()//2, self.ALTURA//2 + 10))
            self.tela.blit(txt_restart, (self.LARGURA//2 - txt_restart.get_width()//2, self.ALTURA//2 + 60))

        pygame.display.flip()

    def executar(self):
        rodando = True
        while rodando:
            rodando = self.processar_eventos()
            
            if self.estado_jogo == "JOGANDO":
                self.atualizar_jogando()
                
            self.desenhar_tela()
            self.relogio.tick(60)


# --- MANTER COMPATIBILIDADE COM SEU CÓDIGO EXTERNO ---
def rodar_proteja_planta(tela):
    """
    Função de ponte para o menu principal. 
    Chama a versão Orientada a Objetos sem quebrar o resto do seu projeto.
    """
    jogo = JogoProtejaPlanta(tela)
    jogo.executar()