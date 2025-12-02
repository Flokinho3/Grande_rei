# Sistema Avançado de Sprites de Personagens

## Visão Geral
O sistema de sprites permite exibir **múltiplas imagens de personagens simultaneamente** durante as cenas do jogo, com suporte a posicionamento, expressões faciais e efeitos de transição.

---

## Como Usar

### 1. Preparar as Imagens
Coloque as imagens dos personagens em: `Game/data/script/imgs/NPC/`

**Estrutura recomendada:**
```
Game/data/script/imgs/NPC/
├── yuno.png              # Sprite padrão
├── yuno_happy.png        # Expressão feliz
├── yuno_sad.png          # Expressão triste
├── yuno_angry.png        # Expressão irritada
├── rei.png
├── rei_serious.png
└── ...
```

**Convenção de nomes para expressões:**
- `personagem.png` — expressão padrão/neutra
- `personagem_expressao.png` — variação de expressão

### 2. Configurar o Personagem
No arquivo JSON do personagem (em `Game/data/script/Base/NPC/`), adicione o campo `"img"`:

```json
{
    "nome": "Yuno",
    "cor": "255, 51, 153",
    "img": "yuno.png"
}
```

### 3. Usar no Script da Cena

#### Sintaxe Básica
```json
{
    "texto": [
        "{sprite:yuno:left}",
        "{yuno}: Olá, seja bem-vindo!"
    ]
}
```

---

## Comandos Disponíveis

### Adicionar Sprites

#### Posicionamento Simples
```json
"{sprite:nome:posição}"
```
- **Posições:** `left` (esquerda), `center` (centro), `right` (direita)
- **Exemplo:** `{sprite:yuno:left}` — Yuno à esquerda

#### Com Expressão
```json
"{sprite:nome:posição:expressão}"
```
- **Exemplo:** `{sprite:yuno:center:happy}` — Yuno no centro, feliz
- **Exemplo:** `{sprite:rei:right:serious}` — Rei à direita, sério

### Remover Sprites

```json
"{sprite_clear:posição}"    # Remove sprite de uma posição específica
"{sprite_clear:all}"         # Remove TODOS os sprites
```

### Mudar Expressão (sem recarregar sprite)

```json
"{expr:posição:nova_expressão}"
```
- **Exemplo:** `{expr:left:sad}` — Muda expressão do sprite à esquerda para "triste"

---

## Comandos Legados (Compatibilidade)

Os comandos antigos ainda funcionam para compatibilidade:

```json
"{img_esquerda:nome}"        # Equivalente a {sprite:nome:left}
"{img_esquerda:}"            # Equivalente a {sprite_clear:all}
"{img_clear}"                # Equivalente a {sprite_clear:all}
```

---

## Comportamento Avançado

### Múltiplos Sprites Simultâneos
✅ **Agora é possível exibir até 3 sprites ao mesmo tempo:**

```json
{
    "texto": [
        "{sprite:yuno:left}",
        "{sprite:rei:right}",
        "{yuno}: Vossa Majestade, é uma honra.",
        "{rei}: Seja bem-vinda ao castelo."
    ]
}
```

### Persistência
- Sprites **permanecem na tela** entre linhas de texto
- Permanecem até serem **explicitamente removidos** ou **substituídos**

### Transições Automáticas
- **Fade In:** Sprites aparecem suavemente (300ms)
- **Fade Out:** Sprites desaparecem suavemente quando removidos

### Ordem de Renderização
1. Background (fundo)
2. **Sprites** (ordenados por z-index)
3. Caixa de texto
4. Botões e UI

### Tamanhos Automáticos
- **Left/Right:** até 30% largura × 60% altura da tela
- **Center:** até 35% largura × 70% altura da tela

---

## Exemplos Completos

### Exemplo 1: Diálogo entre Dois Personagens
```json
{
    "id": "conversa_rei",
    "titulo": "Audiência Real",
    "img_fundo": "trono.png",
    "texto": [
        "{sprite:yuno:left}",
        "{sprite:rei:right}",
        "{rei}: Então você é a representante da Casa Shedow?",
        "{yuno}: Sim, Vossa Majestade.",
        "{expr:left:happy}",
        "{yuno}: É uma grande honra estar aqui.",
        "{sprite_clear:all}",
        "Ambos se curvam e se retiram da sala."
    ]
}
```

### Exemplo 2: Mudança de Expressão Durante Cena
```json
{
    "id": "noticia_ruim",
    "titulo": "Más Notícias",
    "img_fundo": "corredor.png",
    "texto": [
        "{sprite:yuno:center}",
        "{yuno}: Finalmente encontrei você!",
        "Um mensageiro se aproxima com um pergaminho.",
        "{expr:center:sad}",
        "{yuno}: O que...? Não pode ser verdade...",
        "{expr:center:angry}",
        "{yuno}: Eles vão pagar por isso!",
        "{sprite_clear:all}"
    ]
}
```

### Exemplo 3: Três Personagens na Tela
```json
{
    "id": "reuniao",
    "titulo": "Conselho de Guerra",
    "img_fundo": "sala_guerra.png",
    "texto": [
        "{sprite:general:left}",
        "{sprite:yuno:center}",
        "{sprite:conselheiro:right}",
        "{general}: A situação é crítica.",
        "{yuno}: Temos que agir rápido.",
        "{conselheiro}: Sugiro cautela...",
        "{sprite_clear:left}",
        "O general se retira irritado.",
        "{yuno}: Apenas nós dois agora.",
        "{sprite_clear:all}"
    ]
}
```

---

## Dicas de Design

### Imagens
1. **Formato:** PNG com fundo transparente (alpha channel)
2. **Proporção:** Vertical/retrato (melhor resultado)
3. **Resolução Recomendada:** 500×1000 a 800×1600 pixels
4. **Tamanho do Arquivo:** Otimize para < 500KB por imagem

### Expressões
- Crie pelo menos 4-5 expressões por personagem principal:
  - Neutro (padrão)
  - Feliz (`_happy`)
  - Triste (`_sad`)
  - Irritado (`_angry`)
  - Surpreso (`_surprised`)

### Nomenclatura
- Use nomes **simples e consistentes**
- Evite espaços, acentos e caracteres especiais
- **Bons exemplos:** `yuno.png`, `rei_serio.png`, `bruno.png`
- **Evite:** `Bruno O'Neil.png`, `Yúno-Chan!.png`

### Performance
- Evite trocar sprites muito rapidamente (< 1 segundo)
- Use `{sprite_clear:all}` no início de novas cenas para limpar tela
- Não exceda 3 sprites simultâneos para melhor desempenho

---

## Solução de Problemas

### Sprite não aparece
1. ✅ Verifique se o arquivo existe em `Game/data/script/imgs/NPC/`
2. ✅ Confirme que o nome no comando corresponde ao nome no JSON
3. ✅ Verifique se o campo `"img"` está no JSON do personagem
4. ✅ Confira logs do console para mensagens de erro

### Sprite aparece cortado
- Reduza a resolução da imagem
- Use proporção vertical (altura > largura)

### Expressão não muda
- Verifique se o arquivo `personagem_expressao.png` existe
- Confirme que a posição no comando está correta

---

## Referência Rápida

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `{sprite:nome:posição}` | Adiciona sprite | `{sprite:yuno:left}` |
| `{sprite:nome:posição:expr}` | Adiciona com expressão | `{sprite:yuno:center:happy}` |
| `{sprite_clear:posição}` | Remove de posição | `{sprite_clear:left}` |
| `{sprite_clear:all}` | Remove todos | `{sprite_clear:all}` |
| `{expr:posição:expr}` | Muda expressão | `{expr:left:sad}` |

**Posições válidas:** `left`, `center`, `right`

---

## Mudanças da Versão Anterior

### O que mudou?
- ✅ Suporte a **múltiplos sprites** (antes: apenas 1)
- ✅ **Três posições** disponíveis: left, center, right
- ✅ Sistema de **expressões faciais**
- ✅ **Transições suaves** (fade in/out)
- ✅ Comandos mais intuitivos e flexíveis

### Compatibilidade
✅ **Comandos antigos continuam funcionando:**
- `{img_esquerda:nome}` ainda funciona
- `{img_clear}` ainda funciona
- Scripts antigos **não precisam ser atualizados**
