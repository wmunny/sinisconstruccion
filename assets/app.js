/* ============================================================
   Dashboard Premium - logica de navegacion
   - Definicion de informes (ruta recomendada)
   - Routing por hash (#slug) para enlaces compartibles
   - Carga en iframe con estado de carga
   - Toggle de tema claro/oscuro persistente
   ============================================================ */

const REPORTS = [
  {
    slug: "informe-final",
    num: 1,
    badge: "Abrir primero",
    title: "Informe final",
    desc: "Lectura ejecutiva: metodologia, hallazgos, focos de riesgo y limites.",
    file: "reports/informe_final.html",
  },
  {
    slug: "historico",
    num: 2,
    badge: "Profundidad visual",
    title: "Historico 2008-2025",
    desc: "Graficas de evolucion: incidencia, accidentes, mortalidad, afiliacion, vivienda, Euribor y EIPIC.",
    file: "reports/historico_2008_2025.html",
  },
  {
    slug: "evolucion-normalizada",
    num: 3,
    badge: "Lectura temporal",
    title: "Evolucion normalizada",
    desc: "Accidentes y mortales normalizados por viviendas iniciadas a lo largo del tiempo.",
    file: "reports/cruce_analisis.html",
  },
  {
    slug: "formas-mortales",
    num: 4,
    badge: "Estrategia",
    title: "Formas mortales",
    desc: "Tipos de accidente mortal por forma y estrategias preventivas asociadas.",
    file: "reports/formas_mortales.html",
  },
  {
    slug: "calor-pnt",
    num: 5,
    badge: "Hipotesis calor",
    title: "Calor y PNT",
    desc: "Analisis mensual de patologias no traumaticas y meses calidos.",
    file: "reports/calor_pnt.html",
  },
  {
    slug: "simulacion",
    num: 6,
    badge: "Escenarios",
    title: "Simulacion 2026-2030",
    desc: "Proyeccion por regresion, ratios normalizados y conclusiones de sostenibilidad preventiva.",
    file: "reports/simulacion_5_anios.html",
  },
  {
    slug: "modelo",
    num: 7,
    badge: "Modelo",
    title: "Modelo predictivo",
    desc: "Primer modelo predictivo exploratorio con predicciones y errores por ano.",
    file: "reports/modelo_simple.html",
  },
];

const bySlug = (slug) => REPORTS.find((r) => r.slug === slug);

/* ---------------- Elementos ---------------- */
const el = {
  navList: document.getElementById("nav-list"),
  cards: document.getElementById("cards"),
  overview: document.getElementById("view-overview"),
  viewer: document.getElementById("view-report"),
  frame: document.getElementById("report-frame"),
  loader: document.getElementById("loader"),
  crumbTitle: document.getElementById("crumb-title"),
  headerTitle: document.getElementById("header-title"),
  headerSub: document.getElementById("header-sub"),
  openNew: document.getElementById("open-new"),
  fullscreen: document.getElementById("fullscreen"),
  themeToggle: document.getElementById("theme-toggle"),
  menuToggle: document.getElementById("menu-toggle"),
  sidebar: document.getElementById("sidebar"),
  backdrop: document.getElementById("backdrop"),
};

/* ---------------- Construir navegacion y tarjetas ---------------- */
function buildNav() {
  el.navList.innerHTML = "";
  el.cards.innerHTML = "";

  // Item de inicio / resumen
  const home = document.createElement("button");
  home.className = "nav-item";
  home.dataset.slug = "resumen";
  home.innerHTML = `
    <span class="nav-item__num">&#9632;</span>
    <span class="nav-item__body">
      <span class="nav-item__title">Resumen</span>
      <span class="nav-item__desc">Vista general y KPIs del proyecto</span>
    </span>`;
  home.addEventListener("click", () => navigate("resumen"));
  el.navList.appendChild(home);

  REPORTS.forEach((r) => {
    const btn = document.createElement("button");
    btn.className = "nav-item";
    btn.dataset.slug = r.slug;
    btn.innerHTML = `
      <span class="nav-item__num">${r.num}</span>
      <span class="nav-item__body">
        <span class="nav-item__title">${r.title}</span>
        <span class="nav-item__desc">${r.desc}</span>
      </span>`;
    btn.addEventListener("click", () => navigate(r.slug));
    el.navList.appendChild(btn);

    const card = document.createElement("button");
    card.className = "card";
    card.innerHTML = `
      <span class="card__badge">${r.badge}</span>
      <span class="card__num">Paso ${r.num}</span>
      <h3>${r.title}</h3>
      <p>${r.desc}</p>
      <span class="card__cta">Abrir informe</span>`;
    card.addEventListener("click", () => navigate(r.slug));
    el.cards.appendChild(card);
  });
}

/* ---------------- Navegacion ---------------- */
function setActive(slug) {
  document.querySelectorAll(".nav-item").forEach((n) => {
    n.classList.toggle("is-active", n.dataset.slug === slug);
  });
}

function showOverview() {
  el.overview.hidden = false;
  el.viewer.hidden = true;
  el.headerTitle.textContent = "Resumen del proyecto";
  el.headerSub.textContent = "Siniestralidad laboral en construccion (2008-2025)";
  setActive("resumen");
}

function showReport(report) {
  el.overview.hidden = true;
  el.viewer.hidden = false;
  el.loader.hidden = false;

  // Cargar solo si cambia la fuente
  if (el.frame.getAttribute("src") !== report.file) {
    el.frame.setAttribute("src", report.file);
  } else {
    el.loader.hidden = true;
  }

  el.crumbTitle.textContent = report.title;
  el.headerTitle.textContent = report.title;
  el.headerSub.textContent = report.desc;
  el.openNew.dataset.href = report.file;
  setActive(report.slug);
}

function navigate(slug) {
  if (slug && slug !== "resumen" && `#${slug}` !== location.hash) {
    location.hash = slug;
    return; // hashchange se encarga de renderizar
  }
  if (slug === "resumen" && location.hash) {
    location.hash = "";
    return;
  }
  render();
  closeMenu();
}

function render() {
  const slug = location.hash.replace(/^#/, "");
  const report = bySlug(slug);
  if (report) {
    showReport(report);
  } else {
    showOverview();
  }
}

/* ---------------- Iframe: fin de carga ---------------- */
el.frame.addEventListener("load", () => {
  el.loader.hidden = true;
});

/* ---------------- Acciones del visor ---------------- */
el.openNew.addEventListener("click", () => {
  const href = el.openNew.dataset.href;
  if (href) window.open(href, "_blank", "noopener");
});

el.fullscreen.addEventListener("click", () => {
  const wrap = el.frame.parentElement;
  if (!document.fullscreenElement) {
    (wrap.requestFullscreen || wrap.webkitRequestFullscreen)?.call(wrap);
  } else {
    document.exitFullscreen?.();
  }
});

/* ---------------- Tema claro/oscuro ---------------- */
const THEME_KEY = "atr-dashboard-theme";

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const isDark = theme === "dark";
  el.themeToggle.setAttribute("aria-pressed", String(isDark));
  el.themeToggle.querySelector(".theme-label").textContent = isDark ? "Claro" : "Oscuro";
  el.themeToggle.querySelector(".theme-sun").hidden = isDark;
  el.themeToggle.querySelector(".theme-moon").hidden = !isDark;
}

function initTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
  applyTheme(stored || (prefersDark ? "dark" : "light"));
}

el.themeToggle.addEventListener("click", () => {
  const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
  localStorage.setItem(THEME_KEY, next);
  applyTheme(next);
});

/* ---------------- Menu movil ---------------- */
function openMenu() {
  el.sidebar.classList.add("is-open");
  el.backdrop.classList.add("is-open");
}
function closeMenu() {
  el.sidebar.classList.remove("is-open");
  el.backdrop.classList.remove("is-open");
}
el.menuToggle.addEventListener("click", openMenu);
el.backdrop.addEventListener("click", closeMenu);

/* ---------------- Init ---------------- */
window.addEventListener("hashchange", () => { render(); closeMenu(); });

initTheme();
buildNav();
render();
