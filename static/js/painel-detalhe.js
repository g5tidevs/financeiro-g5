// Painel lateral com os detalhes de um lançamento.
// Clicar no cliente, ou em qualquer ponto livre da linha, busca a página de detalhes e mostra o conteúdo no painel.
// Ctrl+clique e clique do meio seguem o link normal: os detalhes abrem como página inteira em outra aba.
(() => {
  const painel = document.getElementById("painel-detalhe");
  if (!painel) return;

  const corpo = painel.querySelector(".painel-detalhe-corpo");
  const offcanvas = bootstrap.Offcanvas.getOrCreateInstance(painel);
  // Elementos que têm ação própria dentro da linha: clicar neles não abre o painel
  const INTERATIVOS = "a, button, input, select, textarea, label, form";

  let pedidoAtual = 0;
  let gatilho = null;

  function aviso(texto) {
    const p = document.createElement("p");
    p.className = "painel-aviso";
    p.textContent = texto;
    corpo.replaceChildren(p);
  }

  function marcarLinha(linha) {
    document.querySelectorAll("tr.selecionada").forEach((tr) => tr.classList.remove("selecionada"));
    linha?.classList.add("selecionada");
  }

  async function abrir(link) {
    const pedido = ++pedidoAtual;
    gatilho = link;
    marcarLinha(link.closest("tr"));
    aviso("Carregando…");
    corpo.setAttribute("aria-busy", "true");
    offcanvas.show();

    try {
      const resposta = await fetch(link.href, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      // Sessão expirada: o servidor redireciona para o login, então abre a página inteira para a pessoa entrar de novo
      if (resposta.redirected) {
        window.location.href = link.href;
        return;
      }
      if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
      const html = await resposta.text();
      if (pedido !== pedidoAtual) return; // outro lançamento foi aberto enquanto este carregava
      corpo.innerHTML = html;
      corpo.scrollTop = 0;
    } catch {
      if (pedido === pedidoAtual) aviso("Não foi possível carregar os detalhes. Feche o painel e tente de novo.");
    } finally {
      if (pedido === pedidoAtual) corpo.removeAttribute("aria-busy");
    }
  }

  document.addEventListener("click", (evento) => {
    if (evento.button !== 0 || evento.ctrlKey || evento.metaKey || evento.shiftKey || evento.altKey) return;

    let link = evento.target.closest("[data-detalhe]");
    if (!link) {
      const linha = evento.target.closest("tr.linha-detalhe");
      if (!linha || evento.target.closest(INTERATIVOS)) return;
      if (window.getSelection().toString()) return; // estava selecionando texto para copiar
      link = linha.querySelector("[data-detalhe]");
      if (!link) return;
    }
    evento.preventDefault();
    abrir(link);
  });

  painel.addEventListener("hidden.bs.offcanvas", () => {
    marcarLinha(null);
    if (gatilho?.isConnected) gatilho.focus();
  });
})();
