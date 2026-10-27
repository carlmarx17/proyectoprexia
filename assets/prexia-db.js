/**
 * PREXIA POA 2026-2 · Motor de Datos, Niveles, Progreso, Multiplicadores Multinivel,
 * Penalizaciones por Incumplimiento y Sincronización con Git.
 * Basado en "Sistema de Evaluación Prexia: Puntos y Multiplicadores"
 */
(function (window) {
  const STORAGE_KEY = "prexia_poa_sistema_db_v3";
  const SESSION_KEY = "prexia_poa_session_user_v3";
  const GIT_SYNC_META_KEY = "prexia_poa_git_meta_v3";

  const PENALTY_CONFIG = {
    id: "incumplimiento_entrega_encuentro",
    nombre: "Incumplimiento de fecha y hora de entrega o encuentro sin justa causa",
    puntosRestaDefault: 50,
    limiteAlertaRoja: 3
  };

  const LEVELS_CONFIG = {
    1: {
      nivel: 1,
      nombre: "Fundamentación",
      rol: "Operativo",
      rangoPct: "0% a 30%",
      minPct: 0,
      maxPct: 30,
      semestres: "Semestres 1 a 3",
      creditosRef: "0 a 52 créditos",
      motivacionPink: "Pertenencia y adaptación rítmica",
      descripcion: "Tareas operativas cortas y concretas; respeta la alta carga de Cálculo, Álgebra Lineal y Física.",
      proyectosTipicos: "Logística de eventos, recopilar cápsulas de conocimiento, gestión de redes sociales.",
      color: "#0f652e",
      badgeBg: "#dcfce7",
      multiplicadores: [
        {
          id: "n1_contenido",
          nombre: "Excelencia en Contenido",
          bono: 3,
          condicion: "Calendario de publicaciones cumplido al 100% sin retrasos (la meta base es 80% o más)."
        },
        {
          id: "n1_valor",
          nombre: "Generación de Valor",
          bono: 4,
          condicion: "Cada cápsula de conocimiento extra recopilada, editada y publicada (meta semestral de 4 o más)."
        },
        {
          id: "n1_cultura",
          nombre: "Cultura Consultor",
          bono: 2,
          condicion: "Participa en el diseño y la publicación de contenido sobre la cultura de un Consultor Prexia."
        }
      ]
    },
    2: {
      nivel: 2,
      nombre: "Transición",
      rol: "Gestor",
      rangoPct: "31% a 60%",
      minPct: 31,
      maxPct: 60,
      semestres: "Semestres 4 a 6",
      creditosRef: "53 a 104 créditos",
      motivacionPink: "Autonomía y coordinación de equipos",
      descripcion: "Liderazgo táctico, proactividad, marketing organizacional y logística de eventos internacionales.",
      proyectosTipicos: "Bienestar y comunidad (Proyecto 3), diseño y web, simulaciones de ventas.",
      color: "#0369a1",
      badgeBg: "#e0f2fe",
      multiplicadores: [
        {
          id: "n2_traccion",
          nombre: "Tracción Web y Redes",
          bono: 5,
          condicion: "Crecimiento de audiencia en redes de la línea del 15% o más."
        },
        {
          id: "n2_convocatoria",
          nombre: "Poder de Convocatoria",
          bono: 4,
          condicion: "Integraciones o eventos con participación del 70% o más de los integrantes."
        },
        {
          id: "n2_bienestar",
          nombre: "Celebración y Bienestar",
          bono: 2,
          condicion: "100% de cumpleaños celebrados y reconocimientos individuales entregados."
        }
      ]
    },
    3: {
      nivel: 3,
      nombre: "Profesionalización",
      rol: "Consultor Junior",
      rangoPct: "61% a 85%",
      minPct: 61,
      maxPct: 85,
      semestres: "Semestres 7 a 9",
      creditosRef: "105 a 147 créditos",
      motivacionPink: "Maestría técnica y rigor analítico",
      descripcion: "Más tareas técnicas que las horas pactadas; meta de +4% de productividad de la línea.",
      proyectosTipicos: "Consultoría a emprendimientos y MiPymes, diseño curricular, simulaciones con datos reales.",
      color: "#4338ca",
      badgeBg: "#e0e7ff",
      multiplicadores: [
        {
          id: "n3_analitica",
          nombre: "Efectividad Analítica",
          bono: 6,
          condicion: "100% de informes finales entregados con calidad profesional, superando expectativas del cliente."
        },
        {
          id: "n3_curricular",
          nombre: "Diseño Curricular",
          bono: 5,
          condicion: "Diseña la estructura del curso o casos de simulación con datos reales del sector."
        },
        {
          id: "n3_productividad",
          nombre: "Productividad Extra",
          bono: 4,
          condicion: "Ejecuta más tareas o vincula más emprendimientos de los pactados."
        }
      ]
    },
    4: {
      nivel: 4,
      nombre: "Cierre y Proyección",
      rol: "Líder",
      rangoPct: "Más de 85%",
      minPct: 86,
      maxPct: 100,
      semestres: "Semestre 10",
      creditosRef: "148 a 172 créditos",
      motivacionPink: "Propósito y legado institucional",
      descripcion: "Gerencia y mentoría; su aporte debe hacer eco en todas las líneas de Prexia.",
      proyectosTipicos: "Liderazgo de línea, vinculación de expertos externos, negociación de retribución.",
      color: "#1f1a3a",
      badgeBg: "#ede9fe",
      multiplicadores: [
        {
          id: "n4_impacto",
          nombre: "Impacto Económico",
          bono: 10,
          condicion: "Cierra negociaciones de retribución sobre utilidades con los emprendimientos y empresas asesoradas."
        },
        {
          id: "n4_relaciones",
          nombre: "Relaciones Públicas",
          bono: 8,
          condicion: "Vincula profesores o expertos externos para dictar el curso (meta de 6 o más sesiones externas)."
        },
        {
          id: "n4_curso",
          nombre: "Finalización de Curso",
          bono: 5,
          condicion: "80% o más de los participantes culminan el curso de consultoría."
        }
      ]
    }
  };

  const DEFAULT_DB = {
    "meta": {
      "sistema": "PREXIA POA · Sistema de Evaluación por Puntos Prexia (PP), Multiplicadores Multinivel y Control de Incumplimientos",
      "cohorte": "Participantes Línea de Consultoría 2026-2",
      "periodo": "2026-2",
      "semanaActual": 1,
      "totalSemanas": 16,
      "creditosCarrera": 172,
      "semestresCarrera": 10,
      "repositorioGit": "https://github.com/carlmarx17/proyectoprexia",
      "archivoDatos": "data/prexia-users-db.json",
      "ultimaActualizacion": "2026-10-27T15:45:00-05:00",
      "ultimoAutor": "Coordinación Línea de Consultoría PREXIA"
    },
    "usuarios": [
      {
        "id": "usr-maestro",
        "username": "maestro",
        "password": "123",
        "nombre": "Prof. José Ignacio Maya",
        "email": "jimaya@unal.edu.co",
        "correoCaracterizacion": "prexiaforum_med@unal.edu.co",
        "rolSistema": "maestro",
        "cargo": "Director General y Coordinador Maestro POA",
        "carrera": "Docente Dpto. Ingeniería de la Organización",
        "linea": "Dirección General · Línea de Consultoría 2026-2",
        "avatar": "JM",
        "nivel": 4,
        "semestre": 10,
        "porcentajeAvance": 100,
        "porcentajeAvanceTexto": "100%",
        "creditosAprobados": 172,
        "creditosTotales": 172,
        "materiasAltoImpacto": false,
        "detalleMaterias": "Dirección Académica y Coordinación General Semillero PREXIA",
        "horasSemanalesTexto": "8",
        "hsa": 8,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "Dirección estratégica, consultoría organizacional, evaluación por Puntos Prexia (PP) y articulación internacional EISI.",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Fundador PREXIA UNAL",
          "Auditor Maestro POA 2026-2",
          "Articulación Internacional EISI"
        ],
        "entregables": [
          {
            "id": "ent-m1",
            "semana": 1,
            "titulo": "Caracterización oficial Participantes Línea de Consultoría 2026-2 (13 integrantes)",
            "tipo": "Gobernanza",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Sistema inicializado con barra de rendimiento desde 0 PP, multiplicadores abiertos entre niveles y control de anotaciones por incumplimiento."
          }
        ]
      },
      {
        "id": "usr-juanjose",
        "ordenHoja": 1,
        "username": "jvargassan",
        "password": "123",
        "nombre": "Juan José Vargas Sánchez",
        "email": "jvargassan@unal.edu.co",
        "correoCaracterizacion": "jvargassan@unal.edu.co",
        "rolSistema": "estudiante",
        "cargo": "Consultor Junior · Gestión de Proyectos y Datos",
        "carrera": "Ingeniería Administrativa",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "JV",
        "nivel": 3,
        "semestre": 8,
        "porcentajeAvance": 75.0,
        "porcentajeAvanceTexto": "75%",
        "creditosAprobados": 129,
        "creditosTotales": 172,
        "materiasAltoImpacto": false,
        "detalleMaterias": "Gestión de proyectos, Análisis de datos",
        "horasSemanalesTexto": "2 a 4",
        "hsa": 3,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "Gestion de proyectos, Analisis de datos",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 3 · Consultor Junior (75%)"
        ],
        "entregables": [
          {
            "id": "ent-jj1",
            "semana": 1,
            "titulo": "Caracterización y Pacto de Dedicación (2 a 4 horas semanales · 75% avance)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 3 HSA = 300 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      },
      {
        "id": "usr-dahiana",
        "ordenHoja": 2,
        "username": "dlozanoy",
        "password": "123",
        "nombre": "Dahiana Lozano Yepes",
        "email": "dlozanoy@unal.edu.co",
        "correoCaracterizacion": "dlozanoy@unal.edu.co",
        "rolSistema": "estudiante",
        "cargo": "Gestora · Analítica BI y Marketing Digital",
        "carrera": "Ingeniería Industrial",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "DL",
        "nivel": 2,
        "semestre": 4,
        "porcentajeAvance": 38.0,
        "porcentajeAvanceTexto": "38%",
        "creditosAprobados": 65,
        "creditosTotales": 172,
        "materiasAltoImpacto": false,
        "detalleMaterias": "Analisis de datos, Marketing digital, Uso de herramientas como Power BI y Looker Studio.",
        "horasSemanalesTexto": "8 a 10",
        "hsa": 9,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "Analisis de datos, Marketing digital, Uso de herramientas como Power BI y Looker Studio.",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 2 · Rol Gestor (38%)"
        ],
        "entregables": [
          {
            "id": "ent-dl1",
            "semana": 1,
            "titulo": "Caracterización y Pacto de Alta Dedicación (8 a 10 horas semanales · 38% avance)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 9 HSA = 900 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      },
      {
        "id": "usr-julian",
        "ordenHoja": 3,
        "username": "juloperag",
        "password": "123",
        "nombre": "Julian David Lopera Grisales",
        "email": "juloperag@unal.edu.co",
        "correoCaracterizacion": "juloperag@unal.edu.co",
        "rolSistema": "estudiante",
        "cargo": "Líder de Línea · Investigación y Coordinación de Equipos",
        "carrera": "Ingeniería Física",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "JL",
        "nivel": 4,
        "semestre": 10,
        "porcentajeAvance": 96.0,
        "porcentajeAvanceTexto": "96%",
        "creditosAprobados": 165,
        "creditosTotales": 172,
        "materiasAltoImpacto": false,
        "detalleMaterias": "Investigación, coordinar equipos de trabajo (monitor fisica), basicas de ofimatica. Analitica de datos",
        "horasSemanalesTexto": "6 a 8",
        "hsa": 7,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "Investigación, coordinar equipos de trabajo (monitor fisica), basicas de ofimatica. Analitica de datos",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 4 · Rol Líder (96%)"
        ],
        "entregables": [
          {
            "id": "ent-jl1",
            "semana": 1,
            "titulo": "Caracterización y Liderazgo Senior (6 a 8 horas semanales · 96% avance en Ingeniería Física)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 7 HSA = 700 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      },
      {
        "id": "usr-jhon",
        "ordenHoja": 4,
        "username": "jvalencia",
        "password": "123",
        "nombre": "Jhon Alejandro Valencia",
        "email": "jvalencia@unal.edu.co",
        "correoCaracterizacion": "—",
        "rolSistema": "estudiante",
        "cargo": "Operativo · Negociación y Manejo de Equipos",
        "carrera": "Administrativa",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "JA",
        "nivel": 1,
        "semestre": 1,
        "porcentajeAvance": 0.0,
        "porcentajeAvanceTexto": "0%",
        "creditosAprobados": 0,
        "creditosTotales": 172,
        "materiasAltoImpacto": true,
        "detalleMaterias": "Ofimatica avanzada, negociación, manejo de equipos",
        "horasSemanalesTexto": "6 a 8",
        "hsa": 7,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "Ofimatica avanzada, negociación, manejo de equipos",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 1 · Rol Operativo (0%)"
        ],
        "entregables": [
          {
            "id": "ent-ja1",
            "semana": 1,
            "titulo": "Caracterización e Ingreso Nivel 1 (6 a 8 horas semanales · Administrativa)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 7 HSA = 700 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      },
      {
        "id": "usr-brayan",
        "ordenHoja": 5,
        "username": "bmartinezag",
        "password": "123",
        "nombre": "Brayan Julian Martinez Aguilar",
        "email": "bmartinezag@unal.edu.co",
        "correoCaracterizacion": "bmartinezag@unal.edu.co",
        "rolSistema": "estudiante",
        "cargo": "Consultor Junior · Analítica de Datos en Power BI",
        "carrera": "Ingeniería Industrial",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "BM",
        "nivel": 3,
        "semestre": 8,
        "porcentajeAvance": 76.4,
        "porcentajeAvanceTexto": "76,40%",
        "creditosAprobados": 131,
        "creditosTotales": 172,
        "materiasAltoImpacto": false,
        "detalleMaterias": "Comunicacion asertiva, ofimática nivel media, analítica de datos en Power Bi.",
        "horasSemanalesTexto": "6 a 8",
        "hsa": 7,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "Comunicacion asertiva, ofimática nivel media, analítica de datos en Power Bi.",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 3 · Consultor Junior (76,40%)"
        ],
        "entregables": [
          {
            "id": "ent-bm1",
            "semana": 1,
            "titulo": "Caracterización y Pacto Semestral (6 a 8 horas semanales · 76,40% avance)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 7 HSA = 700 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      },
      {
        "id": "usr-luisdaniel",
        "ordenHoja": 6,
        "username": "lyepez",
        "password": "123",
        "nombre": "Luis Daniel Yepez Gaviria",
        "email": "lyepez@unal.edu.co",
        "correoCaracterizacion": "lyepez@unal.edu.co",
        "rolSistema": "estudiante",
        "cargo": "Consultor Junior · Programación y Medios Digitales",
        "carrera": "Ingeniería Industrial",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "LY",
        "nivel": 3,
        "semestre": 8,
        "porcentajeAvance": 76.4,
        "porcentajeAvanceTexto": "76,40%",
        "creditosAprobados": 131,
        "creditosTotales": 172,
        "materiasAltoImpacto": false,
        "detalleMaterias": "Trabajo equipo, comunicación acertiva, ofimatica media, programación, edicion de videos.",
        "horasSemanalesTexto": "6 a 8",
        "hsa": 7,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "Trabajo equipo, comunicación acertiva, ofimatica media, programación, edicion de videos.",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 3 · Consultor Junior (76,40%)"
        ],
        "entregables": [
          {
            "id": "ent-ly1",
            "semana": 1,
            "titulo": "Caracterización y Pacto Semestral (6 a 8 horas semanales · 76,40% avance)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 7 HSA = 700 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      },
      {
        "id": "usr-dani",
        "ordenHoja": 7,
        "username": "dani",
        "password": "123",
        "nombre": "Dani GTH",
        "email": "dani@unal.edu.co",
        "correoCaracterizacion": "—",
        "rolSistema": "estudiante",
        "cargo": "Operativo · Gestión de Talento Humano (GTH)",
        "carrera": "Ingeniería Industrial",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "DG",
        "nivel": 1,
        "semestre": 2,
        "porcentajeAvance": 20.0,
        "porcentajeAvanceTexto": "—",
        "creditosAprobados": 34,
        "creditosTotales": 172,
        "materiasAltoImpacto": true,
        "detalleMaterias": "Gestión de Talento Humano (GTH) · Línea de Consultoría",
        "horasSemanalesTexto": "3",
        "hsa": 3,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "—",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 1 · Rol Operativo"
        ],
        "entregables": [
          {
            "id": "ent-dg1",
            "semana": 1,
            "titulo": "Caracterización Línea de Consultoría 2026-2 (3 horas semanales)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 3 HSA = 300 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      },
      {
        "id": "usr-evreydi",
        "ordenHoja": 8,
        "username": "evreydi",
        "password": "123",
        "nombre": "Evreydi Orduz Prexia",
        "email": "evreydi@unal.edu.co",
        "correoCaracterizacion": "—",
        "rolSistema": "estudiante",
        "cargo": "Consultora Junior · Finanzas, Programación y Enfoque Social",
        "carrera": "Ingeniería Industrial",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "EO",
        "nivel": 3,
        "semestre": 8,
        "porcentajeAvance": 80.0,
        "porcentajeAvanceTexto": "80%",
        "creditosAprobados": 138,
        "creditosTotales": 172,
        "materiasAltoImpacto": false,
        "detalleMaterias": "Comunicación, organización, creatividad, un poco de finanzas y de programación, suelo tener pensamiento social y comunitario",
        "horasSemanalesTexto": "8",
        "hsa": 8,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "Comunicación, organización, creatividad, un poco de finanzas y de programación, suelo tener pensamiento social y comunitario",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 3 · Consultora Junior (80%)"
        ],
        "entregables": [
          {
            "id": "ent-eo1",
            "semana": 1,
            "titulo": "Caracterización y Pacto de 8 Horas Semanales (80% avance en Ingeniería Industrial)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 8 HSA = 800 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      },
      {
        "id": "usr-omar",
        "ordenHoja": 9,
        "username": "omar",
        "password": "123",
        "nombre": "Omar",
        "email": "omar@unal.edu.co",
        "correoCaracterizacion": "—",
        "rolSistema": "estudiante",
        "cargo": "Gestor · Toma de Decisiones, Excel y Ventas",
        "carrera": "Ingeniería Industrial",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "OM",
        "nivel": 2,
        "semestre": 5,
        "porcentajeAvance": 51.0,
        "porcentajeAvanceTexto": "51%",
        "creditosAprobados": 88,
        "creditosTotales": 172,
        "materiasAltoImpacto": false,
        "detalleMaterias": "Trabajo en equipo, comunicación, toma de desciciones, Excel e interes por las ventas.",
        "horasSemanalesTexto": "2",
        "hsa": 2,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "Trabajo en equipo, comunicación, toma de desciciones, Excel e interes por las ventas.",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 2 · Rol Gestor (51%)"
        ],
        "entregables": [
          {
            "id": "ent-om1",
            "semana": 1,
            "titulo": "Caracterización y Pacto de 2 Horas Semanales (51% avance en Ingeniería Industrial)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 2 HSA = 200 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      },
      {
        "id": "usr-sofia",
        "ordenHoja": 10,
        "username": "sofia",
        "password": "123",
        "nombre": "Sofia",
        "email": "sofia@unal.edu.co",
        "correoCaracterizacion": "—",
        "rolSistema": "estudiante",
        "cargo": "Operativo · Apoyo Línea de Consultoría",
        "carrera": "Por registrar",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "SF",
        "nivel": 1,
        "semestre": 2,
        "porcentajeAvance": 15.0,
        "porcentajeAvanceTexto": "—",
        "creditosAprobados": 26,
        "creditosTotales": 172,
        "materiasAltoImpacto": true,
        "detalleMaterias": "Participante activa Curso y Línea de Consultoría 2026-2",
        "horasSemanalesTexto": "3",
        "hsa": 3,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "—",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 1 · Rol Operativo"
        ],
        "entregables": [
          {
            "id": "ent-sf1",
            "semana": 1,
            "titulo": "Caracterización Línea de Consultoría 2026-2 (3 horas semanales)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 3 HSA = 300 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      },
      {
        "id": "usr-timi",
        "ordenHoja": 11,
        "username": "timi",
        "password": "123",
        "nombre": "Timi",
        "email": "timi@unal.edu.co",
        "correoCaracterizacion": "—",
        "rolSistema": "estudiante",
        "cargo": "Operativo · Informática y Sistemas Digitales",
        "carrera": "Ingeniería Industrial",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "TM",
        "nivel": 1,
        "semestre": 3,
        "porcentajeAvance": 27.0,
        "porcentajeAvanceTexto": "27%",
        "creditosAprobados": 46,
        "creditosTotales": 172,
        "materiasAltoImpacto": true,
        "detalleMaterias": "Todo lo relacionado con Informática",
        "horasSemanalesTexto": "6",
        "hsa": 6,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "Todo lo relacionado con Informática",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 1 · Rol Operativo (27%)"
        ],
        "entregables": [
          {
            "id": "ent-tm1",
            "semana": 1,
            "titulo": "Caracterización y Pacto de 6 Horas Semanales (27% avance en Ingeniería Industrial)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 6 HSA = 600 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      },
      {
        "id": "usr-zuly",
        "ordenHoja": 12,
        "username": "zuly",
        "password": "123",
        "nombre": "Zuly",
        "email": "zuly@unal.edu.co",
        "correoCaracterizacion": "—",
        "rolSistema": "estudiante",
        "cargo": "Operativo · Apoyo Ingeniería Industrial",
        "carrera": "Ingeniería Industrial",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "ZL",
        "nivel": 1,
        "semestre": 2,
        "porcentajeAvance": 20.0,
        "porcentajeAvanceTexto": "—",
        "creditosAprobados": 34,
        "creditosTotales": 172,
        "materiasAltoImpacto": true,
        "detalleMaterias": "Participante activa Curso y Línea de Consultoría 2026-2",
        "horasSemanalesTexto": "3",
        "hsa": 3,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "—",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 1 · Rol Operativo"
        ],
        "entregables": [
          {
            "id": "ent-zl1",
            "semana": 1,
            "titulo": "Caracterización Línea de Consultoría 2026-2 (3 horas semanales · Ingeniería Industrial)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 3 HSA = 300 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      },
      {
        "id": "usr-dana",
        "ordenHoja": 13,
        "username": "dana",
        "password": "123",
        "nombre": "Dana",
        "email": "dana@unal.edu.co",
        "correoCaracterizacion": "—",
        "rolSistema": "estudiante",
        "cargo": "Consultora Junior · Gestión de Equipos, Negocios y Redes",
        "carrera": "Ingeniería Administrativa",
        "linea": "Línea de Consultoría 2026-2",
        "avatar": "DN",
        "nivel": 3,
        "semestre": 7,
        "porcentajeAvance": 70.0,
        "porcentajeAvanceTexto": "70%",
        "creditosAprobados": 120,
        "creditosTotales": 172,
        "materiasAltoImpacto": false,
        "detalleMaterias": "Redes sociales, Gestión de equipos, negocios y Ofimática",
        "horasSemanalesTexto": "3",
        "hsa": 3,
        "horasCumplidas": 0,
        "puntosExtraManual": 0,
        "herramientasHabilidades": "Redes sociales, Gestión de equipos, negocios y Ofimática",
        "multiplicadoresActivos": [],
        "anotaciones": [],
        "puntosAcumuladosSemestre": 0,
        "insignias": [
          "Nivel 3 · Consultora Junior (70%)"
        ],
        "entregables": [
          {
            "id": "ent-dn1",
            "semana": 1,
            "titulo": "Caracterización y Pacto de 3 Horas Semanales (70% avance en Ingeniería Administrativa)",
            "tipo": "Caracterización 2026-2",
            "estado": "Aprobado"
          }
        ],
        "historialQuincenal": [],
        "bitacoraCrecimiento": [
          {
            "fecha": "2026-10-27",
            "evento": "Barra de rendimiento inicializada en 0 PP (Meta base pactada: 3 HSA = 300 PP). Listo para sumar puntos/hora y multiplicadores."
          }
        ]
      }
    ]
  };

  function clone(obj) {
    return JSON.parse(JSON.stringify(obj));
  }

  function calcularNivelPorCreditos(creditosAprobados, creditosTotales = 172) {
    const pct = Math.round((creditosAprobados / creditosTotales) * 100);
    if (pct <= 30) return 1;
    if (pct <= 60) return 2;
    if (pct <= 85) return 3;
    return 4;
  }

  function obtenerMultiplicadorInfo(multId) {
    for (const lvl of [1, 2, 3, 4]) {
      const cfg = LEVELS_CONFIG[lvl];
      const found = cfg.multiplicadores.find((m) => m.id === multId);
      if (found) {
        return {
          ...found,
          nivel: lvl,
          rolNivel: cfg.rol,
          nombreNivel: cfg.nombre
        };
      }
    }
    return null;
  }

  function obtenerTodosLosMultiplicadores() {
    const list = [];
    [1, 2, 3, 4].forEach((lvl) => {
      const cfg = LEVELS_CONFIG[lvl];
      cfg.multiplicadores.forEach((m) => {
        list.push({
          ...m,
          nivel: lvl,
          rolNivel: cfg.rol,
          nombreNivel: cfg.nombre
        });
      });
    });
    return list;
  }

  function calcularLiquidacionUsuario(user, semanaEval) {
    const semana = Math.min(16, Math.max(1, parseInt(semanaEval || 1, 10)));
    const hsa = Math.max(1, parseInt(user.hsa || 4, 10));
    const basePP = hsa * 100; // Meta base semanal según pacto HSA
    const curvaPct = 100 + (semana - 1); // Sem 1 = 100%, Sem 16 = 115%
    const metaSemanaPP = Math.round(basePP * (curvaPct / 100));

    // La barra de rendimiento arranca desde 0 y avanza a medida que se suman puntos/hora y multiplicadores
    const horasCumplidas = typeof user.horasCumplidas === "number" ? Math.max(0, Number(user.horasCumplidas)) : 0;
    const puntosExtraManual = parseInt(user.puntosExtraManual || 0, 10) || 0;
    const puntosHoraPP = Math.max(0, Math.round(horasCumplidas * 100) + puntosExtraManual);

    const levelCfg = LEVELS_CONFIG[user.nivel] || LEVELS_CONFIG[1];
    let bonoPct = 0;
    const multDetalles = [];

    (user.multiplicadoresActivos || []).forEach((mId) => {
      const mInfo = obtenerMultiplicadorInfo(mId);
      if (mInfo) {
        bonoPct += mInfo.bono;
        multDetalles.push({
          ...mInfo,
          esOtroNivel: mInfo.nivel !== user.nivel
        });
      }
    });

    // El bono de multiplicadores suma sobre la base pactada (basePP) sin importar el nivel
    const bonoPP = Math.round(basePP * (bonoPct / 100));

    // Resta de puntos: Incumplimiento de fecha y hora de entrega o encuentro sin justa causa
    const anotaciones = Array.isArray(user.anotaciones) ? user.anotaciones : [];
    const numAnotaciones = anotaciones.length;
    const puntosRestadosPP = anotaciones.reduce(
      (acc, item) => acc + Math.max(0, parseInt(item.puntosRestados !== undefined ? item.puntosRestados : PENALTY_CONFIG.puntosRestaDefault, 10)),
      0
    );
    const enAlertaRoja = numAnotaciones >= PENALTY_CONFIG.limiteAlertaRoja; // Se pone en rojo al llevar 3 anotaciones

    const brutoPP = puntosHoraPP + bonoPP;
    const finalPP = Math.max(0, brutoPP - puntosRestadosPP);
    const cumplimientoPct = metaSemanaPP > 0 ? Math.max(0, Math.round((finalPP / metaSemanaPP) * 100)) : 0;
    const barraPct = Math.min(100, Math.max(0, cumplimientoPct));
    const superoMeta = finalPP >= metaSemanaPP && !enAlertaRoja;
    const brechaPP = Math.max(0, metaSemanaPP - finalPP);

    const avanceCarreraPct = typeof user.porcentajeAvance === "number"
      ? user.porcentajeAvance
      : Math.min(100, Math.round(((user.creditosAprobados || 0) / (user.creditosTotales || 172)) * 100));
    const avanceDisplay = user.porcentajeAvanceTexto || (avanceCarreraPct + "%");
    const horasDisplay = user.horasSemanalesTexto || String(hsa);
    const herramientas = user.herramientasHabilidades || user.detalleMaterias || "—";
    const correoHoja = user.correoCaracterizacion || user.email || "—";

    return {
      semana,
      hsa,
      horasCumplidas,
      puntosExtraManual,
      puntosHoraPP,
      basePP,
      curvaPct,
      metaSemanaPP,
      bonoPct,
      bonoPP,
      brutoPP,
      anotaciones,
      numAnotaciones,
      puntosRestadosPP,
      enAlertaRoja,
      finalPP,
      cumplimientoPct,
      barraPct,
      superoMeta,
      brechaPP,
      avanceCarreraPct,
      avanceDisplay,
      horasDisplay,
      herramientas,
      correoHoja,
      levelCfg,
      multDetalles
    };
  }

  function normalizeUserFields(u) {
    if (typeof u.horasCumplidas !== "number") u.horasCumplidas = 0;
    if (typeof u.puntosExtraManual !== "number") u.puntosExtraManual = 0;
    if (!Array.isArray(u.multiplicadoresActivos)) u.multiplicadoresActivos = [];
    if (!Array.isArray(u.anotaciones)) u.anotaciones = [];
    if (!Array.isArray(u.insignias)) u.insignias = [];
    if (!Array.isArray(u.entregables)) u.entregables = [];
    if (!Array.isArray(u.historialQuincenal)) u.historialQuincenal = [];
    if (!Array.isArray(u.bitacoraCrecimiento)) u.bitacoraCrecimiento = [];
    return u;
  }

  function getDB() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && Array.isArray(parsed.usuarios)) {
          parsed.usuarios.forEach(normalizeUserFields);
          return parsed;
        }
      }
    } catch (e) {
      console.warn("No se pudo leer localStorage:", e);
    }
    const initial = clone(DEFAULT_DB);
    initial.usuarios.forEach(normalizeUserFields);
    saveDB(initial, "Inicialización del sistema (Barra en 0 PP)", false);
    return initial;
  }

  function saveDB(db, accionDescripcion = "Actualización de datos", markDirty = true) {
    db.meta = db.meta || {};
    db.meta.ultimaActualizacion = new Date().toISOString();
    if (accionDescripcion) {
      db.meta.ultimaAccion = accionDescripcion;
    }
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
      if (markDirty) {
        const syncMeta = getGitSyncMeta();
        syncMeta.pendingChanges = (syncMeta.pendingChanges || 0) + 1;
        syncMeta.lastLocalChange = db.meta.ultimaActualizacion;
        syncMeta.lastAction = accionDescripcion;
        localStorage.setItem(GIT_SYNC_META_KEY, JSON.stringify(syncMeta));
      }
    } catch (e) {
      console.warn("Error guardando en localStorage:", e);
    }
    return db;
  }

  function getGitSyncMeta() {
    try {
      const raw = localStorage.getItem(GIT_SYNC_META_KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) {}
    return {
      pendingChanges: 0,
      lastGitSync: "2026-10-27T15:45:00-05:00",
      lastCommitHash: "HEAD · data/prexia-users-db.json",
      lastAction: "Sincronizado con repositorio Git"
    };
  }

  function markGitSynced(commitInfo = "Sincronizado con Git") {
    const meta = getGitSyncMeta();
    meta.pendingChanges = 0;
    meta.lastGitSync = new Date().toISOString();
    meta.lastCommitHash = commitInfo;
    localStorage.setItem(GIT_SYNC_META_KEY, JSON.stringify(meta));
    return meta;
  }

  async function syncFromCanonicalJSON(jsonPath) {
    try {
      const res = await fetch(jsonPath, { cache: "no-store" });
      if (!res.ok) return getDB();
      const remoteDB = await res.json();
      const syncMeta = getGitSyncMeta();
      if ((syncMeta.pendingChanges || 0) === 0 && remoteDB && Array.isArray(remoteDB.usuarios)) {
        remoteDB.usuarios.forEach(normalizeUserFields);
        saveDB(remoteDB, "Sincronizado desde data/prexia-users-db.json", false);
        return remoteDB;
      }
      return getDB();
    } catch (e) {
      return getDB();
    }
  }

  function resetToFactoryGitDB() {
    const fresh = clone(DEFAULT_DB);
    fresh.usuarios.forEach(normalizeUserFields);
    saveDB(fresh, "Restauración a estado base en 0 PP del repositorio Git", false);
    markGitSynced("Estado inicial en 0 PP restaurado");
    return fresh;
  }

  // ── SESIÓN Y LOGIN ──
  function getCurrentUser() {
    const db = getDB();
    try {
      const userId = localStorage.getItem(SESSION_KEY);
      if (userId) {
        return db.usuarios.find((u) => u.id === userId || u.username === userId) || null;
      }
    } catch (e) {}
    return null;
  }

  function login(identifier, password) {
    const db = getDB();
    const clean = (identifier || "").trim().toLowerCase();
    const user = db.usuarios.find(
      (u) =>
        u.username.toLowerCase() === clean ||
        u.email.toLowerCase() === clean ||
        u.id.toLowerCase() === clean
    );
    if (!user) {
      return { ok: false, error: "Usuario no encontrado. Usa uno de los usuarios de demostración o verifica el correo." };
    }
    if (password !== undefined && password !== null && String(password).trim() !== "" && user.password !== String(password).trim()) {
      return { ok: false, error: "Contraseña incorrecta (Clave demo para todos los perfiles: 123)." };
    }
    localStorage.setItem(SESSION_KEY, user.id);
    return { ok: true, user };
  }

  function logout() {
    localStorage.removeItem(SESSION_KEY);
  }

  // ── ACCIONES DE PROGRESO, PUNTOS/HORA, MULTIPLICADORES MULTINIVEL Y RESTA DE PUNTOS ──
  function registrarSnapshotHistorial(user, semana) {
    const liq = calcularLiquidacionUsuario(user, semana);
    user.historialQuincenal = user.historialQuincenal || [];
    const idx = user.historialQuincenal.findIndex((h) => h.semana === semana);
    const entry = {
      semana,
      horasCumplidas: liq.horasCumplidas,
      puntosHoraPP: liq.puntosHoraPP,
      basePP: liq.basePP,
      metaPP: liq.metaSemanaPP,
      bonoPct: liq.bonoPct,
      bonoPP: liq.bonoPP,
      puntosRestadosPP: liq.puntosRestadosPP,
      numAnotaciones: liq.numAnotaciones,
      finalPP: liq.finalPP,
      cumplimiento: liq.cumplimientoPct
    };
    if (idx >= 0) {
      user.historialQuincenal[idx] = entry;
    } else {
      user.historialQuincenal.push(entry);
      user.historialQuincenal.sort((a, b) => a.semana - b.semana);
    }
    user.puntosAcumuladosSemestre = user.historialQuincenal.reduce((acc, item) => acc + (item.finalPP || 0), 0);
  }

  // Sumar o restar horas cumplidas (1 hora = 100 PP)
  function ajustarHorasCumplidas(userId, deltaHoras) {
    const db = getDB();
    const user = db.usuarios.find((u) => u.id === userId);
    if (!user) return null;

    const actual = typeof user.horasCumplidas === "number" ? user.horasCumplidas : 0;
    const nuevo = Math.max(0, Math.round((actual + Number(deltaHoras || 0)) * 10) / 10);
    user.horasCumplidas = nuevo;

    user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
    user.bitacoraCrecimiento.unshift({
      fecha: new Date().toISOString().slice(0, 10),
      evento: `Puntos/Hora actualizados: ${nuevo}h cumplidas (${Math.round(nuevo * 100)} PP por horas de ${user.hsa * 100} PP pactados).`
    });

    registrarSnapshotHistorial(user, db.meta.semanaActual);
    saveDB(db, `Puntos/Hora (${nuevo}h = ${Math.round(nuevo * 100)} PP) actualizados para ${user.nombre}`);
    return user;
  }

  function establecerHorasCumplidas(userId, nuevasHoras) {
    const db = getDB();
    const user = db.usuarios.find((u) => u.id === userId);
    if (!user) return null;

    const nuevo = Math.max(0, Math.round(Number(nuevasHoras || 0) * 10) / 10);
    user.horasCumplidas = nuevo;

    user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
    user.bitacoraCrecimiento.unshift({
      fecha: new Date().toISOString().slice(0, 10),
      evento: `Registro directo de Puntos/Hora: ${nuevo}h acreditadas (${Math.round(nuevo * 100)} PP).`
    });

    registrarSnapshotHistorial(user, db.meta.semanaActual);
    saveDB(db, `Horas acreditadas (${nuevo}h) actualizadas para ${user.nombre}`);
    return user;
  }

  function ajustarPuntosManual(userId, deltaPP, motivo = "Ajuste de puntos por actividad") {
    const db = getDB();
    const user = db.usuarios.find((u) => u.id === userId);
    if (!user) return null;

    const delta = parseInt(deltaPP || 0, 10);
    if (!delta) return user;
    user.puntosExtraManual = (parseInt(user.puntosExtraManual || 0, 10) || 0) + delta;

    user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
    user.bitacoraCrecimiento.unshift({
      fecha: new Date().toISOString().slice(0, 10),
      evento: `${delta > 0 ? "Suma" : "Ajuste"} de puntos (${delta > 0 ? "+" : ""}${delta} PP): ${motivo}.`
    });

    registrarSnapshotHistorial(user, db.meta.semanaActual);
    saveDB(db, `Ajuste manual de ${delta > 0 ? "+" : ""}${delta} PP para ${user.nombre}`);
    return user;
  }

  // Permite añadir puntos multiplicadores sin importar el nivel (ej: Nivel 1 puede recibir multiplicador de Nivel 3)
  function toggleMultiplicador(userId, multId) {
    const db = getDB();
    const user = db.usuarios.find((u) => u.id === userId);
    if (!user) return null;

    user.multiplicadoresActivos = user.multiplicadoresActivos || [];
    const exists = user.multiplicadoresActivos.includes(multId);
    const mInfo = obtenerMultiplicadorInfo(multId);

    if (exists) {
      user.multiplicadoresActivos = user.multiplicadoresActivos.filter((id) => id !== multId);
      user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
      user.bitacoraCrecimiento.unshift({
        fecha: new Date().toISOString().slice(0, 10),
        evento: `Multiplicador removido en Semana ${db.meta.semanaActual}: ${mInfo ? mInfo.nombre : multId}.`
      });
    } else {
      user.multiplicadoresActivos.push(multId);
      const esTransversal = mInfo && mInfo.nivel !== user.nivel;
      const badgeName = mInfo
        ? `${esTransversal ? `[Tarea N${mInfo.nivel}] ` : ""}${mInfo.nombre} (+${mInfo.bono}%)`
        : multId;
      if (!user.insignias.includes(badgeName)) {
        user.insignias.push(badgeName);
      }
      user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
      user.bitacoraCrecimiento.unshift({
        fecha: new Date().toISOString().slice(0, 10),
        evento: `Multiplicador acreditado en Semana ${db.meta.semanaActual}: ${mInfo ? mInfo.nombre : multId} (+${mInfo ? mInfo.bono : 0}%)${esTransversal ? ` · Asumió tarea de Nivel ${mInfo.nivel} (${mInfo.rolNivel}) estando en Nivel ${user.nivel}` : ""}.`
      });
    }

    registrarSnapshotHistorial(user, db.meta.semanaActual);
    saveDB(db, `Multiplicador ${exists ? "removido" : "acreditado"} (${mInfo ? mInfo.nombre : multId}) para ${user.nombre}`);
    return user;
  }

  // Resta puntos: Incumplimiento de fecha y hora de entrega o encuentro sin justa causa (Rojo a las 3 anotaciones)
  function agregarAnotacionIncumplimiento(userId, opciones = {}) {
    const db = getDB();
    const user = db.usuarios.find((u) => u.id === userId);
    if (!user) return null;

    user.anotaciones = Array.isArray(user.anotaciones) ? user.anotaciones : [];
    const puntosRestados = Math.max(
      0,
      parseInt(opciones.puntosRestados !== undefined ? opciones.puntosRestados : PENALTY_CONFIG.puntosRestaDefault, 10)
    );
    const detalle = (opciones.observacion || "").trim() || PENALTY_CONFIG.nombre;

    const nuevaAnotacion = {
      id: "anot-" + Date.now() + "-" + Math.floor(Math.random() * 100),
      fecha: new Date().toISOString().slice(0, 10),
      semana: db.meta.semanaActual,
      tipo: PENALTY_CONFIG.nombre,
      observacion: detalle,
      puntosRestados
    };

    user.anotaciones.push(nuevaAnotacion);
    const totalAnot = user.anotaciones.length;

    user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
    if (totalAnot >= PENALTY_CONFIG.limiteAlertaRoja) {
      user.bitacoraCrecimiento.unshift({
        fecha: nuevaAnotacion.fecha,
        evento: `🚨 ALERTA ROJA (${totalAnot} anotaciones): "${PENALTY_CONFIG.nombre}" (-${puntosRestados} PP). El participante ha alcanzado ${totalAnot} anotaciones sin justa causa.`
      });
    } else {
      user.bitacoraCrecimiento.unshift({
        fecha: nuevaAnotacion.fecha,
        evento: `⚠️ Resta de puntos (Anotación ${totalAnot}/3 · -${puntosRestados} PP): ${PENALTY_CONFIG.nombre}${opciones.observacion ? " · " + opciones.observacion : ""}.`
      });
    }

    registrarSnapshotHistorial(user, db.meta.semanaActual);
    saveDB(db, `Anotación de incumplimiento (${totalAnot}/3 · -${puntosRestados} PP) registrada para ${user.nombre}`);
    return { user, totalAnotaciones: totalAnot, enAlertaRoja: totalAnot >= PENALTY_CONFIG.limiteAlertaRoja };
  }

  function eliminarAnotacionIncumplimiento(userId, anotacionId = null) {
    const db = getDB();
    const user = db.usuarios.find((u) => u.id === userId);
    if (!user || !Array.isArray(user.anotaciones) || user.anotaciones.length === 0) return null;

    let eliminada = null;
    if (anotacionId) {
      const idx = user.anotaciones.findIndex((a) => a.id === anotacionId);
      if (idx >= 0) {
        eliminada = user.anotaciones.splice(idx, 1)[0];
      }
    } else {
      eliminada = user.anotaciones.pop();
    }

    if (eliminada) {
      user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
      user.bitacoraCrecimiento.unshift({
        fecha: new Date().toISOString().slice(0, 10),
        evento: `Anotación de incumplimiento removida (+${eliminada.puntosRestados || 50} PP restituidos). Total actual: ${user.anotaciones.length}/3.`
      });
      registrarSnapshotHistorial(user, db.meta.semanaActual);
      saveDB(db, `Anotación de incumplimiento removida para ${user.nombre}`);
    }
    return user;
  }

  function reiniciarProgresoUsuario(userId) {
    const db = getDB();
    const targets = userId === "all" ? db.usuarios : db.usuarios.filter((u) => u.id === userId);
    targets.forEach((u) => {
      u.horasCumplidas = 0;
      u.puntosExtraManual = 0;
      u.multiplicadoresActivos = [];
      u.anotaciones = [];
      u.puntosAcumuladosSemestre = 0;
      u.historialQuincenal = [];
      u.bitacoraCrecimiento = u.bitacoraCrecimiento || [];
      u.bitacoraCrecimiento.unshift({
        fecha: new Date().toISOString().slice(0, 10),
        evento: `Barra de rendimiento reiniciada a 0 PP (0 horas cumplidas, 0 multiplicadores, 0 anotaciones).`
      });
    });
    saveDB(db, userId === "all" ? "Todas las barras de rendimiento reiniciadas a 0 PP" : "Barra de rendimiento reiniciada a 0 PP");
    return db;
  }

  function actualizarPactoHSA(userId, nuevasHSA) {
    const db = getDB();
    const user = db.usuarios.find((u) => u.id === userId);
    if (!user) return null;

    const hsa = Math.min(12, Math.max(1, parseInt(nuevasHSA || 4, 10)));
    user.hsa = hsa;
    user.horasSemanalesTexto = String(hsa);
    user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
    user.bitacoraCrecimiento.unshift({
      fecha: new Date().toISOString().slice(0, 10),
      evento: `Actualización de Pacto HSA: ${hsa} horas semanales (${hsa * 100} PP meta base).`
    });

    registrarSnapshotHistorial(user, db.meta.semanaActual);
    saveDB(db, `Pacto HSA actualizado a ${hsa}h para ${user.nombre}`);
    return user;
  }

  function avanzarCrecimientoUsuario(userId, opciones = {}) {
    const db = getDB();
    const user = db.usuarios.find((u) => u.id === userId);
    if (!user) return null;

    const creditosExtra = parseInt(opciones.creditosExtra || 18, 10);
    const forzarAscensoNivel = Boolean(opciones.forzarAscensoNivel);
    const nivelAnterior = user.nivel;

    if (forzarAscensoNivel && user.nivel < 4) {
      const nuevoNivel = user.nivel + 1;
      const minPctNuevo = LEVELS_CONFIG[nuevoNivel].minPct;
      const creditosMinimos = Math.ceil((minPctNuevo / 100) * (user.creditosTotales || 172));
      user.creditosAprobados = Math.min(user.creditosTotales || 172, Math.max((user.creditosAprobados || 0) + creditosExtra, creditosMinimos));
      user.nivel = nuevoNivel;
      user.semestre = Math.min(10, Math.max(user.semestre + 1, nuevoNivel === 2 ? 4 : nuevoNivel === 3 ? 7 : 10));
    } else {
      user.creditosAprobados = Math.min(user.creditosTotales || 172, (user.creditosAprobados || 0) + creditosExtra);
      user.semestre = Math.min(10, Math.max(1, Math.ceil((user.creditosAprobados / (user.creditosTotales || 172)) * 10)));
      user.nivel = calcularNivelPorCreditos(user.creditosAprobados, user.creditosTotales || 172);
    }

    user.porcentajeAvance = Math.min(100, Math.round((user.creditosAprobados / (user.creditosTotales || 172)) * 100));
    user.porcentajeAvanceTexto = user.porcentajeAvance + "%";

    if (user.nivel > nivelAnterior) {
      const cfgNuevo = LEVELS_CONFIG[user.nivel];
      user.cargo = `${cfgNuevo.rol} · ${cfgNuevo.nombre}`;
      const insigniaAscenso = `Ascenso a Nivel ${user.nivel}: ${cfgNuevo.rol}`;
      if (!user.insignias.includes(insigniaAscenso)) {
        user.insignias.push(insigniaAscenso);
      }
      user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
      user.bitacoraCrecimiento.unshift({
        fecha: new Date().toISOString().slice(0, 10),
        evento: `¡ASCENSO DE NIVEL! Promovido de Nivel ${nivelAnterior} a Nivel ${user.nivel} (${cfgNuevo.nombre} · Rol ${cfgNuevo.rol}) con ${user.creditosAprobados}/${user.creditosTotales} créditos (${user.porcentajeAvance}%).`
      });
    } else {
      user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
      user.bitacoraCrecimiento.unshift({
        fecha: new Date().toISOString().slice(0, 10),
        evento: `Avance académico registrado: +${creditosExtra} créditos aprobados (Total: ${user.creditosAprobados}/${user.creditosTotales} créditos · Semestre ${user.semestre}).`
      });
    }

    registrarSnapshotHistorial(user, db.meta.semanaActual);
    saveDB(db, `Crecimiento y avance registrado para ${user.nombre} (Nivel ${user.nivel})`);
    return { user, ascendio: user.nivel > nivelAnterior, nivelAnterior, nivelNuevo: user.nivel };
  }

  function agregarEntregable(userId, datosEntregable) {
    const db = getDB();
    const user = db.usuarios.find((u) => u.id === userId);
    if (!user) return null;

    const mInfo = datosEntregable.multId ? obtenerMultiplicadorInfo(datosEntregable.multId) : null;
    const horasSumadas = parseFloat(datosEntregable.horasSumadas || 0);

    const nuevo = {
      id: "ent-" + Date.now(),
      semana: db.meta.semanaActual,
      titulo: datosEntregable.titulo || "Entregable de línea PREXIA",
      tipo: mInfo
        ? `Multiplicador N${mInfo.nivel} (+${mInfo.bono}%)`
        : datosEntregable.tipo || `Entregable Nivel ${user.nivel}`,
      estado: datosEntregable.estado || "Aprobado"
    };

    user.entregables = user.entregables || [];
    user.entregables.unshift(nuevo);

    if (horasSumadas > 0) {
      user.horasCumplidas = Math.max(0, Math.round(((user.horasCumplidas || 0) + horasSumadas) * 10) / 10);
    }

    if (datosEntregable.multId && !user.multiplicadoresActivos.includes(datosEntregable.multId)) {
      user.multiplicadoresActivos.push(datosEntregable.multId);
      if (mInfo) {
        const esTransversal = mInfo.nivel !== user.nivel;
        const badge = `${esTransversal ? `[Tarea N${mInfo.nivel}] ` : ""}${mInfo.nombre} (+${mInfo.bono}%)`;
        if (!user.insignias.includes(badge)) user.insignias.push(badge);
      }
    }

    if (datosEntregable.insigniaExtra && !user.insignias.includes(datosEntregable.insigniaExtra)) {
      user.insignias.push(datosEntregable.insigniaExtra);
    }

    user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
    user.bitacoraCrecimiento.unshift({
      fecha: new Date().toISOString().slice(0, 10),
      evento: `Nuevo entregable en Semana ${db.meta.semanaActual}: "${nuevo.titulo}"${horasSumadas > 0 ? ` (+${horasSumadas}h = +${Math.round(horasSumadas * 100)} PP)` : ""}${mInfo ? ` · Multiplicador N${mInfo.nivel}: ${mInfo.nombre} (+${mInfo.bono}%)` : ""}.`
    });

    registrarSnapshotHistorial(user, db.meta.semanaActual);
    saveDB(db, `Nuevo entregable registrado por ${user.nombre}`);
    return user;
  }

  function cambiarSemanaGlobal(nuevaSemana) {
    const db = getDB();
    const sem = Math.min(16, Math.max(1, parseInt(nuevaSemana || 1, 10)));
    db.meta.semanaActual = sem;

    db.usuarios.forEach((u) => {
      registrarSnapshotHistorial(u, sem);
    });

    saveDB(db, `Corte del sistema avanzado a Semana ${sem} (Meta progresiva ${100 + sem - 1}%)`);
    return db;
  }

  function crearNuevoUsuario(datos) {
    const db = getDB();
    const nombre = (datos.nombre || "Nuevo Integrante PREXIA").trim();
    const username = (datos.username || nombre.split(" ")[0].toLowerCase().replace(/[^a-z0-9]/g, "") + Math.floor(Math.random() * 90 + 10)).trim();
    const creditosTotales = 172;
    const creditosAprobados = Math.min(172, Math.max(0, parseInt(datos.creditosAprobados || 25, 10)));
    const nivel = datos.nivelForzado ? parseInt(datos.nivelForzado, 10) : calcularNivelPorCreditos(creditosAprobados, creditosTotales);
    const semestre = Math.min(10, Math.max(1, parseInt(datos.semestre || Math.ceil((Math.max(1, creditosAprobados) / creditosTotales) * 10), 10)));
    const hsa = Math.min(12, Math.max(1, parseInt(datos.hsa || 4, 10)));
    const cfg = LEVELS_CONFIG[nivel];
    const pct = Math.round((creditosAprobados / creditosTotales) * 100);

    const partes = nombre.split(" ");
    const avatar = ((partes[0] ? partes[0][0] : "P") + (partes[1] ? partes[1][0] : "X")).toUpperCase();

    const nuevoUser = {
      id: "usr-" + username + "-" + Date.now().toString().slice(-4),
      ordenHoja: db.usuarios.length,
      username,
      password: datos.password || "123",
      nombre,
      email: datos.email || `${username}@unal.edu.co`,
      correoCaracterizacion: datos.email || `${username}@unal.edu.co`,
      rolSistema: datos.rolSistema || "estudiante",
      cargo: datos.cargo || `${cfg.rol} · ${cfg.nombre}`,
      carrera: datos.carrera || "Ingeniería Industrial",
      linea: datos.linea || "Línea de Consultoría 2026-2",
      avatar,
      nivel,
      semestre,
      porcentajeAvance: pct,
      porcentajeAvanceTexto: pct + "%",
      creditosAprobados,
      creditosTotales,
      materiasAltoImpacto: nivel === 1,
      detalleMaterias: datos.herramientasHabilidades || (nivel === 1 ? "Cálculo, Álgebra Lineal y Física" : "Asignaturas profesionales de ingeniería"),
      herramientasHabilidades: datos.herramientasHabilidades || "Gestión de proyectos y consultoría",
      horasSemanalesTexto: String(hsa),
      hsa,
      horasCumplidas: 0,
      puntosExtraManual: 0,
      multiplicadoresActivos: [],
      anotaciones: [],
      puntosAcumuladosSemestre: 0,
      insignias: [`Ingreso Nivel ${nivel} (${cfg.rol})`],
      entregables: [
        {
          id: "ent-init-" + Date.now(),
          semana: db.meta.semanaActual,
          titulo: `Firma de Pacto Inicial (${hsa} HSA = ${hsa * 100} PP meta base · Arranca en 0 PP)`,
          tipo: "Pacto POA",
          estado: "Aprobado"
        }
      ],
      historialQuincenal: [],
      bitacoraCrecimiento: [
        {
          fecha: new Date().toISOString().slice(0, 10),
          evento: `Integrante vinculado en Nivel ${nivel} (${cfg.nombre} · Rol ${cfg.rol}) con pacto de ${hsa} HSA y barra de rendimiento inicializada en 0 PP.`
        }
      ]
    };

    db.usuarios.push(nuevoUser);
    saveDB(db, `Nuevo integrante registrado: ${nuevoUser.nombre} (Nivel ${nivel})`);
    return nuevoUser;
  }

  // ── FUNCIONES DE PERSISTENCIA EN GIT (LOCAL Y GITHUB REST API) ──
  async function guardarEnServidorGitLocal(commitMessage, hacerPush = false) {
    const db = getDB();
    const response = await fetch("http://localhost:8080/api/save-git", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        db,
        commitMessage: commitMessage || `chore(poa): actualización de progreso PREXIA Semana ${db.meta.semanaActual}`,
        commit: true,
        push: Boolean(hacerPush)
      })
    });
    if (!response.ok) {
      throw new Error("El servidor Git local no respondió en localhost:8080");
    }
    const result = await response.json();
    if (result.ok) {
      markGitSynced(result.git.lastCommit || "Commit local en Git realizado");
    }
    return result;
  }

  async function guardarEnGitHubAPI({ token, owner = "carlmarx17", repo = "proyectoprexia", branch = "main", path = "data/prexia-users-db.json", commitMessage }) {
    if (!token) {
      throw new Error("Ingresa un Personal Access Token (PAT) de GitHub con permiso 'repo' o 'contents:write'.");
    }
    const db = getDB();
    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;

    let sha = undefined;
    const getRes = await fetch(`${apiUrl}?ref=${encodeURIComponent(branch)}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github+json"
      }
    });
    if (getRes.ok) {
      const fileData = await getRes.json();
      sha = fileData.sha;
    }

    const jsonString = JSON.stringify(db, null, 2) + "\n";
    const base64Content = btoa(unescape(encodeURIComponent(jsonString)));

    const putRes = await fetch(apiUrl, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: commitMessage || `chore(poa): actualizar base de datos de usuarios y niveles PREXIA (Sem. ${db.meta.semanaActual})`,
        content: base64Content,
        sha,
        branch
      })
    });

    if (!putRes.ok) {
      const errBody = await putRes.json().catch(() => ({}));
      throw new Error(errBody.message || `Error HTTP ${putRes.status} al guardar en GitHub`);
    }

    const data = await putRes.json();
    const shortSha = data.commit && data.commit.sha ? data.commit.sha.slice(0, 7) : "GitHub";
    markGitSynced(`${shortSha} · Sincronizado en GitHub (${owner}/${repo})`);
    return data;
  }

  function descargarJSONParaGit() {
    const db = getDB();
    const blob = new Blob([JSON.stringify(db, null, 2) + "\n"], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "prexia-users-db.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function importarJSONDesdeTexto(jsonText) {
    const parsed = JSON.parse(jsonText);
    if (!parsed || !Array.isArray(parsed.usuarios)) {
      throw new Error("El archivo JSON no tiene el formato válido de PREXIA POA.");
    }
    parsed.usuarios.forEach(normalizeUserFields);
    saveDB(parsed, "Base de datos importada desde archivo JSON", true);
    return parsed;
  }

  window.PrexiaDB = {
    LEVELS_CONFIG,
    PENALTY_CONFIG,
    getDB,
    saveDB,
    getGitSyncMeta,
    markGitSynced,
    syncFromCanonicalJSON,
    resetToFactoryGitDB,
    calcularNivelPorCreditos,
    calcularLiquidacionUsuario,
    obtenerMultiplicadorInfo,
    obtenerTodosLosMultiplicadores,
    getCurrentUser,
    login,
    logout,
    ajustarHorasCumplidas,
    establecerHorasCumplidas,
    ajustarPuntosManual,
    toggleMultiplicador,
    agregarAnotacionIncumplimiento,
    eliminarAnotacionIncumplimiento,
    reiniciarProgresoUsuario,
    actualizarPactoHSA,
    avanzarCrecimientoUsuario,
    agregarEntregable,
    cambiarSemanaGlobal,
    crearNuevoUsuario,
    guardarEnServidorGitLocal,
    guardarEnGitHubAPI,
    descargarJSONParaGit,
    importarJSONDesdeTexto
  };
})(window);
