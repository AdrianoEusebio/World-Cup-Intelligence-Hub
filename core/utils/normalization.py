def normalizar_nome_selecao(nome: str) -> str:
    """
    Normaliza o nome da seleção removendo espaços em branco extras e
    garantindo um formato padronizado (Title Case).
    Mantém o nome no idioma original da fonte (inglês) de forma dinâmica.
    """
    if not nome:
        return ""
    return nome.strip().title()
