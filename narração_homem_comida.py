#!/usr/bin/env python3
"""Narração engraçada para video de comida estranha"""
import asyncio
import edge_tts
import os

async def main():
    texto = """
    E AÍ GENTE! Hoje nós vamos ver esse cara aí comendo a comida mais NOJENTA do mundo!
    Primeiro ele pega... ISSO?! Que diabos é isso?! Parece que ele tirou do LIXO!
    Opa! Ele meteu a colher! EU NÃO ACREDITO! Parece que ele tá gostando?! ISSO É CRIME CONTRA A HUMANIDADE!
    Agora ele tá comendo... ISSO! PIOR QUE CHEIRO DE PEIDO DE VACA!
    MEU DEUS! ELE TÁ COMENDO COM OS OLHOS FECHADOS! O cara tá em outro PLANETA!
    ISSO NÃO É COMIDA! ISSO É ARTESANATO! TU NÃO PODES COMER ISSO, MEU IRMÃO!
    Olha a careta dele! TÁ PIOR QUE BEBÊ QUE NÃO GOSTA DE CEBOLA!
    Caramba! Ele tá REZANDO antes de comer! QUEM ENSINOU ISSO PRA ELE?!
    E AÍ?! GOSTOU?! CADE O BANHEIRO?! CORRE, IRMÃO, CORRE!
    """

    comunicacao = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural")
    await comunicacao.save("C:/Users/CHCONTE RECPÇÃO/Desktop/narracao_comida.mp3")
    print("Narração gerada!")

if __name__ == "__main__":
    asyncio.run(main())
