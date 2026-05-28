"""
Gerador de Infográfico — InfoEngine
Gera estrutura JSON para templates HTML de infográficos.

Uso: python gerar_infografico.py [--export]
"""

import json
import sys

INFO_PADRAO = {
    "titulo": "Produto Pro Max",
    "subtitulo": "A solução completa que vai transformar seus resultados",
    "estatisticas": [
        {"valor": "+50%", "rotulo": "Mais Resultados"},
        {"valor": "12x", "rotulo": "Sem Juros"},
        {"valor": "7", "rotulo": "Dias de Garantia"},
        {"valor": "+2k", "rotulo": "Clientes"},
    ],
    "beneficios": [
        {
            "icone": "⚡",
            "titulo": "Alta Performance",
            "descricao": "Tecnologia de ponta para máxima eficiência.",
        },
        {
            "icone": "🔒",
            "titulo": "Segurança Total",
            "descricao": "Proteção com criptografia nível empresarial.",
        },
        {
            "icone": "📱",
            "titulo": "Multiplataforma",
            "descricao": "Funciona em qualquer dispositivo.",
        },
        {
            "icone": "🤝",
            "titulo": "Suporte Premium",
            "descricao": "Atendimento 24 horas em português.",
        },
    ],
    "especificacoes": {
        "Capacidade": "Ilimitada",
        "Velocidade": "Até 10 Gbps",
        "Armazenamento": "1 TB SSD",
        "Conexão": "5G / Wi-Fi 7",
        "Bateria": "72 horas",
        "Garantia": "12 meses",
    },
    "preco": {
        "original": 4997.00,
        "atual": 1997.00,
        "parcelas": 12,
        "valor_parcela": 199.70,
    },
    "depoimento": {
        "texto": "Comprei há 3 meses e já vi resultado na primeira semana.",
        "autor": "Carolina M., São Paulo",
    },
}


def exportar_json(dados=None, caminho="infografico.json"):
    """Exporta os dados do infográfico como JSON."""
    if dados is None:
        dados = INFO_PADRAO
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"Infográfico exportado: {caminho}")
    return caminho


def resumo(dados=None):
    """Exibe um resumo do infográfico no terminal."""
    if dados is None:
        dados = INFO_PADRAO
    print(f"Título: {dados['titulo']}")
    print(f"Estatísticas: {len(dados['estatisticas'])}")
    print(f"Benefícios: {len(dados['beneficios'])}")
    print(f"Especificações: {len(dados['especificacoes'])}")
    print(f"Preço: R$ {dados['preco']['atual']:.2f}")


TEMPLATES_DISPONIVEIS = [
    "vendas", "social-post", "dados", "comparativo",
]


if __name__ == "__main__":
    print("=== InfoEngine — Gerador de Infográfico ===")
    print(f"Título: {INFO_PADRAO['titulo']}")
    print(f"Benefícios: {len(INFO_PADRAO['beneficios'])}")
    print(f"Templates disponíveis: {', '.join(TEMPLATES_DISPONIVEIS)}")

    if "--export" in sys.argv:
        exportar_json()
    else:
        resumo()
