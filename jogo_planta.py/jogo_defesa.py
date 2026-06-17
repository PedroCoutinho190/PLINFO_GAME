import pygame
import random
import math

# --- NOVA PALETA DE CORES (IDÊNTICA AO MENU) ---
COR_FUNDO         = (240, 242, 235)  
COR_TEXTO         = (44, 53, 57)     
COR_SUBTITULO     = (76, 133, 119)   
COR_BOTAO         = (67, 143, 114)   
COR_BOTAO_HOVER   = (82, 171, 137)   
COR_SOMBRA        = (41, 92, 73)     
COR_BORDA_MOLDURA = (210, 218, 201)  
COR_PRAGA         = (200, 80, 80)    


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
        # Círculo sutil indicando a hitbox com a cor de borda do menu
        pygame.draw.circle(tela, COR_BORDA_MOLDURA, (self.x, self.y), self.raio, 2)

    def desenhar_barra_vida(self, tela):
        largura_barra = 160
        bx = self.x - largura_barra // 2
        by = self.y + self.raio + 20
        
        # Fundo da barra
        pygame.draw.rect(tela, COR_BORDA_MOLDURA, (bx, by, largura_barra, 14), border_radius=4) 
        
        # Vida atual
        largura_vida = int((self.vida / self.vida_max) * largura_barra)
        cor_vida = COR_BOTAO_HOVER if self.vida > 35 else COR_PRAGA 
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
    """Representa um item selecionável na tela de menu inicial (Modificado para Botão 3D)."""
    def __init__(self, nome, arquivo_img, rect):
        self.nome = nome
        self.rect_original = rect
        # Rect dinâmico para o efeito de "afundar"
        self.rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height)
        
        try:
            self.img = pygame.image.load(arquivo_img).convert_alpha()
        except pygame.error:
            self.img = pygame.Surface((rect.width - 20, rect.height - 40))
            self.img.fill((200, 200, 200))

    def desenhar(self, tela, pos_mouse, fonte_pequena):
        # Efeito hover: afunda 3 pixels
        if self.rect_original.collidepoint(pos_mouse):
            cor_atual = COR_BOTAO_HOVER
            self.rect.y = self.rect_original.y + 3
        else:
            cor_atual = COR_BOTAO
            self.rect.y = self.rect_original.y

        # 1. Sombra do Botão
        sombra_rect = pygame.Rect(self.rect_original.x, self.rect_original.y + 5, self.rect_original.width, self.rect_original.height)
        pygame.draw.rect(tela, COR_SOMBRA, sombra_rect, border_radius=15)

        # 2. Botão Principal
        pygame.draw.rect(tela, cor_atual, self.rect, border_radius=15)
        
        # 3. Borda interna
        pygame.draw.rect(tela, (255, 255, 255), self.rect, width=1, border_radius=15)
        
        # 4. Imagem da Planta
        img_menu = pygame.transform.scale(self.img, (self.rect.width - 20, self.rect.height - 40))
        tela.blit(img_menu, (self.rect.x + 10, self.rect.y + 10))
        
        # 5. Texto
        txt_nome = fonte_pequena.render(self.nome, True, (255, 255, 255))
        tela.blit(txt_nome, (self.rect.centerx - txt_nome.get_width()//2, self.rect.bottom - 25))

    def clicou(self, evento):
        # Valida o clique baseado na posição original
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.rect_original.collidepoint(evento.pos)
        return False


class JogoProtejaPlanta:
    """Gerenciador Principal do Minigame."""
    def __init__(self, tela):
        self.tela = tela
        self.LARGURA, self.ALTURA = tela.get_size()
        
        # --- FONTES PADRONIZADAS ---
        self.fonte         = pygame.font.SysFont("segoe ui", 24, bold=True)
        self.fonte_titulo  = pygame.font.SysFont("cambria", 42, bold=True)
        self.fonte_subtit  = pygame.font.SysFont("calibri", 24, italic=True)
        self.fonte_grande  = pygame.font.SysFont("cambria", 52, bold=True)
        self.fonte_pequena = pygame.font.SysFont("segoe ui", 16, bold=True)
        
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
            {"nome": "Ninguém Pode", "arquivo": "imagens/comigo_ninguem_pode.jpg"}
        ]
        
        self.opcoes_plantas = []
        # Tamanho ajustado para caber texto + imagem confortavelmente dentro do botão
        largura_item = 120
        altura_item  = 150
        espacamento  = 25
        x_inicial = (self.LARGURA - (5 * largura_item + 4 * espacamento)) // 2
        
        for i, dados in enumerate(dados_plantas):
            rect = pygame.Rect(x_inicial + i * (largura_item + espacamento), 240, largura_item, altura_item)
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
                        if opcao.clicou(evento):
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
        
        # Moldura externa idêntica ao menu
        pygame.draw.rect(
            self.tela, COR_BORDA_MOLDURA,
            (20, 20, self.LARGURA - 40, self.ALTURA - 40), 3, border_radius=25
        )
        
        pos_mouse = pygame.mouse.get_pos()

        if self.estado_jogo == "SELECAO":
            # Títulos
            titulo = self.fonte_titulo.render("Proteja a Planta", True, COR_TEXTO)
            subtit = self.fonte_subtit.render("Escolha a planta que quer defender contra os ácaros:", True, COR_SUBTITULO)
            
            self.tela.blit(titulo, (self.LARGURA//2 - titulo.get_width()//2, 80))
            self.tela.blit(subtit, (self.LARGURA//2 - subtit.get_width()//2, 140))
            
            # Botões Plantas
            for opcao in self.opcoes_plantas:
                opcao.desenhar(self.tela, pos_mouse, self.fonte_pequena)

            # Voltar
            txt_voltar = self.fonte_pequena.render("Pressione ESC para voltar ao menu", True, COR_SOMBRA)
            self.tela.blit(txt_voltar, (self.LARGURA//2 - txt_voltar.get_width()//2, self.ALTURA - 70))

        elif self.estado_jogo == "JOGANDO":
            self.planta.desenhar(self.tela)
            
            for p in self.pragas:
                p.desenhar(self.tela)
                
            self.planta.desenhar_barra_vida(self.tela)
            
            txt_score = self.fonte.render(f"Pragas Eliminadas: {self.score}", True, COR_TEXTO)
            self.tela.blit(txt_score, (40, 40))
            
            txt_esc = self.fonte.render("ESC: Voltar", True, COR_TEXTO)
            self.tela.blit(txt_esc, (self.LARGURA - txt_esc.get_width() - 40, 40))

        elif self.estado_jogo == "GAME_OVER":
            txt_go = self.fonte_grande.render("PLANTA DESTRUÍDA!", True, COR_PRAGA)
            txt_ponto = self.fonte_titulo.render(f"Você eliminou {self.score} pragas.", True, COR_TEXTO)
            txt_restart = self.fonte_subtit.render("Clique em qualquer lugar para tentar novamente.", True, COR_SUBTITULO)
            txt_esc = self.fonte_pequena.render("Pressione ESC para sair", True, COR_SOMBRA)
            
            self.tela.blit(txt_go, (self.LARGURA//2 - txt_go.get_width()//2, self.ALTURA//2 - 90))
            self.tela.blit(txt_ponto, (self.LARGURA//2 - txt_ponto.get_width()//2, self.ALTURA//2 - 10))
            self.tela.blit(txt_restart, (self.LARGURA//2 - txt_restart.get_width()//2, self.ALTURA//2 + 60))
            self.tela.blit(txt_esc, (self.LARGURA//2 - txt_esc.get_width()//2, self.ALTURA//2 + 100))

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

