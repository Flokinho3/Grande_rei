# Sistema de Cômodos/Salas Interativas

## Visão Geral

O sistema permite criar "loops" interativos onde o jogador pode explorar um cômodo até completar certas ações ou escolher sair. O jogo automaticamente retorna para o ponto exato onde o jogador estava antes de entrar no cômodo.

## Estrutura de Arquivos

### Localização dos Cômodos
Os cômodos devem ser colocados em:
```
Game/data/script/Cap/Cap_X/Comodos/nome_do_comodo.json
```

### Formato do Arquivo JSON

```json
{
    "nome_do_comodo": [
        {
            "id": "entrada",
            "titulo": "Título da Cena",
            "img_fundo": "background.png",
            "texto": [
                "Texto da cena..."
            ],
            "opcoes": [
                {
                    "texto": "Opção 1",
                    "proximo_id": "outra_cena"
                },
                {
                    "texto": "Sair",
                    "proximo_id": "saida"
                }
            ]
        },
        {
            "id": "saida",
            "titulo": "Saindo",
            "texto": ["Você sai..."],
            "return_to_caller": true
        }
    ]
}
```

## Como Funciona

### 1. Entrada no Cômodo

No arquivo principal (ex: `EP_2.json`), use o nome do cômodo como `proximo_id`:

```json
{
    "id": "1_2",
    "texto": ["Você chega ao quarto..."],
    "opcoes": [
        {
            "texto": "Entrar no quarto.",
            "proximo_id": "quarto_1"
        }
    ]
}
```

### 2. Navegação no Cômodo

O jogador pode navegar livremente entre as cenas do cômodo usando `proximo_id` normalmente.

### 3. Saída do Cômodo

Para sair, crie uma cena com `"return_to_caller": true`:

```json
{
    "id": "saida",
    "titulo": "Saindo",
    "texto": ["Texto de saída..."],
    "return_to_caller": true
}
```

Quando o jogador chegar nesta cena, o sistema automaticamente:
1. Restaura as cenas do episódio anterior
2. Volta para o `scene_id` exato onde estava
3. Mantém o `text_index` correto

## Recursos Adicionais

### Flags (Marcar Ações Realizadas)

Use `set_flag` para marcar que o jogador realizou uma ação:

```json
{
    "id": "ler_papeis",
    "texto": ["Você lê os papéis..."],
    "set_flag": "leu_papeis",
    "opcoes": [...]
}
```

Para múltiplas flags na mesma cena, use `set_flag2`:

```json
{
    "id": "pegar_chave",
    "texto": ["Você encontra uma chave..."],
    "set_flag": "revisou_gavetas",
    "set_flag2": "tem_chave_bau",
    "add_item": "Chave de Bronze",
    "opcoes": [...]
}
```

### Condições Baseadas em Flags

Use condições para mostrar/ocultar opções baseado em flags:

```json
{
    "opcoes": [
        {
            "texto": "Ler os papéis",
            "proximo_id": "ler_papeis",
            "condicao": {
                "flag": "!leu_papeis"
            }
        },
        {
            "texto": "Abrir baú com a chave",
            "proximo_id": "abrir_bau",
            "condicao": {
                "flag": "tem_chave_bau"
            }
        }
    ]
}
```

**Sintaxe de Flags:**
- `"flag": "nome_flag"` - Verifica se a flag está definida
- `"flag": "!nome_flag"` - Verifica se a flag NÃO está definida (note o `!`)

## Exemplo Completo: Tutorial Interativo

### EP_2.json (Arquivo Principal)
```json
{
    "EP_2": [
        {
            "id": "1_2",
            "texto": [
                "Yuno o leva até seus aposentos.",
                "Deseja entrar?"
            ],
            "opcoes": [
                {
                    "texto": "Entrar no quarto.",
                    "proximo_id": "quarto_1"
                }
            ]
        }
    ]
}
```

### quarto_1.json (Cômodo)
```json
{
    "quarto_1": [
        {
            "id": "entrada",
            "texto": ["Você entra no quarto. O que fazer?"],
            "opcoes": [
                {
                    "texto": "Examinar cama",
                    "proximo_id": "cama"
                },
                {
                    "texto": "Examinar escrivaninha",
                    "proximo_id": "escrivaninha"
                },
                {
                    "texto": "Sair",
                    "proximo_id": "saida"
                }
            ]
        },
        {
            "id": "cama",
            "texto": ["A cama é confortável..."],
            "opcoes": [
                {"texto": "Voltar", "proximo_id": "entrada"}
            ]
        },
        {
            "id": "escrivaninha",
            "texto": ["Há documentos importantes aqui."],
            "set_flag": "examinou_escrivaninha",
            "opcoes": [
                {"texto": "Voltar", "proximo_id": "entrada"}
            ]
        },
        {
            "id": "saida",
            "texto": ["Você sai do quarto."],
            "return_to_caller": true
        }
    ]
}
```

## Stack de Salas

O sistema suporta múltiplos níveis de salas (sala dentro de sala):
- Jogador em EP_2 → entra em quarto_1 → pode entrar em armario_secreto → etc.
- Ao sair, retorna exatamente ao ponto anterior em cada nível

## Debugging

O sistema imprime logs úteis:
```
[GAME] Entrando no cômodo: quarto_1
[GAME] Estado salvo: scene_id=1_2, text_index=5
[GAME] Cômodo carregado. Iniciando em: entrada
...
[GAME] Cena com return_to_caller detectada
[GAME] Saindo do cômodo
[GAME] Estado restaurado: scene_id=1_2, text_index=5
```

## Vantagens do Sistema

1. **Loop Natural**: O jogador pode explorar livremente até decidir sair
2. **Flags Persistentes**: Ações marcadas permanecem entre visitas
3. **Retorno Preciso**: Volta exatamente ao ponto onde estava
4. **Aninhamento**: Suporta salas dentro de salas
5. **Condições Flexíveis**: Pode bloquear/desbloquear opções dinamicamente
