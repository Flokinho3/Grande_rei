# Sistema de Sprites de Personagens

## Visão Geral
O sistema de sprites permite exibir imagens de personagens durante as cenas do jogo. Os sprites aparecem automaticamente quando comandos especiais são inseridos no texto das cenas.

## Como Usar

### 1. Preparar a Imagem
Coloque a imagem do personagem em: `Game/data/script/imgs/NPC/`

Exemplo: `Game/data/script/imgs/NPC/yuno.png`

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
No arquivo de cena (ex: `EP_1.json`), adicione o comando no texto:

```json
{
    "texto": [
        "{img_esquerda:yuno}",
        "{yuno}: Olá, seja bem-vindo!"
    ]
}
```

**Importante:** Use o nome normalizado do personagem (minúsculas, sem espaços especiais).

## Comandos Disponíveis

- `{img_esquerda:nome}` - Exibe o sprite do personagem chamado "nome"
- `{img_esquerda:}` ou `{img_clear}` - Remove o sprite atual da tela

## Comportamento

- Apenas **um sprite** é exibido por vez
- O sprite **persiste** entre linhas de texto até ser substituído ou removido
- O sprite é exibido:
  - **Depois** do background
  - **Antes** da caixa de texto (atrás dela)
- Posicionamento automático no lado esquerdo da tela
- Tamanho ajustado automaticamente (máx 30% largura, 60% altura da tela)

## Exemplo Completo

```json
{
    "id": "exemplo",
    "titulo": "Conversa",
    "img_fundo": "sala.png",
    "texto": [
        "{img_esquerda:yuno}",
        "{yuno}: Prazer em conhecê-lo!",
        "Ela sorri gentilmente.",
        "{img_clear}",
        "Ela se afasta..."
    ]
}
```

## Dicas

1. **Resolução das Imagens:** Use imagens PNG com fundo transparente para melhor resultado
2. **Proporção:** Imagens verticais (retrato) funcionam melhor
3. **Tamanho Recomendado:** 500x1000 pixels ou similar
4. **Nome do Arquivo:** Use nomes simples sem espaços (ex: `yuno.png`, `rei.png`)
