#!/usr/bin/env python3
"""
TRONIX AI — Demo de navegação (5 min, sem HUD)
Testa as tools de navegação direto, no terminal.
  python demo_navegacao.py play
  python demo_navegacao.py info
  python demo_navegacao.py trending
  python demo_navegacao.py browser
  python demo_navegacao.py tudo
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


class DummyPlayer:
    """Substituto do HUD PyQt6 — logs no terminal."""

    def __init__(self):
        self.muted = True

    def write_log(self, text: str):
        print(f"[LOG] {text}")

    def show_content(self, title: str, text: str):
        print(f"[CONTEUDO] {title}:\n{text}\n")


def demo_play(player):
    from actions.youtube_video import youtube_video
    print("=" * 60)
    print("1) YOUTUBE — tocar 'JRPG 2026' (abre no navegador padrao)")
    print("=" * 60)
    r = youtube_video(parameters={"action": "play", "query": "JRPG 2026"}, player=player)
    print(f"-> {r}")


def demo_info(player):
    from actions.youtube_video import youtube_video
    print("=" * 60)
    print("2) YOUTUBE — info do video (site do HomeLab do Marcos)")
    print("=" * 60)
    r = youtube_video(
        parameters={"action": "get_info", "url": "https://www.youtube.com/watch?v=ud7wzdiM0gk"},
        player=player, speak=lambda t: print(f"[FALA] {t}"),
    )
    print(f"-> {r}")


def demo_trending(player):
    from actions.youtube_video import youtube_video
    print("=" * 60)
    print("3) YOUTUBE — trending Brasil")
    print("=" * 60)
    r = youtube_video(
        parameters={"action": "trending", "region": "BR"},
        player=player, speak=lambda t: print(f"[FALA] {t}"),
    )
    print(f"-> {r}")


def demo_browser(player):
    from actions.browser_control import browser_control
    print("=" * 60)
    print("4) BROWSER — abrir site (playwright)")
    print("=" * 60)
    r = browser_control(parameters={"action": "go_to", "url": "https://opencode.ai"}, player=player)
    print(f"-> {r}")


def demo_search(player):
    from actions.web_search import web_search
    print("=" * 60)
    print("5) WEB SEARCH — noticias do Jellyfin")
    print("=" * 60)
    r = web_search(parameters={"query": "Jellyfin news", "mode": "news"}, player=player)
    print(f"-> {r}")


def demo_arquivos(player):
    from actions.file_controller import file_controller
    print("=" * 60)
    print("6) ARQUIVOS — listar Desktop")
    print("=" * 60)
    r = file_controller(parameters={"action": "list", "path": "desktop"}, player=player)
    print(f"-> {r}")


def main():
    player = DummyPlayer()
    what = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    steps = {
        "play":     demo_play,
        "info":     demo_info,
        "trending": demo_trending,
        "browser":  demo_browser,
        "search":   demo_search,
        "arquivos": demo_arquivos,
        "tudo":     lambda p: [f(p) for f in
                    [demo_play, demo_info, demo_trending, demo_browser, demo_search, demo_arquivos]],
    }
    steps.get(what, lambda p: print("Uso: play|info|trending|browser|search|arquivos|tudo"))(player)
    print("\n[demo] Fim. 5 min e pronto.")


if __name__ == "__main__":
    main()