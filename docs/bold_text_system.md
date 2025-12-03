# Sistema de Formatação de Texto - Negrito

## Funcionalidade

O sistema agora suporta texto em **negrito** usando a sintaxe `**texto**` dentro dos campos `"texto"` das cenas.

## Sintaxe

```json
"texto": [
    "Este é um texto normal com uma palavra **importante** em negrito.",
    "Você pode ter **múltiplas** palavras **em negrito** na mesma linha.",
    "**Frases inteiras** também podem ser destacadas."
]
```

## Como Funciona

1. O `TextProcessor` detecta qualquer texto entre `**` duplos asteriscos
2. Renderiza esse texto usando uma fonte em negrito
3. Funciona junto com:
   - Marcadores de nomes coloridos: `<NomePersonagem>`
   - Placeholders: `[nome_jogador]`, `[yuno]`, etc.

## Exemplos Práticos

### Exemplo 1: Ênfase em Diálogos
```json
"texto": [
    "{yuno}: Meu propósito foi **forjado** em mim, camada por camada!",
    "{yuno}: Sou o escudo que **alegremente racha** por você!"
]
```

### Exemplo 2: Narração com Destaque
```json
"texto": [
    "A marca estava gravada profundamente: **Propriedade da Casa Shadow**",
    "Ela não era apenas uma serva. Era uma **arma viva**."
]
```

### Exemplo 3: Combinando Formatações
```json
"texto": [
    "[nome_jogador] olhou para <Yuno> e disse:",
    "{nome_jogador}: Você é **muito** importante para mim, [yuno]."
]
```
Neste exemplo:
- `[nome_jogador]` → substituído pelo nome do jogador
- `<Yuno>` → nome colorido conforme configuração do personagem
- `**muito**` → renderizado em negrito
- `[yuno]` → substituído e colorido

## Notas Técnicas

### Implementação
- Arquivo: `Game/system/text_processor.py`
- Método: `render_wrapped_colored_text()`
- Funciona com quebra automática de linhas
- Compatível com fontes customizadas do UI Manager

### Performance
- Cria uma fonte em negrito na primeira renderização
- Usa cache do Pygame para otimização
- Não impacta significativamente o desempenho

### Limitações
- Os `**` devem estar na mesma linha (não funcionam entre quebras de linha)
- Não é possível aninhar formatações (`**texto **aninhado****` não funciona)
- Espaços dentro dos asteriscos são preservados: `** texto **` inclui os espaços

## Boas Práticas

### ✅ Recomendado
```json
"texto": [
    "A palavra **chave** está destacada.",
    "{yuno}: Minha **lealdade** é absoluta!",
    "**AVISO:** Esta é uma mensagem importante."
]
```

### ❌ Evitar
```json
"texto": [
    "Não faça **texto muito longo em negrito porque pode dificultar a leitura**",
    "**Evite usar** negrito **excessivamente** em **todas** as **palavras**"
]
```

## Guia de Estilo

Use negrito para:
- **Ênfase emocional** em falas importantes
- **Palavras-chave** ou conceitos centrais
- **Avisos** ou informações críticas
- **Títulos** ou nomes de coisas especiais

Evite usar para:
- Blocos grandes de texto (cansa a leitura)
- Texto decorativo (use com propósito)
- Toda linha (perde o efeito de destaque)

## Exemplo Completo

```json
{
    "id": "exemplo_negrito",
    "titulo": "Demonstração de Negrito",
    "img_fundo": "test_bg.png",
    "texto": [
        "Você encara [yuno] e percebe algo diferente em seus olhos.",
        "{yuno}: Mestre, preciso te contar a **verdade**.",
        "{yuno}: Fui treinada não apenas para servir, mas para **proteger**.",
        "{yuno}: E se necessário... para **sacrificar** tudo.",
        "[nome_jogador] sente o peso daquelas palavras.",
        "Há algo de **profundamente errado** com esta situação."
    ],
    "opcoes": [
        {
            "texto": "Perguntar sobre o treinamento",
            "proximo_id": "next_scene"
        }
    ]
}
```

Resultado renderizado (aproximado):
```
Você encara Yuno e percebe algo diferente em seus olhos.
Yuno: Mestre, preciso te contar a verdade. [verdade em negrito]
Yuno: Fui treinada não apenas para servir, mas para proteger. [proteger em negrito]
Yuno: E se necessário... para sacrificar tudo. [sacrificar em negrito]
Jogador sente o peso daquelas palavras.
Há algo de profundamente errado com esta situação. [profundamente errado em negrito]
```

## Compatibilidade

✅ Funciona com:
- Sistema de nomes coloridos
- Placeholders de personagens
- Comandos de sprite `{img_esquerda:}`, etc.
- Quebra automática de linhas
- Todas as cenas existentes

## Testing

Para testar em uma cena nova:
```json
"texto": [
    "Texto normal e **texto em negrito** misturados.",
    "**Linha inteira em negrito**",
    "Palavras **múltiplas** em **destaque**"
]
```

Execute o jogo e navegue até a cena para verificar a renderização.
