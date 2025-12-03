import re

class TextProcessor:
    def replace_placeholders(self, text, player_name, characters):
        # Remove sprite commands from text (they're display commands, not dialogue)
        text = re.sub(r'\{img_esquerda:[^}]*\}', '', text)
        text = re.sub(r'\{img_clear\}', '', text)
        
        # Substitui [nome_jogador] pelo nome do jogador (case-insensitive)
        text = re.sub(r'\[nome_jogador\]', player_name, text, flags=re.IGNORECASE)

        # Mapeia versões normalizadas (a-z0-9 -> _) para o nome real
        norm_map = {}
        for name in characters:
            norm = re.sub(r'[^a-z0-9]', '_', name.lower())
            norm_map[norm] = name

        # Substitui todas as marcações [token] por <Name> quando houver correspondência
        def repl(match):
            key = match.group(1)
            norm = re.sub(r'[^a-z0-9]', '_', key.lower())
            if norm in norm_map:
                return f"<{norm_map[norm]}>"
            return match.group(0)

        text = re.sub(r'\[([^\]]+)\]', repl, text)

        # Envolve ocorrências literais do nome do jogador com < > para colorização
        text = text.replace(player_name, f"<{player_name}>")
        return text

    def render_colored_text(self, screen, text, font, x, y, default_color, name_colors):
        current_x = x
        i = 0
        while i < len(text):
            # Verifica se encontrou um nome marcado com < >
            if text[i] == '<':
                end = text.find('>', i)
                if end != -1:
                    name = text[i+1:end]
                    color = name_colors.get(name, default_color)
                    word_surf = font.render(name, True, color)
                    screen.blit(word_surf, (current_x, y))
                    current_x += word_surf.get_width()
                    i = end + 1
                    # Adiciona espaço depois do nome se houver
                    if i < len(text) and text[i] == ' ':
                        space_surf = font.render(" ", True, default_color)
                        current_x += space_surf.get_width()
                        i += 1
                    continue
            
            # Processa texto normal até o próximo marcador ou fim
            next_marker = text.find('<', i)
            if next_marker == -1:
                next_marker = len(text)
            
            normal_text = text[i:next_marker]
            if normal_text:
                text_surf = font.render(normal_text, True, default_color)
                screen.blit(text_surf, (current_x, y))
                current_x += text_surf.get_width()
            
            i = next_marker

    def render_wrapped_colored_text(self, screen, text, font, x, y, max_width, line_height, default_color, name_colors):
        """
        Renderiza texto com marcações de nomes (<Name>) coloridas, **negrito** e faz quebra de linhas
        para caber dentro de `max_width`. `line_height` é a distância vertical entre linhas.
        Suporta: <Name> para nomes coloridos e **texto** para negrito
        """
        # Criar fonte em negrito para tokens **texto**
        # Usa SysFont com bold=True ou tenta clonar a fonte atual com bold
        import pygame
        try:
            # Tenta obter o tamanho da fonte atual
            font_size = font.get_height()
            # Cria uma fonte em negrito (usa fonte padrão do sistema)
            bold_font = pygame.font.SysFont(None, font_size, bold=True)
        except:
            # Se falhar, usa a mesma fonte (fallback)
            bold_font = font
        
        # Primeiro, parsear o texto em tokens: ('name', name), ('bold', text) ou ('text', chunk)
        tokens = []
        i = 0
        while i < len(text):
            # Verifica marcadores de nome <Name>
            if text[i] == '<':
                end = text.find('>', i)
                if end != -1:
                    name = text[i+1:end]
                    tokens.append(('name', name))
                    i = end + 1
                    # If there's an immediate space, include it as a separate text token
                    if i < len(text) and text[i] == ' ':
                        tokens.append(('text', ' '))
                        i += 1
                    continue
            
            # Verifica marcadores de negrito **texto**
            if i + 1 < len(text) and text[i:i+2] == '**':
                # Procura o ** de fechamento
                end = text.find('**', i + 2)
                if end != -1:
                    bold_text = text[i+2:end]
                    tokens.append(('bold', bold_text))
                    i = end + 2
                    # If there's an immediate space, include it as a separate text token
                    if i < len(text) and text[i] == ' ':
                        tokens.append(('text', ' '))
                        i += 1
                    continue
            
            # Normal text until next marker
            next_name_marker = text.find('<', i)
            next_bold_marker = text.find('**', i)
            
            # Encontra o próximo marcador (o que vier primeiro)
            next_markers = [m for m in [next_name_marker, next_bold_marker] if m != -1]
            if next_markers:
                next_marker = min(next_markers)
            else:
                next_marker = -1
            
            if next_marker == -1:
                chunk = text[i:]
                i = len(text)
            else:
                chunk = text[i:next_marker]
                i = next_marker
            if chunk:
                # Split chunk into words but keep spaces so measurement is accurate
                words = chunk.split(' ')
                for idx, w in enumerate(words):
                    tokens.append(('text', w))
                    if idx < len(words) - 1:
                        tokens.append(('text', ' '))

        # Agora renderizar linha por linha
        cur_x = x
        cur_y = y
        line_tokens = []

        def flush_line():
            nonlocal cur_x, cur_y, line_tokens
            draw_x = x
            for ttype, tval in line_tokens:
                if ttype == 'name':
                    color = name_colors.get(tval, {}).get('color', default_color)
                    surf = font.render(tval, True, color)
                    screen.blit(surf, (draw_x, cur_y))
                    draw_x += surf.get_width()
                elif ttype == 'bold':
                    # Renderiza em negrito
                    surf = bold_font.render(tval, True, default_color)
                    screen.blit(surf, (draw_x, cur_y))
                    draw_x += surf.get_width()
                else:
                    if tval:
                        surf = font.render(tval, True, default_color)
                        screen.blit(surf, (draw_x, cur_y))
                        draw_x += surf.get_width()
            line_tokens = []
            cur_x = x
            cur_y += line_height

        for ttype, tval in tokens:
            # Measure the token width
            if ttype == 'name':
                w = font.size(tval)[0]
            elif ttype == 'bold':
                w = bold_font.size(tval)[0]
            else:
                w = font.size(tval)[0]

            # If token would overflow current line, flush first
            if cur_x + w - x > max_width and line_tokens:
                flush_line()

            # If a single token is wider than max_width and line is empty, we need to break it
            if w > max_width and (not line_tokens):
                # Break the text token (only applies to 'text' and 'bold' tokens)
                if ttype in ('text', 'bold') and tval:
                    piece = ''
                    use_font = bold_font if ttype == 'bold' else font
                    for ch in tval:
                        ch_w = use_font.size(piece + ch)[0]
                        if cur_x + ch_w - x > max_width:
                            # render piece
                            surf = use_font.render(piece, True, default_color)
                            screen.blit(surf, (cur_x, cur_y))
                            cur_y += line_height
                            piece = ch
                            cur_x = x
                        else:
                            piece += ch
                    if piece:
                        surf = use_font.render(piece, True, default_color)
                        screen.blit(surf, (cur_x, cur_y))
                        cur_x += surf.get_width()
                    # continue to next token
                    continue
                else:
                    # name token too long (unlikely). Render it truncated
                    color = name_colors.get(tval, {}).get('color', default_color) if ttype == 'name' else default_color
                    surf = font.render(tval, True, color)
                    screen.blit(surf, (cur_x, cur_y))
                    cur_x += surf.get_width()
                    continue

            # Append token to line_tokens and advance cur_x
            line_tokens.append((ttype, tval))
            cur_x += w

        # Flush remaining tokens
        if line_tokens:
            flush_line()