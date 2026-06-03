import pygame
import random
import math

def rodar_proteja_planta(tela):
    LARGURA, ALTURA = tela.get_size()
    
    # Paleta de cores coerente com o seu menu
    COR_FUNDO = (244, 241, 222)
    COR_TEXTO = (61, 64, 91)
    COR_BORDA = (190, 200, 175)
    COR_BOTAO = (129, 178, 154)
    COR_BOTAO_HOVER = (156, 197, 178)
    COR_PRAGA  = (224, 122, 95)
    
    fonte = pygame.font.SysFont("arial", 24, bold=True)
    fonte_titulo = pygame.font.SysFont("arial", 36, bold=True)
    fonte_grande = pygame.font.SysFont("arial", 52, bold=True)
    fonte_pequena = pygame.font.SysFont("arial", 16, bold=True)

    # --- 1. CONFIGURAÇÃO E CARREGAMENTO DAS PLANTAS SELECIONÁVEIS ---
    dados_plantas = [
        {"nome": "Babosa", "arquivo": "imagens/babosa.jpg"},
        {"nome": "Coentro", "arquivo": "imagens/coentro.png"},
        {"nome": "Hortelã", "arquivo": "imagens/hortela.jpg"},
        {"nome": "Lótus", "arquivo": "imagens/lotus.jpg"},
        {"nome": "C. Ninguém Pode", "arquivo": "imagens/comigo_ninguem_pode.jpg"}
    ]
    
    plantas_opcoes = []
    largura_item = 110
    espacamento = 30
    x_inicial = (LARGURA - (5 * largura_item + 4 * espacamento)) // 2
    
    for i, dados in enumerate(dados_plantas):
        try:
            img = pygame.image.load(dados["arquivo"]).convert_alpha()
        except pygame.error:
            # Caso falte alguma imagem, cria um quadrado verde reserva para não travar
            img = pygame.Surface((90, 90))
            img.fill(COR_BOTAO)
            
        # Define a caixinha de clique de cada uma no menu de seleção
        rect_clique = pygame.Rect(x_inicial + i * (largura_item + espacamento), 250, largura_item, largura_item)
        
        plantas_opcoes.append({
            "nome": dados["nome"],
            "img": img,
            "rect": rect_clique
        })

    # --- 2. CARREGAR IMAGEM DA PRAGA ---
    try:
        img_praga_original = pygame.image.load("imagens/acaro.png").convert_alpha()
    except pygame.error:
        img_praga_original = None

    # Configurações iniciais do Jogo
    planta_x, planta_y = LARGURA // 2, ALTURA // 2
    planta_raio = 45
    vida_max = 100
    vida = vida_max
    
    pragas = [] 
    tempo_spawn = 0
    frequencia_spawn = 70 
    score = 0
    
    # Estados de jogo: SELECAO, JOGANDO, GAME_OVER
    estado_jogo = "SELECAO" 
    img_planta_selecionada = None
    
    relogio = pygame.time.Clock()
    
    while True:
        tela.fill(COR_FUNDO)
        
        # Desenha a borda padrão em todas as telas do minigame
        pygame.draw.rect(tela, COR_BORDA, (15, 15, LARGURA-30, ALTURA-30), 4, border_radius=20)
        
        pos_mouse = pygame.mouse.get_pos()
        
        # --- CAPTURA DE EVENTOS ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return # Volta ao menu principal do PLINFO Games
                    
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Eventos da Tela de Seleção
                if estado_jogo == "SELECAO":
                    for opcao in plantas_opcoes:
                        if opcao["rect"].collidepoint(evento.pos):
                            img_planta_selecionada = opcao["img"]
                            estado_jogo = "JOGANDO"
                            
                # Eventos de Tiro durante a gameplay
                elif estado_jogo == "JOGANDO":
                    for i in range(len(pragas) - 1, -1, -1):
                        p = pragas[i]
                        dist = math.hypot(p['x'] - pos_mouse[0], p['y'] - pos_mouse[1])
                        if dist <= p['raio'] + 10:
                            pragas.pop(i)
                            score += 1
                            if frequencia_spawn > 25:
                                frequencia_spawn -= 1
                            break 
                            
                # Eventos da Tela de Game Over
                elif estado_jogo == "GAME_OVER":
                    vida = vida_max
                    pragas = []
                    score = 0
                    frequencia_spawn = 70
                    estado_jogo = "SELECAO" # Volta para escolher a planta de novo!

        # =========================================================================
        # TELA 1: SELEÇÃO DE PLANTA
        # =========================================================================
        if estado_jogo == "SELECAO":
            txt_sel = fonte_titulo.render("Escolha a planta que quer defender:", True, COR_TEXTO)
            tela.blit(txt_sel, (LARGURA//2 - txt_sel.get_width()//2, 140))
            
            for opcao in plantas_opcoes:
                # Efeito visual de hover (passar o mouse por cima)
                if opcao["rect"].collidepoint(pos_mouse):
                    pygame.draw.rect(tela, COR_BOTAO_HOVER, opcao["rect"].inflate(10, 10), border_radius=15)
                
                # Desenha a foto da plantinha na caixinha
                img_menu = pygame.transform.scale(opcao["img"], (largura_item - 10, largura_item - 10))
                tela.blit(img_menu, (opcao["rect"].x + 5, opcao["rect"].y + 5))
                pygame.draw.rect(tela, COR_TEXTO, opcao["rect"], 3, border_radius=12)
                
                # Nome da planta abaixo dela
                txt_nome = fonte_pequena.render(opcao["nome"], True, COR_TEXTO)
                tela.blit(txt_nome, (opcao["rect"].centerx - txt_nome.get_width()//2, opcao["rect"].bottom + 10))

            txt_voltar = fonte.render("ESC para voltar ao menu principal", True, COR_TEXTO)
            tela.blit(txt_voltar, (LARGURA//2 - txt_voltar.get_width()//2, ALTURA - 80))

        # =========================================================================
        # TELA 2: GAMEPLAY ATIVA
        # =========================================================================
        elif estado_jogo == "JOGANDO":
            # --- LÓGICA DAS PRAGAS ---
            tempo_spawn += 1
            if tempo_spawn >= frequencia_spawn:
                tempo_spawn = 0
                borda = random.randint(0, 3) 
                raio_praga = random.randint(16, 24)
                
                if borda == 0: px, py = random.randint(40, LARGURA-40), 40
                elif borda == 1: px, py = random.randint(40, LARGURA-40), ALTURA-40
                elif borda == 2: px, py = 40, random.randint(40, ALTURA-40)
                else: px, py = LARGURA-40, random.randint(40, ALTURA-40)
                
                dx, dy = planta_x - px, planta_y - py
                dist_centro = math.hypot(dx, dy)
                
                velocidade_base = random.uniform(1.8, 3.2) + (score * 0.03)
                vx = (dx / dist_centro) * velocidade_base
                vy = (dy / dist_centro) * velocidade_base
                
                pragas.append({'x': px, 'y': py, 'vx': vx, 'vy': vy, 'raio': raio_praga})
            
            for i in range(len(pragas) - 1, -1, -1):
                p = pragas[i]
                p['x'] += p['vx']
                p['y'] += p['vy']
                
                dist_planta = math.hypot(p['x'] - planta_x, p['y'] - planta_y)
                if dist_planta <= (planta_raio + p['raio']):
                    vida -= 10 
                    pragas.pop(i)
                    if vida <= 0:
                        vida = 0
                        estado_jogo = "GAME_OVER"

            # --- RENDERIZAÇÃO DOS ELEMENTOS DO JOGO ---
            # 1. Desenha a Planta Selecionada no Centro da Tela
            diametro_planta = int(planta_raio * 2)
            img_planta_jogo = pygame.transform.scale(img_planta_selecionada, (diametro_planta, diametro_planta))
            # Ajusta para desenhar centralizado perfeitamente
            tela.blit(img_planta_jogo, (planta_x - planta_raio, planta_y - planta_raio))
            # Circulo sutil em volta da planta para indicar a área de colisão
            pygame.draw.circle(tela, COR_BORDA, (planta_x, planta_y), planta_raio, 2)
            
            # 2. Desenha as Pragas (Ácaros)
            for p in pragas:
                if img_praga_original:
                    diametro = int(p['raio'] * 2)
                    img_escalada = pygame.transform.scale(img_praga_original, (diametro, diametro))
                    tela.blit(img_escalada, (int(p['x'] - p['raio']), int(p['y'] - p['raio'])))
                else:
                    pygame.draw.circle(tela, COR_PRAGA, (int(p['x']), int(p['y'])), p['raio'])
            
            # 3. Interface de Vida e Score
            largura_barra = 160
            bx, by = planta_x - largura_barra // 2, planta_y + planta_raio + 20
            pygame.draw.rect(tela, (210, 210, 210), (bx, by, largura_barra, 14), border_radius=4) 
            largura_vida = int((vida / vida_max) * largura_barra)
            cor_vida = (100, 180, 100) if vida > 35 else (200, 90, 90) 
            pygame.draw.rect(tela, cor_vida, (bx, by, largura_vida, 14), border_radius=4)
            
            txt_score = fonte.render(f"Pragas Eliminadas: {score}", True, COR_TEXTO)
            tela.blit(txt_score, (40, 40))
            txt_esc = fonte.render("ESC para Voltar", True, COR_TEXTO)
            tela.blit(txt_esc, (LARGURA - txt_esc.get_width() - 40, 40))

        # =========================================================================
        # TELA 3: GAME OVER
        # =========================================================================
        elif estado_jogo == "GAME_OVER":
            txt_go = fonte_grande.render("PLANTA DESTRUÍDA!", True, COR_PRAGA)
            txt_ponto = fonte.render(f"Você salvou a planta de {score} pragas.", True, COR_TEXTO)
            txt_restart = fonte.render("Clique em qualquer lugar para escolher outra planta ou ESC para sair", True, COR_TEXTO)
            
            tela.blit(txt_go, (LARGURA//2 - txt_go.get_width()//2, ALTURA//2 - 60))
            tela.blit(txt_ponto, (LARGURA//2 - txt_ponto.get_width()//2, ALTURA//2 + 10))
            tela.blit(txt_restart, (LARGURA//2 - txt_restart.get_width()//2, ALTURA//2 + 60))

        pygame.display.flip()
        relogio.tick(60)