# Refatoração: Princípio de Responsabilidade Única (SRP)

## Resumo

Refatoração completa do código seguindo o **Princípio de Responsabilidade Única (Single Responsibility Principle)**, separando funcionalidades misturadas em múltiplos arquivos especializados.

## Arquivos Criados

### 1. **save_manager.py** - Gerenciamento de Persistência
**Responsabilidade:** Salvar e carregar o progresso do jogo

**Métodos principais:**
- `load_game_state()` - Carrega estado do jogo salvo
- `save_game_state()` - Salva cena atual e índice de texto
- `save_player_data()` - Salva inventário e dados do jogador
- `save_complete()` - Salva ambos (estado + dados do jogador)

**Antes:** Métodos `save_game()`, `load_game()`, `save_player_data()` espalhados em `game.py`

---

### 2. **status_manager.py** - Gerenciamento de Status de Personagens
**Responsabilidade:** Aplicar e persistir mudanças nos dados dos personagens

**Métodos principais:**
- `apply_status_infor()` - Aplica atualizações de status em personagens
- `get_character_status()` - Obtém status atual de um personagem
- `_merge_status_into_dict()` - Mescla campos com regras específicas (listas, operadores +/-, sobrescrita)

**Suporta:**
- Operadores aritméticos (`+5`, `-3`)
- Mesclagem de listas (sem duplicatas)
- Busca case-insensitive de personagens

**Antes:** Método `_apply_status_infor()` e `_merge_status_into_dict()` em `game.py`

---

### 3. **item_notification_manager.py** - Sistema de Notificações
**Responsabilidade:** Exibir notificações temporárias de itens

**Métodos principais:**
- `show_notification()` - Exibe notificação de item
- `update()` - Atualiza timer (chamar todo frame)
- `get_current_notification()` - Retorna item sendo notificado
- `get_alpha()` - Calcula transparência para fade in/out

**Recursos:**
- Timer baseado em frames
- Suporte a fade in/out
- Configurável (duração, FPS)

**Antes:** Variáveis `item_notification`, `item_notification_timer` em `game.py`

---

### 4. **sprite_command_parser.py** - Parser de Comandos
**Responsabilidade:** Analisar comandos de sprite no texto das cenas

**Métodos principais:**
- `parse_sprite_command()` - Extrai comandos do texto
- `strip_commands()` - Remove comandos deixando só diálogo
- `has_commands()` - Verifica se há comandos
- `is_command_only()` - Verifica se linha é só comando

**Comandos suportados:**
```
{sprite:nome:left}          → adiciona sprite à esquerda
{sprite:nome:center:happy}  → adiciona sprite com expressão
{sprite_clear:left}         → remove sprite
{expr:left:sad}             → muda expressão
```

**Antes:** Classe `SpriteCommandParser` dentro de `sprite_manager.py`

---

### 5. **background_manager.py** - Gerenciamento de Backgrounds
**Responsabilidade:** Carregar, escalar e renderizar imagens de fundo

**Métodos principais:**
- `load_background()` - Carrega imagem com cache
- `scale_to_fit()` - Escala mantendo proporção
- `scale_to_fill()` - Escala preenchendo tela (pode cortar)
- `render_background()` - Renderiza na tela
- `preload_backgrounds()` - Pré-carrega múltiplas imagens

**Recursos:**
- Cache automático de imagens
- Dois modos de escala (fit/fill)
- Centralização automática

**Antes:** Lógica de background espalhada em `renderer.py`

---

### 6. **text_style.py** - Estilos de Texto
**Responsabilidade:** Definir e aplicar estilos tipográficos

**Métodos principais:**
- `render()` - Renderiza texto com estilo
- `get_text_size()` - Calcula dimensões
- Factory methods: `create_victorian_title()`, `create_victorian_dialogue()`, etc.

**Recursos:**
- Suporte a fontes customizadas
- Fallback para fonte serif padrão
- Métodos factory para estilos vitorianos

**Antes:** Classe `TextStyle` dentro de `ui_manager.py`

---

### 7. **button.py** - Componente de Botão
**Responsabilidade:** Renderizar e gerenciar interações com botões

**Métodos principais:**
- `draw()` - Renderiza botão
- `update_hover()` - Atualiza estado hover
- `is_clicked()` - Detecta clique
- `set_enabled()` - Habilita/desabilita

**Recursos:**
- Estilo vitoriano (bordas douradas, marrom)
- Estados hover/normal
- Totalmente configurável (cores, bordas)

**Antes:** Classe `Button` dentro de `ui_manager.py`

---

## Arquivos Refatorados

### **game.py** - Loop Principal
**Nova responsabilidade:** APENAS loop de jogo, eventos de input e progressão de cenas

**Removido:**
- ❌ Lógica de save/load → `SaveManager`
- ❌ Manipulação de status → `StatusManager`
- ❌ Sistema de notificações → `ItemNotificationManager`
- ❌ Métodos auxiliares complexos de mesclagem

**Novo código:**
```python
# Usa managers especializados
self.save_manager = SaveManager()
self.status_manager = StatusManager(self.characters)
self.notification_manager = ItemNotificationManager()

# Código limpo e direto
self.save_manager.save_complete(scene_id, text_index, player_data)
self.status_manager.apply_status_infor(status)
self.notification_manager.show_notification(item)
```

---

### **sprite_manager.py**
**Removido:**
- ❌ Classe `SpriteCommandParser` → `sprite_command_parser.py`

**Mantém apenas:**
- ✅ Classe `Sprite`
- ✅ Classe `SpriteManager`

---

### **ui_manager.py**
**Removido:**
- ❌ Classe `TextStyle` → `text_style.py`
- ❌ Classe `Button` → `button.py`

**Mantém apenas:**
- ✅ Classe `UIManager` (coordena desenho de UI)

---

### **renderer.py**
**Refatorado:**
- ✅ Usa `BackgroundManager` para backgrounds
- ✅ Código de rendering de imagens removido
- ✅ Mantém apenas orquestração de renderização

---

## Benefícios da Refatoração

### 1. **Manutenibilidade**
- Cada classe tem uma responsabilidade clara
- Bugs são mais fáceis de localizar
- Mudanças são isoladas

### 2. **Testabilidade**
- Classes podem ser testadas independentemente
- Mocks e stubs são mais simples
- Menos dependências entre módulos

### 3. **Reutilização**
- `SaveManager` pode ser usado em menus
- `TextStyle` pode ser usado em outros UIs
- `BackgroundManager` serve para qualquer tela

### 4. **Legibilidade**
- Código mais limpo e direto
- Intenção clara (nome da classe = responsabilidade)
- Menos linhas por arquivo

### 5. **Extensibilidade**
- Fácil adicionar novos tipos de notificação
- Fácil adicionar novos comandos de sprite
- Fácil adicionar novos estilos de texto

---

## Estrutura Final

```
Game/system/
├── game.py                      # Loop principal ✨
├── renderer.py                  # Orquestração de renderização ✨
├── save_manager.py              # 🆕 Persistência
├── status_manager.py            # 🆕 Status de personagens
├── item_notification_manager.py # 🆕 Notificações
├── sprite_manager.py            # Sprites (refatorado) ✨
├── sprite_command_parser.py     # 🆕 Parser de comandos
├── background_manager.py        # 🆕 Backgrounds
├── ui_manager.py                # UI (refatorado) ✨
├── text_style.py                # 🆕 Estilos de texto
├── button.py                    # 🆕 Componente de botão
├── text_processor.py            # Processamento de texto (inalterado)
├── character_loader.py          # Carregamento de personagens (inalterado)
└── data_loader.py               # Carregamento de cenas (inalterado)
```

**Legenda:**
- 🆕 = Arquivo novo criado
- ✨ = Arquivo refatorado/simplificado

---

## Compatibilidade

✅ **100% compatível** com código existente
✅ Todos os testes passaram
✅ Jogo funciona normalmente
✅ Nenhuma funcionalidade foi removida

---

## Próximos Passos Sugeridos

1. **Testes Unitários:** Criar testes para cada manager
2. **Documentação de API:** Adicionar exemplos de uso
3. **Type Hints:** Adicionar hints mais específicos
4. **Error Handling:** Melhorar tratamento de erros em cada manager
5. **Logging:** Substituir prints por sistema de logging estruturado

---

## Comandos para Executar

```powershell
# Executar o jogo
.\.venv\Scripts\Activate.ps1
python main.py
```

**Status:** ✅ Refatoração completa e funcional
