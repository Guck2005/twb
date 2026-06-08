/* ===== DATA ===== */

const revision70 = [
  { q: "Une API est qualifi\u00e9e de RESTful lorsqu'elle respecte :", options: ["L'utilisation obligatoire de JSON", "Les contraintes architecturales de Roy Fielding (stateless, uniform interface, cacheability...)", "L'usage exclusif de SOAP", "L'utilisation de GraphQL comme standard"], correct: 1, part: "REST & GraphQL" },
  { q: "Le principe REST \u00abstateless\u00bb signifie que :", options: ["Le serveur conserve l'\u00e9tat de session client", "Chaque requ\u00eate contient toutes les informations n\u00e9cessaires sans d\u00e9pendance serveur", "Les donn\u00e9es doivent \u00eatre mises en cache syst\u00e9matiquement", "Les requ\u00eates doivent \u00eatre synchrones"], correct: 1, part: "REST & GraphQL" },
  { q: "Une op\u00e9ration HTTP est dite idempotente lorsqu'elle :", options: ["Change toujours l'\u00e9tat du serveur", "Produit un r\u00e9sultat identique apr\u00e8s plusieurs ex\u00e9cutions identiques", "Est toujours ex\u00e9cut\u00e9e une seule fois", "Est asynchrone"], correct: 1, part: "REST & GraphQL" },
  { q: "Parmi les m\u00e9thodes suivantes, laquelle est strictement idempotente par conception ?", options: ["POST", "PATCH", "PUT", "CONNECT"], correct: 2, part: "REST & GraphQL" },
  { q: "La m\u00e9thode POST est principalement utilis\u00e9e pour :", options: ["R\u00e9cup\u00e9rer des donn\u00e9es", "Cr\u00e9er une nouvelle ressource sur le serveur", "Remplacer totalement une ressource existante", "Mettre en cache une r\u00e9ponse"], correct: 1, part: "REST & GraphQL" },
  { q: "PATCH est utilis\u00e9e dans une API REST pour :", options: ["Remplacer compl\u00e8tement une ressource", "Appliquer une modification partielle \u00e0 une ressource", "Supprimer une ressource", "Lister les ressources"], correct: 1, part: "REST & GraphQL" },
  { q: "Le principal probl\u00e8me que GraphQL cherche \u00e0 r\u00e9soudre est :", options: ["La consommation CPU \u00e9lev\u00e9e", "Le sur-fetching et sous-fetching des donn\u00e9es dans les API REST", "La lenteur des bases de donn\u00e9es", "Le stockage local des donn\u00e9es"], correct: 1, part: "REST & GraphQL" },
  { q: "Dans une architecture GraphQL, l'acc\u00e8s aux donn\u00e9es se fait g\u00e9n\u00e9ralement via :", options: ["Plusieurs endpoints REST", "Un endpoint unique HTTP", "Un socket TCP d\u00e9di\u00e9", "Un service FTP"], correct: 1, part: "REST & GraphQL" },
  { q: "Le schema GraphQL est utilis\u00e9 pour :", options: ["D\u00e9finir les tables SQL", "D\u00e9crire les types de donn\u00e9es et leurs relations accessibles \u00e0 l'API", "G\u00e9rer le cache HTTP", "Configurer le load balancing"], correct: 1, part: "REST & GraphQL" },
  { q: "Une contrainte fondamentale de REST est :", options: ["Stateful architecture", "Stateless architecture", "Couplage fort entre client et serveur", "Utilisation obligatoire de XML"], correct: 1, part: "REST & GraphQL" },
  { q: "La m\u00e9thode HTTP GET est consid\u00e9r\u00e9e comme :", options: ["Non idempotente", "Idempotente et sans effet de bord", "Toujours destructive", "Asynchrone uniquement"], correct: 1, part: "REST & GraphQL" },
  { q: "JWT (JSON Web Token) est principalement utilis\u00e9 pour :", options: ["Le stockage local des images", "L'authentification stateless entre client et serveur", "Le routage r\u00e9seau", "Le rendu UI"], correct: 1, part: "REST & GraphQL" },
  { q: "REST repose sur quel protocole principal ?", options: ["FTP", "HTTP", "SMTP", "UDP"], correct: 1, part: "REST & GraphQL" },
  { q: "GraphQL permet au client de :", options: ["D\u00e9finir dynamiquement les donn\u00e9es qu'il souhaite recevoir", "Modifier directement la base de donn\u00e9es", "Remplacer HTTP", "Acc\u00e9der uniquement \u00e0 des donn\u00e9es fixes"], correct: 0, part: "REST & GraphQL" },
  { q: "Une ressource REST est identifi\u00e9e de mani\u00e8re unique par :", options: ["Une classe Java", "Une URL (URI)", "Un objet m\u00e9moire", "Une table SQL"], correct: 1, part: "REST & GraphQL" },
  { q: "Le principe \u00abUniform Interface\u00bb signifie :", options: ["Une interface utilisateur unique", "Une standardisation des interactions client-serveur", "Une base de donn\u00e9es unique", "Un seul serveur backend"], correct: 1, part: "REST & GraphQL" },
  { q: "Cacheability en REST signifie :", options: ["Les r\u00e9ponses ne peuvent jamais \u00eatre mises en cache", "Les r\u00e9ponses peuvent \u00eatre stock\u00e9es pour am\u00e9liorer les performances", "Les donn\u00e9es sont toujours volatiles", "Le serveur doit \u00eatre stateful"], correct: 1, part: "REST & GraphQL" },
  { q: "Layered system implique :", options: ["Une architecture en couches ind\u00e9pendantes", "Une UI multi-\u00e9crans", "Un seul serveur monolithique", "Une base de donn\u00e9es unique"], correct: 0, part: "REST & GraphQL" },
  { q: "REST utilise principalement :", options: ["Les verbes HTTP standard", "Les sockets TCP", "Les fichiers locaux", "Les threads syst\u00e8me"], correct: 0, part: "REST & GraphQL" },
  { q: "GraphQL am\u00e9liore REST en :", options: ["For\u00e7ant plus de requ\u00eates r\u00e9seau", "Permettant une r\u00e9cup\u00e9ration optimis\u00e9e des donn\u00e9es", "Supprimant HTTP", "Rendant les API statiques"], correct: 1, part: "REST & GraphQL" },
  { q: "Flutter est bas\u00e9 sur le langage :", options: ["Java", "Dart", "Kotlin", "Swift"], correct: 1, part: "Flutter & Dart" },
  { q: "Dart est un langage :", options: ["Orient\u00e9 objet compil\u00e9", "Exclusivement fonctionnel", "SQL natif", "Assembleur"], correct: 0, part: "Flutter & Dart" },
  { q: "Un StatelessWidget est :", options: ["Un widget avec \u00e9tat dynamique", "Un widget immuable sans \u00e9tat interne", "Une base de donn\u00e9es UI", "Un service backend"], correct: 1, part: "Flutter & Dart" },
  { q: "Un StatefulWidget permet :", options: ["Aucune modification UI", "Une gestion dynamique de l'\u00e9tat", "Un acc\u00e8s direct au r\u00e9seau", "Une compilation native"], correct: 1, part: "Flutter & Dart" },
  { q: "Flutter utilise le moteur de rendu :", options: ["Skia", "Unity", "DirectX", "OpenGL ES uniquement"], correct: 0, part: "Flutter & Dart" },
  { q: "async/await en Dart permet :", options: ["De bloquer l'application", "De g\u00e9rer des op\u00e9rations asynchrones proprement", "De compiler plus vite", "De cr\u00e9er des widgets"], correct: 1, part: "Flutter & Dart" },
  { q: "Une Future en Dart repr\u00e9sente :", options: ["Une valeur d\u00e9j\u00e0 disponible", "Une valeur disponible ult\u00e9rieurement", "Un thread syst\u00e8me", "Un UI component"], correct: 1, part: "Flutter & Dart" },
  { q: "Stream en Dart repr\u00e9sente :", options: ["Un flux de donn\u00e9es asynchrone", "Une base de donn\u00e9es", "Une UI", "Un serveur"], correct: 0, part: "Flutter & Dart" },
  { q: "setState() sert \u00e0 :", options: ["Modifier la base de donn\u00e9es", "Rebuilder l'interface utilisateur", "Cr\u00e9er une API", "G\u00e9rer le routing"], correct: 1, part: "Flutter & Dart" },
  { q: "Flutter est une technologie :", options: ["Mobile uniquement Android", "Cross-platform", "Backend uniquement", "Desktop uniquement"], correct: 1, part: "Flutter & Dart" },
  { q: "Hot Reload permet :", options: ["Red\u00e9marrage complet du syst\u00e8me", "Mise \u00e0 jour instantan\u00e9e de l'UI", "Compilation lente", "Suppression du cache"], correct: 1, part: "Flutter & Dart" },
  { q: "Widget Flutter est :", options: ["Une donn\u00e9e backend", "Un \u00e9l\u00e9ment UI", "Une API", "Une base de donn\u00e9es"], correct: 1, part: "Flutter & Dart" },
  { q: "Dart supporte :", options: ["Programmation orient\u00e9e objet", "SQL runtime", "HTML natif", "Bash scripting"], correct: 0, part: "Flutter & Dart" },
  { q: "Flutter est d\u00e9velopp\u00e9 par :", options: ["Apple", "Google", "Microsoft", "Meta"], correct: 1, part: "Flutter & Dart" },
  { q: "BuildContext sert \u00e0 :", options: ["Acc\u00e9der \u00e0 la structure de l'arbre UI", "G\u00e9rer la base de donn\u00e9es", "Cr\u00e9er une API REST", "G\u00e9rer le r\u00e9seau"], correct: 0, part: "Flutter & Dart" },
  { q: "Widget tree repr\u00e9sente :", options: ["Une base SQL", "La hi\u00e9rarchie UI", "Un serveur backend", "Une API"], correct: 1, part: "Flutter & Dart" },
  { q: "Dart event loop permet :", options: ["Multithreading classique", "Gestion des t\u00e2ches asynchrones", "UI rendering uniquement", "DB indexing"], correct: 1, part: "Flutter & Dart" },
  { q: "Flutter compile vers :", options: ["JavaScript uniquement", "Code natif", "PHP", "SQL"], correct: 1, part: "Flutter & Dart" },
  { q: "Provider en Flutter sert \u00e0 :", options: ["G\u00e9rer l'\u00e9tat", "Cr\u00e9er des APIs", "G\u00e9rer la DB", "Compiler Dart"], correct: 0, part: "Flutter & Dart" },
  { q: "Flutter est utilis\u00e9 pour :", options: ["Applications mobiles multiplateformes", "Serveurs backend uniquement", "Bases de donn\u00e9es", "OS development"], correct: 0, part: "Flutter & Dart" },
  { q: "Kafka est un :", options: ["SGBD relationnel", "Broker de streaming distribu\u00e9", "Framework UI", "OS"], correct: 1, part: "Kafka & RabbitMQ" },
  { q: "RabbitMQ utilise le protocole :", options: ["AMQP", "HTTP", "FTP", "SMTP"], correct: 0, part: "Kafka & RabbitMQ" },
  { q: "Kafka organise les donn\u00e9es en :", options: ["Tables", "Topics", "Pages", "Fichiers UI"], correct: 1, part: "Kafka & RabbitMQ" },
  { q: "Une partition Kafka permet :", options: ["UI rendering", "Scalabilit\u00e9 et parall\u00e9lisme", "CSS management", "DB locking"], correct: 1, part: "Kafka & RabbitMQ" },
  { q: "Offset Kafka repr\u00e9sente :", options: ["Une erreur", "La position d'un message dans un log", "Un widget UI", "Une API"], correct: 1, part: "Kafka & RabbitMQ" },
  { q: "Producer Kafka :", options: ["Consomme messages", "Publie messages", "UI rendering", "DB access"], correct: 1, part: "Kafka & RabbitMQ" },
  { q: "Consumer Kafka :", options: ["Lit les messages", "Cr\u00e9e UI", "G\u00e8re DB", "Compile code"], correct: 0, part: "Kafka & RabbitMQ" },
  { q: "Kafka conserve les messages :", options: ["Temporairement uniquement", "Persistants selon configuration", "UI only", "RAM only"], correct: 1, part: "Kafka & RabbitMQ" },
  { q: "RabbitMQ Exchange sert \u00e0 :", options: ["Stocker messages", "Router messages", "UI rendering", "DB indexing"], correct: 1, part: "Kafka & RabbitMQ" },
  { q: "Fanout Exchange :", options: ["Routing cibl\u00e9", "Broadcast \u00e0 toutes les queues", "Suppression messages", "Encryption"], correct: 1, part: "Kafka & RabbitMQ" },
  { q: "Direct Exchange :", options: ["Broadcast global", "Routing par cl\u00e9 exacte", "UI rendering", "DB replication"], correct: 1, part: "Kafka & RabbitMQ" },
  { q: "Kafka est optimis\u00e9 pour :", options: ["Big Data streaming", "UI rendering", "CSS", "HTML"], correct: 0, part: "Kafka & RabbitMQ" },
  { q: "RabbitMQ est :", options: ["Messaging system", "UI framework", "OS", "DB"], correct: 0, part: "Kafka & RabbitMQ" },
  { q: "L'architecture de Kafka est :", options: ["Centralis\u00e9e", "Distribu\u00e9e", "UI only", "Single node"], correct: 1, part: "Kafka & RabbitMQ" },
  { q: "Un Producer Kafka :", options: ["Lit les messages", "Envoie des messages", "UI", "DB"], correct: 1, part: "Kafka & RabbitMQ" },
  { q: "Eureka sert \u00e0 :", options: ["UI", "Service discovery", "DB", "Cache"], correct: 1, part: "Microservices & Eureka" },
  { q: "Microservices signifient :", options: ["Monolithe", "Services ind\u00e9pendants", "UI", "DB"], correct: 1, part: "Microservices & Eureka" },
  { q: "API Gateway sert \u00e0 :", options: ["Routing centralis\u00e9", "UI", "DB", "OS"], correct: 0, part: "Microservices & Eureka" },
  { q: "Service registry contient :", options: ["UI", "Services disponibles", "CSS", "DB"], correct: 1, part: "Microservices & Eureka" },
  { q: "Eureka client :", options: ["S'enregistre aupr\u00e8s du registry", "UI", "DB", "Cache"], correct: 0, part: "Microservices & Eureka" },
  { q: "Microservices communiquent via :", options: ["HTTP/REST", "UI", "CSS", "DB"], correct: 0, part: "Microservices & Eureka" },
  { q: "Avantage principal des microservices :", options: ["Scalabilit\u00e9", "Couplage fort", "UI lente", "DB unique"], correct: 0, part: "Microservices & Eureka" },
  { q: "Gateway permet :", options: ["Routing", "UI", "DB", "OS"], correct: 0, part: "Microservices & Eureka" },
  { q: "Load balancing permet :", options: ["UI", "R\u00e9partition de la charge", "DB", "CSS"], correct: 1, part: "Microservices & Eureka" },
  { q: "Microservices favorisent :", options: ["Ind\u00e9pendance", "Monolithe", "UI only", "DB unique"], correct: 0, part: "Microservices & Eureka" },
  { q: "Event-driven architecture repose sur :", options: ["Events", "UI", "DB", "CPU"], correct: 0, part: "Architecture avanc\u00e9e" },
  { q: "Tol\u00e9rance aux pannes signifie :", options: ["Crash syst\u00e8me", "Continuer \u00e0 fonctionner malgr\u00e9 les pannes", "UI fail", "DB reset"], correct: 1, part: "Architecture avanc\u00e9e" },
  { q: "Scalabilit\u00e9 signifie :", options: ["R\u00e9duction", "Support d'une charge croissante", "UI scaling", "CSS"], correct: 1, part: "Architecture avanc\u00e9e" },
  { q: "Cloud-native utilise :", options: ["Microservices", "Monolithes", "Desktop apps", "Local DB"], correct: 0, part: "Architecture avanc\u00e9e" },
  { q: "Couplage faible signifie :", options: ["Forte d\u00e9pendance", "Ind\u00e9pendance des services", "UI dependency", "DB dependency"], correct: 1, part: "Architecture avanc\u00e9e" },
];

const devoir6 = [
  { q: "Quel est le type de la variable notes ?", options: ["int", "List", "String", "double"], correct: 1, part: "Dart" },
  { q: "Que repr\u00e9sente l'expression notes.length ?", options: ["La valeur maximale de la liste", "Le nombre d'\u00e9l\u00e9ments dans la liste", "L'index maximum de la liste", "La moyenne des \u00e9l\u00e9ments"], correct: 1, part: "Dart" },
  { q: "Combien de fois la boucle for sera-t-elle ex\u00e9cut\u00e9e ?", options: ["3 fois", "4 fois", "5 fois", "6 fois"], correct: 2, part: "Dart" },
  { q: "Quelle sera la valeur affich\u00e9e pour Max ?", options: ["12", "15", "10", "9"], correct: 1, part: "Dart" },
  { q: "Quelle sera la valeur affich\u00e9e pour Min ?", options: ["8", "9", "10", "12"], correct: 0, part: "Dart" },
  { q: "Combien d'\u00e9tudiants seront compt\u00e9s comme admis (note \u2265 10) ?", options: ["2", "3", "4", "5"], correct: 1, part: "Dart" },
];

const quizzes = {
  revision70: { title: "QCM R\u00e9vision Technologies Web & Mobile", items: revision70 },
  devoir6: { title: "QCM Dart \u2014 Devoir Mobile", items: devoir6 },
};

/* ===== DOM ELEMENTS ===== */
const quizCategoryEl = document.getElementById("quiz-category");
const quizCounterEl = document.getElementById("quiz-counter");
const questionTextEl = document.getElementById("question-text");
const answersEl = document.getElementById("answers");
const feedbackEl = document.getElementById("feedback");
const resultEl = document.getElementById("result");
const resultIconEl = document.getElementById("result-icon");
const resultTitleEl = document.getElementById("result-title");
const resultScoreEl = document.getElementById("result-score");
const restartBtn = document.getElementById("restart-btn");
const quizCard = document.getElementById("quiz-card");
const progressFill = document.getElementById("progress-fill");
const progressText = document.getElementById("progress-text");
const prevBtn = document.getElementById("prev-btn");
const validateBtn = document.getElementById("validate-btn");
const nextBtn = document.getElementById("next-btn");
const quizTabs = document.querySelectorAll(".quiz-tab");
const tabs = document.querySelectorAll(".tab");

/* ===== STATE ===== */
let currentQuizKey = "revision70";
let currentIndex = 0;
let answers = [];
let validated = new Set();

/* ===== TABS (Corrections) ===== */
tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    document.getElementById("panel-" + tab.dataset.tab).classList.add("active");
  });
});

/* ===== QUIZ TABS ===== */
quizTabs.forEach((btn) => {
  btn.addEventListener("click", () => {
    setQuiz(btn.dataset.quiz);
  });
});

/* ===== QUIZ LOGIC ===== */
function setQuiz(key) {
  currentQuizKey = key;
  currentIndex = 0;
  answers = Array(quizzes[key].items.length).fill(null);
  validated = new Set();

  quizTabs.forEach((btn) => btn.classList.toggle("active", btn.dataset.quiz === key));
  resultEl.classList.add("hidden");
  quizCard.style.display = "";
  render();
}

function render() {
  const quiz = quizzes[currentQuizKey];
  const item = quiz.items[currentIndex];
  const total = quiz.items.length;

  quizCategoryEl.textContent = item.part;
  quizCounterEl.textContent = `Question ${currentIndex + 1} / ${total}`;
  questionTextEl.textContent = item.q;

  const pct = Math.round((validated.size / total) * 100);
  progressFill.style.width = pct + "%";
  progressText.textContent = pct + "%";

  answersEl.innerHTML = "";
  item.options.forEach((opt, idx) => {
    const label = document.createElement("label");
    label.className = "answer-option";

    if (answers[currentIndex] === idx) label.classList.add("selected");

    if (validated.has(currentIndex)) {
      if (idx === item.correct) label.classList.add("correct");
      else if (answers[currentIndex] === idx) label.classList.add("wrong");
    }

    label.innerHTML = `
      <input type="radio" name="answer" value="${idx}" ${answers[currentIndex] === idx ? "checked" : ""} ${validated.has(currentIndex) ? "disabled" : ""}>
      <span class="answer-option__radio"></span>
      <span class="answer-option__text">${opt}</span>
    `;
    answersEl.appendChild(label);
  });

  answersEl.querySelectorAll("input").forEach((input) => {
    input.addEventListener("change", () => {
      answers[currentIndex] = parseInt(input.value);
      render();
    });
  });

  prevBtn.disabled = currentIndex === 0;
  nextBtn.disabled = currentIndex === total - 1;
  validateBtn.disabled = validated.has(currentIndex);

  if (validated.has(currentIndex)) {
    const isCorrect = answers[currentIndex] === item.correct;
    feedbackEl.className = "quiz-card__feedback visible " + (isCorrect ? "success" : "error");
    feedbackEl.textContent = isCorrect
      ? "\u2714 Correct !"
      : `\u2718 Incorrect. R\u00e9ponse : ${item.options[item.correct]}`;
  } else {
    feedbackEl.className = "quiz-card__feedback";
    feedbackEl.textContent = "";
  }
}

function validateCurrent() {
  const quiz = quizzes[currentQuizKey];
  const item = quiz.items[currentIndex];

  if (answers[currentIndex] === null) {
    feedbackEl.className = "quiz-card__feedback visible warning";
    feedbackEl.textContent = "\u26a0 S\u00e9lectionne une r\u00e9ponse avant de valider.";
    return;
  }

  validated.add(currentIndex);
  render();

  if (validated.size === quiz.items.length) {
    setTimeout(showResult, 600);
  }
}

function showResult() {
  const quiz = quizzes[currentQuizKey];
  let score = 0;
  quiz.items.forEach((item, idx) => {
    if (answers[idx] === item.correct) score++;
  });

  const pct = Math.round((score / quiz.items.length) * 100);
  let icon, title;

  if (pct >= 80) { icon = "\ud83c\udf89"; title = "Excellent !"; }
  else if (pct >= 60) { icon = "\ud83d\udc4d"; title = "Bien jou\u00e9 !"; }
  else if (pct >= 40) { icon = "\ud83d\udcaa"; title = "Peut mieux faire"; }
  else { icon = "\ud83d\udcd6"; title = "Continue de r\u00e9viser"; }

  resultIconEl.textContent = icon;
  resultTitleEl.textContent = title;
  resultScoreEl.textContent = `${score} / ${quiz.items.length} (${pct}%)`;

  quizCard.style.display = "none";
  resultEl.classList.remove("hidden");

  progressFill.style.width = "100%";
  progressText.textContent = "100%";
}

/* ===== EVENT LISTENERS ===== */
prevBtn.addEventListener("click", () => {
  if (currentIndex > 0) { currentIndex--; render(); }
});

nextBtn.addEventListener("click", () => {
  const total = quizzes[currentQuizKey].items.length;
  if (currentIndex < total - 1) { currentIndex++; render(); }
});

validateBtn.addEventListener("click", validateCurrent);

restartBtn.addEventListener("click", () => {
  setQuiz(currentQuizKey);
});

/* ===== NAV SECTIONS ===== */
const navLinks = document.querySelectorAll(".nav-link[data-section]");
const pageSections = document.querySelectorAll(".section[id]");

function showSection(sectionId) {
  pageSections.forEach((section) => {
    section.classList.toggle("section--hidden", section.id !== sectionId);
  });

  navLinks.forEach((link) => {
    link.classList.toggle("active", link.dataset.section === sectionId);
  });

  window.scrollTo({ top: 0, behavior: "smooth" });
}

navLinks.forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    showSection(link.dataset.section);
  });
});

document.querySelector(".navbar__brand").addEventListener("click", () => {
  showSection("corrections");
});

/* ===== INIT ===== */
showSection("corrections");
setQuiz("revision70");
