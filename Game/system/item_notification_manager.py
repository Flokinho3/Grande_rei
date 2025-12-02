"""
Gerenciador de notificações de itens
Responsabilidade: Exibir notificações temporárias quando itens são adicionados ao inventário
"""

from typing import Optional


class ItemNotificationManager:
    """Gerencia notificações temporárias de itens"""
    
    def __init__(self, duration: int = 180, fps: int = 60):
        """
        Inicializa o gerenciador de notificações
        
        Args:
            duration: Duração da notificação em frames (padrão 180 = 3 segundos a 60 FPS)
            fps: Taxa de frames por segundo do jogo
        """
        self.duration = duration
        self.fps = fps
        self.current_item: Optional[str] = None
        self.timer: int = 0
        
    def show_notification(self, item_name: str):
        """
        Exibe uma notificação para um item
        
        Args:
            item_name: Nome ou descrição do item a ser notificado
        """
        self.current_item = item_name
        self.timer = self.duration
        print(f"[ITEM_NOTIFICATION] Notificação: {item_name}")
        
    def update(self):
        """
        Atualiza o timer da notificação (deve ser chamado todo frame)
        """
        if self.timer > 0:
            self.timer -= 1
            if self.timer <= 0:
                self.clear_notification()
                
    def clear_notification(self):
        """
        Remove a notificação atual
        """
        if self.current_item:
            print(f"[ITEM_NOTIFICATION] Notificação removida: {self.current_item}")
        self.current_item = None
        self.timer = 0
        
    def get_current_notification(self) -> Optional[str]:
        """
        Retorna o item atualmente sendo notificado, se houver
        
        Returns:
            Nome do item ou None se não há notificação ativa
        """
        return self.current_item
        
    def is_showing(self) -> bool:
        """
        Verifica se há uma notificação ativa
        
        Returns:
            True se há notificação ativa, False caso contrário
        """
        return self.current_item is not None and self.timer > 0
        
    def get_progress(self) -> float:
        """
        Retorna o progresso da notificação (para animações de fade)
        
        Returns:
            Valor entre 0.0 (início) e 1.0 (fim), ou 0.0 se não há notificação
        """
        if not self.is_showing():
            return 0.0
        return 1.0 - (self.timer / self.duration)
        
    def get_alpha(self, fade_in_duration: int = 15, fade_out_duration: int = 30) -> int:
        """
        Calcula o valor alpha (transparência) baseado no timer para fade in/out
        
        Args:
            fade_in_duration: Frames para fade in (padrão 15 = 0.25s a 60fps)
            fade_out_duration: Frames para fade out (padrão 30 = 0.5s a 60fps)
            
        Returns:
            Valor alpha entre 0 (transparente) e 255 (opaco)
        """
        if not self.is_showing():
            return 0
            
        # Fade in no início
        if self.timer > (self.duration - fade_in_duration):
            elapsed = self.duration - self.timer
            return int((elapsed / fade_in_duration) * 255)
            
        # Fade out no final
        if self.timer < fade_out_duration:
            return int((self.timer / fade_out_duration) * 255)
            
        # Totalmente opaco no meio
        return 255
