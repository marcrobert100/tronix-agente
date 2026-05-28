"""
Criador de Histórias Infantis — InfoEngine
Gera estrutura JSON para templates HTML de livros infantis.
"""

import json

HISTORIA_PADRAO = {
    "titulo": "O Sonho da Estrelinha Lua",
    "subtitulo": "Uma história para embalar os sonhos",
    "autor": "Marcos Roberto",
    "faixa_etaria": "2 — 6 anos",
    "paginas": [
        {
            "numero": 1,
            "titulo": "Lá no céu...",
            "texto": "Lá no céu, bem alto, morava uma estrelinha chamada Lua. Ela era a menor de todas, mas tinha o brilho mais bonito que já existiu. Todas as noites, Lua acordava com o pôr do sol e se preparava para iluminar o céu. Mas havia um problema: a Estrelinha Lua estava com muito sono!",
            "dialogue": "Ai, que soninho! Será que as crianças lá embaixo também estão com sono?",
            "ilustracao": "estrela_bocejando",
            "cor_topo": "var(--coral-400)"
        },
        {
            "numero": 2,
            "titulo": "A Fada dos Sonhos",
            "texto": "Foi quando uma luz suave e dourada apareceu ao seu lado. Era a Fada dos Sonhos, com seu vestido feito de névoa e cabelos de luar.",
            "dialogue": "Estrelinha Lua, por que você está tão cansada?",
            "ilustracao": "fada_magica",
            "cor_topo": "var(--pastel-lavender)"
        },
        {
            "numero": 3,
            "titulo": "O segredo do sono",
            "texto": "Lua arregalou os olhos. — De verdade? — Sim! E sabe o que mais? Lá embaixo, tem uma criança que também não consegue dormir. Ela precisa de você. Quando você brilha, as crianças sabem que está tudo bem. Seu brilho é como um abraço quentinho vindo do céu.",
            "dialogue": "Querida estrelinha, deixe eu te contar um segredo: quando você dorme, seu brilho descansa. E quando descansa, ele fica ainda mais forte!",
            "ilustracao": "segredos_subindo",
            "cor_topo": "var(--gold-400)"
        },
        {
            "numero": 4,
            "titulo": "A criança acordada",
            "texto": "Lua olhou para baixo e viu uma casinha com uma luz acesa. Dentro, um menino chamado Pedro estava sentado na cama, olhando pela janela. Ele não conseguia dormir. Pensava em dragões, em monstros debaixo da cama e em sombras estranhas no corredor.",
            "dialogue": "Oi, estrelinha...",
            "ilustracao": "quarto_pedro",
            "cor_topo": "var(--pastel-blue)"
        },
        {
            "numero": 5,
            "titulo": "Um brilho de amizade",
            "texto": "Lá no céu, a Estrelinha Lua entendeu o pedido. Ela se sentou bem pertinho da janela de Pedro e começou a brilhar com toda a força do seu coração. Seu brilho dançava como uma música suave.",
            "dialogue": "Vou fazer um pedido: queria que a estrelinha ficasse comigo até eu dormir.",
            "ilustracao": "coracao_conexao",
            "cor_topo": "var(--pastel-lavender)"
        },
        {
            "numero": 6,
            "titulo": "A dança das estrelas",
            "texto": "Uma a uma, as outras estrelas foram acordando. Viram Lua brilhando com tanto carinho para o menino e resolveram ajudar. Formaram um círculo de luz ao redor da casa de Pedro.",
            "dialogue": "Olha só — quando a gente se junta, a noite fica mais bonita!",
            "ilustracao": "danca_estrelas",
            "cor_topo": "var(--pastel-peach)"
        },
        {
            "numero": 7,
            "titulo": "O sono chegou",
            "texto": "O quarto de Pedro foi ficando mais quentinho. Seu cobertor parecia uma nuvem macia. Ele estava sonhando. Sonhando que voava entre as estrelas, montado numa nuvem fofinha.",
            "dialogue": "Obrigado, estrelinha...",
            "ilustracao": "sonho_nuvem",
            "cor_topo": "var(--pastel-blue)"
        },
        {
            "numero": 8,
            "titulo": "Hora de descansar",
            "texto": "E assim, a Estrelinha Lua fechou os olhos. Seu brilho foi ficando suave, suave, como a respiração de um bebê dormindo. Lá embaixo, Pedro também dormia. Os dois, juntos, no mesmo sonho.",
            "dialogue": "Viu só? Você conseguiu! Agora pode dormir tranquila.",
            "ilustracao": "estrela_dormindo",
            "cor_topo": "var(--pastel-lavender)"
        }
    ]
}


def exportar_json(historia=None, caminho="historia.json"):
    """Exporta a história como JSON."""
    if historia is None:
        historia = HISTORIA_PADRAO
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(historia, f, ensure_ascii=False, indent=2)
    print(f"História exportada: {caminho}")
    return caminho


def listar_templates_disponiveis():
    """Lista as ilustrações disponíveis no sistema."""
    return [
        "estrela_bocejando",
        "fada_magica",
        "segredos_subindo",
        "quarto_pedro",
        "coracao_conexao",
        "danca_estrelas",
        "sonho_nuvem",
        "estrela_dormindo",
    ]


if __name__ == "__main__":
    print("=== InfoEngine — Criador de Histórias ===")
    print(f"Título: {HISTORIA_PADRAO['titulo']}")
    print(f"Páginas: {len(HISTORIA_PADRAO['paginas'])}")
    print(f"Templates disponíveis: {len(listar_templates_disponiveis())}")
    exportar_json()
