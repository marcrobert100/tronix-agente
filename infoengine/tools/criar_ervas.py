#!/usr/bin/env python3
"""Gerador do ebook 'ERVAS — Indicações e Usos' — InfoEngine.

Transforma o conteúdo do documento .doc em um ebook digital
página a página, com capa, índice, seções e navegação completa.

Uso:
    python tools/criar_ervas.py
    -> gera examples/ervas_book.json
    -> gera output/ervas.html  (ebook pronto, auto-contido)
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA_JSON = RAIZ / "examples" / "ervas_book.json"
SAIDA_HTML = RAIZ / "output" / "ervas.html"

AUTOR = "Marcos Roberto"
MARCA = "Pesquisador das Matas"
LOCAL = "Viçosa — Alagoas · Brasil"
YOUTUBE_NOME = "Pesquisador das Matas Viçosa Alagoas"
YOUTUBE_URL = "https://www.youtube.com/results?search_query=pesquisador+das+matas+vicosa"
EMAIL = "silvamrs100@gmail.com"
WHATSAPP = "5582991856656"

# --------------------------------------------------------------------------
# CONTEÚDO — transcrito do documento original
# --------------------------------------------------------------------------

INTRO_PARAGRAFOS = [
    "Um corpo saudável é, sem dúvida, um ótimo instrumento para a canalização das energias que desenvolvemos quase que diariamente. E a saúde é um bem precioso que podemos conservar mantendo uma boa e equilibrada alimentação.",
    "Muitas doenças, provocadas por desequilíbrios energéticos, podem ser curadas através da alimentação; outras podem ser evitadas; e em algumas já instaladas, agregando-se a alimentação ao tratamento médico, alcançamos a cura com mais rapidez.",
    "A seguir, uma lista de vegetais, ervas e frutos, bem como suas propriedades, auxiliam não só no combate a doenças como atuam no perfeito funcionamento do organismo.",
    "Sempre se deve ter atenção especial: em doenças já instaladas, o tratamento médico é imprescindível. A alimentação, nesses casos, vem somar para uma cura mais rápida — mas não substitui as prescrições médicas. Mantenha uma alimentação saudável e evite a desarmonia orgânica que provoca as doenças.",
]

ERVAS_PARA = [
    ("Meditação", "ânula, zimbro, bálsamo-de-tolu, ciperácea, sálvia esclaréia, giesta, glicínia, sândalo, câlamo-aromático, magnólia, mirra"),
    ("A Sorte", "canela, jasmim, lótus, jacinto, baunilha, cumaru, gerânio, noz-moscada, bergamota, cipreste"),
    ("Atrair Sucesso e Promoções", "azálea, cravo-de-defunto, olíbano, hortelã-pimenta, erva-cidreira, hissopo"),
    ("O Amor", "ervilha-de-cheiro, lótus, jacinto, baunilha, bétula, camélia, coentro, lírio-florentino, rosa, cumarina, laranja-azeda"),
    ("Clarividência e Estímulo da Mente", "açafrão, capim-limão, louro, anis-estrelado, babosa, aipo, cânfora, ânula, zimbro, estoraque, funcho, madressilva, cacto, câlamo-aromático, gengibre"),
    ("Sonhos Proféticos", "peônia, mimosa, amarílis, giesta"),
    ("Afastar Energias Negativas", "cânfora, comigo-ninguém-pode, guiné, arruda, alecrim, espada-de-são-jorge"),
    ("Melhorar as Finanças", "camomila, olíbano, alfazema, erva-cidreira, cedro, hissopo, cipreste, abóbora"),
    ("Amizades", "ervilha-de-cheiro, urze, citronela, erva-cidreira"),
    ("Contra Magia Negra", "alecrim, louro, jasmim, cenoura, violeta, hortelã-pimenta, verbena, assa-fétida, gerânio, manjericão, patchouli, hissopo, noz-moscada, bergamota"),
]

BANHOS = [
    ("Felicidade", "manjerona, cravo, alecrim, canela, 1/2 xícara de álcool de cereais"),
    ("Proteção Contra Perigos", "espada-de-são-jorge, guiné, arruda e hortelã"),
    ("Proteger Seu Amor", "rosa branca, erva-cidreira, palma branca"),
]

FUNCAO_ENERGETICA = [
    ("Alecrim", "Ajuda a perdoar mágoas"),
    ("Alfazema", "Aumenta a autoconfiança"),
    ("Anis-estrelado", "Ajuda com os sentimentos e na liberação de emoções"),
    ("Arnica", "Promove a concentração de pensamentos"),
    ("Artemísia", "Estimula a ação e a manifestação das ideias"),
    ("Arruda", "Limpa a aura das sujeiras astrais"),
    ("Babosa", "Ajuda no desligamento mental"),
    ("Camomila", "Ajuda a cultivar a paciência e a confiança"),
    ("Cânfora", "Promove o desprendimento material"),
    ("Capuchinha", "Promove o sentimento de integridade e equilíbrio"),
    ("Carqueja", "Limpa o corpo das velhas emoções"),
    ("Confrei", "Estimula o sentimento de segurança pessoal"),
    ("Dente-de-leão", "Traz coragem para enfrentar os obstáculos"),
    ("Erva-cidreira", "Ajuda na tomada de decisões importantes da vida"),
    ("Guiné", "Limpa o corpo de energias negativas"),
    ("Mil-folhas", "Purifica o corpo de traumas e sentimentos negativos"),
    ("Sabugueiro", "Ajuda na tomada de rápidas decisões"),
    ("Sálvia", "Dá ânimo para colocar em movimento todas as energias do corpo"),
    ("Tanchagem", "Estimula a iniciativa"),
]

USO_MEDICINAL = [
    ("Abacate", "Persea gratissima", "O abacate pode substituir a carne, porque contém gordura e o mesmo valor nutritivo. O abacateiro serve especialmente aos diabéticos, tanto através da fruta como das folhas. Às pessoas atacadas por esse mal é aconselhável um tratamento à base do abacateiro, durante quinze dias: comer em jejum metade de um abacate amassado; após as refeições tomar um chá de folhas SECAS do abacateiro, sem açúcar. Outra indicação das folhas do abacateiro é para a limpeza do fígado: se o fígado não vai bem por estar saturado de gordura e tóxicos, fazer um chá das folhas SECAS do abacateiro e tomá-lo em goles, de hora em hora, durante todo o dia, repetindo por 15 dias. O caroço serve como tônico capilar. Em dores de cabeça, aplicar folhas quentes do abacateiro sobre a cabeça, em compressa. Usar sempre folhas secas, pois as verdes provocam palpitações cardíacas."),
    ("Abacaxi", "Ananás sativus", "O abacaxi, além de ótimo purificador do sangue, é diurético e ajuda a digestão. Sua indicação notável é no tratamento das feridas, inflamações e infecções. Em infecções agudas, consumido em fatias, é um ótimo parceiro dos antibióticos. Contra tosse catarral, usa-se duas colheres de suco de abacaxi diluídas em uma xícara de água quente e uma colher de mel. Beber bastante quente antes de deitar-se."),
    ("Abóbora", "Cucúrbita pepo", "Rica em potássio, ferro, fósforo e magnésio, é eficaz como diurético e para combater a prisão de ventre. Faz-se um suco fresco com pedaços grossos de abóbora madura, colocando-os em um guardanapo e torcendo para extrair o suco. Adoçar com pouco açúcar e tomar uma manhã sim e uma não, em jejum, por um mês."),
    ("Acelga", "Beta vulgaris", "Hortaliça indicada para oxigenar o sangue e normalizar a digestão, além de acalmar os nervos e robustecer o cérebro. É muito útil para ser ingerida por pessoas nervosas."),
    ("Agrião", "Nasturtium officinale", "O agrião é tão eficaz que não se deve usá-lo diariamente, a não ser para tratamento dos brônquios, durante períodos limitados. A quantidade de ferro, iodo e vitaminas que contém faz passar para a água em que é deixado de molho uma boa parte de sua força; por isso, uma receita para a carência de ferro e para a depuração do sangue é chamada de Água de Agrião: em um copo de água na temperatura ambiente, mergulhar folhas de agrião. Cobrir o copo e deixá-lo no quarto de dormir. De manhã, coar e bebê-la sem açúcar. As propriedades terapêuticas do agrião combatem o raquitismo, o ácido úrico e as doenças do pulmão, agindo na purificação do fígado e do estômago. Os fumantes devem fazer uso do agrião, uma vez por semana, para a desintoxicação do organismo. O seu suco, adoçado com mel, é um excelente xarope para combater bronquite, tosse, tuberculose pulmonar e toda sorte de enfermidades catarrais. Usa-se em saladas para combater a diabetes, e no consumo diário para os que sofrem de ácido úrico."),
    ("Aipo", "Apium graveolens", "Essa verdura combate a depressão. Por ser rico em cloreto de sódio, é ideal para casos de insônia e perturbações nervosas, podendo entrar no preparo de saladas, ser bebido como suco ou mesmo mastigando seus talos. Como alimento é recomendado àqueles que sofrem de artrite, reumatismo e ácido úrico. É também indicado seu uso externo em frieiras; para tanto, colocar 100g de aipo em um litro de água e ferver lentamente por 20 minutos. Dar um banho bem quente nos pés ou mãos, uma vez por dia."),
    ("Alface", "Lactuca sativa", "Contém várias vitaminas e é uma fonte de ferro e minerais. Seu poder de limpeza dos intestinos é fantástico. Fortalece o sistema nervoso e a musculatura, além de ajudar a digestão. É um grande calmante para os nervos e combate a insônia mais recalcitrante. Um chá para dormir é feito fervendo-se rapidamente duas folhas de alface fresca em uma xícara de chá de água. Tomar morno na hora de deitar-se. É ainda recomendada contra as doenças do coração e dos rins, seja em forma de chá ou saladas, estas com pouco azeite, vinagre e sal. Para contusões e inchaços, fazer uma cataplasma fervendo algumas folhas de alface em pouca água por cinco minutos. Deixar amornar, untar as folhas com azeite de oliva, estender sobre uma gaze e aplicar na região atingida. Este mesmo método pode ser usado para irritações e rubores da pele."),
    ("Alho", "Allium sativum", "O alho purifica o sangue, atua sobre as mucosas do nariz, da garganta e dos pulmões, desinfeta todo o organismo e funciona como antibiótico para combater infecções. Para o enfraquecimento do organismo, principalmente nos idosos, consumir durante as refeições um dente de alho bem amassado com uma cenoura; isso previne contra doenças mais graves. Atua na circulação — e para esses problemas, consumir pão de centeio temperado com alho socado, salsa e gotas de azeite, sendo este o primeiro alimento do dia, repetido por uma semana; descansar 15 dias e fazer novamente, assim sucessivamente. O alho cozido tem grande perda de sua eficácia; cru em grande quantidade irrita os rins."),
    ("Almeirão", "Chicorium intybus", "Rico em vitamina A e C. Indicado para falta de apetite, usado cru em saladas ou ligeiramente refogado."),
    ("Ameixa", "Prunus domestica", "Poderoso laxante. Indicada contra prisão de ventre, sendo, neste caso, consumida seca. É rica em potássio, fósforo, cálcio e minerais. Para problemas do estômago faz-se um licor digestivo de ameixa: cozinhar em dois litros e meio de vinho branco, 20 ameixas frescas sem casca e sem caroço. Depois de quinze minutos, apagar o fogo, adicionando no máximo 3 gramas de casca de canela, e deixar macerar. Após três dias, filtrar o líquido, adicionar meio quilo de açúcar e colocar no fogo, deixando ferver por alguns minutos. Esperar esfriar totalmente e adicionar meio litro de álcool a 90 graus, colocando em uma ou duas garrafas. Tomar um cálice após as refeições."),
    ("Aspargo", "Asparagus officinalis", "O aspargo deve ser ingerido ao natural, já que quando cozido pode irritar os rins, tornando contrário o seu efeito de limpá-los. É indicado nas doenças do fígado, do baço e do estômago. Nos problemas do coração combate a hipertrofia e acalma as palpitações. Para o coração se faz uma decocção fervendo 50g de raízes de aspargo em um litro de água, deixando em repouso até esfriar. Tomar três cálices por dia, entre as refeições principais, sem adoçar. Ainda pode ser usado em regimes de emagrecimento fervendo em três quartos de litro de água 40g de raízes de aspargo. Bebe-se pela manhã em jejum e durante todo o dia. Esta mesma decocção pode ser administrada a pessoas nervosas e excitáveis."),
    ("Aveia", "Avena sativa", "Fonte natural de vitaminas, proteínas e sais minerais, contendo muitas calorias. Usada em flocos ou farinha, adapta-se aos organismos delicados, garantindo um bom funcionamento dos intestinos preguiçosos. É também anti-hemorróidas; sua ingestão tem a virtude de reduzir o teor de gorduras e de açúcar do sangue, auxiliando nas arterioscleroses e no diabetes. Contra ácido úrico, ferver um punhado de palha de aveia triturada em um litro de água, coar e beber durante o dia."),
    ("Azeitona", "Olea europaea", "Uma curiosidade sobre a oliveira: conta-se que Atenas, a deusa grega da sabedoria, fez nascer de uma lança a oliveira. Os frutos dessa árvore, além de alimentarem o homem, produziriam um óleo para temperar sua comida, fortalecer seu corpo, curar as suas feridas e iluminar sua noite. A azeitona tem grande teor de gordura e sais minerais, devendo ser consumida com cautela."),
    ("Banana", "Musa paradisiaca", "Bastante nutritiva e regulariza as funções do intestino. O suco da banana São Tomé é particularmente indicado contra a diarréia. Emprega-se o suco das flores nas afecções do peito. Do tronco se extrai a seiva que é indicada para a laringite, as aftas, como tônico capilar e soro antiofídico."),
    ("Batata", "Solanum tuberosum", "Rica em carboidratos e vitaminas. Usada crua, tem aplicação para combater dores de cabeça (colocadas em rodelas sobre a testa) e contra irritações da pele. A batata-baroa é bastante indicada para quem sofre de doenças renais. Para eritemas ou queimaduras solares, faz-se uma compressa com batata ralada, trocada três vezes ao dia. O suco feito com batata é excelente remédio para úlceras do estômago e do duodeno, desde que tomado em pequenas doses, pois o seu uso exagerado pode provocar sintomas de intoxicação. A água do cozimento da batata serve para prevenir e combater a gota."),
    ("Brócolos", "Brassica oleracea", "Rico em vitamina C, fósforo, potássio e enxofre. É melhor consumi-lo em saladas cruas para aproveitar todo o seu valor nutritivo. É um ótimo alimento para dietas de emagrecimento, já que produz uma limpeza geral do organismo e elimina gorduras."),
    ("Café", "Coffea arabica", "É contraindicado para pessoas nervosas e insones. Adoçado com mel, serve de remédio para a angina do peito. É um excitante do sistema nervoso, dos músculos, cérebro, rins e coração. É usado para lavar ulcerações das pernas. Facilita a digestão."),
    ("Camomila", "Matricaria chamomilla", "Indicada para cólicas de crianças, feito chá. É também calmante, antiespasmódico e sonífero, devendo ser feito o chá na hora de tomar. Indicada para dores reumáticas: neste caso usam-se as flores secas, cozidas em banho-maria no óleo; após duas horas de cozimento, côa-se e, depois de frio, massageia-se com esse óleo as regiões doloridas. Usa-se o chá também para combater dores abdominais, cólicas intestinais com gases, cistite, inflamações bucais e conjuntivites."),
    ("Canela", "Cinnamomum zeylanicum", "Em doces, não se discute, é um ótimo tempero. Suas propriedades medicinais estão no combate à anemia; para isso, tomar um chá da casca de canela quatro vezes ao dia. Recomendada também para catarro nos brônquios. É indicada na atonia gástrica (fraqueza do estômago), como tintura: colocar 50g de casca de canela em um quarto de litro de álcool a 60 graus. Depois de 24 horas, filtrar o líquido e coá-lo em uma garrafa, consumindo-o em colheres antes das refeições."),
    ("Cebola", "Allium cepa", "Deve ser sempre ingerida crua, já que cozida perde suas propriedades. Combate vermes intestinais, infecções e resfriados. O consumo diário de cebola previne doenças cardíacas, como também impede o desenvolvimento das já existentes."),
    ("Cenoura", "Daucus carota", "Indicada para as vistas, já que é rica em vitamina A. Atua também como purificadora do fígado e fortifica o organismo. Para casos de digestão difícil, usa-se ferver uma pitada de sementes de cenoura em um cálice de água e beber após as refeições (neste caso, as sementes precisam ser retiradas do pé, visto que as destinadas a plantio possuem agrotóxicos prejudiciais). Para rouquidão, cozinhar 100g de cenoura, esmagando e misturando com a água do cozimento, adoçar com mel e beber bem quente."),
    ("Cereja", "Prunus cerasus", "Outro purificador do organismo, que atua principalmente nos rins e no fígado. Como possui açúcares e minerais, é usada para a confecção de xaropes para a tosse. Usada em casos de artrite e gota: para tal, ferve-se 30g de pedúnculos secos em um litro de água, filtrar e adoçar levemente, bebendo um cálice durante o dia. Como reconstituinte do organismo, cozinha-se cerejas frescas ou secas (não em conserva) em tanto vinho quanto necessário para cobri-las. Bebe-se bem adoçado."),
    ("Cevada", "Hordeum vulgare", "Diurética, tônica e digestiva. Usada em pó, é um ótimo substituto para o café, principalmente para pessoas nervosas e insones. Para infecções na garganta, ferver 70g de cevada em um litro de água por 20 minutos. Quando morno, filtrar o líquido, adoçar com uma colherinha de mel, misturando bem, e fazer gargarejos durante o dia. Para inflamações do intestino e colite, ferver em um litro e meio de água por dez minutos três punhados de cevada lavada. Filtrar o líquido quando frio, adoçar com mel e beber em xícaras."),
    ("Chicória", "Chicorium intybus", "Deve-se usá-la somente em sucos e saladas. Como a cenoura, é indicada para problemas oculares. Atua também na circulação: a ingestão de três copos de suco de chicória durante o dia evita muitos males da circulação. Um ótimo alimento para normalizar a circulação é uma salada de chicória com pão de centeio. Como diurético, pode ser usada em infusão: em uma xícara de água fervente, colocar 5g de raiz de chicória. Coar e beber durante o dia."),
    ("Chuchu", "Sechium edule", "Indicado para combate à hipertensão. Ingerir o chuchu como parte importante da refeição e tomar o chá diariamente regulariza a pressão alta."),
    ("Coco", "Cocos nucifera", "A água de coco é reguladora do coração. Contém vitaminas, sais minerais e potássio. Seus efeitos são notados na pele, e a ingestão diária elimina cálculos renais e normaliza o funcionamento dos rins. Combate ainda a icterícia, irritações gastrintestinais, doenças do peito, inflamações dos olhos e vômitos na gravidez, e atua na eliminação de vermes intestinais."),
    ("Coentro", "Coriandrum sativum", "Indicado como calmante. O chá de coentro deve ser feito com toda a planta — folhas, talos e raiz — depois de bem lavados. Como estimulante do estômago e fígado, verter uma xícara de água fervente em 5g de frutos de coentro secos, filtrar, adoçar e tomar após as refeições."),
    ("Couve", "Brassica oleracea", "Hortaliça que contém enxofre e que se acredita curar até as doenças ocultas. Além do enxofre, contém iodo, arsênico, magnésio, potássio, cálcio e vitaminas. Na Roma Antiga, aconselhava-se que, para possuir uma saúde invejável, a simples ingestão de muita couve era suficiente. O suco de couve, adoçado com mel, bebido diariamente durante três meses antes do almoço, é eficaz para combater a gota (ácido úrico), a bronquite e a má circulação. O mesmo suco, sem adoçar, em aplicações tópicas cura ulcerações; misturado com água morna, é recomendado contra cólicas de crianças. O consumo da couve ainda depura o sangue, atua contra a hipertensão e é uma defesa para o organismo contra o câncer. Em casos de úlceras varicosas, fazer uma compressa: depois de eliminar a nervura mais grossa de uma folha de couve, lavá-la muito bem em água corrente e colocá-la em uma solução de ácido bórico (encontrado em farmácias), deixando macerar por três horas. Aplicar a folha, estendida numa gaze, sobre a ferida limpa, e enfaixar. Renovar à noite e pela manhã. Úlceras internas no estômago ou duodeno podem ser controladas e até curadas com a ingestão do suco de couve feito com 200g dos bordos e talos da couve espremidos. O líquido deverá ser ingerido em jejum, todos os dias, em pequenos goles."),
    ("Erva-doce", "Foeniculum vulgare", "Contém potássio, sódio e ferro. O chá das sementes é um regulador intestinal e calmante para o estômago. Desobstrui os brônquios, oxigenando melhor os pulmões. Acredita-se que mulheres que amamentam devem tomar chá de erva-doce para que os efeitos calmantes passem através do leite para a criança. Para os idosos, esse mesmo chá normaliza a circulação do sangue e combate a depressão. Atua ainda como estimulante da digestão e do aparelho urinário. No uso geral, o chá de erva-doce é feito em um litro de água fervente com 10g de sementes. Coar, adoçar pouco e tomar de quatro a cinco xícaras por dia."),
    ("Espinafre", "Spinacia oleracea", "Riquíssimo em vitaminas A, B, C e H, contendo ainda potássio, sódio, cálcio, magnésio e ferro. É indicado para pessoas com tendência a hemorragias, diabéticos, nervosos, portadores de vermes intestinais e doenças da vista; o espinafre deve ser comido cru, em saladas, ou bebido em forma de suco."),
    ("Figo", "Ficus carica", "É um laxativo natural, combate a prisão de ventre e substitui muito bem os purgativos destinados às crianças. Tem efeitos benéficos em casos de bronquite, gripe, resfriado e tosse: para esses casos, cortar em pedaços 20g de figos secos, fervendo em 250g de leite por uns quinze minutos. Depois de adoçar com uma colherada de mel, filtrar o leite e bebê-lo bem quente. Contra afecções na boca e garganta, ferver em uma xícara de leite dois figos frescos cortados em pedaços e uma colherinha de mel por quinze minutos. Depois de filtrado e morno, usar o leite para gargarejos e bochechos."),
    ("Gengibre", "Zingiber officinalis", "Uma raiz com altos poderes medicinais. Combate as náuseas, provocando o aumento de salivação; pode ser mastigado para prevenir enjôos em viagens marítimas. Age muito bem na garganta, sendo seu chá indicado a todas as pessoas que utilizam bastante a voz, como oradores, cantores, etc. Combate a flatulência, bastando para isso apenas usá-lo como tempero nas refeições. Tem também aplicação em casos de reumatismo, problemas pulmonares e de circulação sanguínea, usando-se o chá."),
    ("Goiaba", "Psidium guajava", "Famosa contra diarréias: a fruta em casos amenos e as folhas em casos mais extremos. Usa-se o chá das folhas até cessar o distúrbio. Os frutos são benéficos em casos de doenças das vias respiratórias, como tosse e bronquite."),
    ("Hortelã", "Mentha piperita", "A hortelã-miúda é empregada como tempero e age como calmante quando usada em chá. A hortelã-pimenta estimula a pele e os terminais nervosos sensíveis ao frio. Para aquecer ambientes muito frios, coloca-se uma bacia com água e folhas de hortelã. Como digestivo, faz-se uma infusão com 100g de água quente já adoçada, colocam-se 5g de folhas frescas ou secas de hortelã, filtra-se e bebe-se em seguida, bem devagar. Para excitação nervosa e insônia, colocar uma pitada de folhas frescas de hortelã em uma xícara de água quente, filtrar e beber o líquido (em casos de insônia, tomar antes de deitar)."),
    ("Inhame", "Colocasia antiquorum", "O inhame cru é um poderoso antianêmico e, mesmo cozido, conserva muito de seu poder curativo. É um grande depurador do sangue; deve ser ingerido pelas pessoas que sofrem processos inflamatórios de qualquer espécie e por todas aquelas que precisam beneficiar o sangue."),
    ("Laranja", "Citrus aurantium", "Esta fruta combate a tendência às hemorragias, a gripe, a febre e as inflamações nas veias. Para combater excitação nervosa, verter uma xícara de água fervente em 2g de folhas de laranjeira, filtrar, adoçar com mel e beber. Contra febre, colocar uma laranja madura, cortada, com a casca e em pedaços, em 30g de água fervente adoçada com duas colheradas de açúcar. Depois de totalmente frio, coar o líquido e beber."),
    ("Lentilha", "Ervum lens", "Rica em proteínas. Além de ser considerada um alimento que atrai a prosperidade, é indicada para as mães no período de amamentação. É também aconselhado seu consumo para pessoas anêmicas."),
    ("Limão", "Citrus limonum", "Fruta medicinal por excelência. Atende as necessidades de vitamina C e atua sobre o ácido úrico, doenças da vesícula biliar, da boca, da garganta, do estômago, da vista, dos nervos, dos brônquios e do pulmão. Combate ainda a esterilidade, o alcoolismo, a inapetência e o mau hálito. Os usos mais freqüentes são como chá da fruta. Uma limonada pela manhã, diariamente, previne doenças. O suco misturado com água morna pode ser ingerido nos dias mais frios para evitar problemas com a temperatura. O suco misturado à água quente usa-se para gargarejos benéficos para afecções na boca e garganta. Contra o ácido úrico e gota, beber em jejum pela manhã o suco de três limões diluído em meio cálice de água, pelo menos por dez dias; interromper o tratamento por sete dias e depois repeti-lo por mais dez dias, e assim por diante. Esse mesmo tratamento serve também para os casos de arteriosclerose e hipertensão. Com o suco de um limão se confecciona um amálgama simples contra os resfriados: basta misturar o suco com uma clara de ovo e bater com um garfo por dez minutos, tomando uma colher da mistura de meia em meia hora."),
    ("Losna", "Artemísia absinthium", "É aconselhado o chá nos problemas de fígado e intestinos, assim como nos casos de urina solta. Em diarréias pode-se fervê-la em vinho e beber o chá ou usá-lo em compressas sobre o ventre. Esse mesmo chá é um excelente colírio."),
    ("Maçã", "Pyrus malus", "Digestiva e exerce um controle sobre a flora intestinal. Recomendada contra febres e inflamações e em dietas curtas nos casos de diarréias. Contra febres, má digestão e prisão de ventre, pode-se confeccionar a Água de Maçãs: misturar uma maçã grande, descascada, mondada (livre de partes inúteis, sementes e cabo, muito bem lavada) e cortada em fatias bem finas, com 10g de folhas de erva-cidreira (melissa, a de folhas, não a de capim), suco de meio limão e um pedaço de canela. Acrescentar duas colheres de mel e meio litro de água fervente, deixando repousar por dez minutos. Passar o preparado por uma peneira, bebendo o líquido no final das refeições. No caso de febres e inflamações intestinais, consumir a água no decorrer do dia. Pode-se ainda confeccionar o Vinho de Maçãs, indicado para distúrbios digestivos e prisão de ventre: colocar uma colher de açúcar e um pedaço de casca de limão em um cálice e meio de vinho, cozinhando nele uma maçã mondada e descascada. Passar tudo pela peneira e beber esse vinho logo após as refeições."),
    ("Melancia", "Cucúrbita citrullus", "Diurética e nutritiva. Indicada para doenças nos rins, purifica o fígado, combate resfriados e bronquites. Seu consumo é altamente indicado em casos de obstrução renal, pois seu suco promove a rápida eliminação do ácido úrico. Em estado natural, auxilia no tratamento de artrite, reumatismo, acidez gástrica, dispepsia e afecções dos rins e da bexiga."),
    ("Morango", "Fragaria vesca", "Mais rico em vitamina C do que a laranja ou o limão, portanto bastante indicado para prevenção de gripes e resfriados. Cozido não tem nenhum valor; cru, atua na purificação do organismo e combate reumatismos. O consumo de morangos facilita a digestão, estimula as funções hepáticas e o apetite; combate a gota e o reumatismo articular. Uma dieta à base de morangos traz inúmeros benefícios a quem sofre de hemorróidas, perturbações circulatórias e afecções renais."),
    ("Nabo", "Brassica napius", "O nabo é indicado para combater a gripe e doenças dos brônquios. O chá de suas folhas e até da raiz fortalece os ossos, agindo também como diurético."),
    ("Pepino", "Cucumis sativus", "O pepino, para não se tornar indigesto, não deve ser descascado — a casca é que facilita a digestão. A ingestão diária fortifica as unhas e o cabelo, atuando como adstringente para a pele. Neutraliza a acidez estomacal e tonifica o fígado e os rins."),
    ("Pêra", "Pyrus communis", "Um fruto leve, pode ser ingerido sem restrições. Sua atuação é marcante nos rins, por ser um diurético excelente. Seu consumo é indicado para pessoas portadoras dos inchaços edematosos característicos dos doentes do aparelho circulatório e dos rins, e elimina esses inchaços. Cruas ou cozidas, e algumas vezes combinadas com pão integral e iogurte, são indicadas nos regimes contra a obesidade."),
    ("Pimentão", "Capsicum annuum", "Um alimento que não produz calorias. O consumo é indicado para o fortalecimento da pele, das unhas e do cabelo. Sua ingestão também é benéfica para a desinfecção da mucosa bucal e gástrica, destruindo os germes intestinais sem prejudicar a flora bacteriana normal."),
    ("Quiabo", "Hibiscus esculentus", "Favorece os órgãos digestivos, intestinais, renais e urinários. Usado como auxiliar no tratamento da bronquite e fortalece os ossos pelo seu conteúdo de cálcio."),
    ("Rabanete", "Raphanus sativus", "Estimula a digestão, purifica o sangue e tonifica os nervos, atuando principalmente sobre o aparelho renal."),
    ("Repolho", "Brassica oleracea capitata", "Indicado para pessoas enfraquecidas, anêmicas, portadoras de câncer ou tuberculose. O seu teor de ferro reconstitui o sangue e, sendo um ótimo queimador de gorduras, é aconselhado para dietas de emagrecimento."),
    ("Sabugueiro", "Sambucus nigra", "O chá, bebido como água, é eficaz nos casos de sarampo. Para o diabetes é indicado um tratamento de no mínimo três meses, tomando-se diariamente o chá das folhas. Como depurativo e contra intoxicações do fígado, ferver sete gramas de folhas frescas de sabugueiro trituradas em meio litro de água durante dez minutos; beber meia xícara do líquido filtrado e adoçado com mel, pela manhã em jejum."),
    ("Salsa", "Petroselinum sativum", "Combate gases intestinais, estimula o apetite, facilita a digestão e limpa os brônquios. Um chá de folhas de salsa é um poderoso diurético, aconselhado em casos de gota. A salsa atua também como auxiliar na cura de afecções hepáticas e hipertensão. A infusão da salsa é feita deixando por dez minutos 30g de sementes de salsa (novamente, não usar as destinadas a plantio, e sim as retiradas da planta) em 200g de água fervente; filtrar o líquido, bebendo metade em seguida e o restante três horas depois."),
    ("Uva", "Vitis vinifera", "As folhas da parreira são indicadas para se fazer chás que refrescam os intestinos, relaxam os nervos e tonificam o coração."),
]

INDICACOES = [
    ("ABACATE", "amor"),
    ("AÇAFRÃO", "purificação, saúde, felicidade"),
    ("ACÁCIA", "proteção, contra pesadelos e proteção do sono"),
    ("AGRIMÔNIA", "dissolução de influências negativas e proteção"),
    ("AIPO", "poderes mentais e psíquicos"),
    ("ALECRIM", "limpeza e concentração, calmante, adivinhação, estudos, cura, proteção, purificação"),
    ("ALFAFA", "prosperidade, dinheiro, felicidade"),
    ("ALFAZEMA", "calmante, estudos, purificação"),
    ("ALHO", "saúde, proteção"),
    ("ALMÍSCAR", "afrodisíaco, amor — Planeta: Vênus"),
    ("AMÊNDOAS", "dinheiro, prosperidade, sabedoria"),
    ("AMORA", "saúde, dinheiro, proteção"),
    ("ANETO", "sorte"),
    ("ANGÉLICA", "proteção, purificação, saúde, clarividência"),
    ("ANIS ESTRELADO", "adivinhação, purificação, sorte"),
    ("ARNICA", "clarividência"),
    ("ARROZ", "fertilidade"),
    ("ARRUDA", "proteção, limpeza, cura, purificação"),
    ("ARTEMÍSIA", "adivinhação, alteração da consciência"),
    ("ASSA-FÉTIDA", "exorcismo, proteção"),
    ("BABOSA", "proteção, sorte e amor"),
    ("BAMBU", "realização de desejos"),
    ("BARBATIMÃO", "espiritualidade, purificação"),
    ("BARDANA", "saúde, proteção"),
    ("BAUNILHA", "amor, sedução"),
    ("BETERRABA", "amor"),
    ("BENJOIM", "negócios, exorcismo — Planeta: Vênus"),
    ("BOCA DE LEÃO", "proteção"),
    ("BRIONIA", "dinheiro"),
    ("CALÊNDULA", "proteção, solução de problemas"),
    ("CAMÉLIA", "prosperidade, riqueza"),
    ("CAMOMILA", "dinheiro, amor, purificação"),
    ("CANELA", "negócios, bens materiais, amor, limpeza, energizar, sucesso, proteção"),
    ("CÂNFORA", "desenvolvimento psíquico, clarividência, saúde"),
    ("CARDAMOMO", "sedução, amor"),
    ("CARDO SANTO", "cura"),
    ("CARVALHO", "fertilidade"),
    ("CÁSCARA SAGRADA", "problemas com a justiça, dinheiro e proteção"),
    ("CAVALINHA", "fertilidade"),
    ("CEBOLA", "proteção, saúde, dinheiro"),
    ("CIPRESTE", "longevidade, saúde"),
    ("CRAVO", "negócios, forças, energizar, amor, limpeza"),
    ("DAMASCO", "feitiços de amor"),
    ("ERVA CIDREIRA", "sucesso, amor"),
    ("ERVA DOCE", "proteção"),
    ("EUCALIPTO", "limpeza, atrair encantos, energizar, cura, saúde, proteção"),
    ("FIGUEIRA", "clarividência, fertilidade"),
    ("FLOR DE MAÇÃ", "calmante"),
    ("FREIXO", "adivinhação, cura, proteção, prosperidade"),
    ("GENGIBRE", "dinheiro e sucesso"),
    ("GERGELIM", "dinheiro"),
    ("GINSENG", "amor, realização de desejos, beleza, saúde, proteção e poder"),
    ("GIRASSOL", "fertilidade"),
    ("HERA", "proteção, amor, saúde (planta não eficaz para os homens)"),
    ("HORTELÃ", "cura"),
    ("JASMIM", "melhorar o humor, amor, calmante, cura"),
    ("LARANJA", "amor, dinheiro"),
    ("LAVANDA", "cura, amor"),
    ("LIMÃO", "amor"),
    ("LÓTUS", "amor"),
    ("LOURO", "negócios, adivinhação, proteção, força, saúde"),
    ("MAÇÃ", "amor, atrair encantos, cura, imortalidade"),
    ("MANJERICÃO", "amor, purificação espiritual, proteção"),
    ("MANDRÁGORA", "fertilidade"),
    ("MADRESSILVA", "dinheiro"),
    ("MARACUJÁ", "paz, amizade"),
    ("MIL FOLHAS", "exorcismo, amor"),
    ("MIRRA", "boa sorte, espiritualidade, meditação, cura, proteção"),
    ("MORANGO", "amor, sorte"),
    ("NARCISO", "cura, sorte, fertilidade"),
    ("NOZ MOSCADA", "adivinhação, fertilidade"),
    ("OLÍBANO", "cura, purificação (resina chave)"),
    ("OLIVEIRA", "paz, fertilidade, proteção"),
    ("PATCHULI", "clarividência — Planeta: Vênus"),
    ("PINHO", "atrair encantos, fertilidade"),
    ("ROMÃ", "fertilidade"),
    ("ROSA", "amor, espiritualidade, adivinhação, fertilidade"),
    ("SABUGUEIRO", "purificação"),
    ("SÁLVIA", "cura, feitiços, longevidade, sabedoria, realização de desejos"),
    ("SÂNDALO", "amor, adivinhação, purificação"),
    ("SANGUE DE DRAGÃO", "purificação"),
    ("TRIGO", "fartura, dinheiro, fertilidade"),
    ("URTIGA", "exorcismo, proteção, saúde"),
    ("UVA", "fertilidade, dinheiro, fartura"),
    ("VETIVER", "comando — Planeta: Vênus"),
    ("VERBENA", "meditação, amor"),
    ("VISGO", "proteção"),
    ("VIOLETA", "afrodisíaco, meditação, espiritualidade"),
]

SIGNOS = [
    ("Áries", "Almíscar, Sândalo, Ópio"),
    ("Touro", "Pinho, Eucalipto, Cravo, Canela"),
    ("Gêmeos", "Rosa, Alecrim, Jasmim"),
    ("Câncer", "Maçã, Alfazema, Violeta"),
    ("Leão", "Patchouli, Almíscar, Sândalo, Ópio"),
    ("Virgem", "Rosa, Alfazema, Benjoim"),
    ("Libra", "Maçã, Rosa, Cedro"),
    ("Escorpião", "Almíscar, Ópio, Eucalipto"),
    ("Sagitário", "Cravo, Canela, Rosa"),
    ("Capricórnio", "Lótus, Alecrim"),
    ("Aquário", "Violeta, Rosas, Flores do Campo"),
    ("Peixes", "Violeta, Alecrim, Alfazema"),
]

FINAL_PARAGRAFOS = [
    "Este é um pequeno apanhado dos alimentos que podemos fazer uso diário, que não só nos nutrem, mas, bem combinados, nos trazem saúde.",
    "A arte de cozinhar é uma alquimia com a qual podemos transformar doenças em saúde. Aproveitando ao máximo os poderes da Natureza que a Deusa criou, mesmo porque ao cozinhar estamos atuando com os quatro elementos — água, terra, fogo e ar — e sabemos que esses poderes transformam qualquer coisa.",
    "Que estas ervas, plantas e saberes cheguem até você como um presente da natureza, para o corpo, para a alma e para o seu caminho.",
]

# --------------------------------------------------------------------------
# DECORAÇÕES SVG
# --------------------------------------------------------------------------

COR_OURO = "#b8860b"
COR_VERDE = "#1e4d33"
COR_VERDE_CLARO = "#3f7a56"


def svg_ramo(lado: str = "e") -> str:
    """Ramo de folhas decorativo."""
    if lado == "d":
        return f'''<svg class="ramo dir" viewBox="0 0 160 220" fill="none" stroke="{COR_VERDE_CLARO}" stroke-width="3" stroke-linecap="round">
<path d="M8 212C10 150 30 90 90 10" opacity=".55"/>
<path d="M20 190c22-6 40-18 52-38-22 2-42 12-52 38Z" opacity=".5"/>
<path d="M42 140c24-12 40-30 46-52-24 6-44 22-46 52Z" opacity=".6"/>
<path d="M66 92c18-14 26-30 24-52-18 8-28 24-24 52Z" opacity=".7"/>
</svg>'''
    return f'''<svg class="ramo esq" viewBox="0 0 160 220" fill="none" stroke="{COR_VERDE_CLARO}" stroke-width="3" stroke-linecap="round">
<path d="M152 212C150 150 130 90 70 10" opacity=".55"/>
<path d="M140 190c-22-6-40-18-52-38 22 2 42 12 52 38Z" opacity=".5"/>
<path d="M118 140c-24-12-40-30-46-52 24 6 44 22 46 52Z" opacity=".6"/>
<path d="M94 92c-18-14-26-30-24-52 18 8 28 24 24 52Z" opacity=".7"/>
</svg>'''


def svg_medalha(n: int) -> str:
    """Selo circular com número."""
    return f'''<svg class="medalha" viewBox="0 0 120 120">
<defs>
  <radialGradient id="medg{n}" cx="50%" cy="40%" r="65%">
    <stop offset="0%" stop-color="#3f7a56"/>
    <stop offset="100%" stop-color="#1e4d33"/>
  </radialGradient>
</defs>
<circle cx="60" cy="60" r="54" fill="url(#medg{n})"/>
<circle cx="60" cy="60" r="48" fill="none" stroke="{COR_OURO}" stroke-width="1.6" opacity=".9"/>
<circle cx="60" cy="60" r="42" fill="none" stroke="{COR_OURO}" stroke-width=".7" stroke-dasharray="3 4" opacity=".7"/>
<text x="60" y="72" text-anchor="middle" font-family="Georgia,serif" font-size="44" fill="{COR_OURO}">{n}</text>
</svg>'''


def svg_estrela() -> str:
    return f'''<svg class="estrela" viewBox="0 0 64 64" fill="{COR_OURO}">
<path d="M32 4l7.5 16.5L57 22.5l-13 12.5 3.5 18L32 44 16.5 53l3.5-18-13-12.5 17.5-2Z"/>
</svg>'''


# --------------------------------------------------------------------------
# RENDERIZAÇÃO DE PÁGINAS
# --------------------------------------------------------------------------

E = html.escape


def _wrap(html_page: str, titulo: str) -> str:
    return f'<section class="page" data-title="{E(titulo)}">{html_page}</section>'


def page_cover() -> str:
    return _wrap(f'''
<div class="cover-inner">
  <div class="c-topo"><span class="c-badge">GUIA ESOTÉRICO · NATURAL · COMPLETO</span></div>
  <div class="c-coroa">{svg_estrela()}</div>
  <h1 class="c-titulo">ERVAS</h1>
  <p class="c-sub">Indicações e Usos</p>
  <div class="c-linha"></div>
  <p class="c-desc">As ervas e suas propriedades energéticas, místicas e medicinais —<br>do cultivo ao uso no dia a dia.</p>
  <div class="c-ramo">{svg_ramo()}</div>
  <p class="c-autor">{E(AUTOR)}</p>
  <p class="c-marca">{E(MARCA)}</p>
  <p class="c-local">{E(LOCAL)}</p>
</div>''', "Capa")


def page_toc(paginas: list[tuple[str, str, int]]) -> str:
    itens = "\n".join(
        f'<li><a href="#" data-ir="{idx}"><span class="toc-num">{idx:02d}</span><span class="toc-txt">{E(t)}</span><span class="toc-arrow">›</span></a></li>'
        for t, _, idx in paginas
    )
    return _wrap(f'''
<div class="toc-inner">
  <h2 class="pg-super">ÍNDICE</h2>
  <div class="toc-faixa"></div>
  <ol class="toc">{itens}</ol>
  <p class="toc-note">Use o menu no topo ou as setas para navegar. Toque em um item para ir direto à seção.</p>
</div>''', "Índice")


def page_texto(titulo: str, paragrafos: list[str], etiqueta: str = "", num: int = 1) -> str:
    corpo = "\n".join(f'<p>{E(p)}</p>' for p in paragrafos)
    return _wrap(f'''
<div class="texto-inner">
  {svg_medalha(num)}
  <p class="pg-kicker">{E(etiqueta)}</p>
  <h2 class="pg-titulo">{E(titulo)}</h2>
  <div class="pg-faixa"></div>
  <div class="pg-corpo">{corpo}</div>
</div>''', titulo)


def page_lista(titulo: str, itens: list[tuple[str, str]], parte: str = "") -> str:
    cards = ""
    for k, v in itens:
        chips = "".join(
            f'<span class="chip">{E(c.strip())}</span>'
            for c in v.split(",")
        )
        cards += f'<div class="lcard"><h3>{E(k)}</h3><div class="chips">{chips}</div></div>'
    subt = f' <span class="pg-parte">— {E(parte)}</span>' if parte else ""
    return _wrap(f'''
<div class="lista-inner">
  <p class="pg-kicker">ERVAS PARA…</p>
  <h2 class="pg-titulo">{E(titulo)}{subt}</h2>
  <div class="pg-faixa"></div>
  <div class="lcards">{cards}</div>
</div>''', f"{titulo} {parte}".strip())


def page_banhos() -> str:
    cards = ""
    for k, v in BANHOS:
        cards += f'''<div class="bcard">
  <span class="b-icone">🛁</span>
  <h3>{E(k)}</h3>
  <p class="b-mix">Misture:</p>
  <p class="b-ing">{E(v)}</p>
</div>'''
    return _wrap(f'''
<div class="lista-inner">
  <p class="pg-kicker">RITUAIS</p>
  <h2 class="pg-titulo">Banhos de Ervas Para…</h2>
  <div class="pg-faixa"></div>
  <div class="bcards">{cards}</div>
  <p class="b-dica">Ervas frescas ou secas, maceradas em água morna. Colha com intenção e agradeça a natureza.</p>
</div>''', "Banhos de Ervas")


def page_energia(chunk: list[tuple[str, str]], parte: str) -> str:
    cards = "".join(
        f'<div class="ecard"><span class="e-icone">{svg_estrela()}</span><h3>{E(k)}</h3><p>{E(v)}</p></div>'
        for k, v in chunk
    )
    return _wrap(f'''
<div class="lista-inner">
  <p class="pg-kicker">ENERGIA DAS PLANTAS</p>
  <h2 class="pg-titulo">Nome da Planta e Sua Função Energética <span class="pg-parte">— {E(parte)}</span></h2>
  <div class="pg-faixa"></div>
  <div class="ecards">{cards}</div>
</div>''', f"Função Energética {parte}")


def page_divisor(titulo: str, sub: str, num: int) -> str:
    return _wrap(f'''
<div class="divisor-inner">
  <div class="d-ramo">{svg_ramo("d")}</div>
  <span class="d-num">{num:02d}</span>
  <h2 class="d-titulo">{E(titulo)}</h2>
  <p class="d-sub">{E(sub)}</p>
  <div class="d-estrelas">{svg_estrela()}{svg_estrela()}{svg_estrela()}</div>
</div>''', titulo)


def page_erva(item: tuple[str, str, str], idx: int) -> str:
    nome, latin, texto = item
    return _wrap(f'''
<div class="erva-inner">
  {svg_ramo()}
  {svg_medalha(idx + 1)}
  <p class="pg-kicker">O USO DAS ERVAS E VEGETAIS</p>
  <h2 class="erva-nome">{E(nome)}</h2>
  <p class="erva-latin">{E(latin)}</p>
  <div class="pg-faixa"></div>
  <p class="erva-texto">{E(texto)}</p>
</div>''', nome)


def page_indicacoes(chunk: list[tuple[str, str]]) -> str:
    linhas = "".join(
        f'<tr><td class="i-nome">{E(k)}</td><td>{E(v)}</td></tr>'
        for k, v in chunk
    )
    return _wrap(f'''
<div class="ind-inner">
  <p class="pg-kicker">DICIONÁRIO MÁGICO</p>
  <h2 class="pg-titulo">Indicações das Ervas</h2>
  <div class="pg-faixa"></div>
  <table class="ind-tab"><tbody>{linhas}</tbody></table>
</div>''', "Indicações das Ervas")


def page_signos() -> str:
    cards = "".join(
        f'<div class="scard"><span class="s-simbolo">{"♈♉♊♋♌♍♎♏♐♑♒♓"[i]}</span><h3>{E(k)}</h3><p>{E(v)}</p></div>'
        for i, (k, v) in enumerate(SIGNOS)
    )
    return _wrap(f'''
<div class="lista-inner">
  <p class="pg-kicker">CORRESPONDÊNCIA CELESTE</p>
  <h2 class="pg-titulo">Ervas dos Signos</h2>
  <div class="pg-faixa"></div>
  <div class="scards">{cards}</div>
</div>''', "Ervas dos Signos")


def page_final() -> str:
    corpo = "\n".join(f'<p>{E(p)}</p>' for p in FINAL_PARAGRAFOS)
    return _wrap(f'''
<div class="texto-inner">
  <div class="f-estrelas">{svg_estrela()}{svg_estrela()}{svg_estrela()}</div>
  <h2 class="pg-titulo">Para Finalizar</h2>
  <div class="pg-faixa"></div>
  <div class="pg-corpo">{corpo}</div>
</div>''', "Para Finalizar")


def page_sobre_autor() -> str:
    return _wrap(f'''
<div class="texto-inner">
  {svg_medalha(2)}
  <p class="pg-kicker">SOBRE O AUTOR</p>
  <h2 class="pg-titulo">Pesquisador das Matas</h2>
  <div class="pg-faixa"></div>
  <div class="pg-corpo">
    <p>Olá! Eu sou {E(AUTOR)}, o <strong>{E(MARCA)}</strong> de {E(LOCAL.split(' — ')[0])}. Apaixonado pela natureza e pelos saberes populares, percorro as matas do agreste alagoano coletando, estudando e preservando o conhecimento tradicional sobre plantas, ervas e seus usos.</p>
    <p>Meu trabalho une ciência, cultura e espiritualidade — sempre com respeito à floresta e às pessoas que guardam esses segredos. Este guia é fruto dessa caminhada.</p>
    <div class="sobre-contato">
      <p>📺 <strong>YouTube:</strong> <a href="{YOUTUBE_URL}" target="_blank">{E(YOUTUBE_NOME)}</a></p>
      <p>✉️ <strong>E-mail:</strong> <a href="mailto:{EMAIL}">{E(EMAIL)}</a></p>
    </div>
    <p class="sobre-assinatura">"Cada erva tem uma história. Cada mata, um segredo."</p>
  </div>
</div>''', "Sobre o Autor")


def page_contracapa() -> str:
    return _wrap(f'''
<div class="contra-inner">
  <div class="c-ramo">{svg_ramo()}</div>
  <h2 class="c-fim">ERVAS</h2>
  <p class="c-fim-sub">Indicações e Usos</p>
  <div class="c-linha"></div>
  <p class="c-marca-fim">{E(AUTOR)} · {E(MARCA)}</p>
  <p class="c-local-fim">{E(LOCAL)}</p>
  <div class="c-contato">
    <p>📺 {E(YOUTUBE_NOME)}</p>
    <p>✉️ {E(EMAIL)}</p>
  </div>
  <p class="c-aviso">Aviso: este guia tem caráter informativo e cultural. As receitas e indicações não substituem orientação médica. Em caso de doença, procure um profissional de saúde.</p>
  <p class="c-copy">© {E(AUTOR)} — {E(MARCA)}</p>
</div>''', "Contracapa")


# --------------------------------------------------------------------------
# MONTAGEM DO LIVRO
# --------------------------------------------------------------------------

def montar_paginas() -> tuple[list[str], list[dict], list[tuple[str, str, int]]]:
    paginas_html: list[str] = []
    indice: list[dict] = []          # {t, s} para menu
    toc: list[tuple[str, str, int]] = []  # (titulo, sub, pagina_0index) para página de índice

    def add(h, t, s=""):
        paginas_html.append(h)
        indice.append({"t": t, "s": s})
        return len(paginas_html) - 1

    p_capa = add(page_cover(), "Capa", "ERVAS — Indicações e Usos")
    p_toc = add(page_toc([]), "Índice", "Navegue pelo guia")

    # separa páginas "ervas para" em 2 grupos
    metade = (len(ERVAS_PARA) + 1) // 2
    p_ep1 = add(page_lista("Ervas Para…", ERVAS_PARA[:metade], "Parte I"), "Ervas Para…", "Parte I")
    p_ep2 = add(page_lista("Ervas Para…", ERVAS_PARA[metade:], "Parte II"), "Ervas Para…", "Parte II")

    p_banhos = add(page_banhos(), "Banhos de Ervas", "Rituais")

    fe_metade = (len(FUNCAO_ENERGETICA) + 1) // 2
    p_fe1 = add(page_energia(FUNCAO_ENERGETICA[:fe_metade], "Parte I"), "Função Energética", "Parte I")
    p_fe2 = add(page_energia(FUNCAO_ENERGETICA[fe_metade:], "Parte II"), "Função Energética", "Parte II")

    p_div_uso = add(page_divisor("O Uso das Ervas e Vegetais", "Saúde e medicina natural, planta por planta", 3), "O Uso das Ervas e Vegetais", "Divisão")
    for i, item in enumerate(USO_MEDICINAL):
        add(page_erva(item, i), item[0], item[1])

    p_div_ind = add(page_divisor("Indicações das Ervas", "Dicionário energético de A a Z", 4), "Indicações das Ervas", "Divisão")
    n = len(INDICACOES)
    tam = 30
    for c in range(0, n, tam):
        add(page_indicacoes(INDICACOES[c : c + tam]), "Indicações das Ervas", f"páginas {c + 1}–{min(c + tam, n)}")

    p_signos = add(page_signos(), "Ervas dos Signos", "Correspondência celeste")
    p_sobre = add(page_sobre_autor(), "Sobre o Autor", "Pesquisador das Matas")
    p_final = add(page_final(), "Para Finalizar", "Encerramento")
    p_contra = add(page_contracapa(), "Contracapa", "Créditos e aviso")

    # índice (títulos principais, 1 página cada referência)
    toc = [
        ("Capa", "Abertura", p_capa),
        ("Ervas Para…", "Finalidades de cada erva", p_ep1),
        ("Banhos de Ervas", "Rituais de banho", p_banhos),
        ("Função Energética", "Nome e função de cada planta", p_fe1),
        ("O Uso das Ervas e Vegetais", "Guia medicinal, planta por planta", p_div_uso),
        ("Indicações das Ervas", "Dicionário de A a Z", p_div_ind),
        ("Ervas dos Signos", "Correspondência celeste", p_signos),
        ("Sobre o Autor", "Pesquisador das Matas", p_sobre),
        ("Para Finalizar", "Encerramento", p_final),
        ("Contracapa", "Créditos e aviso", p_contra),
    ]
    paginas_html[p_toc] = page_toc(toc)

    return paginas_html, indice, toc


# --------------------------------------------------------------------------
# TEMPLATE HTML (auto-contido)
# --------------------------------------------------------------------------

TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITULO__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,500&family=Playfair+Display:ital,wght@0,600;0,800;1,600&family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --ouro:#b8860b; --ouro2:#d4af37; --verde:#1e4d33; --verde-c:#3f7a56;
  --papel:#f7f1e1; --papel2:#efe6d0; --tinta:#2c2518; --tinta2:#6b5f45;
  --fundo:#0e1a13; --barra:#0d150f;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{
  background:
    radial-gradient(1200px 500px at 50% -100px, #16321f 0%, transparent 60%),
    var(--fundo);
  color:var(--tinta);
  font-family:'Cormorant Garamond',Georgia,serif;
  display:flex;flex-direction:column;height:100vh;overflow:hidden;
}

/* ---------- TOPBAR ---------- */
.topbar{
  display:flex;align-items:center;gap:10px;padding:10px 14px;
  background:var(--barra);border-bottom:1px solid #22372a;z-index:50;
}
.tb-titulo{font-family:'Playfair Display',serif;color:var(--ouro2);font-size:1.02rem;letter-spacing:.04em;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tb-btn{
  background:#182218;color:#d9e6d5;border:1px solid #2c4a36;border-radius:8px;
  padding:7px 12px;font-family:'Poppins',sans-serif;font-size:.72rem;font-weight:500;cursor:pointer;transition:all .15s;
}
.tb-btn:hover{border-color:var(--ouro);color:var(--ouro2)}
.tb-btn.destaque{background:var(--ouro);color:#141000;border-color:var(--ouro)}

/* ---------- MENU ---------- */
.menu{
  position:fixed;top:54px;right:12px;width:290px;max-height:70vh;overflow-y:auto;z-index:60;
  background:#101a12;border:1px solid #2c4a36;border-radius:12px;box-shadow:0 20px 50px rgba(0,0,0,.6);
  display:none;padding:8px;
}
.menu.aberto{display:block}
.menu .m-tit{font-family:'Poppins',sans-serif;font-size:.68rem;letter-spacing:.18em;text-transform:uppercase;color:var(--ouro2);padding:8px 10px 6px}
.menu button{
  display:block;width:100%;text-align:left;background:none;border:none;color:#cfe0c8;cursor:pointer;
  padding:8px 10px;border-radius:8px;font-family:'Poppins',sans-serif;font-size:.8rem;
}
.menu button:hover{background:#1c2a1f}
.menu button small{display:block;color:#7d937a;font-size:.68rem}

/* ---------- LIVRO ---------- */
.livro{flex:1;overflow:hidden;position:relative}
.rolagem{
  height:100%;overflow-y:auto;scroll-snap-type:y proximity;
  scroll-behavior:smooth;
}
.page{
  min-height:100%;display:flex;align-items:center;justify-content:center;
  padding:34px 16px 70px;scroll-snap-align:start;
  width:100%;
}
.page>div{width:100%;max-width:680px;margin:0 auto}

/* ---------- PÁGINAS GENÉRICAS ---------- */
.pg-kicker{
  font-family:'Poppins',sans-serif;font-size:.66rem;letter-spacing:.3em;text-transform:uppercase;
  color:var(--ouro);text-align:center;margin-bottom:10px;font-weight:600;
}
.pg-titulo{
  font-family:'Playfair Display',serif;font-size:clamp(1.7rem,4vw,2.6rem);font-weight:800;
  text-align:center;line-height:1.1;color:#23311f;
}
.pg-parte{font-size:.6em;color:var(--ouro);font-family:'Poppins',sans-serif;font-weight:500;letter-spacing:.06em}
.pg-faixa{
  width:120px;height:3px;background:linear-gradient(90deg,transparent,var(--ouro),transparent);
  margin:16px auto 22px;border-radius:3px;
}
.pg-corpo p{
  font-size:1.14rem;line-height:1.65;margin-bottom:14px;color:#3a3222;text-align:justify;
}
.pg-corpo p:last-child{margin-bottom:0}

/* papel */
.page>div{
  background:linear-gradient(180deg,var(--papel) 0%,var(--papel2) 100%);
  border-radius:6px;box-shadow:0 24px 60px rgba(0,0,0,.55), inset 0 0 0 1px rgba(0,0,0,.08);
  padding:44px 44px 40px;position:relative;min-height:calc(100vh - 200px);
}
.page>div::before{
  content:'';position:absolute;left:0;top:0;bottom:0;width:34px;
  background:linear-gradient(90deg,#e5dbc0,rgba(231,219,190,0));
}

/* ---------- CAPA ---------- */
.cover-inner{
  background:radial-gradient(140% 100% at 50% -10%, #245338 0%, #123523 55%, #0a2417 100%) !important;
  color:#efe6cf;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;
  border-radius:6px;position:relative;overflow:hidden;
}
.cover-inner::before{display:none}
.c-topo{margin-bottom:22px}
.c-badge{
  font-family:'Poppins',sans-serif;font-size:.62rem;letter-spacing:.34em;text-transform:uppercase;
  border:1px solid var(--ouro2);color:var(--ouro2);padding:7px 18px;border-radius:30px;display:inline-block;
}
.c-coroa{margin-bottom:16px}
.c-coroa .estrela{width:44px;height:44px;filter:drop-shadow(0 0 12px rgba(212,175,55,.7))}
.c-titulo{
  font-family:'Playfair Display',serif;font-size:clamp(4rem,14vw,7rem);font-weight:800;line-height:1;
  color:#f6ecd2;letter-spacing:.04em;text-shadow:0 4px 30px rgba(0,0,0,.4);
}
.c-sub{
  font-family:'Cormorant Garamond',serif;font-style:italic;font-size:clamp(1.5rem,4.5vw,2.2rem);
  color:var(--ouro2);margin-top:10px;
}
.c-linha{width:140px;height:2px;background:linear-gradient(90deg,transparent,var(--ouro2),transparent);margin:24px auto}
.c-desc{font-size:1.02rem;color:#c8d8c2;line-height:1.6;max-width:420px;margin-bottom:26px;font-style:italic}
.c-ramo{position:relative;width:100%;max-width:150px;margin-bottom:8px}
.c-ramo .ramo{width:100%;height:auto}
.c-autor{
  font-family:'Poppins',sans-serif;font-size:.72rem;letter-spacing:.3em;text-transform:uppercase;color:#b7c9ae;
}
.c-marca{
  font-family:'Playfair Display',serif;font-style:italic;color:var(--ouro2);font-size:1.05rem;margin-top:8px;
}
.c-local{
  font-family:'Poppins',sans-serif;font-size:.62rem;letter-spacing:.22em;text-transform:uppercase;color:#9db395;margin-top:8px;
}
.sobre-contato{
  margin:16px 0;padding:16px 18px;background:#fdf8ec;border:1px solid #e0d3b0;border-radius:12px;
  font-size:1.02rem;
}
.sobre-contato a{color:var(--verde);font-weight:600}
.sobre-contato p{margin-bottom:6px}
.sobre-contato p:last-child{margin-bottom:0}
.sobre-assinatura{
  font-style:italic;color:var(--ouro);text-align:center;font-size:1.08rem;
}
.c-marca-fim{font-family:'Playfair Display',serif;font-style:italic;color:var(--ouro2);font-size:1.15rem;margin-top:8px}
.c-local-fim{font-family:'Poppins',sans-serif;font-size:.66rem;letter-spacing:.22em;text-transform:uppercase;color:#b7c9ae;margin-top:6px}
.c-contato{margin-top:18px;font-family:'Poppins',sans-serif;font-size:.72rem;color:#c8d8c2;line-height:1.7}
.c-contato p{margin:0}

/* ---------- ÍNDICE ---------- */
.toc-inner .toc{list-style:none;margin-top:8px}
.toc li{margin-bottom:4px}
.toc a{
  display:flex;align-items:center;gap:14px;text-decoration:none;color:var(--tinta);
  padding:9px 12px;border-radius:10px;border:1px solid transparent;transition:all .15s;
}
.toc a:hover{background:#e9dfc6;border-color:#d6c7a4}
.toc-num{font-family:'Playfair Display',serif;font-weight:800;color:var(--ouro);font-size:1rem;width:30px}
.toc-txt{flex:1;font-size:1.08rem;font-weight:600;color:#2c2518}
.toc-arrow{color:var(--ouro);font-size:1.2rem}
.toc-note{margin-top:18px;font-size:.82rem;color:var(--tinta2);text-align:center;font-style:italic}

/* ---------- LISTAS ---------- */
.lcards,.bcards{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.lcard{
  background:#fdf8ec;border:1px solid #e0d3b0;border-radius:12px;padding:14px 16px;
}
.lcard h3{font-family:'Playfair Display',serif;font-size:1.12rem;color:#23311f;margin-bottom:10px;line-height:1.2}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{
  font-family:'Poppins',sans-serif;font-size:.62rem;font-weight:500;color:var(--verde);
  background:#e7efdd;border:1px solid #cfe0bd;border-radius:30px;padding:3px 9px;
}
.bcard{
  background:#fdf8ec;border:1px solid #e0d3b0;border-radius:12px;padding:18px;text-align:center;
}
.b-icone{font-size:1.6rem;display:block;margin-bottom:6px}
.bcard h3{font-family:'Playfair Display',serif;font-size:1.18rem;color:#23311f;margin-bottom:8px}
.b-mix{font-family:'Poppins',sans-serif;font-size:.64rem;letter-spacing:.18em;text-transform:uppercase;color:var(--ouro);margin-bottom:6px}
.b-ing{font-size:1.04rem;line-height:1.5;color:#3a3222}
.b-dica{margin-top:16px;font-size:.86rem;color:var(--tinta2);text-align:center;font-style:italic}

/* ---------- ENERGIA ---------- */
.ecards{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.ecard{
  background:#fdf8ec;border:1px solid #e0d3b0;border-radius:12px;padding:12px 14px;display:flex;gap:10px;align-items:flex-start;
}
.e-icone{flex-shrink:0}
.e-icone .estrela{width:18px;height:18px}
.ecard h3{font-family:'Playfair Display',serif;font-size:1.05rem;color:#23311f;line-height:1.1}
.ecard p{font-size:.96rem;color:#4a4130;margin-top:4px;line-height:1.45}

/* ---------- DIVISOR ---------- */
.divisor-inner{
  background:
    radial-gradient(140% 100% at 50% -10%, #245338 0%, #123523 55%, #0a2417 100%) !important;
  color:#efe6cf;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;
}
.divisor-inner::before{display:none}
.d-ramo{width:110px;margin-bottom:14px}
.d-ramo .ramo{width:100%;height:auto;opacity:.8}
.d-num{font-family:'Playfair Display',serif;font-size:1rem;letter-spacing:.2em;color:var(--ouro2)}
.d-titulo{font-family:'Playfair Display',serif;font-size:clamp(2rem,5.5vw,3rem);font-weight:800;color:#f6ecd2;margin-top:10px;line-height:1.1}
.d-sub{font-style:italic;font-size:1.1rem;color:#c8d8c2;margin-top:12px}
.d-estrelas{display:flex;gap:12px;margin-top:26px}
.d-estrelas .estrela{width:20px;height:20px;opacity:.85}

/* ---------- ERVA ---------- */
.erva-inner{position:relative}
.erva-inner .ramo{position:absolute;width:86px;height:auto;opacity:.5;top:-14px}
.erva-inner .ramo.esq{left:-30px;transform:rotate(6deg)}
.erva-inner .ramo.dir{right:-30px;transform:rotate(-6deg)}
.erva-inner .medalha{position:absolute;top:-20px;right:8px;width:74px;height:74px}
.erva-nome{
  font-family:'Playfair Display',serif;font-size:clamp(2rem,5vw,2.9rem);font-weight:800;
  text-align:center;color:#23311f;line-height:1.05;margin-top:14px;
}
.erva-latin{
  font-style:italic;text-align:center;color:var(--verde);font-size:1.15rem;margin-top:6px;letter-spacing:.02em;
}
.erva-texto{
  font-size:1.13rem;line-height:1.7;color:#3a3222;text-align:justify;
}

/* ---------- INDICAÇÕES ---------- */
.ind-tab{width:100%;border-collapse:collapse;font-size:.98rem}
.ind-tab td{padding:8px 12px;border-bottom:1px solid #e0d3b0;vertical-align:top}
.ind-tab tr:nth-child(even) td{background:#f3ead5}
.i-nome{font-family:'Playfair Display',serif;font-weight:800;color:var(--verde);white-space:nowrap;width:38%}

/* ---------- SIGNOS ---------- */
.scards{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.scard{
  background:#fdf8ec;border:1px solid #e0d3b0;border-radius:12px;padding:12px;text-align:center;
}
.s-simbolo{font-size:1.5rem;color:var(--ouro);display:block;margin-bottom:4px}
.scard h3{font-family:'Playfair Display',serif;font-size:1.05rem;color:#23311f}
.scard p{font-size:.9rem;color:#4a4130;margin-top:6px;line-height:1.4}

/* ---------- FINAL / CONTRACAPA ---------- */
.f-estrelas{display:flex;gap:12px;justify-content:center;margin-bottom:18px}
.f-estrelas .estrela{width:20px;height:20px}
.contra-inner{
  background:radial-gradient(140% 100% at 50% -10%, #245338 0%, #123523 55%, #0a2417 100%) !important;
  color:#efe6cf;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;
}
.contra-inner::before{display:none}
.contra-inner .c-ramo{width:120px;margin-bottom:16px}
.c-fim{font-family:'Playfair Display',serif;font-size:2.6rem;font-weight:800;color:#f6ecd2}
.c-fim-sub{font-style:italic;font-size:1.2rem;color:var(--ouro2);margin-top:6px}
.c-aviso{margin-top:22px;font-size:.86rem;line-height:1.6;color:#c8d8c2;max-width:380px}
.c-copy{margin-top:22px;font-family:'Poppins',sans-serif;font-size:.66rem;letter-spacing:.2em;text-transform:uppercase;color:#9db395}

/* ---------- BARRA INFERIOR ---------- */
.bottom{
  display:flex;align-items:center;gap:14px;padding:10px 16px;background:var(--barra);border-top:1px solid #22372a;z-index:50;
}
.prog-wrap{flex:1;height:4px;background:#1c2a1f;border-radius:4px;overflow:hidden}
.prog{height:100%;width:0;background:linear-gradient(90deg,var(--ouro),var(--ouro2));transition:width .2s}
.pos{font-family:'Poppins',sans-serif;font-size:.7rem;color:#9db395;min-width:64px;text-align:center}
.nav-btn{
  background:#182218;color:#d9e6d5;border:1px solid #2c4a36;border-radius:8px;
  width:38px;height:38px;font-size:1rem;cursor:pointer;transition:all .15s;font-family:'Poppins',sans-serif;
}
.nav-btn:hover:not(:disabled){border-color:var(--ouro);color:var(--ouro2)}
.nav-btn:disabled{opacity:.35;cursor:default}

/* ---------- RESPONSIVO ---------- */
@media (max-width:760px){
  .lcards,.bcards{grid-template-columns:1fr}
  .scards{grid-template-columns:1fr 1fr}
  .page>div{padding:34px 22px 30px}
  .erva-inner .ramo.dir{right:-14px}
  .erva-inner .ramo.esq{left:-14px}
}
@media (max-width:480px){
  .tb-btn span{display:none}
  .tb-btn{padding:7px 9px}
}

/* ---------- IMPRESSÃO / PDF ---------- */
@media print{
  body{background:#fff;height:auto;overflow:visible;display:block}
  .topbar,.bottom,.menu{display:none!important}
  .livro{overflow:visible}
  .rolagem{height:auto;overflow:visible;scroll-snap-type:none}
  .page{min-height:0;padding:0;page-break-after:always;display:block}
  .page>div{min-height:0;box-shadow:none;border:1px solid #ddd;border-radius:0}
  @page{size:A4;margin:0}
}
</style>
</head>
<body>

<div class="topbar">
  <span class="tb-titulo">🌿 ERVAS — Indicações e Usos</span>
  <button class="tb-btn" onclick="abrirMenu()">☰ <span>Capítulos</span></button>
  <button class="tb-btn destaque" onclick="window.print()">⬇ <span>PDF</span></button>
  <button class="tb-btn" onclick="whats()">📱 <span>WhatsApp</span></button>
</div>

<div class="menu" id="menu">__MENU__</div>

<div class="livro"><div class="rolagem" id="rolagem">__PAGINAS__</div></div>

<div class="bottom">
  <button class="nav-btn" id="btPrev" onclick="ir(-1)">‹</button>
  <div class="prog-wrap"><div class="prog" id="prog"></div></div>
  <span class="pos" id="pos"></span>
  <button class="nav-btn" id="btNext" onclick="ir(1)">›</button>
</div>

<script>
(function(){
  var rolagem=document.getElementById('rolagem');
  var paginas=Array.prototype.slice.call(document.querySelectorAll('.page'));
  var total=paginas.length;
  var pos=document.getElementById('pos');
  var prog=document.getElementById('prog');

  function atual(){
    var atual=0;
    for(var i=0;i<total;i++){ if(paginas[i].getBoundingClientRect().top>40){ atual=i-1; break; } atual=i; }
    if(atual<0)atual=0;
    var frac=rolagem.scrollTop/(rolagem.scrollHeight-rolagem.clientHeight||1);
    prog.style.width=(Math.round(frac*1000)/10)+'%';
    pos.textContent=(atual+1)+' / '+total;
    document.getElementById('btPrev').disabled=(atual===0);
    document.getElementById('btNext').disabled=(atual===total-1);
    return atual;
  }
  window.ir=function(d){
    var atual=0;
    var margem=rolagem.getBoundingClientRect().top;
    for(var i=0;i<total;i++){ var t=paginas[i].getBoundingClientRect().top-margem; if(t>-60) break; atual=i; }
    var alvo=atual+d;
    if(alvo<0)alvo=0; if(alvo>=total)alvo=total-1;
    paginas[alvo].scrollIntoView({behavior:'smooth'});
  };
  rolagem.addEventListener('scroll',atual,{passive:true});
  document.addEventListener('keydown',function(e){
    if(e.key==='ArrowRight'||e.key==='PageDown'){ir(1);}
    if(e.key==='ArrowLeft'||e.key==='PageUp'){ir(-1);}
  });
  var inicioX=null;
  rolagem.addEventListener('touchstart',function(e){inicioX=e.touches[0].clientX},{passive:true});
  rolagem.addEventListener('touchend',function(e){
    if(inicioX===null)return;
    var dx=e.changedTouches[0].clientX-inicioX;
    if(Math.abs(dx)>50){ ir(dx<0?1:-1); }
    inicioX=null;
  });
  document.querySelectorAll('.toc a, .menu button').forEach(function(a){
    a.addEventListener('click',function(ev){
      ev.preventDefault();
      var idx=+(a.getAttribute('data-ir')||0);
      paginas[idx].scrollIntoView({behavior:'smooth'});
      var m=document.getElementById('menu'); m.classList.remove('aberto');
    });
  });
  atual();
})();
function abrirMenu(){document.getElementById('menu').classList.toggle('aberto')}
function whats(){
  window.open('https://wa.me/__WHATSAPP__?text='+encodeURIComponent('Olá! Estou vendendo o ebook ERVAS — Indicações e Usos. 🌿'),'_blank');
}
</script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------

def main() -> None:
    paginas_html, indice, toc = montar_paginas()

    livro = {
        "titulo": "ERVAS — Indicações e Usos",
        "subtitulo": "Guia esotérico, energético e medicinal das ervas",
        "autor": AUTOR,
        "lang": "pt-BR",
        "secoes": indice,
        "total_paginas": len(paginas_html),
        "conteudo": {
            "ervas_para": ERVAS_PARA,
            "banhos": BANHOS,
            "funcao_energetica": FUNCAO_ENERGETICA,
            "uso_medicinal": USO_MEDICINAL,
            "indicacoes": INDICACOES,
            "signos": SIGNOS,
        },
    }
    SAIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_JSON.write_text(
        json.dumps(livro, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    menu_itens = "\n".join(
        f'<button data-ir="{i}">{E(t)}<small>{E(s)}</small></button>'
        for i, (t, s) in enumerate(zip(
            [p["t"] for p in indice], [p["s"] for p in indice]
        ))
    )

    gerado = (
        TEMPLATE
        .replace("__TITULO__", html.escape(livro["titulo"], quote=True))
        .replace("__PAGINAS__", "\n".join(paginas_html))
        .replace("__MENU__", menu_itens)
        .replace("__WHATSAPP__", WHATSAPP)
    )
    SAIDA_HTML.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_HTML.write_text(gerado, encoding="utf-8")

    print(f"[criar_ervas] OK  {SAIDA_JSON}")
    print(f"[criar_ervas] OK  {SAIDA_HTML}  ({len(paginas_html)} páginas, {SAIDA_HTML.stat().st_size // 1024} KB)")
    print(f"[criar_ervas]     {len(USO_MEDICINAL)} ervas medicinais · {len(INDICACOES)} indicações · {len(SIGNOS)} signos")


if __name__ == "__main__":
    main()
