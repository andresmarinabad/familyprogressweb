var count = 500;
var defaults = {
  origin: { y: 0.8, x: 0.5 },
};

const titulo = document.getElementById("Fire");
const gradientes = [
  "g1", "g2", "g3", "g4", "g5", "g6", "g7",
  "g8", "g9", "g10", "g11", "g12", "g13", "g14",
];

let indiceGradiente = 0;
document.getElementById("Fire").onclick = FireCannon;

function Fire(particleRatio, opts) {
  confetti(Object.assign({}, defaults, opts, {
    particleCount: Math.floor(count * particleRatio),
  }));
}

function FireCannon(multiplier) {
  const previousCount = count;
  if (typeof multiplier === "number") count = Math.floor(count * multiplier);

  Fire(0.25, { spread: 26, startVelocity: 55 });
  Fire(0.2, { spread: 60 });
  Fire(0.35, { spread: 100, decay: 0.91, scalar: 0.4 });
  Fire(0.1, { spread: 120, startVelocity: 25, decay: 0.92, scalar: 1.2 });
  Fire(0.1, { spread: 120, startVelocity: 45 });

  count = previousCount;
  titulo.classList.remove(gradientes[indiceGradiente]);
  let nuevoIndice;
  do {
    nuevoIndice = Math.floor(Math.random() * gradientes.length);
  } while (nuevoIndice === indiceGradiente);

  indiceGradiente = nuevoIndice;
  titulo.classList.add(gradientes[indiceGradiente]);
}

function initBirthdayMode() {
  const cards = document.querySelectorAll('[data-birthday-card="true"]');
  if (!cards.length) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduceMotion) {
    cards.forEach((card) => card.classList.add("birthday-gold", "birthday-settled"));
    return;
  }

  /* La misma celebración del título, una sola vez y algo más abundante. */
  window.setTimeout(() => FireCannon(1.35), 180);

  cards.forEach((card) => {
    requestAnimationFrame(() => card.classList.add("birthday-flipping"));

    /* El cambio a oro ocurre cuando la tarjeta está casi de canto. */
    window.setTimeout(() => card.classList.add("birthday-gold"), 500);
    window.setTimeout(() => {
      card.classList.remove("birthday-flipping");
      card.classList.add("birthday-settled");
    }, 1080);
  });
}

document.addEventListener("DOMContentLoaded", initBirthdayMode);

document.getElementById("filtro").addEventListener("change", function () {
  if (this.checked) ordenarDivsDorsal();
  else ordenarDivsFecha();
});

function mostrarVideo(kidid) {
  var divid = kidid + "-div";
  var div = document.getElementById(divid);
  var imagen = div.querySelector("img");
  var video = div.querySelector("video");
  imagen.style.display = "none";
  video.style.display = "block";
  video.setAttribute("playsinline", "");
  video.currentTime = 0;
  video.play();
  video.onended = function () {
    video.currentTime = 0;
    video.load();
    video.pause();
    imagen.style.display = "block";
    video.style.display = "none";
  };
}

function ordenarDivsDorsal() {
  const container = document.getElementById("contenedor");
  const items = Array.from(container.querySelectorAll(".kid"));
  items.sort((a, b) => {
    const numA = parseInt(a.querySelector(".dorsal").textContent.replace("#", ""));
    const numB = parseInt(b.querySelector(".dorsal").textContent.replace("#", ""));
    return numA - numB;
  });
  items.forEach((item) => container.appendChild(item));
}

function ordenarDivsFecha() {
  const container = document.getElementById("contenedor");
  const items = Array.from(container.querySelectorAll(".kid"));
  items.sort((a, b) => {
    const fechaA = a.querySelector(".fecha").textContent.trim();
    const fechaB = b.querySelector(".fecha").textContent.trim();
    return new Date(fechaA) - new Date(fechaB);
  });
  items.forEach((item) => container.appendChild(item));
}

const selectorClan = document.getElementById("clanes");
const contenedor = document.getElementById("contenedor");
selectorClan.addEventListener("change", function () {
  const filtro = this.value;
  const kids = contenedor.getElementsByClassName("kid");
  Array.from(kids).forEach((kid) => {
    const spanClan = kid.querySelector(".clan");
    if (spanClan) {
      const valorClan = spanClan.textContent.trim();
      kid.style.display = !filtro || valorClan === filtro ? "" : "none";
    }
  });
});
