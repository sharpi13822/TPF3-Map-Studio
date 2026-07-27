class Command:
    """
    Basisklasse aller Undo-Kommandos.
    """

    @property
    def name(self):
        return self.__class__.__name__

    def execute(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError