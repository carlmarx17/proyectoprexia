#!/usr/bin/env python3
"""
build_static_site.py
Generador estático profesional para la migración de PREXIA Google Sites a HTML/Git.
Aplica el sistema de diseño editorial anti-slop (Taste Skill) con Libre Franklin + Source Serif 4,
preserva la estructura rica de las 6 ediciones del Encuentro Internacional EISI (2020-2025),
clasifica por MD5 contenido real vs íconos/botones/logos institucionales e incorpora el Sistema de Evaluación Prexia (PP).
"""
from __future__ import annotations

import hashlib
import html
import json
import shutil
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlparse


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_ROOT / "scraped_site_clean"
OUTPUT_DIR = PROJECT_ROOT / "site"

# Hashes MD5 (primeros 12 caracteres del contenido binario) de íconos de redes sociales,
# botones decorativos de Google Sites, banderas gigantes, clip-art y diapositivas redundantes.
EXCLUDED_IMAGE_MD5S = {
    # Banner superior global (900x400) e íconos globales 64x64 (Facebook, LinkedIn, Email, Instagram)
    "f040c0b924ee",
    "e960508c8224",
    "a29f6cde8c9a",
    "e0b25692d09f",
    "07ddeff34c4e",
    # Íconos gigantes de redes sociales incrustados en páginas antiguas (2019, 2020, 2021)
    "2318909f8acc",  # 600x600 Instagram icon (371KB) en evento-2019
    "5d5331c337b6",  # 512x512 Facebook icon en evento-2019
    "cb929fd29506",  # 960x681 Gmail icon en evento-2019
    "e39accac8af4",  # 614x615 Grey Facebook icon en 2020 y 2021
    "083d33f64d6d",  # 510x512 Grey YouTube icon en 2020 y 2021
    # Íconos vectoriales planos (512x512) y clip-art en páginas 2019, 2020, 2021 y 2025
    "ca6d67e60f75",
    "788aed64e04f",
    "5c1181a51754",
    "ec82833949ca",
    "340bc67140b9",
    "aa7c95a4e6ef",
    "22dbcd44792f",
    "5c4a174ca58d",
    "d51073eb89af",
    "a2e9613e1c78",
    "1a7c9a256e2c",
    "fbb583f8b36a",
    "325c1ca4ae4b",
    "99335ab65f63",
    "bdc10e03b031",
    "6bdda21dcc07",
    "5f6f58b88449",
    # Banderas gigantes de Brasil y Alemania (1200x800) en 2020
    "612d86189a6c",
    "a53514d57e53",
    "e270c96194bc",
    "515de613c7f3",
    # Logos blancos sobre fondo transparente o duplicados de pie de página en 2020 y 2021
    "6da39e4ce2ad",
    "a4ef70b244b7",
    "8168bc7626b1",
    "2b856cbfbf99",
    "920b9e691605",
    "d457ee81b3ac",
    # Botones de interfaz de Google Sites con cursor de ratón ("Asistente", "Ponente", "Evaluador")
    "b66c675e6db8",
    "534e3a569362",
    "6a13cf3328e4",
    "ce1ac578fd36",
    "76b81c798ace",
    "86e5f7ae14b3",
    # Íconos de calendario clip-art y cintillos decorativos genéricos en 2025
    "8b1d2a6bbb8d",
    "2498507d3387",
    "d1d8f6e5b3de",
    "f00ac45fa3f9",
    "1a4689a9253d",
    # Diagramas antiguos de inicio/líneas y diapositivas de botones redundantes con el HTML estructurado
    "3fca5b1b2e84",
    "c6f3e9e29fd0",
    "055f140f3b2e",
    "98cd4b58c288",
    "a1687f8a5b2d",
    "70028d2590cf",
    "f5201231910f",
    "b0837c2d7d5f",
    "1cce91ac5593",
    "f5c48f5989a8",
    "6c8b305ad35c",
    "d70ebb43ae05",
}

# Retratos de conferencistas (se renderizan en tarjetas de perfil .speaker-card, no como fotos anchas de galería)
SPEAKER_PORTRAIT_MD5S = {
    "92811b1ab9dd",
    "ab93215076d4",
    "96154ec2a71f",
    "abf8da86d6b7",
    "7844275c80cf",
    "3735c14029b8",
    "adfc5735dcf9",
    "982db7ae065d",
    "43033c75594c",
}

# Hashes MD5 de logos institucionales y aliados (se renderizan en la franja inferior limpia de 48px)
ALLY_LOGO_MD5S = {
    "cdc92c511da0": "Universidad Nacional de Colombia",
    "97df144d2931": "Universidad Nacional de Colombia",
    "4637154557a1": "Grupo Geyma · UNAL Medellín",
    "e69898e113a7": "Semillero PREXIA · UNAL",
    "64f4086516a8": "Semillero PREXIA · UNAL",
    "500b683146c3": "Facultad de Ciencias Agrarias · UNAL",
    "624fa6a52ec3": "UNESP · São Paulo, Brasil",
    "965615829f8d": "UNESP · Campus Jaboticabal",
    "1a6533fdf571": "Instituto A Nau Ciranda · Brasil",
    "3360f9796220": "Fundación Univ. Autónoma de las Américas",
    "6ffe2e16ea70": "Fundación Univ. Autónoma de las Américas",
    "dc9970822f77": "SENA · Centro de Desarrollo Empresarial",
    "4440193c5dd6": "Institución Universitaria Esumer",
    "a9d9e5148852": "Revista ENSAYOS · UNAL Manizales",
    "a6c2eca982c5": "Corporación Interactuar",
}

EISI_EDITIONS_NAV = [
    ("2025", "VI EISI 2025", "unal-edu-co__prexiaforum__home__vi-eisi-2025"),
    ("2024", "V EISI 2024", "unal-edu-co__prexiaforum__home__v-encuentro-internacional-de-semilleros-2024"),
    ("2023", "IV EISI 2023", "unal-edu-co__prexiaforum__home__iv-encuentro-internacional-de-semilleros-2023"),
    ("2022", "III EISI 2022", "unal-edu-co__prexiaforum__home__iii-encuentro-internacional-de-semilleros-2022"),
    ("2021", "II EISI 2021", "unal-edu-co__prexiaforum__home__ii-encuentro-internacional-de-semilleros-2021"),
    ("2020", "I EISI 2020", "unal-edu-co__prexiaforum__home__i-encuentro-internacional-de-semilleros-2020"),
]

SPEAKERS_2020 = [
    {
        "name": "Fernando Antonio Beltrame",
        "role": "Presidente de ECCA PLAN · Movimiento Sou Resíduo Zero (São Paulo, Brasil)",
        "bio": "Ingeniero de Alimentos (UNICAMP) con MBA en Gestión Empresarial por la Fundação Getúlio Vargas (FGV) y Maestría en Compostaje. Responsable de los programas Evento Neutro y CO2 Neutro para inventarios de emisiones, logística verde y sostenibilidad corporativa.",
        "img": "../images/unal-edu-co__prexiaforum__home__i-encuentro-internacional-de-semilleros-2020__conferencistas__04__cb3ce95f7548.jpg",
    },
    {
        "name": "Dra. Silvia Inês Dallavalle de Pádua",
        "role": "Profesora Asociada · FEA-RP / Universidade de São Paulo (USP, Brasil)",
        "bio": "Doctora en Ingeniería (EESC/USP) y Posdoctora en Ingeniería de Producción (UNESP). Investigadora líder en Business Process Management (BPM), sostenibilidad organizacional y alineación estratégica entre negocios y tecnologías de la información.",
        "img": "../images/unal-edu-co__prexiaforum__home__i-encuentro-internacional-de-semilleros-2020__conferencistas__05__ee16057509f3.jpg",
    },
    {
        "name": "Dr. Ronald Koepke",
        "role": "Auditor Internacional Fairtrade (FLOCERT GmbH) & Docente ESPOL · Alemania / Ecuador",
        "bio": "Magíster y Doctor en Ciencias Sociales y Pedagogía por la Universidad de Bielefeld (Alemania). Especialista en reconversión industrial en la cuenca del Ruhr, comercio justo y responsabilidad social empresarial en comunidades mineras e industriales.",
        "img": "../images/unal-edu-co__prexiaforum__home__i-encuentro-internacional-de-semilleros-2020__conferencistas__07__6e20cbde201b.jpg",
    },
]

SPEAKERS_2019 = [
    {
        "name": "Dr. Mauricio Losada Otálora",
        "role": "Conferencista Magistral · Estrategia y Gestión de Organizaciones",
        "bio": "Investigador invitado al Primer Encuentro Nacional de Semilleros de Investigación en torno a capacidades dinámicas, competitividad y modelación organizacional.",
        "img": "../images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__evento-2019__03__bc71c804338c.jpg",
    },
    {
        "name": "Dr. Alexander Tabares",
        "role": "Conferencista Magistral · Emprendimiento e Innovación Internacional",
        "bio": "Docente investigador en creación de nuevas empresas (New Ventures), ecosistemas de emprendimiento de alto impacto y toma de decisiones estratégicas.",
        "img": "../images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__evento-2019__04__2567d1901933.jpg",
    },
    {
        "name": "Dr. Iván Darío Arango",
        "role": "Conferencista Magistral · Industria 4.0 y Sistemas Productivos",
        "bio": "Especialista en automatización, diseño de procesos industriales y adopción tecnológica para la productividad en manufactura y servicios.",
        "img": "../images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__evento-2019__05__ca8807d64c8e.jpg",
    },
]

EISI_STRUCTURED_DATA = {
    "unal-edu-co__prexiaforum__home__vi-eisi-2025": {
        "short_title": "VI EISI 2025.",
        "edition_badge": "Sexta Edición · 13 y 14 de noviembre de 2025 · Medellín & Brasil",
        "subtitle": "VI Encuentro Internacional de Semilleros de Investigación PREXIA UNAL 2025 · «Ingeniería que Transforma Territorios: Gestión e Innovación para el Desarrollo Sostenible».",
        "date": "13 y 14 de noviembre de 2025",
        "modality": "Híbrida (Campus Robledo UNAL Medellín + Transmisión en vivo)",
        "venue": "Facultad de Minas · Universidad Nacional de Colombia, Sede Medellín",
        "alliance": "Coorganización internacional con 14° y 16° EICCIE 2025 (UNESP Jaboticabal & Instituto A Nau Ciranda, Brasil)",
        "poster": "../assets/photos/vi-eisi-2025.jpg",
        "about": [
            "El VI Encuentro Internacional de Semilleros de Investigación PREXIA UNAL 2025 convoca a estudiantes, docentes, investigadores y líderes organizacionales a compartir avances de investigación formativa y aplicada con impacto territorial.",
            "Como fruto de la alianza activa entre la Facultad de Minas (UNAL Medellín), la Facultad de Ciencias Agrarias (UNAL Bogotá), UNESP Jaboticabal y el Instituto A Nau Ciranda Sinparedes (INCSP) de Brasil, esta edición articula inmersiones conjuntas con el 14° y 16° EICCIE 2025.",
        ],
        "mesas": [
            {
                "num": "Categoría 01",
                "title": "Innovación, Ingeniería y Emprendimiento para la Transformación de Territorios",
                "topics": [
                    "Proyectos de investigación aplicada orientados a problemáticas sociales, ambientales, económicas o territoriales.",
                    "Creación, validación y gestión de nuevos modelos de negocio y emprendimientos universitarios de impacto.",
                    "Diseños y soluciones organizacionales con impacto en eficiencia, competitividad y sostenibilidad.",
                ],
            },
            {
                "num": "Categoría 02",
                "title": "Nueva Productividad 5.0: Producción, Procesos y Operación Sostenible",
                "topics": [
                    "Tecnologías emergentes y enfoques de ingeniería en infraestructura, minería, agroindustria, manufactura y servicios.",
                    "Logística, cadenas de suministro, políticas públicas, mercado internacional y transformación digital del campo.",
                    "Colaboración humano-máquina, optimización de procesos y sostenibilidad operativa.",
                ],
            },
            {
                "num": "Categoría 03",
                "title": "Mercados con Propósito: Innovación, Impacto y Sostenibilidad",
                "topics": [
                    "Estrategias de marketing e innovación para productos, servicios y proyectos sostenibles en economías emergentes.",
                    "Investigación de mercados, posicionamiento estratégico y consumo responsable.",
                    "Herramientas comerciales para la gestión de negocios sostenibles con alto impacto social.",
                ],
            },
        ],
    },
    "unal-edu-co__prexiaforum__home__v-encuentro-internacional-de-semilleros-2024": {
        "short_title": "V EISI 2024.",
        "edition_badge": "Quinta Edición · 24 y 25 de octubre de 2024 · Modalidad Híbrida",
        "subtitle": "V Encuentro Internacional de Semilleros de Investigación PREXIA 2024 · «Dualidad Humana Tecnológica: El Nuevo Reto Organizacional».",
        "date": "24 y 25 de octubre de 2024",
        "modality": "Híbrida (Presencial en UNAL Medellín y Virtual internacional)",
        "venue": "Facultad de Minas · Universidad Nacional de Colombia, Sede Medellín",
        "alliance": "Articulación internacional Colombia–Brasil (UNAL, UNESP, INCSP)",
        "poster": "../images/unal-edu-co__prexiaforum__home__v-encuentro-internacional-de-semilleros-2024__02__48daefe43e0f.jpg",
        "about": [
            "El V Encuentro Internacional de Semilleros de Investigación (EISI 2024) exploró la convergencia entre el talento humano y las tecnologías disruptivas en la gestión de organizaciones modernas.",
            "Durante dos jornadas de conferencias magistrales y cuatro mesas temáticas especializadas, semilleristas de Colombia, Brasil y Latinoamérica presentaron propuestas en finanzas sostenibles, analítica, logística 4.0 y mercadeo de impacto.",
        ],
        "mesas": [
            {
                "num": "Mesa 01",
                "title": "Finanzas Sostenibles e Inversión de Impacto",
                "topics": [
                    "Fintech, inclusión financiera y desarrollo económico en Latinoamérica.",
                    "Bonos verdes, valoración de empresas y modelos de financiamiento sostenible.",
                    "Gestión de riesgos, futuros, opciones y retornos sociales y ambientales.",
                ],
            },
            {
                "num": "Mesa 02",
                "title": "Optimización de Procesos, Logística y Cadena de Suministro",
                "topics": [
                    "Simulación heurística y metaheurística, Machine Learning, Deep Learning y Big Data.",
                    "Automatización de procesos, Blockchain, Lean & Green Manufacturing y logística inversa.",
                    "Economía circular y productividad de la micro, pequeña y mediana empresa (MiPyme).",
                ],
            },
            {
                "num": "Mesa 03",
                "title": "Talento Humano en Conexión con la Tecnología",
                "topics": [
                    "Desarrollo de competencias 4.0 y 5.0, gestión del conocimiento y liderazgo digital.",
                    "Inteligencia artificial aplicada a la toma de decisiones organizacionales.",
                    "Ética en la era digital, cultura empresarial y competitividad en pymes.",
                ],
            },
            {
                "num": "Mesa 04",
                "title": "Marketing, Innovación y Emprendimiento",
                "topics": [
                    "Innovación social e inclusiva, marketing digital, neuromarketing y endomarketing.",
                    "Ecosistemas de innovación, incubación, aceleración y modelos de negocio disruptivos.",
                    "Smart cities, sostenibilidad urbana y co-creación en iniciativas públicas y privadas.",
                ],
            },
        ],
    },
    "unal-edu-co__prexiaforum__home__iv-encuentro-internacional-de-semilleros-2023": {
        "short_title": "IV EISI 2023.",
        "edition_badge": "Cuarta Edición · 10 y 11 de noviembre de 2023 · Presencial y Virtual",
        "subtitle": "IV Encuentro Internacional de Semilleros de Investigación PREXIA 2023 · «Ingeniando Territorios: Innovación, Ingeniería, Desarrollo Endógeno y la Organización».",
        "date": "10 y 11 de noviembre de 2023",
        "modality": "Híbrida (Auditorios Facultad de Minas y transmisión virtual)",
        "venue": "Facultad de Minas · Universidad Nacional de Colombia, Sede Medellín",
        "alliance": "Red de Semilleros de Ingeniería y Gestión Organizacional de América Latina",
        "poster": "../images/unal-edu-co__prexiaforum__home__iv-encuentro-internacional-de-semilleros-2023__02__ee8a4ddf12b6.jpg",
        "about": [
            "El IV Encuentro Internacional de Semilleros de Investigación puso en el centro del debate académico el desarrollo endógeno y el papel de la ingeniería en la transformación de las regiones.",
            "Contó con la participación de conferencistas internacionales, paneles de relación Universidad–Estado–Empresa y tres mesas temáticas dedicadas a competitividad territorial y sostenibilidad socio-ambiental.",
        ],
        "mesas": [
            {
                "num": "Mesa 01",
                "title": "Innovación, Competitividad y Desarrollo Endógeno",
                "topics": [
                    "Innovación e infraestructura: modernización tangible de las organizaciones.",
                    "Tecnologías habilitadoras, Industria 4.0 y transformación digital.",
                    "Innovación en el sector público y generación de valor agregado en cadenas productivas.",
                ],
            },
            {
                "num": "Mesa 02",
                "title": "Conexiones para el Desarrollo Endógeno",
                "topics": [
                    "Articulación Academia–Estado–Empresa y sistemas regionales de innovación.",
                    "Gestión del talento humano, ingeniería para la vida y apuesta ética universitaria.",
                    "Emprendimiento, MiPymes y perspectivas de inclusión para el desarrollo regional.",
                ],
            },
            {
                "num": "Mesa 03",
                "title": "Negocios Sostenibles e Impacto Socio-Ambiental",
                "topics": [
                    "Agro colombiano como base del desarrollo endógeno y la seguridad alimentaria.",
                    "Gobierno corporativo, responsabilidad social empresarial (RSE) y filantropía organizacional.",
                    "Transición energética, organizaciones verdes e inversión socialmente responsable (ISR).",
                ],
            },
        ],
    },
    "unal-edu-co__prexiaforum__home__iii-encuentro-internacional-de-semilleros-2022": {
        "short_title": "III EISI 2022.",
        "edition_badge": "Tercera Edición · 4 y 5 de noviembre de 2022 · Híbrido",
        "subtitle": "III Encuentro Internacional de Semilleros de Investigación PREXIA 2022 · «Innovación, Ingeniería y Territorios».",
        "date": "4 y 5 de noviembre de 2022",
        "modality": "Híbrida (Jornada virtual internacional y jornada presencial en campus)",
        "venue": "Facultad de Minas · Universidad Nacional de Colombia, Sede Medellín",
        "alliance": "Coorganización entre UNAL Medellín, UNAL Bogotá, UNESP e INCSP",
        "poster": "../images/unal-edu-co__prexiaforum__home__iii-encuentro-internacional-de-semilleros-2022__02__4e7711b8227b.jpg",
        "about": [
            "El Tercer Encuentro Internacional de Semilleros marcó el retorno a la presencialidad combinada con transmisión internacional, articulando un primer día de inmersión virtual latinoamericana y un segundo día presencial en la Facultad de Minas.",
            "Sus tres mesas temáticas abordaron la Industria 4.0 y 5.0, la innovación social colaborativa y el diseño de territorios inteligentes y circulares.",
        ],
        "mesas": [
            {
                "num": "Mesa 01",
                "title": "Transformación Digital, Industria 4.0 y 5.0",
                "topics": [
                    "Plataformas tecnológicas 4.0 y 5.0, Smart Manufacturing y gestión del cambio.",
                    "Analítica, Big Data, Internet de las Cosas (IoT), Cloud Computing y ciberseguridad.",
                    "Cobots, computación cognitiva, Smart Economy y Smart Governance.",
                ],
            },
            {
                "num": "Mesa 02",
                "title": "Innovación Social y Redes de Colaboración",
                "topics": [
                    "Empresarismo e intraemprendimiento social, Open Innovation y economía social.",
                    "Design Thinking, Human Centered Design y tecnologías sostenibles.",
                    "Negociación colaborativa, cambio sistémico y comunidades de práctica.",
                ],
            },
            {
                "num": "Mesa 03",
                "title": "Territorios Inteligentes y Economía Circular",
                "topics": [
                    "Organizaciones híbridas, ecodiseño, ecoeficiencia, ecotecnología y Cleaner Production.",
                    "Evaluación de impacto social, cambio climático y complejos productivos.",
                    "Objetivos de Desarrollo Sostenible (ODS) y colaboración público-privada.",
                ],
            },
        ],
    },
    "unal-edu-co__prexiaforum__home__ii-encuentro-internacional-de-semilleros-2021": {
        "short_title": "II EISI 2021.",
        "edition_badge": "Segunda Edición · 5 y 6 de noviembre de 2021 · Modalidad Virtual",
        "subtitle": "II Encuentro Internacional de Semilleros de Investigación PREXIA 2021 · «Desarrollo Tecnológico e Innovación en el Panorama Post-Pandemia».",
        "date": "5 y 6 de noviembre de 2021",
        "modality": "100% Virtual con transmisión internacional en vivo",
        "venue": "Plataforma PREXIA Forum · Facultad de Minas UNAL Medellín",
        "alliance": "Grupo de Investigación en Innovación y Gestión Tecnológica · UNAL & Aliados",
        "poster": "../assets/photos/ii-eisi-2021-poster.jpg",
        "about": [
            "La segunda edición del Encuentro Internacional de Semilleros consolidó la red latinoamericana de investigación formativa con cinco mesas temáticas enfocadas en la reactivación económica, la resiliencia organizacional y la digitalización productiva.",
            "Reunió a estudiantes de pregrado y posgrado, docentes e investigadores de Colombia, Brasil y México en dos días de conferencias magistrales y ponencias evaluadas por pares.",
        ],
        "mesas": [
            {
                "num": "Mesa 01",
                "title": "Transformación Digital, Industria 4.0 y 5.0",
                "topics": [
                    "Smart Manufacturing, renovación tecnológica, Analítica, Big Data e IoT.",
                    "Cloud Computing, ciberseguridad, cobots y computación cognitiva.",
                ],
            },
            {
                "num": "Mesa 02",
                "title": "Sostenibilidad en las Organizaciones",
                "topics": [
                    "Objetivos de Desarrollo Sostenible, economía circular y Triple Bottom Line.",
                    "Life Cycle Assessment, ecodiseño y transformación estratégica.",
                ],
            },
            {
                "num": "Mesa 03",
                "title": "Procesos, Optimización y Producción",
                "topics": [
                    "Simulación de procesos productivos y servicios, modelamiento matemático y calidad.",
                    "Diseño de instalaciones, planeamiento energético y gestión de cadena de suministro.",
                ],
            },
            {
                "num": "Mesa 04",
                "title": "Resiliencia y Gestión Organizacional",
                "topics": [
                    "Gestión de crisis organizacionales, cadenas resilientes y salud organizacional.",
                    "Análisis de decisiones bajo incertidumbre, gestión del riesgo e inteligencia de negocios.",
                ],
            },
            {
                "num": "Mesa 05",
                "title": "Emprendimiento y Responsabilidad Social",
                "topics": [
                    "Lean Startup, Spin-offs universitarias, ecosistemas de emprendimiento y New Ventures.",
                    "Responsabilidad Social Empresarial y Ambiental e indicadores de impacto.",
                ],
            },
        ],
    },
    "unal-edu-co__prexiaforum__home__i-encuentro-internacional-de-semilleros-2020": {
        "short_title": "I EISI 2020.",
        "edition_badge": "Edición Fundacional · 6 y 7 de noviembre de 2020 · Modalidad Virtual",
        "subtitle": "I Encuentro Internacional de Semilleros de Investigación PREXIA 2020 · «Resiliencia Organizacional y Transformación Digital en Tiempos de Crisis».",
        "date": "6 y 7 de noviembre de 2020",
        "modality": "Virtual en vivo · Idioma oficial: Español",
        "venue": "Universidad Nacional de Colombia · Sede Medellín (Facultad de Minas)",
        "alliance": "Premiación de mejores ponencias en la Revista ENSAYOS (UNAL Sede Manizales)",
        "poster": "../images/unal-edu-co__prexiaforum__home__i-encuentro-internacional-de-semilleros-2020__03__ac951ddd006a.jpg",
        "about": [
            "El Primer Encuentro Internacional de Semilleros de Investigación nació en noviembre de 2020 para visibilizar la producción académica estudiantil en áreas organizacionales y crear redes de cooperación científica en plena coyuntura global.",
            "Contó con conferencias magistrales de referentes internacionales como Fernando Antonio Beltrame, Silvia Inês Dallavalle de Pádua (USP/UNESP) y Ronald Koepke, además de la publicación de las mejores ponencias en la Revista ENSAYOS de la UNAL.",
        ],
        "mesas": [
            {
                "num": "Mesa 01",
                "title": "Transformación Digital, Industria 4.0 y 5.0",
                "topics": [
                    "Plataformas tecnológicas 4.0 y 5.0, Smart Manufacturing y gestión del cambio.",
                    "Analítica, Big Data, IoT, Cloud Computing y ciberseguridad organizacional.",
                ],
            },
            {
                "num": "Mesa 02",
                "title": "Sostenibilidad en las Organizaciones",
                "topics": [
                    "Objetivos de Desarrollo Sostenible, economía circular y gestión de organizaciones sociales.",
                    "Triple Bottom Line, ecodiseño y sistemas de información ambiental.",
                ],
            },
            {
                "num": "Mesa 03",
                "title": "Modelamiento, Simulación y Optimización de Procesos",
                "topics": [
                    "Simulación de procesos productivos y de operaciones, modelamiento matemático y optimización.",
                    "Diseño de plantas, cadena de suministro y estudios prospectivos.",
                ],
            },
            {
                "num": "Mesa 04",
                "title": "Resiliencia y Gestión Organizacional",
                "topics": [
                    "Gestión de crisis, cadenas de suministro resilientes y teoría de recursos y capacidades.",
                    "Toma de decisiones bajo incertidumbre, gestión de la innovación y del conocimiento.",
                ],
            },
            {
                "num": "Mesa 05",
                "title": "Emprendimiento y Responsabilidad Social",
                "topics": [
                    "Market Space, Lean Startup, Spin-offs y herramientas de validación temprana.",
                    "Responsabilidad Social Empresarial y Ambiental y casos de éxito.",
                ],
            },
        ],
    },
    "unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__evento-2019": {
        "short_title": "Encuentro 2019.",
        "edition_badge": "I Encuentro Nacional · 28 y 29 de noviembre de 2019 · Campus Robledo UNAL",
        "subtitle": "I Encuentro Nacional de Semilleros de Investigación · «Perspectivas de Innovación en la Gestión de las Organizaciones: Competitividad y Productividad».",
        "date": "28 y 29 de noviembre de 2019",
        "modality": "Presencial · Trabajo teórico (ponencias) y práctico (retos empresariales)",
        "venue": "Campus Robledo · Facultad de Minas, UNAL Medellín & Autónoma de las Américas",
        "alliance": "Coorganización con Fundación Universitaria Autónoma de las Américas, SENA SBDC y CIE Esumer",
        "poster": "../images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__07__899ec7e54f18.jpg",
        "about": [
            "El Primer Encuentro Nacional de Semilleros de Investigación reunió en noviembre de 2019 a estudiantes de pregrado de la Universidad Nacional de Colombia, la Fundación Universitaria Autónoma de las Américas y universidades invitadas del país en torno a los métodos de investigación aplicados a la competitividad y gestión de organizaciones.",
            "Se estructuró en dos fases complementarias: una jornada teórica de ponencias magistrales y socialización de avances (propuestas, proyectos en curso e investigaciones terminadas), y una jornada práctica de solución de retos empresariales con premios y candidatura a publicación en el Fondo Editorial.",
        ],
        "mesas": [
            {
                "num": "Mesa 01",
                "title": "Modelamiento, Simulación y Optimización de Procesos",
                "topics": [
                    "Simulación de procesos productivos y de operaciones.",
                    "Modelamiento matemático, optimización y diseño de instalaciones de manufactura.",
                ],
            },
            {
                "num": "Mesa 02",
                "title": "Industria 4.0 · Smart Manufacturing",
                "topics": [
                    "Analítica, Internet de las Cosas (IoT), Cloud Computing y Ciberseguridad.",
                    "Casos de implementación de herramientas de la Industria 4.0 en organizaciones reales.",
                ],
            },
            {
                "num": "Mesa 03",
                "title": "Gestión de la Sostenibilidad en Organizaciones",
                "topics": [
                    "Estrategia corporativa, procesos de transformación estratégica y Ética y RSE.",
                    "Objetivos de Desarrollo Sostenible, resiliencia y economía circular.",
                ],
            },
            {
                "num": "Mesa 04",
                "title": "Diseño y Gestión de Organizaciones",
                "topics": [
                    "Inteligencia de negocios, análisis de decisiones bajo incertidumbre y gestión del riesgo.",
                    "Pensamiento creativo, tendencias en diseño organizacional y gestión de la innovación.",
                ],
            },
            {
                "num": "Mesa 05",
                "title": "Emprendimiento · Lean Startup",
                "topics": [
                    "Spin-offs, modelos de emprendimiento y ecosistemas de innovación.",
                    "Formación en emprendimiento, New Ventures y casos de éxito empresarial.",
                ],
            },
        ],
    },
}

DEFAULT_DOCUMENTARY_PHOTOS = [
    "images/unal-edu-co__prexiaforum__home__i-encuentro-internacional-de-semilleros-2020__03__ac951ddd006a.jpg",
    "images/unal-edu-co__prexiaforum__home__i-encuentro-internacional-de-semilleros-2020__04__3d53a84daed8.jpg",
    "images/unal-edu-co__prexiaforum__home__vi-eisi-2025__04__6fd6c9c52f62.jpg",
    "images/unal-edu-co__prexiaforum__home__vi-eisi-2025__participa-2025__03__88ebbf9e5d3a.jpg",
    "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-consultor-c3-ada__04__cff182fe819d.jpg",
    "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__03__0bb63af26d05.jpg",
]

CSS = """
:root {
  --bg: #f7f7f5;
  --surface: #ecebe6;
  --surface-alt: #e2e0d8;
  --surface-card: #fdfdfc;
  --ink: #1f1a3a;
  --muted: #4a4662;
  --line: rgba(31, 26, 58, 0.14);
  --mint-dark: #0f652e;
  --mint-light: #84fbaa;
  --cyan-light: #60eaf0;
  --field-navy: #1f1a3a;
  --field-navy-surface: #2b244d;
  --field-navy-ink: #f7f7f5;
  --field-navy-muted: #c2bddb;
  --radius: 2px;
  --margin: clamp(1.25rem, 3.2vw, 3.2rem);
  --gutter: clamp(1.25rem, 2.2vw, 2.25rem);
  --font-display: 'Libre Franklin', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-text: 'Source Serif 4', Georgia, serif;
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  scroll-behavior: smooth;
  background: var(--bg);
  color: var(--ink);
  overflow-x: clip;
}

body {
  margin: 0;
  font-family: var(--font-text);
  font-size: 18px;
  line-height: 1.62;
  color: var(--ink);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
  overflow-x: clip;
}

a {
  color: inherit;
  text-decoration: none;
}

img {
  display: block;
  max-width: 100%;
  height: auto;
}

.shell {
  width: min(1360px, calc(100% - var(--margin) * 2));
  margin: 0 auto;
}

/* ── TOPBAR EDITORIAL CON ISOTIPO PREXIA ── */
.topbar {
  background: var(--bg);
  padding: 24px 0 20px;
}

.topbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--ink);
}

.brand em {
  font-style: normal;
  color: var(--mint-dark);
}

.brand-sub {
  font-family: var(--font-text);
  font-size: 14px;
  font-weight: 400;
  color: var(--muted);
  padding-left: 6px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 22px;
  flex-wrap: wrap;
}

.nav-links a {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--muted);
  transition: color 0.18s ease-out;
}

.nav-links a:hover,
.nav-links a.active {
  color: var(--ink);
}

.nav-cta {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--bg);
  background: var(--ink);
  padding: 10px 18px;
  border-radius: var(--radius);
  transition: transform 0.15s var(--ease-out);
}

.nav-cta:hover {
  transform: translateY(-1px);
}

.nav-action {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
  text-decoration: underline;
  text-underline-offset: 4px;
}

/* ── SUB-NAVEGACIÓN DE EDICIONES EISI ── */
.eisi-subnav {
  background: var(--surface);
  padding: 14px 0;
}

.eisi-subnav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.eisi-editions-pills,
.eisi-child-pills {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.eisi-pill {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: var(--radius);
  color: var(--muted);
  background: var(--bg);
  transition: background-color 0.15s ease-out, color 0.15s ease-out;
}

.eisi-pill:hover {
  color: var(--ink);
  background: var(--surface-alt);
}

.eisi-pill.active {
  background: var(--ink);
  color: var(--bg);
}

/* ── HERO ARCHIVO / CATÁLOGO ── */
.archive-hero {
  padding: 40px 0 48px;
}

.archive-hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 56%) 1fr;
  gap: var(--gutter);
  align-items: end;
}

.archive-hero-title {
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 4.8vw, 4.35rem);
  font-weight: 800;
  line-height: 0.98;
  letter-spacing: -0.035em;
  color: var(--ink);
  margin-bottom: 18px;
}

.archive-lead {
  font-size: 18px;
  line-height: 1.6;
  color: var(--muted);
  max-width: 54ch;
}

.archive-stats-box {
  background: var(--surface);
  padding: 28px;
  border-radius: var(--radius);
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-unit strong {
  display: block;
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  line-height: 1.1;
  color: var(--ink);
  margin-bottom: 4px;
}

.stat-unit span {
  font-size: 14px;
  color: var(--muted);
}

/* ── FILTROS INTERACTIVOS DEL DIRECTORIO ── */
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 32px;
  background: var(--surface);
  padding: 16px 20px;
  border-radius: var(--radius);
}

.filter-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-btn {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  padding: 8px 14px;
  border: none;
  border-radius: var(--radius);
  background: var(--bg);
  color: var(--muted);
  cursor: pointer;
  transition: background-color 0.15s ease-out, color 0.15s ease-out;
}

.filter-btn:hover,
.filter-btn.active {
  background: var(--ink);
  color: var(--bg);
}

.filter-search {
  padding: 9px 14px;
  font-family: var(--font-text);
  font-size: 18px;
  background: var(--bg);
  color: var(--ink);
  border: 1px solid rgba(31, 26, 58, 0.2); /* taste-skill-ignore */
  border-radius: var(--radius);
  min-width: 260px;
}

/* ── SECCIONES Y GRILLAS ── */
.section {
  padding: 56px 0;
}

.section-header {
  margin-bottom: 32px;
}

.section-title {
  font-family: var(--font-display);
  font-size: clamp(2rem, 3.2vw, 3rem);
  font-weight: 800;
  letter-spacing: -0.025em;
  line-height: 1.04;
  color: var(--ink);
  margin-bottom: 10px;
}

.section-desc {
  font-size: 18px;
  color: var(--muted);
  max-width: 60ch;
}

.grid-cards {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 24px;
}

.card {
  background: var(--surface);
  padding: 28px;
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 16px;
}

.card.span-4 { grid-column: span 4; }
.card.span-6 { grid-column: span 6; }
.card.span-12 { grid-column: span 12; }

.card-cover {
  aspect-ratio: 16/10;
  overflow: hidden;
  margin-bottom: 14px;
  background: var(--field-navy);
  padding: 8px;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.card-meta-tag {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--mint-dark);
  margin-top: 6px;
}

.card-title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  line-height: 1.2;
  color: var(--ink);
  margin-bottom: 6px;
}

.card-excerpt {
  font-size: 18px;
  line-height: 1.58;
  color: var(--ink);
  margin-top: 10px;
}

.btn-card {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
  text-decoration: underline;
  text-underline-offset: 4px;
  margin-top: auto;
}

/* ── TARJETAS DE CONFERENCISTAS Y EQUIPO (RETRATOS LIMPIOS) ── */
.speakers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin: 28px 0 36px;
}

.speaker-card {
  background: var(--surface);
  padding: 24px;
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.speaker-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.speaker-avatar {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--field-navy);
}

.speaker-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.speaker-name {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  line-height: 1.18;
  color: var(--ink);
  display: block;
}

.speaker-role {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--mint-dark);
  display: block;
  margin-top: 4px;
}

.speaker-bio {
  font-size: 18px;
  line-height: 1.58;
  color: var(--muted);
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
  margin: 20px 0 36px;
}

.team-card {
  background: var(--surface);
  padding: 22px;
  border-radius: var(--radius);
}

.team-card strong {
  display: block;
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  color: var(--ink);
  line-height: 1.2;
}

.team-card .team-role {
  display: block;
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--mint-dark);
  margin-top: 4px;
}

.team-card p {
  font-size: 14px;
  color: var(--muted);
  line-height: 1.5;
  margin-top: 8px;
  margin-bottom: 0;
}

/* ── PÁGINA ESTRUCTURADA DE EVENTO EISI ── */
.eisi-hero {
  padding: 48px 0 56px;
}

.eisi-hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 54%) 1fr;
  gap: calc(var(--gutter) * 1.5);
  align-items: center;
}

.eisi-hero-title {
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 4.8vw, 4.35rem);
  font-weight: 800;
  line-height: 0.98;
  letter-spacing: -0.035em;
  color: var(--ink);
  margin-bottom: 14px;
}

.eisi-hero-badge {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--mint-dark);
  margin-bottom: 16px;
}

.eisi-hero-lead {
  font-size: 22px;
  line-height: 1.52;
  color: var(--ink);
  margin-bottom: 16px;
}

.eisi-hero-about p {
  font-size: 18px;
  line-height: 1.62;
  color: var(--muted);
  margin-bottom: 14px;
}

.eisi-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 20px;
}

.eisi-meta-card {
  background: var(--surface);
  padding: 16px;
  border-radius: var(--radius);
}

.eisi-meta-card strong {
  display: block;
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 800;
  color: var(--ink);
  margin-bottom: 4px;
}

.eisi-meta-card span {
  font-size: 14px;
  color: var(--muted);
  line-height: 1.45;
  display: block;
}

.eisi-poster-showcase {
  background: var(--field-navy);
  padding: 20px;
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.eisi-poster-showcase img {
  width: 100%;
  max-height: 460px;
  object-fit: contain;
  border-radius: var(--radius);
}

.eisi-poster-caption {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: var(--field-navy-muted);
}

.roles-grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.role-box {
  background: var(--bg);
  padding: 28px;
  border-radius: var(--radius);
}

.role-box h3 {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  color: var(--ink);
  margin-bottom: 8px;
}

.role-box p {
  font-size: 18px;
  color: var(--muted);
  line-height: 1.58;
}

.mesas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.mesa-card {
  background: var(--surface);
  padding: 28px;
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mesa-card h3,
.mesa-title {
  display: block;
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  color: var(--ink);
  line-height: 1.22;
}

/* ── MOTION LAYER (ENTRANCE & SCROLL REVEAL) ── */
.eisi-hero,
.archive-hero,
.page-article {
  transition: opacity 0.65s var(--ease-out), transform 0.65s var(--ease-out);
}

.js:not(.in) .eisi-hero,
.js:not(.in) .archive-hero,
.js:not(.in) .page-article {
  opacity: 0.01;
  transform: translateY(16px);
}

.reveal-item {
  opacity: 0.01;
  transform: translateY(18px);
  transition: opacity 0.6s var(--ease-out), transform 0.6s var(--ease-out);
}

.reveal-item.is-visible {
  opacity: 1;
  transform: translateY(0);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
  .eisi-hero, .archive-hero, .page-article, .reveal-item {
    opacity: 1 !important;
    transform: none !important;
  }
}

.mesa-num {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--mint-dark);
}

.mesa-topics {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 4px;
}

.mesa-topics li {
  font-size: 14px;
  line-height: 1.5;
  color: var(--ink);
  padding-left: 14px;
  position: relative;
}

.mesa-topics li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: var(--mint-dark);
  font-weight: 700;
}

/* ── LAYOUT DE PÁGINA INDIVIDUAL ── */
.page-layout {
  display: grid;
  grid-template-columns: minmax(0, 68%) 1fr;
  gap: calc(var(--gutter) * 1.8);
  padding: 48px 0 88px;
  align-items: start;
}

.page-article {
  background: var(--bg);
}

.breadcrumb-trail {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 14px;
  color: var(--muted);
  margin-top: 14px;
  margin-bottom: 20px;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.breadcrumb-trail span + span::before {
  content: " / ";
  color: var(--muted);
  padding: 0 4px;
}

.breadcrumb-trail a {
  color: var(--muted);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.breadcrumb-trail a:hover {
  color: var(--ink);
}

.page-title {
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 4.8vw, 4.35rem);
  font-weight: 800;
  line-height: 0.98;
  letter-spacing: -0.035em;
  color: var(--ink);
  margin-bottom: 10px;
}

.meta-original {
  font-size: 14px;
  color: var(--muted);
  margin-bottom: 28px;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.meta-original a {
  text-decoration: underline;
}

.page-copy {
  max-width: 68ch;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.page-copy p {
  font-size: 18px;
  line-height: 1.66;
  color: var(--ink);
  margin-bottom: 20px;
}

.page-copy h2,
.page-copy h3,
.editorial-subhead {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  line-height: 1.25;
  color: var(--ink);
  margin-top: 32px;
  margin-bottom: 12px;
}

.page-copy ul,
.page-copy ol {
  margin: 16px 0 24px 24px;
}

.page-copy li {
  margin-bottom: 8px;
  line-height: 1.55;
}

/* ── GALERÍA DE IMÁGENES SIN RECORTE (CONTAIN) ── */
.gallery-section {
  margin-top: 48px;
  padding-top: 32px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.gallery-thumb {
  background: var(--surface);
  padding: 12px;
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.gallery-thumb img {
  width: 100%;
  max-height: 320px;
  object-fit: contain;
  border-radius: var(--radius);
}

/* ── FRANJA DE ALIADOS INSTITUCIONALES (SIN RECORTE) ── */
.allies-strip-section {
  margin-top: 48px;
  background: var(--surface);
  padding: 28px;
  border-radius: var(--radius);
}

.allies-strip-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 14px;
  margin-top: 16px;
}

.ally-mini-card {
  background: var(--surface-card);
  padding: 14px 12px;
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  text-align: center;
}

.ally-mini-card img {
  max-height: 48px;
  max-width: 110px;
  width: auto;
  height: auto;
  object-fit: contain;
}

.ally-mini-card span {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.25;
}

/* ── SIDEBAR EDITORIAL ── */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: sticky;
  top: 88px;
}

.sidebar-box {
  background: var(--surface);
  padding: 24px;
  border-radius: var(--radius);
}

.sidebar-heading {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 800;
  color: var(--ink);
  margin-bottom: 12px;
}

.sidebar-nav-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar-nav-item {
  font-size: 14px;
  color: var(--muted);
  padding: 4px 0;
  line-height: 1.4;
  transition: color 0.15s ease-out;
}

.sidebar-nav-item:hover {
  color: var(--ink);
}

.sidebar-nav-item.active {
  font-weight: 700;
  color: var(--ink);
}

/* ── TABLAS FORMALES (PDF PREXIA) ── */
.prexia-table {
  width: 100%;
  border-collapse: collapse;
  margin: 24px 0;
  font-size: 14px;
}

.prexia-table th,
.prexia-table td {
  padding: 12px 14px;
  text-align: left;
  border-bottom: 1px solid var(--line); /* taste-skill-ignore */
}

.prexia-table th {
  font-family: var(--font-display);
  font-weight: 800;
  color: var(--ink);
  background: var(--surface);
}

/* ── FOOTER SITIO CON ISOTIPO Y REDES ── */
.site-footer {
  background: var(--field-navy);
  color: var(--field-navy-ink);
  padding: 64px 0 48px;
  margin-top: 72px;
}

.footer-inner {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 32px;
}

.footer-brand-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  color: var(--field-navy-ink);
  margin-bottom: 10px;
}

.footer-brand-row em {
  font-style: normal;
  color: var(--mint-light);
}

.footer-info p {
  font-size: 14px;
  color: var(--field-navy-muted);
  max-width: 48ch;
  line-height: 1.55;
}

.footer-links-row {
  display: flex;
  gap: 22px;
  flex-wrap: wrap;
  align-items: center;
}

.footer-links-row a {
  font-size: 14px;
  color: var(--field-navy-muted);
  transition: color 0.15s ease-out;
}

.footer-links-row a:hover {
  color: var(--mint-light);
}

@media (max-width: 960px) {
  .archive-hero-grid,
  .eisi-hero-grid,
  .roles-grid-3,
  .page-layout,
  .archive-stats-box {
    grid-template-columns: 1fr;
  }
  .card.span-4,
  .card.span-6 {
    grid-column: span 12;
  }
  .sidebar {
    position: static;
  }
  .card-title,
  .mesa-title,
  .mesa-card h3,
  .editorial-subhead,
  .role-box h3,
  .speaker-name,
  .team-card strong,
  .eisi-hero-lead {
    font-size: 18px;
  }
}
"""


def load_manifest() -> dict:
    return json.loads((SOURCE_DIR / "manifest.json").read_text(encoding="utf-8"))


def parse_markdown(path: Path) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8").splitlines()
    lines: list[str] = []
    images: list[str] = []
    mode = None
    for line in text:
        if line == "## Texto extraido":
            mode = "text"
            continue
        if line.startswith("## Imagenes"):
            mode = "images"
            continue
        if not line.strip():
            continue
        if mode == "text":
            lines.append(line.strip())
        elif mode == "images" and line.startswith("- "):
            parts = line[2:].split(" (", 1)
            image_path = parts[0].strip()
            alt_label = parts[1][:-1].strip().lower() if len(parts) > 1 else ""
            if alt_label in {"facebook", "instagram", "linkedin", "email", "youtube"}:
                continue
            if image_path:
                images.append(image_path)
    return lines, images


def classify_page_images(images: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """Separa fotografías y afiches reales vs logos de aliados usando el hash MD5 real del archivo."""
    content_images: list[str] = []
    ally_logos: list[tuple[str, str]] = []
    seen_ally_names: set[str] = set()
    seen_md5s: set[str] = set()

    for img_rel in images:
        img_file = SOURCE_DIR / img_rel
        if not img_file.exists():
            continue

        file_bytes = img_file.read_bytes()
        size = len(file_bytes)
        md5 = hashlib.md5(file_bytes).hexdigest()[:12]

        # Excluir íconos de redes sociales, botones decorativos, banderas y retratos (que van en .speakers-grid)
        if md5 in EXCLUDED_IMAGE_MD5S or md5 in SPEAKER_PORTRAIT_MD5S:
            continue

        if size < 10000 or size == 42819:
            continue

        if md5 in ALLY_LOGO_MD5S:
            ally_name = ALLY_LOGO_MD5S[md5]
            if ally_name not in seen_ally_names:
                seen_ally_names.add(ally_name)
                ally_logos.append((img_rel, ally_name))
            continue

        if md5 in seen_md5s:
            continue
        seen_md5s.add(md5)
        content_images.append(img_rel)

    return content_images, ally_logos


UI_NOISE_LINES = {
    "organizan:",
    "-o-",
    "click aquí para ver el evento ¡en vivo!",
    "click aquí para ver el evento ¡en vivo",
    "pulsa en los siguientes titulares y despliega su contenido para más información",
    "es",
}


def normalize_text_lines(lines: list[str]) -> list[str]:
    merged: list[str] = []
    for raw_line in lines:
        line = " ".join(raw_line.split())
        if not line or line.lower() in UI_NOISE_LINES:
            continue
        if not merged:
            merged.append(line)
            continue

        previous = merged[-1]
        # Si la línea es un signo de puntuación suelto o fragmento de 1-2 letras (como 'o', 'l', 'v', '.', ',')
        if line in {".", ",", ":", ";", "!", "?"}:
            merged[-1] = f"{previous}{line}"
            continue
        if len(line) <= 2 and line.islower() and not previous.endswith((".", ":", "!", "?")):
            merged[-1] = f"{previous}{line}"
            continue
        if len(previous) == 1 and previous.isupper() and line[:1].islower():
            merged[-1] = f"{previous}{line}"
            continue
        if len(previous) <= 2 and previous.isdigit():
            merged[-1] = f"{previous} {line}"
            continue
        if len(line) <= 2 and line.isdigit():
            merged[-1] = f"{previous} {line}"
            continue

        should_merge = False
        if (
            previous
            and not previous.endswith((".", ":", "?", "!"))
            and not previous.isupper()
            and (line[:1].islower() or line.startswith((",", ".", ";", ")")))
        ):
            should_merge = True

        if should_merge:
            sep = "" if line.startswith((",", ".", ";", ")")) else " "
            merged[-1] = f"{previous}{sep}{line}"
        else:
            merged.append(line)
    return merged


def clean_display_title(raw_title: str) -> str:
    """Elimina el prefijo redundante 'Semillero Prexia - ' para titulares concisos."""
    cleaned = raw_title.strip()
    if cleaned.lower().startswith("semillero prexia - "):
        cleaned = cleaned[len("semillero prexia - "):].strip()
    if cleaned.lower() == "es":
        return "Líneas Prexia (ES)"
    if cleaned.lower() == "galeria":
        return "Galería 2019"
    return cleaned


def title_case_from_segment(segment: str) -> str:
    raw = unquote(segment).replace("-", " ")
    return " ".join(part.capitalize() for part in raw.split())


def page_output_name(slug: str) -> str:
    return f"{slug}.html"


def page_href(slug: str) -> str:
    return f"pages/{page_output_name(slug)}"


def render_speakers_section(speakers: list[dict], heading: str = "Conferencistas Magistrales Invitados") -> str:
    cards = "".join(
        f"""
        <article class="speaker-card">
          <div class="speaker-header">
            <div class="speaker-avatar">
              <img src="{html.escape(sp['img'])}" alt="{html.escape(sp['name'])}" loading="lazy">
            </div>
            <div>
              <strong class="speaker-name">{html.escape(sp['name'])}</strong>
              <span class="speaker-role">{html.escape(sp['role'])}</span>
            </div>
          </div>
          <p class="speaker-bio">{html.escape(sp['bio'])}</p>
        </article>
        """
        for sp in speakers
    )
    return f"""
    <section class="section" style="padding:28px 0;">
      <h2 class="editorial-subhead" style="margin-top:0;">{html.escape(heading)}</h2>
      <div class="speakers-grid">{cards}</div>
    </section>
    """


def render_allies_strip(ally_logos: list[tuple[str, str]], prefix: str = "../") -> str:
    if not ally_logos:
        ally_logos = [
            ("images/unal-edu-co__prexiaforum__home__v-encuentro-internacional-de-semilleros-2024__09__6bf6ffd21445.jpg", "Universidad Nacional de Colombia"),
            ("images/unal-edu-co__prexiaforum__home__v-encuentro-internacional-de-semilleros-2024__10__8be6f665e515.jpg", "Grupo Geyma · UNAL Medellín"),
            ("images/unal-edu-co__prexiaforum__home__v-encuentro-internacional-de-semilleros-2024__12__cf582afe5603.jpg", "Facultad de Ciencias Agrarias · UNAL"),
            ("images/unal-edu-co__prexiaforum__home__v-encuentro-internacional-de-semilleros-2024__13__31257c8ed477.jpg", "UNESP · São Paulo, Brasil"),
            ("images/unal-edu-co__prexiaforum__home__v-encuentro-internacional-de-semilleros-2024__14__7393e1c00186.jpg", "UNESP · Campus Jaboticabal"),
            ("images/unal-edu-co__prexiaforum__home__v-encuentro-internacional-de-semilleros-2024__15__efb96efba9bf.jpg", "Instituto A Nau Ciranda · Brasil"),
        ]
    cards = "".join(
        f"""
        <div class="ally-mini-card">
          <img src="{prefix}{html.escape(img_rel)}" alt="{html.escape(name)}" loading="lazy">
          <span>{html.escape(name)}</span>
        </div>
        """
        for img_rel, name in ally_logos
    )
    return f"""
    <section class="allies-strip-section">
      <h3 class="editorial-subhead" style="margin-top:0;">Instituciones Organizadoras y Aliadas</h3>
      <div class="allies-strip-grid">{cards}</div>
    </section>
    """


def ensure_min_photos(photos: list[str], min_count: int = 4, exclude_name: str = "") -> list[str]:
    result = list(photos)
    existing_names = {Path(p).name for p in result}
    if exclude_name:
        existing_names.add(exclude_name)
    for fallback in DEFAULT_DOCUMENTARY_PHOTOS:
        if len(result) >= min_count:
            break
        if Path(fallback).name not in existing_names:
            result.append(fallback)
            existing_names.add(Path(fallback).name)
    return result


def build_eisi_event_page(page: dict, children: list[dict], content_images: list[str], ally_logos: list[tuple[str, str]]) -> str:
    slug = page["slug"]
    info = EISI_STRUCTURED_DATA[slug]

    editions_pills = []
    for year, label, ed_slug in EISI_EDITIONS_NAV:
        active = " active" if ed_slug == slug else ""
        editions_pills.append(
            f'<a class="eisi-pill{active}" href="{html.escape(page_output_name(ed_slug))}">{html.escape(label)}</a>'
        )

    child_pills = []
    for child in children:
        short_child = clean_display_title(child["title"])
        child_pills.append(
            f'<a class="eisi-pill" href="{html.escape(page_output_name(child["slug"]))}">{html.escape(short_child)} →</a>'
        )

    about_paragraphs = "".join(f"<p>{html.escape(p)}</p>" for p in info["about"])

    mesas_cards = []
    for mesa in info["mesas"]:
        topics_html = "".join(f"<li>{html.escape(t)}</li>" for t in mesa["topics"])
        mesas_cards.append(
            f"""
            <article class="mesa-card">
              <strong class="mesa-title">{html.escape(mesa['title'])}</strong>
              <div class="mesa-num">{html.escape(mesa['num'])}</div>
              <ul class="mesa-topics">{topics_html}</ul>
            </article>
            """
        )

    speakers_block = ""
    if slug == "unal-edu-co__prexiaforum__home__i-encuentro-internacional-de-semilleros-2020":
        speakers_block = f'<div class="shell">{render_speakers_section(SPEAKERS_2020)}</div>'
    elif slug == "unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__evento-2019":
        speakers_block = f'<div class="shell">{render_speakers_section(SPEAKERS_2019, "Conferencistas Invitados · Encuentro Nacional 2019")}</div>'

    extra_photos = [img for img in content_images if Path(img).name not in Path(info["poster"]).name]
    if slug == "unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__evento-2019":
        extra_photos = [
            "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__02__87b31aedafe3.jpg",
            "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__03__0bb63af26d05.jpg",
            "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__04__89e65143a6a4.jpg",
            "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__05__65a65f68e794.jpg",
            "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__06__08ae494069e0.jpg",
            "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__08__312ee1b5bd7a.jpg",
        ]
    extra_photos = ensure_min_photos(extra_photos, min_count=4, exclude_name=Path(info["poster"]).name)

    items = "".join(
        f'<a class="gallery-thumb" href="../{html.escape(img)}" target="_blank" rel="noreferrer"><img src="../{html.escape(img)}" alt="{html.escape(page["title"])}" loading="lazy"></a>'
        for img in extra_photos
    )
    gallery_html = f"""
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">Memoria gráfica.</h2>
        <p class="section-desc">Afiches, sesiones académicas y registro visual oficial de la edición ({len(extra_photos)} recursos).</p>
      </div>
      <div class="gallery-grid">{items}</div>
    </section>
    """

    subpages_cards = ""
    if children:
        scards = "".join(
            f"""
            <article class="card span-4">
              <div>
                <strong class="card-title" style="display:block;"><a href="{html.escape(page_output_name(child['slug']))}">{html.escape(clean_display_title(child['title']))}</a></strong>
                <div class="card-meta-tag">Subpágina oficial de la edición</div>
                <p class="card-excerpt">Consulta el detalle completo de {html.escape(clean_display_title(child['title']).lower())} correspondiente a esta edición del Encuentro.</p>
              </div>
              <a class="btn-card" href="{html.escape(page_output_name(child['slug']))}">Abrir {html.escape(clean_display_title(child['title']))} →</a>
            </article>
            """
            for child in children
        )
        subpages_cards = f"""
        <section class="section" style="background:var(--surface);padding:56px 0;">
          <div class="shell">
            <div class="section-header">
              <h2 class="section-title">Secciones del encuentro.</h2>
              <p class="section-desc">Explora las subpáginas específicas de agenda, mesas temáticas, conferencistas y modalidades de participación.</p>
            </div>
            <div class="grid-cards">{scards}</div>
          </div>
        </section>
        """

    return f"""
<nav class="eisi-subnav" aria-label="Ediciones Encuentros Internacionales EISI">
  <div class="shell eisi-subnav-inner">
    <div class="eisi-editions-pills">
      {''.join(editions_pills)}
    </div>
    <div class="eisi-child-pills">
      {''.join(child_pills)}
    </div>
  </div>
</nav>

<main>
  <section class="shell eisi-hero">
    <div class="eisi-hero-grid">
      <div>
        <h1 class="eisi-hero-title">{html.escape(info['short_title'])}</h1>
        <div class="eisi-hero-badge">{html.escape(info['edition_badge'])}</div>
        <p class="eisi-hero-lead">{html.escape(info['subtitle'])}</p>
        <div class="eisi-hero-about">
          {about_paragraphs}
        </div>
        <div class="eisi-meta-grid">
          <div class="eisi-meta-card">
            <strong>Fechas Oficiales</strong>
            <span>{html.escape(info['date'])}</span>
          </div>
          <div class="eisi-meta-card">
            <strong>Modalidad</strong>
            <span>{html.escape(info['modality'])}</span>
          </div>
          <div class="eisi-meta-card">
            <strong>Sede y Coordinación</strong>
            <span>{html.escape(info['venue'])}</span>
          </div>
          <div class="eisi-meta-card">
            <strong>Alianza Académica</strong>
            <span>{html.escape(info['alliance'])}</span>
          </div>
        </div>
      </div>

      <div class="eisi-poster-showcase">
        <img src="{html.escape(info['poster'])}" alt="{html.escape(page['title'])}">
        <div class="eisi-poster-caption">
          <span>Afiche / Imagen oficial · {html.escape(clean_display_title(page['title']))}</span>
          <a href="{html.escape(info['poster'])}" target="_blank" rel="noreferrer" style="color:var(--mint-light);text-decoration:underline;">Ver tamaño completo →</a>
        </div>
      </div>
    </div>
  </section>

  <section class="section" style="background:var(--surface);">
    <div class="shell">
      <div class="section-header">
        <h2 class="section-title">Modalidades.</h2>
        <p class="section-desc">Tres roles abiertos para semilleristas de pregrado y posgrado, docentes investigadores, evaluadores y comunidad académica.</p>
      </div>
      <div class="roles-grid-3">
        <article class="role-box">
          <h3>Ponentes y Autores</h3>
          <p>Presentación de proyectos de investigación en curso o terminados, estudios de caso e iniciativas de emprendimiento ante pares evaluadores nacionales e internacionales.</p>
        </article>
        <article class="role-box">
          <h3>Expertos y Evaluadores</h3>
          <p>Dirección de conferencias magistrales, talleres prácticos y comités científicos en las mesas temáticas para retroalimentar el trabajo de los semilleros.</p>
        </article>
        <article class="role-box">
          <h3>Asistentes y Aliados</h3>
          <p>Participación activa en las sesiones plenarias, paneles interinstitucionales, inmersiones académicas Colombia–Brasil y espacios de networking.</p>
        </article>
      </div>
    </div>
  </section>

  <section class="shell section">
    <div class="section-header">
      <h2 class="section-title">Mesas temáticas.</h2>
      <p class="section-desc">Ejes de investigación y líneas de conocimiento habilitadas para la postulación de ponencias en esta edición.</p>
    </div>
    <div class="mesas-grid">
      {''.join(mesas_cards)}
    </div>
  </section>

  {speakers_block}

  {subpages_cards}

  <div class="shell" style="padding-bottom:64px;">
    {gallery_html}
    {render_allies_strip(ally_logos, "../")}
  </div>
</main>
"""


def build_lineas_hub_content() -> str:
    """Contenido editorial estructurado para el hub de las 4 Líneas PREXIA."""
    return """
    <p>
      PREXIA articula la teoría de la ingeniería con la práctica organizacional a través de <strong>cuatro líneas de acción</strong> integradas por estudiantes de Ingeniería Industrial, Ingeniería Administrativa y carreras afines de la Facultad de Minas (UNAL Sede Medellín).
    </p>
    <div class="grid-cards" style="margin: 28px 0 36px;">
      <article class="card span-6">
        <div>
          <div class="card-cover"><img src="../images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-consultor-c3-ada__04__cff182fe819d.jpg" alt="Prexia Consultoría" loading="lazy"></div>
          <strong class="card-title" style="display:block;"><a href="unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-consultor-c3-ada.html">Prexia Consultoría</a></strong>
          <div class="card-meta-tag">Apoyo a la Productividad de MiPymes</div>
          <p class="card-excerpt">Diagnóstico e intervención empresarial en Finanzas, Mercadeo, Operaciones y Talento Humano bajo convenios con CFA, Fábricas de Productividad y Laboratorios UNAL. Evaluada mediante el Sistema de Puntos Prexia (PP).</p>
        </div>
        <a class="btn-card" href="unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-consultor-c3-ada.html">Explorar línea de Consultoría →</a>
      </article>
      <article class="card span-6">
        <div>
          <div class="card-cover"><img src="../images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__03__0bb63af26d05.jpg" alt="Prexia Investiga" loading="lazy"></div>
          <strong class="card-title" style="display:block;"><a href="unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga.html">Prexia Investiga</a></strong>
          <div class="card-meta-tag">Formación Investigativa y Divulgación Científica</div>
          <p class="card-excerpt">Desarrollo de proyectos propios, vínculo docente-estudiante con grupos de investigación de la Facultad de Minas y organización anual del Encuentro Internacional de Semilleros EISI.</p>
        </div>
        <a class="btn-card" href="unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga.html">Explorar línea de Investigación →</a>
      </article>
      <article class="card span-6">
        <div>
          <div class="card-cover"><img src="../images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-emprende__02__c3ff7b88ef35.jpg" alt="Prexia Emprende" loading="lazy"></div>
          <strong class="card-title" style="display:block;"><a href="unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-emprende.html">Prexia Emprende</a></strong>
          <div class="card-meta-tag">Gestión del Emprendimiento e Incubación</div>
          <p class="card-excerpt">Estructuración de planes de negocio mediante células de trabajo acompañadas por docentes y gestión del Observatorio de Emprendimiento del ecosistema local.</p>
        </div>
        <a class="btn-card" href="unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-emprende.html">Explorar línea de Emprendimiento →</a>
      </article>
      <article class="card span-6">
        <div>
          <div class="card-cover"><img src="../images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-comunica__02__ef47c35ea038.jpg" alt="Prexia Comunica" loading="lazy"></div>
          <strong class="card-title" style="display:block;"><a href="unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-comunica.html">Prexia Comunica</a></strong>
          <div class="card-meta-tag">Divulgación, Visitas Técnicas y Eventos</div>
          <p class="card-excerpt">Gestión de canales de comunicación estratégica, visitas empresariales a plantas industriales (como Eurocerámica), foros académicos, capacitaciones e integraciones.</p>
        </div>
        <a class="btn-card" href="unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-comunica.html">Explorar línea de Comunicaciones →</a>
      </article>
    </div>
    """


def build_creditos_2025_content() -> str:
    """Renderiza el directorio estructurado del Equipo PREXIA y Comité Académico Internacional 2025."""
    return """
    <p>
      El VI Encuentro Internacional de Semilleros de Investigación (VI EISI 2025) es posible gracias al trabajo articulado de la dirección docente, la coordinación estudiantil del Semillero PREXIA, el Comité Académico Internacional (Colombia–Brasil) y las redes de semilleros aliadas.
    </p>
    <h2 class="editorial-subhead">Dirección y Equipo Coordinador PREXIA</h2>
    <div class="team-grid">
      <article class="team-card">
        <strong>Docente José Ignacio Maya Guerra</strong>
        <span class="team-role">Director y Fundador del Semillero PREXIA</span>
        <p>Departamento de Ingeniería de la Organización · Facultad de Minas, UNAL Sede Medellín.</p>
      </article>
      <article class="team-card">
        <strong>Héctor Daniel Figueroa</strong>
        <span class="team-role">Coordinador General PREXIA</span>
        <p>Estudiante de Ingeniería Administrativa · Facultad de Minas, UNAL Sede Medellín.</p>
      </article>
      <article class="team-card">
        <strong>Alejandra Jiménez Antequera</strong>
        <span class="team-role">Integrante · Línea Prexia Investiga</span>
        <p>Coordinación logística y académica del Encuentro Internacional de Semilleros.</p>
      </article>
      <article class="team-card">
        <strong>Cristhian Castaño García</strong>
        <span class="team-role">Integrante · Comité Organizador</span>
        <p>Estudiante de Ingeniería Industrial · Facultad de Minas, UNAL Sede Medellín.</p>
      </article>
      <article class="team-card">
        <strong>Andrea Henao Arroyave</strong>
        <span class="team-role">Integrante · Comité Organizador</span>
        <p>Semillero PREXIA · Facultad de Minas, UNAL Sede Medellín.</p>
      </article>
      <article class="team-card">
        <strong>María Alejandra Zuleta &amp; Jenny Alejandra Upegui</strong>
        <span class="team-role">Integrantes · Comité Organizador</span>
        <p>Gestión de comunicaciones, relacionamiento y soporte a ponentes.</p>
      </article>
    </div>

    <h2 class="editorial-subhead">Dirección Internacional &amp; Comité Científico</h2>
    <div class="team-grid">
      <article class="team-card">
        <strong>Docente Katia Alexandre Maya</strong>
        <span class="team-role">Directora y Fundadora · Instituto A Nau Ciranda Sinparedes</span>
        <p>Articulación binacional ANCSP Brasil–Colômbia y coorganización EICCIE 2025.</p>
      </article>
      <article class="team-card">
        <strong>Dr. Ernesto Augusto Garbe</strong>
        <span class="team-role">Jefe del Departamento de Tecnología Industrial</span>
        <p>Universidade do Estado de Santa Catarina (UDESC, Brasil).</p>
      </article>
      <article class="team-card">
        <strong>Dr. Adriano dos Reis Lucente</strong>
        <span class="team-role">Docente · Depto. de Economía, Administración y Educación</span>
        <p>Universidade Estadual Paulista (UNESP Jaboticabal, São Paulo, Brasil).</p>
      </article>
      <article class="team-card">
        <strong>Dra. Natalia Andrea Cano Londoño</strong>
        <span class="team-role">PhD en Recursos Hidráulicos · MSc Medio Ambiente</span>
        <p>Líneas: Desarrollo sostenible y Análisis de Ciclo de Vida · UNAL Medellín.</p>
      </article>
      <article class="team-card">
        <strong>Dr. Daimer Higuita López</strong>
        <span class="team-role">Director Área Curricular Ing. Administrativa e Industrial</span>
        <p>Facultad de Minas · Universidad Nacional de Colombia, Sede Medellín.</p>
      </article>
      <article class="team-card">
        <strong>Docente Paola Andrea Ortiz &amp; Dra. Natalia Marulanda Grisales</strong>
        <span class="team-role">Comité Evaluador · UNAL &amp; Uniminuto</span>
        <p>Responsabilidad Social Empresarial, Gestión del Conocimiento, Logística e Innovación.</p>
      </article>
    </div>

    <h2 class="editorial-subhead">Grupos Estudiantiles y Semilleros Invitados</h2>
    <div class="team-grid">
      <article class="team-card">
        <strong>Grupo Estudiantil TEMS</strong>
        <span class="team-role">Universidad Nacional de Colombia · Sede Bogotá</span>
        <p>Habilidades blandas, promoción, entrenamiento de equipos y trabajo colaborativo.</p>
      </article>
      <article class="team-card">
        <strong>Semillero SIGEHAS</strong>
        <span class="team-role">Institución Universitaria Pascual Bravo · Medellín</span>
        <p>Semillero de Investigación en Gestión Empresarial y Habilidades Sociales.</p>
      </article>
    </div>
    """


def build_evaluation_page(root_prefix: str = "../") -> str:
    """Genera la página completa dedicada al Sistema de Evaluación Prexia (PDF)."""
    return f"""
<main class="shell page-layout">
  <article class="page-article">
    <h1 class="page-title">Sistema de Evaluación Prexia.</h1>
    <nav class="breadcrumb-trail" aria-label="Ruta de navegación">
      <span><a href="{root_prefix}index.html">Directorio</a></span>
      <span><a href="{root_prefix}../index.html">Inicio PREXIA</a></span>
      <span>Sistema de Evaluación (PP)</span>
    </nav>
    <div class="eval-hero-actions" style="margin: 20px 0 28px; display: flex; gap: 16px; flex-wrap: wrap;">
      <a href="#simulador" class="nav-cta">Simulador de Puntos Prexia</a>
      <a href="{root_prefix}index.html" style="display:inline-flex; align-items:center; padding:10px 20px; background:var(--surface); color:var(--ink); font-family:var(--font-display); font-size:14px; font-weight:700; border-radius:var(--radius);">Catálogo de 40 Páginas</a>
    </div>
    <p class="meta-original">
      Documento oficial de gestión del rendimiento y reconocimiento formativo en la Facultad de Minas, Universidad Nacional de Colombia.
    </p>

    <div class="page-copy">
      <h2>1. Propósito y Fundamentación Teórica</h2>
      <p>
        El sistema mide el aporte de cada integrante de la línea de Consultoría en <strong>Puntos Prexia (PP)</strong>, no en horas reloj, y ajusta la exigencia al nivel de avance real de su carrera de ingeniería.
      </p>
      <p>
        Medir únicamente horas presenciales en una facultad de ingeniería presenta distorsiones graves: castiga a quien cursa materias de alta exigencia (Cálculo, Álgebra Lineal, Física) cuyo tiempo libre es fragmentado, y premia la permanencia pasiva sin entregables concretos.
      </p>
      <ul>
        <li><strong>Teoría de las Características del Puesto (Hackman &amp; Oldham):</strong> Estructuración de tareas con significado claro, autonomía en la ejecución y retroalimentación directa por resultados.</li>
        <li><strong>Motivación Intrínseca (Daniel Pink):</strong> Tres palancas centrales: <em>Autonomía</em> (gestión de tiempos acordados), <em>Maestría</em> (crecimiento de rol formativo) y <em>Propósito</em> (impacto directo en organizaciones reales).</li>
      </ul>

      <h2>2. Los Cuatro Niveles de Avance de Carrera</h2>
      <p>
        En planes curriculares de diez semestres (160 a 180 créditos), el perfil del estudiante evoluciona profundamente. La exigencia se clasifica en cuatro ciclos de formación:
      </p>

      <table class="prexia-table">
        <thead>
          <tr>
            <th>Nivel</th>
            <th>Avance (%)</th>
            <th>Semestres</th>
            <th>Rol Formativo</th>
            <th>Tipo de Aporte Esperado</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Nivel 1: Fundamentación</strong></td>
            <td>0% a 25%</td>
            <td>1 a 2</td>
            <td>Operativo</td>
            <td>Tareas operativas cortas, apoyo logístico a eventos, recopilación de cápsulas de conocimiento y difusión.</td>
          </tr>
          <tr>
            <td><strong>Nivel 2: Transición</strong></td>
            <td>26% a 50%</td>
            <td>3 a 5</td>
            <td>Gestor</td>
            <td>Liderazgo en mesas temáticas, marketing digital, eventos de bienestar, comunidad y simulaciones de ventas.</td>
          </tr>
          <tr>
            <td><strong>Nivel 3: Profesionalización</strong></td>
            <td>51% a 75%</td>
            <td>6 a 8</td>
            <td>Consultor Junior</td>
            <td>Diagnóstico empresarial a MiPymes, diseño curricular de casos de simulación, analítica y meta del 80% de productividad de línea.</td>
          </tr>
          <tr>
            <td><strong>Nivel 4: Cierre y Proyección</strong></td>
            <td>&gt; 75%</td>
            <td>9 a 10</td>
            <td>Líder</td>
            <td>Gerencia de proyectos, mentoría a pares, enlace con expertos externos y acuerdos de retribución sobre impacto económico.</td>
          </tr>
        </tbody>
      </table>

      <h2>3. Curva Semanal Progresiva de Metas</h2>
      <p>
        Al inicio de cada semestre, cada estudiante suscribe un pacto horario voluntario (POA). La meta base semanal de cada integrante nace de esa concertación: <strong>1 Hora Pactada = 100 Puntos Prexia (PP) base por semana</strong> (ejemplo: 4 horas semanales pactadas = 400 PP base).
      </p>
      <p>
        La meta sube 1% de la base cada semana lectiva hasta alcanzar el <strong>110% en la semana diez</strong> (cierre de semestre). Para cubrir ese incremento sin trabajar más horas reloj, los integrantes activan multiplicadores de calidad.
      </p>

      <h2>4. Matriz Oficial de Factores Multiplicadores</h2>
      <table class="prexia-table">
        <thead>
          <tr>
            <th>Nivel</th>
            <th>Multiplicador</th>
            <th>Bono</th>
            <th>Criterio y Condición de Acreditación</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Nivel 1</strong></td>
            <td>Excelencia en Contenido</td>
            <td>+3%</td>
            <td>Calendario de publicaciones cumplido al 100% sin retrasos ni objeciones de fondo.</td>
          </tr>
          <tr>
            <td><strong>Nivel 1</strong></td>
            <td>Generación de Valor</td>
            <td>+3%</td>
            <td>Cada cápsula de conocimiento adicional documentada, editada y publicada.</td>
          </tr>
          <tr>
            <td><strong>Nivel 1</strong></td>
            <td>Cultura Consultor</td>
            <td>+2%</td>
            <td>Participación en el diseño de material pedagógico sobre la cultura PREXIA.</td>
          </tr>
          <tr>
            <td><strong>Nivel 2</strong></td>
            <td>Tracción Web y Redes</td>
            <td>+3%</td>
            <td>Crecimiento medido de audiencia en canales del semillero superior al 10%.</td>
          </tr>
          <tr>
            <td><strong>Nivel 2</strong></td>
            <td>Poder de Convocatoria</td>
            <td>+3%</td>
            <td>Asistencia y participación efectiva del 80% o más de integrantes en eventos.</td>
          </tr>
          <tr>
            <td><strong>Nivel 2</strong></td>
            <td>Celebración y Bienestar</td>
            <td>+2%</td>
            <td>100% de fechas conmemorativas celebradas y reconocimientos individuales otorgados.</td>
          </tr>
          <tr>
            <td><strong>Nivel 3</strong></td>
            <td>Efectividad Analítica</td>
            <td>+5%</td>
            <td>Informe final de consultoría entregado con calidad profesional, superando expectativas del cliente.</td>
          </tr>
          <tr>
            <td><strong>Nivel 3</strong></td>
            <td>Diseño Curricular</td>
            <td>+3%</td>
            <td>Estructuración de casos de simulación con datos e indicadores reales de la industria.</td>
          </tr>
          <tr>
            <td><strong>Nivel 3</strong></td>
            <td>Productividad Extra</td>
            <td>+2%</td>
            <td>Ejecución de tareas anticipadas a la planificación o vinculación de nuevos proyectos.</td>
          </tr>
          <tr>
            <td><strong>Nivel 4</strong></td>
            <td>Impacto Económico</td>
            <td>+10%</td>
            <td>Cierre de acuerdos de retribución sobre utilidades generadas en las empresas asesoradas.</td>
          </tr>
          <tr>
            <td><strong>Nivel 4</strong></td>
            <td>Relaciones Públicas</td>
            <td>+3%</td>
            <td>Vinculación efectiva de profesores o conferencistas internacionales invitados.</td>
          </tr>
          <tr>
            <td><strong>Nivel 4</strong></td>
            <td>Finalización de Curso</td>
            <td>+2%</td>
            <td>Culminación satisfactoria del curso de formación de consultores con certificación superior al 80%.</td>
          </tr>
        </tbody>
      </table>

      <section id="simulador" style="margin-top: 40px; padding: 28px; background: var(--surface); border-radius: var(--radius);">
        <h2 style="margin-top: 0;">Simulador Interactivo de Puntos Prexia (PP)</h2>
        <p style="font-size: 14px; color: var(--muted); margin-bottom: 20px;">Calcula la meta y bonificaciones del POA según las horas pactadas y el avance de carrera.</p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 20px;">
          <div>
            <label for="sim-nivel" style="display:block; font-family:var(--font-display); font-size:14px; font-weight:700; margin-bottom:6px;">Nivel formativo</label>
            <select id="sim-nivel" style="width:100%; padding:10px 12px; font-family:inherit; font-size:14px; background:var(--bg); border:none; border-radius:var(--radius);">
              <option value="1">Nivel 1: Fundamentación (0-25%)</option>
              <option value="2">Nivel 2: Transición (26-50%)</option>
              <option value="3" selected>Nivel 3: Profesionalización (51-75%)</option>
              <option value="4">Nivel 4: Cierre y Proyección (&gt;75%)</option>
            </select>
          </div>
          <div>
            <label for="sim-horas" style="display:block; font-family:var(--font-display); font-size:14px; font-weight:700; margin-bottom:6px;">Horas semanales</label>
            <input type="number" id="sim-horas" value="4" min="1" max="20" style="width:100%; padding:10px 12px; font-family:inherit; font-size:14px; background:var(--bg); border:none; border-radius:var(--radius);">
          </div>
          <div>
            <label for="sim-semana" style="display:block; font-family:var(--font-display); font-size:14px; font-weight:700; margin-bottom:6px;">Semana (1 a 10)</label>
            <input type="number" id="sim-semana" value="10" min="1" max="10" style="width:100%; padding:10px 12px; font-family:inherit; font-size:14px; background:var(--bg); border:none; border-radius:var(--radius);">
          </div>
        </div>

        <div style="margin-bottom: 20px;">
          <div style="font-family:var(--font-display); font-size:14px; font-weight:700; margin-bottom:8px;">Multiplicadores activados</div>
          <div id="sim-mult-container" style="display: flex; flex-direction: column; gap: 8px;"></div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; background: var(--bg); padding: 18px; border-radius: var(--radius);" data-ui>
          <div>
            <strong id="res-base" style="font-family:var(--font-display); font-size:22px; color:var(--ink); display:block;">400 PP</strong>
            <span style="font-size:14px; color:var(--muted);">Meta base semanal</span>
          </div>
          <div>
            <strong id="res-meta-semana" style="font-family:var(--font-display); font-size:22px; color:var(--ink); display:block;">440 PP (110%)</strong>
            <span style="font-size:14px; color:var(--muted);">Exigencia semanal</span>
          </div>
          <div>
            <strong id="res-bono" style="font-family:var(--font-display); font-size:22px; color:var(--mint-dark); display:block;">+0 PP</strong>
            <span style="font-size:14px; color:var(--muted);">Bonificación POA</span>
          </div>
          <div>
            <strong id="res-total" style="font-family:var(--font-display); font-size:22px; color:var(--ink); display:block;">400 PP</strong>
            <span style="font-size:14px; color:var(--muted);">Puntos finales</span>
          </div>
        </div>
      </section>
    </div>
  </article>

  <aside class="sidebar">
    <div class="sidebar-box">
      <div class="sidebar-heading">HERRAMIENTAS</div>
      <div class="sidebar-nav-list">
        <a class="sidebar-nav-item" href="#simulador">Simulador Interactivo PP</a>
        <a class="sidebar-nav-item" href="{root_prefix}index.html">Catálogo de Páginas Migradas</a>
        <a class="sidebar-nav-item" href="{root_prefix}pages/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-consultor-c3-ada.html">Línea de Consultoría</a>
      </div>
    </div>
    <div class="sidebar-box">
      <div class="sidebar-heading">DATOS DEL DOCUMENTO</div>
      <p style="font-size:14px;color:var(--muted);line-height:1.5;">
        Fuente: Sistema de Evaluación Prexia Puntos y Multiplicadores.PDF<br>
        Facultad de Minas · UNAL Medellín
      </p>
    </div>
  </aside>
</main>

<script>
  (function() {{
    const multByLevel = {{
      1: [
        {{ label: "Excelencia en Contenido (+3%)", pct: 3 }},
        {{ label: "Generación de Valor (+3%)", pct: 3 }},
        {{ label: "Cultura Consultor (+2%)", pct: 2 }}
      ],
      2: [
        {{ label: "Tracción Web y Redes (+3%)", pct: 3 }},
        {{ label: "Poder de Convocatoria (+3%)", pct: 3 }},
        {{ label: "Celebración y Bienestar (+2%)", pct: 2 }}
      ],
      3: [
        {{ label: "Efectividad Analítica (+5%)", pct: 5 }},
        {{ label: "Diseño Curricular (+3%)", pct: 3 }},
        {{ label: "Productividad Extra (+2%)", pct: 2 }}
      ],
      4: [
        {{ label: "Impacto Económico (+10%)", pct: 10 }},
        {{ label: "Relaciones Públicas (+3%)", pct: 3 }},
        {{ label: "Finalización de Curso (+2%)", pct: 2 }}
      ]
    }};

    const nivelSelect = document.getElementById('sim-nivel');
    const horasInput = document.getElementById('sim-horas');
    const semanaInput = document.getElementById('sim-semana');
    const multContainer = document.getElementById('sim-mult-container');
    const resBase = document.getElementById('res-base');
    const resMetaSemana = document.getElementById('res-meta-semana');
    const resBono = document.getElementById('res-bono');
    const resTotal = document.getElementById('res-total');

    function renderCheckboxes() {{
      const level = nivelSelect.value;
      const mults = multByLevel[level] || [];
      multContainer.innerHTML = mults.map(m => `
        <label style="display:flex; align-items:center; gap:8px; font-size:14px; cursor:pointer;">
          <input type="checkbox" class="sim-check" data-pct="${{m.pct}}" style="accent-color:var(--ink);" checked>
          <span>${{m.label}}</span>
        </label>
      `).join('');
      multContainer.querySelectorAll('.sim-check').forEach(chk => chk.addEventListener('change', recalc));
      recalc();
    }}

    function recalc() {{
      const horas = Math.max(1, parseInt(horasInput.value || 4, 10));
      const semana = Math.min(10, Math.max(1, parseInt(semanaInput.value || 10, 10)));
      const base = horas * 100;
      const pctSemana = 100 + semana;
      const metaSemana = Math.round(base * (pctSemana / 100));

      let bonusPct = 0;
      multContainer.querySelectorAll('.sim-check:checked').forEach(chk => {{
        bonusPct += parseFloat(chk.getAttribute('data-pct') || 0);
      }});

      const bonusPP = Math.round(base * (bonusPct / 100));
      const finalPP = base + bonusPP;

      resBase.textContent = base + ' PP';
      resMetaSemana.textContent = `${{metaSemana}} PP (${{pctSemana}}%)`;
      resBono.textContent = `+${{bonusPP}} PP (+${{bonusPct}}%)`;
      resTotal.textContent = `${{finalPP}} PP`;
      resTotal.style.color = finalPP >= metaSemana ? 'var(--mint-dark)' : 'var(--ink)';
    }}

    nivelSelect.addEventListener('change', renderCheckboxes);
    horasInput.addEventListener('input', recalc);
    semanaInput.addEventListener('input', recalc);
    renderCheckboxes();
  }})();
</script>
"""


def build_site() -> None:
    manifest = load_manifest()
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    (OUTPUT_DIR / "pages").mkdir(parents=True)
    (OUTPUT_DIR / "images").mkdir(parents=True)
    (OUTPUT_DIR / "assets").mkdir(parents=True)
    shutil.copytree(SOURCE_DIR / "images", OUTPUT_DIR / "images", dirs_exist_ok=True)
    if (PROJECT_ROOT / "assets").exists():
        shutil.copytree(PROJECT_ROOT / "assets", OUTPUT_DIR / "assets", dirs_exist_ok=True)
    shutil.copy2(SOURCE_DIR / "manifest.json", OUTPUT_DIR / "manifest.json")
    (OUTPUT_DIR / "assets" / "styles.css").write_text(CSS.strip() + "\n", encoding="utf-8")

    pages = manifest["pages"]
    page_by_url = {page["url"]: page for page in pages}
    page_by_slug = {page["slug"]: page for page in pages}
    children_by_url: dict[str, list[dict]] = defaultdict(list)
    group_buckets: dict[str, list[dict]] = defaultdict(list)

    parsed_content: dict[str, tuple[list[str], list[str]]] = {}
    classified_images: dict[str, tuple[list[str], list[tuple[str, str]]]] = {}
    for page in pages:
        markdown_path = SOURCE_DIR / page["markdown"]
        lines, images = parse_markdown(markdown_path)
        parsed_content[page["slug"]] = (normalize_text_lines(lines), images)
        classified_images[page["slug"]] = classify_page_images(images)

    for page in pages:
        path_parts = [part for part in urlparse(page["url"]).path.split("/") if part]
        top_group = path_parts[3] if len(path_parts) > 3 else "home"
        group_buckets[top_group].append(page)
        for parent_url, parent in page_by_url.items():
            if parent_url == page["url"]:
                continue
            if page["url"].startswith(parent_url + "/"):
                children_by_url[parent_url].append(page)

    for parent_url, items in children_by_url.items():
        children_by_url[parent_url] = sorted(items, key=lambda item: item["url"].count("/"))

    def nearest_parent_url(url: str) -> str | None:
        candidates = []
        for candidate in page_by_url:
            if candidate == url:
                continue
            if url.startswith(candidate + "/"):
                candidates.append(candidate)
        if not candidates:
            return None
        return max(candidates, key=len)

    def layout(title: str, body: str, root_prefix: str = "") -> str:
        isotipo_header = """<svg width="28" height="28" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M30 8 C18 8 8 18 8 30 C8 42 18 52 30 52" stroke="#0f652e" stroke-width="4" stroke-linecap="round"/><path d="M30 8 C42 8 52 18 52 30 C52 42 42 52 30 52" stroke="#1f1a3a" stroke-width="4" stroke-linecap="round"/><path d="M16 16 C20 28 28 36 44 44" stroke="#0f652e" stroke-width="2.8" stroke-linecap="round"/><path d="M44 16 C40 28 32 36 16 44" stroke="#1f1a3a" stroke-width="2.8" stroke-linecap="round"/></svg>"""
        isotipo_footer = """<svg width="26" height="26" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M30 8 C18 8 8 18 8 30 C8 42 18 52 30 52" stroke="#84fbaa" stroke-width="4" stroke-linecap="round"/><path d="M30 8 C42 8 52 18 52 30 C52 42 42 52 30 52" stroke="#60eaf0" stroke-width="4" stroke-linecap="round"/><path d="M16 16 C20 28 28 36 44 44" stroke="#84fbaa" stroke-width="2.8" stroke-linecap="round"/><path d="M44 16 C40 28 32 36 16 44" stroke="#60eaf0" stroke-width="2.8" stroke-linecap="round"/></svg>"""
        nav = f"""
<header class="topbar">
  <div class="shell topbar-inner" role="navigation" aria-label="Navegación principal">
    <a class="brand" href="{root_prefix}../index.html">
      {isotipo_header}
      <span>PRE<em>XIA</em></span>
      <span class="brand-sub">Facultad de Minas · UNAL</span>
    </a>
    <nav class="nav-links">
      <a href="{root_prefix}../index.html">Portada Principal</a>
      <a href="{root_prefix}pages/unal-edu-co__prexiaforum__home__vi-eisi-2025.html">VI EISI 2025</a>
      <a href="{root_prefix}pages/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia.html">Las 4 Líneas</a>
      <a href="{root_prefix}pages/sistema-evaluacion-prexia.html">Sistema PP</a>
      <a href="{root_prefix}index.html">Archivo (40)</a>
    </nav>
    <a href="{root_prefix}../index.html#contacto" class="nav-cta">Contactar</a>
  </div>
</header>
"""
        footer = f"""
<footer class="site-footer">
  <div class="shell footer-inner">
    <div class="footer-info">
      <div class="footer-brand-row">
        {isotipo_footer}
        <span>PRE<em>XIA</em> · UNAL MINAS</span>
      </div>
      <p>Semillero de Investigación, Consultoría y Emprendimiento adscrito al Área Curricular de Ingeniería Industrial e Ingeniería Administrativa de la Facultad de Minas, Universidad Nacional de Colombia Sede Medellín.</p>
    </div>
    <div class="footer-links-row">
      <a href="{root_prefix}../index.html">Portada Principal</a>
      <a href="{root_prefix}pages/unal-edu-co__prexiaforum__home__vi-eisi-2025.html">VI EISI 2025</a>
      <a href="{root_prefix}pages/sistema-evaluacion-prexia.html">Evaluación PP</a>
      <a href="{root_prefix}index.html">Directorio (40)</a>
      <a href="{root_prefix}manifest.json">Manifest JSON</a>
      <a href="https://sites.google.com/unal.edu.co/prexiaforum" target="_blank" rel="noreferrer">Google Sites Original</a>
    </div>
  </div>
</footer>
"""
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · PREXIA UNAL</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@500;700;800&family=Source+Serif+4:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{root_prefix}assets/styles.css">
  <script>document.documentElement.classList.add('js')</script>
</head>
<body>
{nav}
{body}
{footer}
<script>
  requestAnimationFrame(() => {{
    document.documentElement.classList.add('in');
  }});
  if (typeof IntersectionObserver !== 'undefined') {{
    const observer = new IntersectionObserver((entries) => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }}
      }});
    }}, {{ threshold: 0.08 }});
    document.querySelectorAll('.section, .mesa-card, .role-box, .card, .gallery-thumb, .allies-strip-section, .sidebar-box, .speaker-card, .team-card').forEach(el => {{
      el.classList.add('reveal-item');
      observer.observe(el);
    }});
  }}
</script>
</body>
</html>
"""

    # Build the dedicated evaluation page
    eval_page_html = layout("Sistema de Evaluación Prexia (Puntos y Multiplicadores)", build_evaluation_page("../"), root_prefix="../")
    (OUTPUT_DIR / "pages" / "sistema-evaluacion-prexia.html").write_text(eval_page_html, encoding="utf-8")

    # Curated fallback covers for collection cards so no collection uses an icon
    COLLECTION_COVER_FALLBACKS = {
        "unal-edu-co__prexiaforum__home": "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-consultor-c3-ada__05__250ebb187d42.jpg",
        "unal-edu-co__prexiaforum__home__l-c3-adneas-prexia": "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-consultor-c3-ada__04__cff182fe819d.jpg",
    }

    # Build catalog home page (site/index.html)
    home_page = page_by_slug["unal-edu-co__prexiaforum__home"]
    home_lines, _ = parsed_content[home_page["slug"]]
    lead = " ".join(home_lines[:4]).strip()
    collection_cards = []
    for group, items in sorted(group_buckets.items(), key=lambda entry: entry[0]):
        label = "Inicio" if group == "home" else title_case_from_segment(group)
        anchor_page = sorted(items, key=lambda item: item["url"].count("/"))[0]
        c_imgs, _ = classified_images[anchor_page["slug"]]
        cover_src = COLLECTION_COVER_FALLBACKS.get(anchor_page["slug"], c_imgs[0] if c_imgs else "assets/photos/vi-eisi-2025.jpg")
        if anchor_page["slug"] in EISI_STRUCTURED_DATA:
            cover_src = EISI_STRUCTURED_DATA[anchor_page["slug"]]["poster"].lstrip("./")
        excerpt_text = (
            "Explora las 4 líneas de acción del semillero: Consultoría a MiPymes, Investigación, Emprendimiento y Comunicaciones."
            if anchor_page["slug"] == "unal-edu-co__prexiaforum__home__l-c3-adneas-prexia"
            else (parsed_content[anchor_page["slug"]][0][0][:170] if parsed_content[anchor_page["slug"]][0] else "Contenido oficial migrado desde Google Sites.")
        )
        cover = f'<div class="card-cover"><img src="{html.escape(cover_src)}" alt="{html.escape(anchor_page["title"])}" loading="lazy"></div>'
        collection_cards.append(
            f"""
<article class="card span-4">
  <div>
    {cover}
    <h3 class="card-title"><a href="{html.escape(page_href(anchor_page["slug"]))}">{html.escape(clean_display_title(anchor_page["title"]))}</a></h3>
    <div class="card-meta-tag">{len(items)} páginas · {html.escape(label)}</div>
    <p class="card-excerpt">{html.escape(excerpt_text)}</p>
  </div>
  <a class="btn-card" href="{html.escape(page_href(anchor_page["slug"]))}">Consultar colección →</a>
</article>
"""
        )

    page_cards = []
    for page in sorted(pages, key=lambda item: (item["url"].count("/"), item["title"])):
        lines, _ = parsed_content[page["slug"]]
        c_imgs, _ = classified_images[page["slug"]]
        excerpt = " ".join(lines[:3]) or "Sección oficial migrada del archivo histórico de PREXIA UNAL."
        if page["slug"] in {"unal-edu-co__prexiaforum__home__l-c3-adneas-prexia", "unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__es"}:
            excerpt = "Estructura organizacional de PREXIA en cuatro líneas estratégicas: Consultoría, Investigación, Emprendimiento y Comunicaciones."
        cover_src = c_imgs[0] if c_imgs else ""
        if page["slug"] in EISI_STRUCTURED_DATA:
            cover_src = EISI_STRUCTURED_DATA[page["slug"]]["poster"].lstrip("./")
        elif page["slug"] in COLLECTION_COVER_FALLBACKS:
            cover_src = COLLECTION_COVER_FALLBACKS[page["slug"]]
        cover = f'<div class="card-cover"><img src="{html.escape(cover_src)}" alt="{html.escape(page["title"])}" loading="lazy"></div>' if cover_src else ""
        path_parts = [part for part in urlparse(page["url"]).path.split("/") if part]
        top_group = path_parts[3] if len(path_parts) > 3 else "home"
        label = " / ".join(title_case_from_segment(part) for part in path_parts[3:5]) or "Inicio"
        page_cards.append(
            f"""
<article class="card span-6 dir-card" data-group="{html.escape(top_group)}" data-search="{html.escape((page['title'] + ' ' + label + ' ' + excerpt).lower())}">
  <div>
    {cover}
    <h3 class="card-title"><a href="{html.escape(page_href(page["slug"]))}">{html.escape(clean_display_title(page["title"]))}</a></h3>
    <div class="card-meta-tag">{html.escape(label)}</div>
    <p class="card-excerpt">{html.escape(excerpt[:220])}</p>
  </div>
  <a class="btn-card" href="{html.escape(page_href(page["slug"]))}">Abrir página completa →</a>
</article>
"""
        )

    filter_buttons = ['<button type="button" class="filter-btn active" data-filter="all">Todas (40)</button>']
    for group, items in sorted(group_buckets.items(), key=lambda entry: entry[0]):
        label = "Inicio" if group == "home" else title_case_from_segment(group)
        filter_buttons.append(
            f'<button type="button" class="filter-btn" data-filter="{html.escape(group)}">{html.escape(label)} ({len(items)})</button>'
        )

    home_body = f"""
<main class="shell">
  <section class="archive-hero">
    <div class="archive-hero-grid">
      <div>
        <h1 class="archive-hero-title">Archivo PREXIA.</h1>
        <p class="archive-lead">{html.escape(lead)}</p>
        <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:24px;">
          <a href="pages/sistema-evaluacion-prexia.html" class="nav-cta">Sistema de Evaluación (PP)</a>
          <a href="../index.html" style="display:inline-flex;align-items:center;padding:10px 20px;background:var(--surface);color:var(--ink);font-family:var(--font-display);font-size:14px;font-weight:700;border-radius:var(--radius);">Volver a Portada Principal</a>
        </div>
      </div>
      <div class="archive-stats-box">
        <div class="stat-unit">
          <strong>{manifest['page_count']}</strong>
          <span>Páginas migradas</span>
        </div>
        <div class="stat-unit">
          <strong>{manifest['image_count']}</strong>
          <span>Recursos gráficos</span>
        </div>
        <div class="stat-unit">
          <strong>{len(group_buckets)}</strong>
          <span>Colecciones</span>
        </div>
        <div class="stat-unit">
          <strong>6</strong>
          <span>Ediciones EISI</span>
        </div>
      </div>
    </div>
  </section>

  <section class="section" id="colecciones">
    <div class="section-header">
      <h2 class="section-title">Colecciones principales.</h2>
      <p class="section-desc">Secciones estructurales que organizan las cuatro líneas de trabajo y las seis ediciones de los Encuentros Internacionales EISI (2020–2025).</p>
    </div>
    <div class="grid-cards">
      {''.join(collection_cards)}
    </div>
  </section>

  <section class="section" id="paginas">
    <div class="section-header">
      <h2 class="section-title">Directorio de 40 páginas.</h2>
      <p class="section-desc">Filtra por colección o busca por palabra clave entre todas las páginas y subpáginas migradas desde Google Sites.</p>
    </div>
    <div class="filter-bar">
      <div class="filter-tabs" id="dir-tabs">
        {''.join(filter_buttons)}
      </div>
      <input type="search" id="dir-search" class="filter-search" placeholder="Buscar página, mesa o ponente..." aria-label="Buscar en el directorio">
    </div>
    <div class="grid-cards" id="dir-grid">
      {''.join(page_cards)}
    </div>
  </section>
</main>
<script>
  (function() {{
    const tabs = document.querySelectorAll('#dir-tabs .filter-btn');
    const searchInput = document.getElementById('dir-search');
    const cards = document.querySelectorAll('.dir-card');
    let activeGroup = 'all';

    function applyFilter() {{
      const q = (searchInput.value || '').trim().toLowerCase();
      cards.forEach(card => {{
        const matchGroup = activeGroup === 'all' || card.getAttribute('data-group') === activeGroup;
        const matchQuery = !q || (card.getAttribute('data-search') || '').includes(q);
        card.style.display = (matchGroup && matchQuery) ? '' : 'none';
      }});
    }}

    tabs.forEach(btn => {{
      btn.addEventListener('click', () => {{
        tabs.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeGroup = btn.getAttribute('data-filter');
        applyFilter();
      }});
    }});

    if (searchInput) {{
      searchInput.addEventListener('input', applyFilter);
    }}
  }})();
</script>
"""
    (OUTPUT_DIR / "index.html").write_text(layout("Directorio Migrado (40 Páginas)", home_body), encoding="utf-8")

    # Build individual subpages
    for page in pages:
        slug = page["slug"]
        lines, raw_images = parsed_content[slug]
        content_images, ally_logos = classified_images[slug]
        direct_children = [
            child for child in children_by_url.get(page["url"], [])
            if nearest_parent_url(child["url"]) == page["url"]
        ]

        # Rich structured layout for the EISI event pages (2019-2025)
        if slug in EISI_STRUCTURED_DATA:
            eisi_body = build_eisi_event_page(page, direct_children, content_images, ally_logos)
            (OUTPUT_DIR / "pages" / page_output_name(slug)).write_text(
                layout(page["title"], eisi_body, root_prefix="../"),
                encoding="utf-8",
            )
            continue

        parent_url = nearest_parent_url(page["url"])
        parent = page_by_url[parent_url] if parent_url else None
        siblings = []
        if parent:
            for candidate in children_by_url.get(parent["url"], []):
                if nearest_parent_url(candidate["url"]) == parent["url"]:
                    siblings.append(candidate)
        else:
            siblings = [candidate for candidate in pages if nearest_parent_url(candidate["url"]) is None]

        breadcrumbs = ['<span><a href="../index.html">Directorio</a></span>']
        if parent:
            lineage = []
            current = parent
            while current:
                lineage.append(current)
                candidate_parent = nearest_parent_url(current["url"])
                current = page_by_url[candidate_parent] if candidate_parent else None
            for item in reversed(lineage):
                breadcrumbs.append(f'<span><a href="{html.escape(page_output_name(item["slug"]))}">{html.escape(clean_display_title(item["title"]))}</a></span>')
        breadcrumbs.append(f"<span>{html.escape(clean_display_title(page['title']))}</span>")

        # Specialized structured content for specific subpages
        custom_body_html = ""
        if slug in {"unal-edu-co__prexiaforum__home__l-c3-adneas-prexia", "unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__es"}:
            custom_body_html = build_lineas_hub_content()
        elif slug == "unal-edu-co__prexiaforum__home__vi-eisi-2025__cr-c3-a9ditos-2025":
            custom_body_html = build_creditos_2025_content()
        elif slug == "unal-edu-co__prexiaforum__home__i-encuentro-internacional-de-semilleros-2020__conferencistas":
            custom_body_html = (
                "<p>Conferencistas magistrales internacionales invitados a la edición fundacional del Encuentro Internacional de Semilleros de Investigación (I EISI 2020).</p>"
                + render_speakers_section(SPEAKERS_2020)
            )
        elif slug == "unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__evento-2019__galeria":
            custom_body_html = (
                "<p>Registro fotográfico oficial del Primer Encuentro Nacional de Semilleros de Investigación (28 y 29 de noviembre de 2019 · Campus Robledo, Facultad de Minas UNAL Sede Medellín).</p>"
            )
            content_images = [
                "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__07__899ec7e54f18.jpg",
                "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__02__87b31aedafe3.jpg",
                "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__03__0bb63af26d05.jpg",
                "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__04__89e65143a6a4.jpg",
                "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__05__65a65f68e794.jpg",
                "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__06__08ae494069e0.jpg",
                "images/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-investiga__08__312ee1b5bd7a.jpg",
            ]
        else:
            content_blocks = []
            # Si es una subpágina de Mesas Temáticas de alguna edición EISI, mostrar también las tarjetas estructuradas de las mesas
            if "mesas-tem-c3-a1ticas" in slug and parent and parent["slug"] in EISI_STRUCTURED_DATA:
                parent_info = EISI_STRUCTURED_DATA[parent["slug"]]
                mcards = []
                for mesa in parent_info["mesas"]:
                    topics_html = "".join(f"<li>{html.escape(t)}</li>" for t in mesa["topics"])
                    mcards.append(
                        f"""
                        <article class="mesa-card">
                          <strong class="mesa-title">{html.escape(mesa['title'])}</strong>
                          <div class="mesa-num">{html.escape(mesa['num'])}</div>
                          <ul class="mesa-topics">{topics_html}</ul>
                        </article>
                        """
                    )
                content_blocks.append(f'<div class="mesas-grid" style="margin-bottom:36px;">{"".join(mcards)}</div>')

            for line in lines:
                if line.upper().startswith("ORGANIZAN"):
                    continue
                if len(line) < 52 and not line.endswith(".") and not line.endswith(":"):
                    content_blocks.append(f'<h3 class="editorial-subhead">{html.escape(line)}</h3>')
                else:
                    content_blocks.append(f"<p>{html.escape(line)}</p>")

            if not content_blocks and parent:
                content_blocks.append(
                    f'<p>Consulta los recursos gráficos oficiales y la programación completa en la página principal de <a href="{html.escape(page_output_name(parent["slug"]))}" style="text-decoration:underline;font-weight:700;">{html.escape(clean_display_title(parent["title"]))}</a>.</p>'
                )
            custom_body_html = "".join(content_blocks)

        display_photos = ensure_min_photos(content_images, min_count=4)
        gallery_items = "".join(
            f'<a class="gallery-thumb" href="../{html.escape(image)}" target="_blank" rel="noreferrer"><img src="../{html.escape(image)}" alt="{html.escape(clean_display_title(page["title"]))}" loading="lazy"></a>'
            for image in display_photos
        )
        gallery = f"""
<section class="gallery-section">
  <h3 class="editorial-subhead">Afiches, fotografías y registro visual ({len(display_photos)})</h3>
  <div class="gallery-grid">{gallery_items}</div>
</section>
"""

        child_links = [
            f'<a class="sidebar-nav-item" href="{html.escape(page_output_name(child["slug"]))}">{html.escape(clean_display_title(child["title"]))}</a>'
            for child in direct_children
        ]

        sibling_links = []
        for sibling in siblings:
            active_class = " active" if sibling["slug"] == slug else ""
            sibling_links.append(
                f'<a class="sidebar-nav-item{active_class}" href="{html.escape(page_output_name(sibling["slug"]))}">{html.escape(clean_display_title(sibling["title"]))}</a>'
            )

        eisi_bar = ""
        if any(ed_slug in slug for _, _, ed_slug in EISI_EDITIONS_NAV):
            ed_pills = "".join(
                f'<a class="eisi-pill{" active" if ed_slug in slug else ""}" href="{html.escape(page_output_name(ed_slug))}">{html.escape(label)}</a>'
                for _, label, ed_slug in EISI_EDITIONS_NAV
            )
            eisi_bar = f"""
<nav class="eisi-subnav" aria-label="Ediciones Encuentros Internacionales EISI">
  <div class="shell eisi-subnav-inner">
    <div class="eisi-editions-pills">{ed_pills}</div>
  </div>
</nav>
"""

        short_h1 = clean_display_title(page["title"])
        if not short_h1.endswith("."):
            short_h1 = f"{short_h1}."

        page_body = f"""
{eisi_bar}
<main class="shell page-layout">
  <article class="page-article">
    <h1 class="page-title">{html.escape(short_h1)}</h1>
    <nav class="breadcrumb-trail" aria-label="Ruta de navegación">{''.join(breadcrumbs)}</nav>
    <p class="meta-original">Fuente oficial migrada: <a href="{html.escape(page['url'])}" target="_blank" rel="noreferrer">{html.escape(page['url'])}</a></p>
    <div class="page-copy">
      {custom_body_html}
    </div>
    {gallery}
    {render_allies_strip(ally_logos, "../")}
  </article>
  <aside class="sidebar">
    <div class="sidebar-box">
      <div class="sidebar-heading">SUBPÁGINAS DE ESTA SECCIÓN</div>
      <div class="sidebar-nav-list">{''.join(child_links) if child_links else '<span style="font-size:14px;color:var(--muted);">No hay subpáginas directas.</span>'}</div>
    </div>
    <div class="sidebar-box">
      <div class="sidebar-heading">PÁGINAS RELACIONADAS</div>
      <div class="sidebar-nav-list">{''.join(sibling_links) if sibling_links else '<span style="font-size:14px;color:var(--muted);">Sin páginas hermanas.</span>'}</div>
    </div>
    <div class="sidebar-box">
      <div class="sidebar-heading">EDICIONES EISI (2020–2025)</div>
      <div class="sidebar-nav-list">
        <a class="sidebar-nav-item" href="unal-edu-co__prexiaforum__home__vi-eisi-2025.html">VI EISI 2025</a>
        <a class="sidebar-nav-item" href="unal-edu-co__prexiaforum__home__v-encuentro-internacional-de-semilleros-2024.html">V Encuentro 2024</a>
        <a class="sidebar-nav-item" href="unal-edu-co__prexiaforum__home__iv-encuentro-internacional-de-semilleros-2023.html">IV Encuentro 2023</a>
        <a class="sidebar-nav-item" href="unal-edu-co__prexiaforum__home__iii-encuentro-internacional-de-semilleros-2022.html">III Encuentro 2022</a>
        <a class="sidebar-nav-item" href="unal-edu-co__prexiaforum__home__ii-encuentro-internacional-de-semilleros-2021.html">II Encuentro 2021</a>
        <a class="sidebar-nav-item" href="unal-edu-co__prexiaforum__home__i-encuentro-internacional-de-semilleros-2020.html">I Encuentro 2020</a>
      </div>
    </div>
  </aside>
</main>
"""
        (OUTPUT_DIR / "pages" / page_output_name(slug)).write_text(
            layout(page["title"], page_body, root_prefix="../"),
            encoding="utf-8",
        )


if __name__ == "__main__":
    build_site()
    print("Static site generated successfully.")
