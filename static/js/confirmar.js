// Confirmação antes de excluir, desativar ou sair.
// Basta o formulário ter data-confirmar com a pergunta: o envio só segue se a pessoa confirmar no modal.
// Opcionais: data-confirmar-texto (explicação), data-confirmar-botao (rótulo do botão) e data-confirmar-perigo (botão vermelho).
(() => {
  const modal = document.getElementById("modal-confirmar");
  if (!modal) return;

  const titulo = document.getElementById("modal-confirmar-titulo");
  const texto = document.getElementById("modal-confirmar-texto");
  const cancelar = modal.querySelector("[data-bs-dismiss]");
  const confirmar = modal.querySelector(".modal-confirmar-ok");
  const dialogo = bootstrap.Modal.getOrCreateInstance(modal);

  let pendente = null;
  let gatilho = null;

  document.addEventListener("submit", (evento) => {
    const form = evento.target;
    if (!form.matches("form[data-confirmar]")) return;
    evento.preventDefault();

    pendente = form;
    gatilho = evento.submitter;
    const perigo = "confirmarPerigo" in form.dataset;
    titulo.textContent = form.dataset.confirmar;
    texto.textContent = form.dataset.confirmarTexto || "";
    texto.hidden = !form.dataset.confirmarTexto;
    confirmar.textContent = form.dataset.confirmarBotao || "Confirmar";
    confirmar.classList.toggle("btn-perigo", perigo);
    confirmar.classList.toggle("btn-primario", !perigo);
    confirmar.disabled = false;
    dialogo.show();
  });

  // O foco começa no "Cancelar": um Enter distraído não exclui nada
  modal.addEventListener("shown.bs.modal", () => cancelar.focus());

  confirmar.addEventListener("click", () => {
    if (!pendente) return;
    confirmar.disabled = true; // evita envio duplo com clique repetido
    // submit() não dispara o evento "submit", então o formulário segue direto sem abrir o modal de novo
    pendente.submit();
  });

  modal.addEventListener("hidden.bs.modal", () => {
    if (gatilho?.isConnected) gatilho.focus();
    pendente = gatilho = null;
  });
})();
