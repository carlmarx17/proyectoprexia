/**
 * PREXIA POA 2026-2 · Motor de Datos, Niveles, Progreso y Sincronización con Git
 * Basado íntegramente en "Sistema de Evaluación Prexia: Puntos y Multiplicadores"
 */
(function (window) {
  const STORAGE_KEY = "prexia_poa_sistema_db_v1";
  const SESSION_KEY = "prexia_poa_session_user_v1";
  const GIT_SYNC_META_KEY = "prexia_poa_git_meta_v1";

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
    meta: {
      sistema: "PREXIA POA · Sistema de Evaluación por Puntos Prexia (PP) y Multiplicadores",
      periodo: "2026-2",
      semanaActual: 6,
      totalSemanas: 16,
      creditosCarrera: 172,
      semestresCarrera: 10,
      repositorioGit: "https://github.com/carlmarx17/proyectoprexia",
      archivoDatos: "data/prexia-users-db.json",
      ultimaActualizacion: "2026-10-17T14:40:00-05:00",
      ultimoAutor: "Prof. José Ignacio Maya (Maestro)"
    },
    usuarios: [
      {
        id: "usr-maestro",
        username: "maestro",
        password: "123",
        nombre: "Prof. José Ignacio Maya",
        email: "jimaya@unal.edu.co",
        rolSistema: "maestro",
        cargo: "Director General y Coordinador Maestro POA",
        carrera: "Docente Dpto. Ingeniería de la Organización",
        linea: "Dirección General · 4 Líneas PREXIA",
        avatar: "JM",
        nivel: 4,
        semestre: 10,
        creditosAprobados: 172,
        creditosTotales: 172,
        materiasAltoImpacto: false,
        detalleMaterias: "Dirección Académica y Coordinación General Semillero PREXIA",
        hsa: 8,
        multiplicadoresActivos: ["n4_impacto", "n4_relaciones", "n4_curso"],
        puntosAcumuladosSemestre: 5420,
        insignias: [
          "Fundador PREXIA UNAL",
          "Auditor Maestro POA 2026-2",
          "Articulación Internacional EISI"
        ],
        entregables: [
          {
            id: "ent-m1",
            semana: 1,
            titulo: "Firma de Pactos HSA 2026-2 con toda la cohorte",
            tipo: "Gobernanza",
            estado: "Aprobado"
          },
          {
            id: "ent-m2",
            semana: 4,
            titulo: "Auditoría Quincenal 2 y Cuadro de Honor Bienestar",
            tipo: "Auditoría",
            estado: "Aprobado"
          }
        ],
        historialQuincenal: [
          { semana: 1, basePP: 800, metaPP: 800, bonoPct: 23, finalPP: 984, cumplimiento: 123 },
          { semana: 2, basePP: 800, metaPP: 808, bonoPct: 23, finalPP: 984, cumplimiento: 122 },
          { semana: 4, basePP: 800, metaPP: 824, bonoPct: 23, finalPP: 984, cumplimiento: 119 },
          { semana: 6, basePP: 800, metaPP: 840, bonoPct: 23, finalPP: 984, cumplimiento: 117 }
        ],
        bitacoraCrecimiento: [
          { fecha: "2026-08-01", evento: "Configuración inicial del Plan de Acción 2026-2 y matriz de Puntos Prexia." }
        ]
      },
      {
        id: "usr-ana",
        username: "ana",
        password: "123",
        nombre: "Ana Sofía Restrepo",
        email: "asrestrepo@unal.edu.co",
        rolSistema: "estudiante",
        cargo: "Encargada de Redes y Cápsulas",
        carrera: "Ingeniería Industrial",
        linea: "PREXIA Consultoría · Apoyo Conecta",
        avatar: "AR",
        nivel: 1,
        semestre: 2,
        creditosAprobados: 32,
        creditosTotales: 172,
        materiasAltoImpacto: true,
        detalleMaterias: "Cálculo Integral, Álgebra Lineal, Física Mecánica",
        hsa: 5,
        multiplicadoresActivos: ["n1_contenido", "n1_valor"],
        puntosAcumuladosSemestre: 1595,
        insignias: [
          "Excelencia en Contenido Sem. 1",
          "Generadora de Cápsulas POA",
          "Pertenencia Nivel 1"
        ],
        entregables: [
          {
            id: "ent-a1",
            semana: 1,
            titulo: "Calendario de publicaciones 100% al día sin retrasos",
            tipo: "Multiplicador +3%",
            estado: "Aprobado"
          },
          {
            id: "ent-a2",
            semana: 4,
            titulo: "2 cápsulas de conocimiento recopiladas y editadas",
            tipo: "Multiplicador +4%",
            estado: "Aprobado"
          },
          {
            id: "ent-a3",
            semana: 6,
            titulo: "Infografía sobre Cultura de un Consultor Prexia",
            tipo: "Multiplicador +2%",
            estado: "En revisión"
          }
        ],
        historialQuincenal: [
          { semana: 1, basePP: 500, metaPP: 500, bonoPct: 3, finalPP: 515, cumplimiento: 103 },
          { semana: 2, basePP: 500, metaPP: 505, bonoPct: 5, finalPP: 525, cumplimiento: 104 },
          { semana: 4, basePP: 500, metaPP: 515, bonoPct: 7, finalPP: 535, cumplimiento: 104 },
          { semana: 6, basePP: 500, metaPP: 525, bonoPct: 7, finalPP: 535, cumplimiento: 102 }
        ],
        bitacoraCrecimiento: [
          { fecha: "2026-08-05", evento: "Ingreso en Nivel 1 (Fundamentación · 18.6% avance curricular). Pacto de 5 HSA (500 PP base)." },
          { fecha: "2026-09-15", evento: "Acreditó bono de Generación de Valor (+4%) tras publicar su segunda cápsula técnica." }
        ]
      },
      {
        id: "usr-mateo",
        username: "mateo",
        password: "123",
        nombre: "Mateo Valencia Ríos",
        email: "mvalenciar@unal.edu.co",
        rolSistema: "estudiante",
        cargo: "Operativo de Logística y Eventos",
        carrera: "Ingeniería Administrativa",
        linea: "PREXIA Consultoría",
        avatar: "MV",
        nivel: 1,
        semestre: 3,
        creditosAprobados: 49,
        creditosTotales: 172,
        materiasAltoImpacto: true,
        detalleMaterias: "Cálculo en Varias Variables, Física de Electricidad y Magnetismo",
        hsa: 4,
        multiplicadoresActivos: ["n1_contenido", "n1_cultura"],
        puntosAcumuladosSemestre: 1248,
        insignias: [
          "Rigor Operativo EISI",
          "Cultura Consultor"
        ],
        entregables: [
          {
            id: "ent-mt1",
            semana: 2,
            titulo: "Protocolo logístico de aulas M8B y Auditorio M3",
            tipo: "Operativo Nivel 1",
            estado: "Aprobado"
          },
          {
            id: "ent-mt2",
            semana: 6,
            titulo: "Pieza editorial sobre hábitos del consultor junior",
            tipo: "Multiplicador +2%",
            estado: "Aprobado"
          }
        ],
        historialQuincenal: [
          { semana: 1, basePP: 400, metaPP: 400, bonoPct: 3, finalPP: 412, cumplimiento: 103 },
          { semana: 2, basePP: 400, metaPP: 404, bonoPct: 3, finalPP: 412, cumplimiento: 102 },
          { semana: 4, basePP: 400, metaPP: 412, bonoPct: 5, finalPP: 420, cumplimiento: 102 },
          { semana: 6, basePP: 400, metaPP: 420, bonoPct: 5, finalPP: 420, cumplimiento: 100 }
        ],
        bitacoraCrecimiento: [
          { fecha: "2026-08-05", evento: "Ubicado en Nivel 1 (28.5% avance curricular). A solo 4 créditos de ascender a Nivel 2 (Gestor)." }
        ]
      },
      {
        id: "usr-camila",
        username: "camila",
        password: "123",
        nombre: "Camila Mejía Botero",
        email: "cmejiab@unal.edu.co",
        rolSistema: "estudiante",
        cargo: "Gestora de Bienestar y Tracción Digital",
        carrera: "Ingeniería Administrativa",
        linea: "PREXIA Consultoría · Proyecto 3 Bienestar",
        avatar: "CM",
        nivel: 2,
        semestre: 5,
        creditosAprobados: 82,
        creditosTotales: 172,
        materiasAltoImpacto: false,
        detalleMaterias: "Ingeniería Económica, Estadística II, Marketing Organizacional",
        hsa: 6,
        multiplicadoresActivos: ["n2_traccion", "n2_convocatoria", "n2_bienestar"],
        puntosAcumuladosSemestre: 1998,
        insignias: [
          "Ascenso a Gestora Nivel 2",
          "Tracción Digital +15%",
          "Embajadora de Bienestar 100%"
        ],
        entregables: [
          {
            id: "ent-c1",
            semana: 2,
            titulo: "Crecimiento del 18.4% en alcance orgánico de la línea",
            tipo: "Multiplicador +5%",
            estado: "Aprobado"
          },
          {
            id: "ent-c2",
            semana: 4,
            titulo: "Integración semestral con 78% de asistencia efectiva",
            tipo: "Multiplicador +4%",
            estado: "Aprobado"
          },
          {
            id: "ent-c3",
            semana: 6,
            titulo: "Reconocimientos individuales quincenales al 100%",
            tipo: "Multiplicador +2%",
            estado: "Aprobado"
          }
        ],
        historialQuincenal: [
          { semana: 1, basePP: 600, metaPP: 600, bonoPct: 6, finalPP: 636, cumplimiento: 106 },
          { semana: 2, basePP: 600, metaPP: 606, bonoPct: 9, finalPP: 654, cumplimiento: 108 },
          { semana: 4, basePP: 600, metaPP: 618, bonoPct: 11, finalPP: 666, cumplimiento: 108 },
          { semana: 6, basePP: 600, metaPP: 630, bonoPct: 11, finalPP: 666, cumplimiento: 106 }
        ],
        bitacoraCrecimiento: [
          { fecha: "2026-02-10", evento: "Ingresó como Nivel 1 Operativo en 2026-1." },
          { fecha: "2026-08-02", evento: "Ascendió a Nivel 2 (Transición · Rol Gestor) al superar el 31% de créditos aprobados (47.7%)." }
        ]
      },
      {
        id: "usr-santiago",
        username: "santiago",
        password: "123",
        nombre: "Santiago Gómez Arango",
        email: "sgomeza@unal.edu.co",
        rolSistema: "estudiante",
        cargo: "Gestor de Simulaciones Comerciales y Web",
        carrera: "Ingeniería Industrial",
        linea: "PREXIA Consultoría · Emprende",
        avatar: "SG",
        nivel: 2,
        semestre: 6,
        creditosAprobados: 101,
        creditosTotales: 172,
        materiasAltoImpacto: false,
        detalleMaterias: "Investigación de Operaciones, Gestión Tecnológica, Costos",
        hsa: 5,
        multiplicadoresActivos: ["n2_traccion", "n2_convocatoria"],
        puntosAcumuladosSemestre: 1635,
        insignias: [
          "Poder de Convocatoria (>70%)",
          "Arquitecto Web PREXIA"
        ],
        entregables: [
          {
            id: "ent-s1",
            semana: 3,
            titulo: "Simulación comercial B2B para portafolio de consultoría",
            tipo: "Proyecto Nivel 2",
            estado: "Aprobado"
          },
          {
            id: "ent-s2",
            semana: 6,
            titulo: "Convocatoria plenaria VI EISI con 74% de participación",
            tipo: "Multiplicador +4%",
            estado: "Aprobado"
          }
        ],
        historialQuincenal: [
          { semana: 1, basePP: 500, metaPP: 500, bonoPct: 5, finalPP: 525, cumplimiento: 105 },
          { semana: 2, basePP: 500, metaPP: 505, bonoPct: 5, finalPP: 525, cumplimiento: 104 },
          { semana: 4, basePP: 500, metaPP: 515, bonoPct: 9, finalPP: 545, cumplimiento: 106 },
          { semana: 6, basePP: 500, metaPP: 525, bonoPct: 9, finalPP: 545, cumplimiento: 104 }
        ],
        bitacoraCrecimiento: [
          { fecha: "2026-08-05", evento: "Nivel 2 consolidado (58.7% de avance curricular). Candidato directo a Nivel 3 Consultor Junior." }
        ]
      },
      {
        id: "usr-carlos",
        username: "carlos",
        password: "123",
        nombre: "Carlos Alberto Martínez",
        email: "camartinez@unal.edu.co",
        rolSistema: "estudiante",
        cargo: "Consultor Junior · Líder Técnico de Diagnóstico",
        carrera: "Ingeniería Industrial",
        linea: "PREXIA Consultoría",
        avatar: "CA",
        nivel: 3,
        semestre: 8,
        creditosAprobados: 132,
        creditosTotales: 172,
        materiasAltoImpacto: false,
        detalleMaterias: "Ingeniería de Métodos, Simulación Discreta, Consultoría Organizacional",
        hsa: 8,
        multiplicadoresActivos: ["n3_analitica", "n3_curricular", "n3_productividad"],
        puntosAcumuladosSemestre: 2760,
        insignias: [
          "Efectividad Analítica Impecable (+6%)",
          "Diseñador Curricular con Datos Reales",
          "Productividad Extra +4% Línea",
          "Cuadro de Honor POA"
        ],
        entregables: [
          {
            id: "ent-ca1",
            semana: 1,
            titulo: "Informe final de diagnóstico MiPyme entregado con calidad impecable",
            tipo: "Multiplicador +6%",
            estado: "Aprobado"
          },
          {
            id: "ent-ca2",
            semana: 4,
            titulo: "Caso de simulación con datos reales del sector manufacturero",
            tipo: "Multiplicador +5%",
            estado: "Aprobado"
          },
          {
            id: "ent-ca3",
            semana: 6,
            titulo: "Vinculación de emprendimiento adicional sobre la cuota pactada",
            tipo: "Multiplicador +4%",
            estado: "Aprobado"
          }
        ],
        historialQuincenal: [
          { semana: 1, basePP: 800, metaPP: 800, bonoPct: 6, finalPP: 848, cumplimiento: 106 },
          { semana: 2, basePP: 800, metaPP: 808, bonoPct: 11, finalPP: 888, cumplimiento: 110 },
          { semana: 4, basePP: 800, metaPP: 824, bonoPct: 15, finalPP: 920, cumplimiento: 112 },
          { semana: 6, basePP: 800, metaPP: 840, bonoPct: 15, finalPP: 920, cumplimiento: 110 }
        ],
        bitacoraCrecimiento: [
          { fecha: "2025-08-10", evento: "Ascendió de Nivel 2 (Gestor) a Nivel 3 (Consultor Junior) al superar el 61% de la carrera." },
          { fecha: "2026-08-12", evento: "Caso testigo Semana 1: 8 HSA (800 PP base) + 6% Efectividad Analítica = 848 PP (106% cumplimiento)." },
          { fecha: "2026-10-01", evento: "Completó los 3 multiplicadores de Nivel 3 (+15% total = 920 PP semanales)." }
        ]
      },
      {
        id: "usr-valentina",
        username: "valentina",
        password: "123",
        nombre: "Valentina Salazar Cano",
        email: "vsalazarc@unal.edu.co",
        rolSistema: "estudiante",
        cargo: "Consultora Junior · Analítica y Datos Reales",
        carrera: "Ingeniería de Sistemas e Informática",
        linea: "PREXIA Consultoría · Investiga",
        avatar: "VS",
        nivel: 3,
        semestre: 9,
        creditosAprobados: 144,
        creditosTotales: 172,
        materiasAltoImpacto: false,
        detalleMaterias: "Ciencia de Datos Aplicada, Arquitectura de Software, Finanzas",
        hsa: 6,
        multiplicadoresActivos: ["n3_analitica", "n3_curricular"],
        puntosAcumuladosSemestre: 1998,
        insignias: [
          "Efectividad Analítica (+6%)",
          "Simulación Sectorial Real"
        ],
        entregables: [
          {
            id: "ent-v1",
            semana: 2,
            titulo: "Tablero de indicadores financieros para empresa aliada",
            tipo: "Multiplicador +6%",
            estado: "Aprobado"
          },
          {
            id: "ent-v2",
            semana: 5,
            titulo: "Repositorio de datasets reales anonimizados para el curso de consultoría",
            tipo: "Multiplicador +5%",
            estado: "Aprobado"
          }
        ],
        historialQuincenal: [
          { semana: 1, basePP: 600, metaPP: 600, bonoPct: 6, finalPP: 636, cumplimiento: 106 },
          { semana: 2, basePP: 600, metaPP: 606, bonoPct: 6, finalPP: 636, cumplimiento: 105 },
          { semana: 4, basePP: 600, metaPP: 618, bonoPct: 11, finalPP: 666, cumplimiento: 108 },
          { semana: 6, basePP: 600, metaPP: 630, bonoPct: 11, finalPP: 666, cumplimiento: 106 }
        ],
        bitacoraCrecimiento: [
          { fecha: "2026-08-05", evento: "Ubicada en Nivel 3 (83.7% de avance curricular). A solo 4 créditos de ascender a Nivel 4 (Líder)." }
        ]
      },
      {
        id: "usr-laura",
        username: "laura",
        password: "123",
        nombre: "Laura Gaviria Londoño",
        email: "lgavirial@unal.edu.co",
        rolSistema: "estudiante",
        cargo: "Líder de Línea Consultoría y Negociación",
        carrera: "Ingeniería Industrial",
        linea: "PREXIA Consultoría (Liderazgo)",
        avatar: "LG",
        nivel: 4,
        semestre: 10,
        creditosAprobados: 159,
        creditosTotales: 172,
        materiasAltoImpacto: false,
        detalleMaterias: "Trabajo de Grado, Gerencia Estratégica",
        hsa: 6,
        multiplicadoresActivos: ["n4_impacto", "n4_relaciones", "n4_curso"],
        puntosAcumuladosSemestre: 2214,
        insignias: [
          "Líder Nivel 4 · Legado PREXIA",
          "Impacto Económico (+10%)",
          "Relaciones Públicas Internacionales (+8%)",
          "Mentora Senior de Consultores"
        ],
        entregables: [
          {
            id: "ent-l1",
            semana: 2,
            titulo: "Acuerdo de retribución sobre utilidades firmado con MiPyme del Valle de Aburrá",
            tipo: "Multiplicador +10%",
            estado: "Aprobado"
          },
          {
            id: "ent-l2",
            semana: 4,
            titulo: "Vinculación de 6 expertos externos (UNAL / UNESP / Industria) al curso",
            tipo: "Multiplicador +8%",
            estado: "Aprobado"
          },
          {
            id: "ent-l3",
            semana: 6,
            titulo: "Seguimiento de cohorte: 88% de permanencia activa en el curso de consultoría",
            tipo: "Multiplicador +5%",
            estado: "Aprobado"
          }
        ],
        historialQuincenal: [
          { semana: 1, basePP: 600, metaPP: 600, bonoPct: 10, finalPP: 660, cumplimiento: 110 },
          { semana: 2, basePP: 600, metaPP: 606, bonoPct: 18, finalPP: 708, cumplimiento: 117 },
          { semana: 4, basePP: 600, metaPP: 618, bonoPct: 23, finalPP: 738, cumplimiento: 119 },
          { semana: 6, basePP: 600, metaPP: 630, bonoPct: 23, finalPP: 738, cumplimiento: 117 }
        ],
        bitacoraCrecimiento: [
          { fecha: "2024-08-01", evento: "Recorrió Nivel 2 y Nivel 3 liderando diagnósticos empresariales." },
          { fecha: "2026-08-01", evento: "Promovida a Nivel 4 (Cierre y Proyección · 92.4% de carrera). Mentora general de la línea." }
        ]
      },
      {
        id: "usr-andres",
        username: "andres",
        password: "123",
        nombre: "Andrés Felipe Ochoa",
        email: "afochoa@unal.edu.co",
        rolSistema: "estudiante",
        cargo: "Líder de Relaciones Públicas y Expertos Externos",
        carrera: "Ingeniería Administrativa",
        linea: "PREXIA Consultoría · Alianzas EISI",
        avatar: "AO",
        nivel: 4,
        semestre: 10,
        creditosAprobados: 165,
        creditosTotales: 172,
        materiasAltoImpacto: false,
        detalleMaterias: "Práctica Profesional / Proyecto de Grado",
        hsa: 4,
        multiplicadoresActivos: ["n4_impacto", "n4_relaciones"],
        puntosAcumuladosSemestre: 1416,
        insignias: [
          "Líder Nivel 4",
          "Embajador Coorganizador Brasil-Colombia",
          "Impacto Económico (+10%)"
        ],
        entregables: [
          {
            id: "ent-ao1",
            semana: 3,
            titulo: "Convenio con 7 conferencistas invitados y expertos sectoriales",
            tipo: "Multiplicador +8%",
            estado: "Aprobado"
          },
          {
            id: "ent-ao2",
            semana: 5,
            titulo: "Cierre de negociación de retribución con emprendimiento asesorado",
            tipo: "Multiplicador +10%",
            estado: "Aprobado"
          }
        ],
        historialQuincenal: [
          { semana: 1, basePP: 400, metaPP: 400, bonoPct: 8, finalPP: 432, cumplimiento: 108 },
          { semana: 2, basePP: 400, metaPP: 404, bonoPct: 18, finalPP: 472, cumplimiento: 117 },
          { semana: 4, basePP: 400, metaPP: 412, bonoPct: 18, finalPP: 472, cumplimiento: 115 },
          { semana: 6, basePP: 400, metaPP: 420, bonoPct: 18, finalPP: 472, cumplimiento: 112 }
        ],
        bitacoraCrecimiento: [
          { fecha: "2026-08-01", evento: "Nivel 4 (95.9% de avance curricular). Caso testigo de cierre de semestre con 4 HSA y +18% de multiplicador (472 PP)." }
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
      const found = LEVELS_CONFIG[lvl].multiplicadores.find((m) => m.id === multId);
      if (found) return { ...found, nivel: lvl };
    }
    return null;
  }

  function calcularLiquidacionUsuario(user, semanaEval) {
    const semana = Math.min(16, Math.max(1, parseInt(semanaEval || 1, 10)));
    const hsa = Math.max(1, parseInt(user.hsa || 4, 10));
    const basePP = hsa * 100;
    const curvaPct = 100 + (semana - 1); // Sem 1 = 100%, Sem 16 = 115%
    const metaSemanaPP = Math.round(basePP * (curvaPct / 100));

    const levelCfg = LEVELS_CONFIG[user.nivel] || LEVELS_CONFIG[1];
    let bonoPct = 0;
    const multDetalles = [];

    (user.multiplicadoresActivos || []).forEach((mId) => {
      const mInfo = levelCfg.multiplicadores.find((m) => m.id === mId) || obtenerMultiplicadorInfo(mId);
      if (mInfo) {
        bonoPct += mInfo.bono;
        multDetalles.push(mInfo);
      }
    });

    const bonoPP = Math.round(basePP * (bonoPct / 100));
    const finalPP = basePP + bonoPP;
    const cumplimientoPct = Math.round((finalPP / metaSemanaPP) * 100);
    const superoMeta = finalPP >= metaSemanaPP;
    const brechaPP = metaSemanaPP - finalPP;
    const avanceCarreraPct = Math.min(100, Math.round(((user.creditosAprobados || 0) / (user.creditosTotales || 172)) * 100));

    return {
      semana,
      hsa,
      basePP,
      curvaPct,
      metaSemanaPP,
      bonoPct,
      bonoPP,
      finalPP,
      cumplimientoPct,
      superoMeta,
      brechaPP,
      avanceCarreraPct,
      levelCfg,
      multDetalles
    };
  }

  function getDB() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && Array.isArray(parsed.usuarios)) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn("No se pudo leer localStorage:", e);
    }
    const initial = clone(DEFAULT_DB);
    saveDB(initial, "Inicialización del sistema", false);
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
      lastGitSync: "2026-10-17T14:40:00-05:00",
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
      if (!res.ok) return null;
      const remoteDB = await res.json();
      const syncMeta = getGitSyncMeta();
      // Solo sobreescribir si no hay cambios locales pendientes
      if ((syncMeta.pendingChanges || 0) === 0 && remoteDB && Array.isArray(remoteDB.usuarios)) {
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
    saveDB(fresh, "Restauración a estado base del repositorio Git", false);
    markGitSynced("Estado oficial restaurado");
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

  // ── ACCIONES DE PROGRESO Y CRECIMIENTO ──
  function registrarSnapshotHistorial(user, semana) {
    const liq = calcularLiquidacionUsuario(user, semana);
    user.historialQuincenal = user.historialQuincenal || [];
    const idx = user.historialQuincenal.findIndex((h) => h.semana === semana);
    const entry = {
      semana,
      basePP: liq.basePP,
      metaPP: liq.metaSemanaPP,
      bonoPct: liq.bonoPct,
      finalPP: liq.finalPP,
      cumplimiento: liq.cumplimientoPct
    };
    if (idx >= 0) {
      user.historialQuincenal[idx] = entry;
    } else {
      user.historialQuincenal.push(entry);
      user.historialQuincenal.sort((a, b) => a.semana - b.semana);
    }
  }

  function toggleMultiplicador(userId, multId) {
    const db = getDB();
    const user = db.usuarios.find((u) => u.id === userId);
    if (!user) return null;

    user.multiplicadoresActivos = user.multiplicadoresActivos || [];
    const exists = user.multiplicadoresActivos.includes(multId);
    const mInfo = obtenerMultiplicadorInfo(multId);

    if (exists) {
      user.multiplicadoresActivos = user.multiplicadoresActivos.filter((id) => id !== multId);
    } else {
      user.multiplicadoresActivos.push(multId);
      const badgeName = mInfo ? `${mInfo.nombre} (+${mInfo.bono}%)` : multId;
      if (!user.insignias.includes(badgeName)) {
        user.insignias.push(badgeName);
      }
      user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
      user.bitacoraCrecimiento.unshift({
        fecha: new Date().toISOString().slice(0, 10),
        evento: `Multiplicador acreditado en Semana ${db.meta.semanaActual}: ${mInfo ? mInfo.nombre : multId} (+${mInfo ? mInfo.bono : 0}%).`
      });
    }

    registrarSnapshotHistorial(user, db.meta.semanaActual);
    saveDB(db, `Multiplicador ${exists ? "removido" : "acreditado"} para ${user.nombre}`);
    return user;
  }

  function actualizarPactoHSA(userId, nuevasHSA) {
    const db = getDB();
    const user = db.usuarios.find((u) => u.id === userId);
    if (!user) return null;

    const hsa = Math.min(12, Math.max(1, parseInt(nuevasHSA || 4, 10)));
    user.hsa = hsa;
    user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
    user.bitacoraCrecimiento.unshift({
      fecha: new Date().toISOString().slice(0, 10),
      evento: `Actualización de Pacto HSA: ${hsa} horas semanales (${hsa * 100} PP base).`
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

    const liqAntes = calcularLiquidacionUsuario(user, db.meta.semanaActual);
    user.puntosAcumuladosSemestre = (user.puntosAcumuladosSemestre || 0) + liqAntes.finalPP;

    if (user.nivel > nivelAnterior) {
      const cfgNuevo = LEVELS_CONFIG[user.nivel];
      user.cargo = `${cfgNuevo.rol} · ${cfgNuevo.nombre}`;
      // Activar el primer multiplicador del nuevo nivel para arrancar con impulso
      const primerMult = cfgNuevo.multiplicadores[0].id;
      user.multiplicadoresActivos = [primerMult];
      const insigniaAscenso = `Ascenso a Nivel ${user.nivel}: ${cfgNuevo.rol}`;
      if (!user.insignias.includes(insigniaAscenso)) {
        user.insignias.push(insigniaAscenso);
      }
      user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
      user.bitacoraCrecimiento.unshift({
        fecha: new Date().toISOString().slice(0, 10),
        evento: `¡ASCENSO DE NIVEL! Promovido de Nivel ${nivelAnterior} a Nivel ${user.nivel} (${cfgNuevo.nombre} · Rol ${cfgNuevo.rol}) con ${user.creditosAprobados}/${user.creditosTotales} créditos (${Math.round((user.creditosAprobados / user.creditosTotales) * 100)}%).`
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

    const nuevo = {
      id: "ent-" + Date.now(),
      semana: db.meta.semanaActual,
      titulo: datosEntregable.titulo || "Entregable de línea PREXIA",
      tipo: datosEntregable.tipo || `Entregable Nivel ${user.nivel}`,
      estado: datosEntregable.estado || "Aprobado"
    };

    user.entregables = user.entregables || [];
    user.entregables.unshift(nuevo);

    if (datosEntregable.multId && !user.multiplicadoresActivos.includes(datosEntregable.multId)) {
      user.multiplicadoresActivos.push(datosEntregable.multId);
      const mInfo = obtenerMultiplicadorInfo(datosEntregable.multId);
      if (mInfo) {
        const badge = `${mInfo.nombre} (+${mInfo.bono}%)`;
        if (!user.insignias.includes(badge)) user.insignias.push(badge);
      }
    }

    if (datosEntregable.insigniaExtra && !user.insignias.includes(datosEntregable.insigniaExtra)) {
      user.insignias.push(datosEntregable.insigniaExtra);
    }

    const liq = calcularLiquidacionUsuario(user, db.meta.semanaActual);
    user.puntosAcumuladosSemestre = (user.puntosAcumuladosSemestre || 0) + Math.round(liq.finalPP * 0.25);

    user.bitacoraCrecimiento = user.bitacoraCrecimiento || [];
    user.bitacoraCrecimiento.unshift({
      fecha: new Date().toISOString().slice(0, 10),
      evento: `Nuevo entregable registrado en Semana ${db.meta.semanaActual}: "${nuevo.titulo}" (${nuevo.estado}).`
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
      if (sem > 1) {
        const liq = calcularLiquidacionUsuario(u, sem);
        // Asegurar acumulado coherente
        const sumaHistorial = (u.historialQuincenal || []).reduce((acc, item) => acc + (item.finalPP || 0), 0);
        if (sumaHistorial > (u.puntosAcumuladosSemestre || 0)) {
          u.puntosAcumuladosSemestre = sumaHistorial;
        }
      }
    });

    saveDB(db, `Corte del sistema avanzado a Semana ${sem} (Meta progresiva ${100 + sem - 1}%)`);
    return db;
  }

  function crearNuevoUsuario(datos) {
    const db = getDB();
    const nombre = (datos.nombre || "Nuevo Integrante PREXIA").trim();
    const username = (datos.username || nombre.split(" ")[0].toLowerCase().replace(/[^a-z0-9]/g, "") + Math.floor(Math.random() * 90 + 10)).trim();
    const creditosTotales = 172;
    const creditosAprobados = Math.min(172, Math.max(5, parseInt(datos.creditosAprobados || 25, 10)));
    const nivel = datos.nivelForzado ? parseInt(datos.nivelForzado, 10) : calcularNivelPorCreditos(creditosAprobados, creditosTotales);
    const semestre = Math.min(10, Math.max(1, parseInt(datos.semestre || Math.ceil((creditosAprobados / creditosTotales) * 10), 10)));
    const hsa = Math.min(12, Math.max(1, parseInt(datos.hsa || 4, 10)));
    const cfg = LEVELS_CONFIG[nivel];

    const partes = nombre.split(" ");
    const avatar = ((partes[0] ? partes[0][0] : "P") + (partes[1] ? partes[1][0] : "X")).toUpperCase();
    const primerMult = cfg.multiplicadores[0].id;

    const nuevoUser = {
      id: "usr-" + username + "-" + Date.now().toString().slice(-4),
      username,
      password: datos.password || "123",
      nombre,
      email: datos.email || `${username}@unal.edu.co`,
      rolSistema: datos.rolSistema || "estudiante",
      cargo: datos.cargo || `${cfg.rol} · ${cfg.nombre}`,
      carrera: datos.carrera || "Ingeniería Industrial",
      linea: datos.linea || "PREXIA Consultoría",
      avatar,
      nivel,
      semestre,
      creditosAprobados,
      creditosTotales,
      materiasAltoImpacto: nivel === 1,
      detalleMaterias: nivel === 1 ? "Cálculo, Álgebra Lineal y Física" : "Asignaturas profesionales de ingeniería",
      hsa,
      multiplicadoresActivos: [primerMult],
      puntosAcumuladosSemestre: hsa * 100,
      insignias: [`Ingreso Nivel ${nivel} (${cfg.rol})`],
      entregables: [
        {
          id: "ent-init-" + Date.now(),
          semana: db.meta.semanaActual,
          titulo: `Firma de Pacto Inicial (${hsa} HSA = ${hsa * 100} PP base)`,
          tipo: "Pacto POA",
          estado: "Aprobado"
        }
      ],
      historialQuincenal: [],
      bitacoraCrecimiento: [
        {
          fecha: new Date().toISOString().slice(0, 10),
          evento: `Integrante vinculado en Nivel ${nivel} (${cfg.nombre} · Rol ${cfg.rol}) con ${creditosAprobados}/${creditosTotales} créditos y pacto de ${hsa} HSA.`
        }
      ]
    };

    registrarSnapshotHistorial(nuevoUser, db.meta.semanaActual);
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

    // 1. Obtener SHA actual del archivo si existe
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

    // 2. Codificar JSON en Base64 UTF-8
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
    saveDB(parsed, "Base de datos importada desde archivo JSON", true);
    return parsed;
  }

  window.PrexiaDB = {
    LEVELS_CONFIG,
    getDB,
    saveDB,
    getGitSyncMeta,
    markGitSynced,
    syncFromCanonicalJSON,
    resetToFactoryGitDB,
    calcularNivelPorCreditos,
    calcularLiquidacionUsuario,
    obtenerMultiplicadorInfo,
    getCurrentUser,
    login,
    logout,
    toggleMultiplicador,
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
