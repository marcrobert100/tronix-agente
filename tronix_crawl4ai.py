#!/usr/bin/env python3
"""
tronix_crawl4ai.py — Wrapper Tronix para Crawl4AI
Scraping LLM-friendly para agentes RESEARCH e DEV
Uso: python tronix_crawl4ai.py <url> [--output arquivo.md] [--json] [--search "query"]
"""

import asyncio
import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

try:
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
    HAS_CRAWL4AI = True
except ImportError:
    HAS_CRAWL4AI = False
    print("ERRO: crawl4ai nao instalado. Rode: pip install crawl4ai", file=sys.stderr)
    sys.exit(1)


async def scrape_url(url: str, output: str = None, as_json: bool = False,
                     headless: bool = True, wait: int = 3) -> dict:
    """Scrapa URL e retorna markdown limpo"""
    config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(),
        wait_until="networkidle",
        page_timeout=30000,
    )
    browser_config = BrowserConfig(headless=headless)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=config)

        data = {
            "url": url,
            "title": result.metadata.get("title", "") if result.metadata else "",
            "markdown": result.markdown.raw_markdown if result.markdown else "",
            "success": result.success,
            "timestamp": datetime.now().isoformat(),
        }

        if output:
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            if as_json:
                Path(output).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            else:
                Path(output).write_text(data["markdown"], encoding="utf-8")
            print(f"Salvo: {output}")

        return data


async def search_and_scrape(query: str, num_results: int = 5) -> list:
    """Pesquisa e scrapa top resultados"""
    try:
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        config = CrawlerRunConfig()
        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun(
                url=f"https://www.google.com/search?q={query}",
                config=config
            )
            return [{"query": query, "markdown": results.markdown.raw_markdown if results.markdown else ""}]
    except Exception as e:
        return [{"error": str(e)}]


async def scrape_multiple(urls: list, output_dir: str = "output/crawl4ai") -> list:
    """Scrapa multiplas URLs em paralelo"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    results = []

    config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(),
        wait_until="networkidle",
    )

    async with AsyncWebCrawler() as crawler:
        tasks = []
        for url in urls:
            tasks.append(crawler.arun(url=url, config=config))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for url, resp in zip(urls, responses):
            if isinstance(resp, Exception):
                results.append({"url": url, "error": str(resp)})
            else:
                filename = url.replace("https://", "").replace("http://", "")[:50].replace("/", "_")
                filepath = Path(output_dir) / f"{filename}.md"
                md = resp.markdown.raw_markdown if resp.markdown else ""
                filepath.write_text(md, encoding="utf-8")
                results.append({"url": url, "file": str(filepath), "length": len(md)})

    return results


def main():
    parser = argparse.ArgumentParser(description="Tronix Crawl4AI Wrapper")
    parser.add_argument("url", nargs="?", help="URL para scrapar")
    parser.add_argument("--output", "-o", help="Arquivo de saida")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")
    parser.add_argument("--headless", action="store_true", default=True, help="Browser headless (padrao)")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Browser visivel")
    parser.add_argument("--search", "-s", help="Pesquisar e scrapar")
    parser.add_argument("--multi", nargs="+", help="Scrapar multiplas URLs")
    parser.add_argument("--batch-dir", default="output/crawl4ai", help="Diretorio para batch")

    args = parser.parse_args()

    if args.search:
        results = asyncio.run(search_and_scrape(args.search))
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.multi:
        results = asyncio.run(scrape_multiple(args.multi, args.batch_dir))
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.url:
        data = asyncio.run(scrape_url(args.url, args.output, args.json, args.headless))
        if not args.output:
            print(data["markdown"][:5000])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
