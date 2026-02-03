class BaseAI:
    """
    Classe base para sistemas de IA de inimigos.
    """
    def __init__(self, owner):
        """
        Inicializa a IA.
        
        Args:
            owner: entidade que possui esta IA
        """
        self.owner = owner

    def update(self):
        """
        Atualiza a lógica da IA.
        Deve ser sobrescrito nas subclasses.
        """
        pass
