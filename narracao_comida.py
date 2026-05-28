#!/usr/bin/env python3
"""Narracao engraçada para video de comida estranha"""
import asyncio
import edge_tts
import os

async def main():
    texto = """
    E AI GENTE! Hoje nos vamos ver esse cara ai comendo a comida mais NOJENTA do mundo!
    Primeiro ele pega... ISSO?! Que diabos e isso?! Parece que ele tirou do LIXO!
    Opa! Ele meteu a colher! EU NAO ACREDITO! Parece que ele ta gostando?! ISSO E CRIME CONTRA A HUMANIDADE!
    Agora ele ta comendo... ISSO! PIOR QUE CHEIRO DE PEIDO DE VACA!
    MEU DEUS! ELE TA COMENDO COM OS OLHOS FECHADOS! O cara ta em outro PLANETA!
    ISSO NAO E COMIDA! ISSO E ARTESANATO! TU NAO PODES COMER ISSO, MEU IRMAO!
    Olha a careta dele! TA PIOR QUE BEBE QUE NAO GOSTA DE CEBOLA!
    Caramba! Ele ta REZANDO antes de comer! QUEM ENSINOU ISSO PRA ELE?!
    E AI?! GOSTOU?! CADE O BANHEIRO?! CORRE, IRMAO, CORRE!
    """

    comunicacao = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural")
    await comunicacao.save("C:/Users/CHCONTE RECPCAO/Desktop/narracao_comida.mp3")
    print("Narracao gerada!")

if __name__ == "__main__":
    asyncio.run(main())
