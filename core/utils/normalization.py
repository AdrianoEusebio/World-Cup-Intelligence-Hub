def normalizar_nome_selecao(nome: str) -> str:
    """
    Normaliza o nome da seleção removendo espaços em branco extras e
    garantindo um formato padronizado.
    """
    if not nome:
        return ""
    return nome.strip().title()
