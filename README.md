# Grande_rei

Pequeno motor de visual novel criado com Pygame.

Descrição rápida
- O entrypoint da aplicação é `main.py`. O jogo carrega cenas JSON de `Game/data/script/` e usa classes em `Game/system/` para gestão de cena, personagens, renderização e processamento de texto.

Como executar (desenvolvimento)
1. Crie e ative um ambiente virtual (PowerShell):
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Instale dependências (ex.: `pygame`):
```
pip install pygame
```
3. Execute:
```
python main.py
```

Estrutura principal de pastas
- `main.py` — bootstrap e loop principal.
- `Game/system/` — código do motor: `game.py`, `renderer.py`, `ui_manager.py`, `data_loader.py`, `character_loader.py`, `text_processor.py`.
- `Game/data/script/` — conteúdo do jogo (cenas, personagens). `Cap/` tem capítulos (ex.: `Cap_1/EP_1.json`).
- `Game/data/imgs/` — imagens de fundo e assets usados pelas cenas.

Padrões importantes
- Cenas: cada JSON de episódio tem uma chave de nível superior (ex.: `"EP_1"`) com uma lista de objetos de cena. Cada cena costuma ter `id`, `titulo`, `texto` (lista), `opcoes` (lista de opções), `img_fundo` e possivelmente `x_x` para próxima cena explícita.
- Personagens: arquivos em `Game/data/script/Base/` com `nome` e `cor` (string `r,g,b`). Se um JSON de personagem contém `save`, esse `nome` é considerado o nome do jogador.
- Tokens de texto: placeholders como `[nome_jogador]` e `[Personagem]` são normalizados e substituídos; nomes são então envoltos em `<Name>` para colorização.

Contribuições
- Issue/Pull Request bem descrita. Para mudanças no formato de cena, atualize `DataLoader` e `Game.run()` juntos.

Licença
- Sem licença explícita neste repositório (adicionar se necessário).
