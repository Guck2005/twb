/* ===== TABS (Cours) ===== */
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    document.getElementById("panel-" + tab.dataset.tab).classList.add("active");
  });
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
  showSection("cours");
});

/* ===== QCM ===== */
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

const quiz = gpQuiz;
let currentIndex = 0;
let answers = [];
let validated = new Set();

function isMulti(item) {
  return Array.isArray(item.correct);
}

function initQuiz() {
  currentIndex = 0;
  answers = quiz.items.map((item) =>
    isMulti(item) ? new Set() : null
  );
  validated = new Set();
  resultEl.classList.add("hidden");
  quizCard.style.display = "";
  progressFill.style.width = "0%";
  progressText.textContent = "0%";
  render();
}

function isAnswered(idx) {
  const item = quiz.items[idx];
  if (isMulti(item)) return answers[idx] instanceof Set && answers[idx].size > 0;
  return answers[idx] !== null;
}

function isCorrectAt(idx) {
  const item = quiz.items[idx];
  if (isMulti(item)) {
    const userSet = answers[idx];
    if (!(userSet instanceof Set) || userSet.size !== item.correct.length) return false;
    return item.correct.every((c) => userSet.has(c));
  }
  return answers[idx] === item.correct;
}

function render() {
  const item = quiz.items[currentIndex];
  const total = quiz.items.length;
  const multi = isMulti(item);

  quizCategoryEl.textContent = item.part;
  quizCounterEl.textContent = `Question ${currentIndex + 1} / ${total}`;
  questionTextEl.textContent = item.q;

  const pct = Math.round((validated.size / total) * 100);
  progressFill.style.width = pct + "%";
  progressText.textContent = pct + "%";

  answersEl.innerHTML = "";

  if (multi && item.correct.length > 1 && !validated.has(currentIndex)) {
    const hint = document.createElement("div");
    hint.className = "quiz-card__hint";
    hint.textContent = `\u2139 ${item.correct.length} r\u00e9ponses attendues`;
    answersEl.appendChild(hint);
  }

  item.options.forEach((opt, idx) => {
    const label = document.createElement("label");
    label.className = "answer-option";

    if (multi) {
      const userSet = answers[currentIndex];
      if (userSet.has(idx)) label.classList.add("selected");
      if (validated.has(currentIndex)) {
        if (item.correct.includes(idx)) label.classList.add("correct");
        else if (userSet.has(idx)) label.classList.add("wrong");
      }
      label.innerHTML = `
        <input type="checkbox" name="answer" value="${idx}" ${userSet.has(idx) ? "checked" : ""} ${validated.has(currentIndex) ? "disabled" : ""}>
        <span class="answer-option__check"></span>
        <span class="answer-option__text">${opt}</span>
      `;
    } else {
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
    }

    answersEl.appendChild(label);
  });

  if (multi) {
    answersEl.querySelectorAll('input[type="checkbox"]').forEach((input) => {
      input.addEventListener("change", () => {
        const val = parseInt(input.value, 10);
        const userSet = answers[currentIndex];
        if (input.checked) userSet.add(val);
        else userSet.delete(val);
        render();
      });
    });
  } else {
    answersEl.querySelectorAll('input[type="radio"]').forEach((input) => {
      input.addEventListener("change", () => {
        answers[currentIndex] = parseInt(input.value, 10);
        render();
      });
    });
  }

  prevBtn.disabled = currentIndex === 0;
  nextBtn.disabled = currentIndex === total - 1;
  validateBtn.disabled = validated.has(currentIndex);

  if (validated.has(currentIndex)) {
    const ok = isCorrectAt(currentIndex);
    feedbackEl.className = "quiz-card__feedback visible " + (ok ? "success" : "error");
    if (ok) {
      feedbackEl.textContent = "\u2714 Correct !";
    } else if (multi) {
      const correctTexts = item.correct.map((c) => item.options[c]);
      feedbackEl.textContent = `\u2718 Incorrect. R\u00e9ponses : ${correctTexts.join(" \u2014 ")}`;
    } else {
      feedbackEl.textContent = `\u2718 Incorrect. R\u00e9ponse : ${item.options[item.correct]}`;
    }
  } else {
    feedbackEl.className = "quiz-card__feedback";
    feedbackEl.textContent = "";
  }
}

function validateCurrent() {
  if (!isAnswered(currentIndex)) {
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
  let score = 0;
  quiz.items.forEach((_, idx) => {
    if (isCorrectAt(idx)) score++;
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

prevBtn.addEventListener("click", () => { if (currentIndex > 0) { currentIndex--; render(); } });
nextBtn.addEventListener("click", () => { if (currentIndex < quiz.items.length - 1) { currentIndex++; render(); } });
validateBtn.addEventListener("click", validateCurrent);
restartBtn.addEventListener("click", initQuiz);

showSection("cours");
initQuiz();
