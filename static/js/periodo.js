/* Calendário de período (Vanilla Calendar Pro).
   Troca os campos nativos "De" e "Até" de cada filtro por um campo único "Período".
   Os campos originais continuam no formulário (escondidos) e são eles que vão para o servidor. */
(function () {
  if (!window.VanillaCalendarPro) return; // sem a biblioteca, ficam os campos nativos

  const { Calendar } = window.VanillaCalendarPro;

  // "2026-10-05" -> "05/10/2026"
  const paraBR = (iso) => (iso ? iso.split("-").reverse().join("/") : "");

  function textoPeriodo(inicio, fim) {
    if (inicio && fim) return inicio === fim ? paraBR(inicio) : `${paraBR(inicio)} – ${paraBR(fim)}`;
    if (inicio) return `A partir de ${paraBR(inicio)}`;
    if (fim) return `Até ${paraBR(fim)}`;
    return "";
  }

  document.querySelectorAll("form.painel-filtros").forEach((form) => {
    const inicio = form.querySelector('input[name="inicio"]');
    const fim = form.querySelector('input[name="fim"]');
    if (!inicio || !fim) return;

    const campoInicio = inicio.closest("div");
    const campoFim = fim.closest("div");

    // Campo novo, só para mostrar e abrir o calendário (sem "name": não vai para o servidor)
    const campo = document.createElement("div");
    campo.className = "campo--periodo";
    const id = `periodo-${inicio.id || "filtro"}`;
    campo.innerHTML = `
      <label class="form-label" for="${id}">Período</label>
      <input type="text" id="${id}" class="form-control" readonly
             placeholder="Escolha o período" autocomplete="off">`;
    const visor = campo.querySelector("input");
    visor.value = textoPeriodo(inicio.value, fim.value);

    campoInicio.before(campo);
    campoInicio.hidden = true;
    campoFim.hidden = true;
    // Escondidos, os campos nativos não podem barrar o envio por "campo obrigatório"
    inicio.required = false;
    fim.required = false;

    const selecionadas = [];
    if (inicio.value && fim.value) selecionadas.push(`${inicio.value}:${fim.value}`);
    else if (inicio.value) selecionadas.push(inicio.value);

    const calendario = new Calendar(visor, {
      inputMode: true,
      positionToInput: "auto",
      selectedTheme: "light",
      locale: "pt-BR",
      firstWeekday: 0,
      selectionDatesMode: "multiple-ranged",
      selectedDates: selecionadas,
      labels: {
        application: "Calendário",
        navigation: "Navegação do calendário",
        arrowNext: { month: "Próximo mês", year: "Próximos anos" },
        arrowPrev: { month: "Mês anterior", year: "Anos anteriores" },
        month: "Escolher mês, mês atual:",
        months: "Lista de meses",
        year: "Escolher ano, ano atual:",
        years: "Lista de anos",
        week: "Dias da semana",
        dates: "Datas do mês",
      },
      onChangeToInput(self) {
        const datas = [...self.context.selectedDates].sort();
        inicio.value = datas[0] || "";
        fim.value = datas.length > 1 ? datas[datas.length - 1] : "";
        visor.value = textoPeriodo(inicio.value, fim.value);
        // Fecha quando o período estiver completo (segundo clique)
        if (datas.length > 1) self.hide();
      },
    });
    calendario.init();

    // Teclado: Enter, espaço ou seta para baixo abrem o calendário
    visor.addEventListener("keydown", (evento) => {
      if (["Enter", " ", "ArrowDown"].includes(evento.key)) {
        evento.preventDefault();
        calendario.show();
      }
    });
  });
})();