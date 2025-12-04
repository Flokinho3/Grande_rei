# Sistema de Exibição Dinâmica de Diálogos e Opções

## 📋 Visão Geral

Sistema que permite criar diálogos e opções que aparecem dinamicamente baseado em:
- Status de personagens (humor, afeto, dedicação, etc)
- Valores do jogador
- Inventário
- Qualquer campo nos JSONs de personagens

---

## 🎯 Funcionalidades

### 1. **Condições em Cenas** (`condicao` em cenas)

Permite que uma cena avalie condições e **redirecione automaticamente** para outra cena.

**Exemplo:**
```json
{
    "id": "1",
    "titulo": "Início do Episódio 2",
    "condicao": [
        {
            "dev": "tratou mal",
            "yuno_humor": "Triste",
            "yuno_afeto": "<=0",
            "proximo_id": "1_1"
        },
        {
            "dev": "tratou bem",
            "yuno_humor": "Feliz",
            "yuno_afeto": ">=10",
            "proximo_id": "1_2"
        },
        {
            "dev": "tratou normal",
            "yuno_humor": "Neutro",
            "yuno_afeto": "1-9",
            "proximo_id": "1_3"
        }
    ]
}
```

**Como funciona:**
1. O jogo avalia cada condição em **ordem**
2. A **primeira** que atender **todas** as condições é escolhida
3. Redireciona automaticamente para o `proximo_id`
4. Campo `dev` é opcional e serve apenas para documentação

### 2. **Condições em Opções** (`condicao` em opcoes)

Permite que opções apareçam ou desapareçam baseado em condições.

**Exemplo:**
```json
{
    "id": "1_3",
    "titulo": "Conversa",
    "texto": ["O que você quer dizer?"],
    "opcoes": [
        {
            "texto": "Opção sempre visível",
            "proximo_id": "2"
        },
        {
            "texto": "Só aparece se afeto >= 5",
            "proximo_id": "3",
            "condicao": {
                "yuno_afeto": ">=5"
            }
        },
        {
            "texto": "Só se humor é Feliz",
            "proximo_id": "4",
            "condicao": {
                "yuno_humor": "Feliz"
            }
        },
        {
            "texto": "Múltiplas condições",
            "proximo_id": "5",
            "condicao": {
                "yuno_afeto": ">=10",
                "yuno_humor": "Feliz",
                "yuno_dedicacao": ">5"
            }
        }
    ]
}
```

**Como funciona:**
- Opções **sem** `condicao` sempre aparecem
- Opções **com** `condicao` só aparecem se **todas** as condições forem atendidas
- Se nenhuma opção atende às condições, o jogador fica sem escolhas (cuidado!)

---

## 📖 Sintaxe de Condições

### ⚡ Formato do Campo - PADRÃO OBRIGATÓRIO

```
{personagem}_{atributo}
```

**✔ SEMPRE use este formato para atributos de personagens:**
- `yuno_afeto` → Campo `afeto` do personagem `Yuno`
- `yuno_humor` → Campo `humor` do personagem `Yuno`
- `thiago_vida` → Campo `vida` do personagem `Thiago`
- `protagonista_coragem` → Campo `coragem` do protagonista
- `chefao_poder` → Campo `poder` do chefão

**✔ Por que este padrão?**
- ✅ Zero ambiguidade - sempre sabe de quem é o atributo
- ✅ Funciona com qualquer personagem (NPCs novos, DLCs, etc)
- ✅ Código robusto - suporta nomes compostos
- ✅ Consistência total em todo o projeto

**❌ O que NÃO fazer:**
- ❌ `afeto` sozinho - de quem é esse afeto?
- ❌ Misturar `yuno_afeto` com `afeto` - caos total
- ❌ Inventar formatos diferentes - quebra tudo

**📌 Exceção: Atributos Globais do Jogador**

Use nomes simples **APENAS** para variáveis realmente globais:
- `dinheiro` - moedas do jogador
- `nivel` - level do jogador
- `inventario_slots` - espaço do inventário
- `capitulo_atual` - progresso na história
- `karma` - sistema de moralidade global

**NUNCA use atributos globais para coisas de personagens!**

### Operadores Suportados

#### 1. **Comparação Numérica**

```json
"yuno_afeto": ">=10"   // Afeto maior ou igual a 10
"yuno_afeto": "<=0"    // Afeto menor ou igual a 0
"yuno_afeto": ">5"     // Afeto maior que 5
"yuno_afeto": "<3"     // Afeto menor que 3
```

#### 2. **Range (Intervalo)**

```json
"yuno_afeto": "1-9"    // Afeto entre 1 e 9 (inclusivo)
"yuno_afeto": "10-20"  // Afeto entre 10 e 20
```

#### 3. **Igualdade Exata**

```json
"yuno_humor": "Feliz"      // Humor é exatamente "Feliz"
"yuno_humor": "Neutro"     // Humor é exatamente "Neutro"
"yuno_status": "Confusa"   // Status contém "Confusa"
```

**Observação:** Comparações de string são **case-insensitive** (`"feliz"` = `"Feliz"`)

---

## 🛠️ Como Usar

### Passo 1: Definir Campos no JSON do Personagem

```json
{
    "nome": "Yuno",
    "humor": "Neutro",
    "afeto": 5,
    "dedicacao": 10,
    "mental": 50
}
```

### Passo 2: Usar `status_infor` para Modificar Valores

```json
{
    "id": "2_1",
    "titulo": "Cumprimentar educadamente",
    "status_infor": {
        "nome": "Yuno",
        "humor": "Feliz",
        "afeto": "+5",
        "dedicacao": "+5",
        "ID": "2_1"
    }
}
```

### 📋 Campo "ID" - Controle de Aplicação Única

O campo `"ID"` previne que o mesmo `status_infor` seja aplicado múltiplas vezes:

**No status_infor (cena JSON):**
```json
"ID": "2_1_1"  // String simples
```

**No arquivo do personagem (Yuno.json):**
```json
{
    "nome": "Yuno",
    "ID": ["2_1", "2_1_1", "2_1_2"]  // Lista de IDs já aplicados
}
```

**Como funciona:**
- ✅ Sistema verifica se o ID do `status_infor` está na lista `ID` do personagem
- ✅ **Se estiver na lista:** Não aplica (já foi aplicado antes)
- ✅ **Se não estiver na lista:** Aplica e adiciona à lista do personagem
- ✅ **Histórico persistente:** IDs ficam salvos no arquivo do personagem

**Exemplo prático:**
```json
// status_infor em cena
{
    "id": "2_1_1",
    "status_infor": {
        "nome": "Yuno",
        "afeto": "+5",
        "ID": "2_1_1"  // Será verificado contra Yuno.json
    }
}

// Yuno.json antes
{
    "nome": "Yuno",
    "ID": ["2_1"]  // Já tem 2_1 aplicado
}

// Sistema verifica: "2_1_1" não está em ["2_1"] → APLICA
// Yuno.json depois
{
    "nome": "Yuno", 
    "ID": ["2_1", "2_1_1"]  // Agora tem os dois
}
```

### Passo 3: Criar Condições Baseadas nos Valores

```json
{
    "id": "10",
    "titulo": "Reação de Yuno",
    "condicao": [
        {
            "yuno_humor": "Feliz",
            "yuno_afeto": ">=10",
            "proximo_id": "10_feliz"
        },
        {
            "yuno_humor": "Triste",
            "proximo_id": "10_triste"
        }
    ]
}
```

---

## 🎮 Exemplos Práticos

### Exemplo 1: Sistema de Relacionamento

```json
{
    "id": "encontro",
    "titulo": "Encontro com Yuno",
    "condicao": [
        {
            "dev": "amizade alta",
            "yuno_afeto": ">=20",
            "proximo_id": "encontro_romantico"
        },
        {
            "dev": "amizade média",
            "yuno_afeto": "10-19",
            "proximo_id": "encontro_amigavel"
        },
        {
            "dev": "amizade baixa",
            "yuno_afeto": "<10",
            "proximo_id": "encontro_distante"
        }
    ]
}
```

### Exemplo 2: Opções Bloqueadas

```json
{
    "id": "dialogo",
    "titulo": "Conversa",
    "texto": ["O que você quer fazer?"],
    "opcoes": [
        {
            "texto": "Conversar normalmente",
            "proximo_id": "conversa_normal"
        },
        {
            "texto": "Fazer uma piada [Requer afeto >= 15]",
            "proximo_id": "fazer_piada",
            "condicao": {
                "yuno_afeto": ">=15"
            }
        },
        {
            "texto": "Falar sobre o passado [Requer afeto >= 25]",
            "proximo_id": "passado",
            "condicao": {
                "yuno_afeto": ">=25",
                "yuno_mental": ">=0"
            }
        }
    ]
}
```

### Exemplo 3: Múltiplas Condições

```json
{
    "id": "cena_especial",
    "titulo": "Momento Especial",
    "condicao": [
        {
            "dev": "rota verdadeira - todas condições perfeitas",
            "yuno_afeto": ">=30",
            "yuno_dedicacao": ">=20",
            "yuno_humor": "Feliz",
            "yuno_mental": ">0",
            "proximo_id": "true_ending"
        },
        {
            "dev": "fallback - condições não atendidas",
            "proximo_id": "normal_ending"
        }
    ]
}
```

---

## 🎯 Boas Práticas e Anti-Padrões

### ✅ FAÇA:

```json
{
    "condicao": {
        "yuno_afeto": ">=10",
        "yuno_humor": "Feliz",
        "protagonista_nivel": ">=5"
    }
}
```

**Por que funciona:**
- Sempre sabe de quem é cada atributo
- Código limpo e previsível
- Fácil de debugar
- Escalável para centenas de personagens

### ❌ NÃO FAÇA:

```json
{
    "condicao": {
        "afeto": ">=10",           ❌ De quem??
        "humor": "Feliz",          ❌ De quem??
        "Yuno_Afeto": ">=10"       ❌ Capitalização inconsistente
    }
}
```

**Por que quebra:**
- Ambiguidade: não sabe de quem é o `afeto`
- Bugs em cascata quando adicionar novos personagens
- Código se torna imprevisível
- Impossível de manter em projetos grandes

### 🔧 Nomenclatura Consistente

```python
# Personagens no código
yuno_afeto          # ✅ lowercase, underscore
yuno_humor          # ✅ lowercase, underscore
tora_forca          # ✅ lowercase, underscore

# NO JSON também
"yuno_afeto": ">=10"   # ✅ Consistente
"Yuno_Afeto": ">=10"   # ❌ Capitalização desnecessária
"yunoAfeto": ">=10"    # ❌ camelCase não funciona
```

### 📦 Estrutura de Personagem Recomendada

```json
{
    "nome": "Yuno",
    "afeto": 0,
    "humor": "Neutro",
    "dedicacao": 10,
    "mental": 50,
    "forca": 15,
    "vida": 100
}
```

**Todos esses campos serão acessados como:**
- `yuno_afeto`
- `yuno_humor`
- `yuno_dedicacao`
- `yuno_mental`
- `yuno_forca`
- `yuno_vida`

---

## 🐛 Debug e Logs

O sistema imprime logs úteis durante a execução:

```
[CONDITION] Yuno: 5 in range [1-9] = True
[CONDITION] humor: 'Neutro' == 'Neutro' = True
[CONDITION] Condição atendida: tratou normal -> 1_3
[RENDERER] Opções filtradas: 4 -> 2
[CONDITION] Opção 'Fazer piada' bloqueada
[CONDITION] Opção 'Conversar' disponível
```

---

## ⚠️ Avisos Importantes

1. **Ordem importa:** Condições de cena são avaliadas em ordem. Coloque as mais específicas primeiro.
2. **Fallback:** Sempre tenha uma condição sem restrições no final como fallback.
3. **Case-insensitive:** Nomes de personagens são case-insensitive (`yuno` = `Yuno`)
4. **ID único:** Não esqueça de usar IDs únicos em `status_infor` para evitar aplicações duplicadas
5. **Opções vazias:** Se todas as opções tiverem condições não atendidas, o jogador ficará preso!

---

## 🎨 Arquivo de Teste

Veja o arquivo `Game/data/script/Cap/Cap_1/EP_2.json` para exemplos completos funcionais.
