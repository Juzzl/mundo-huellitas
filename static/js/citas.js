document.addEventListener("DOMContentLoaded", () => {

  document.querySelectorAll("form[data-confirm]").forEach((f) => {
    f.addEventListener("submit", (e) => {
      if (!confirm(f.dataset.confirm)) e.preventDefault();
    });
  });

  const form = document.getElementById("form-cita");
  if (!form) return;

  const fecha = form.querySelector("#id_fecha");
  const hora = form.querySelector("#id_hora");
  const empleado = form.querySelector("#id_empleado");
  const duracion = form.querySelector("#id_duracion");
  const url = form.dataset.urlOcupadas;
  const citaId = form.dataset.citaId;

  const aMin = (s) => {
    const [h, m] = s.split(":").map(Number);
    return h * 60 + m;
  };

  fecha.min = new Date().toLocaleDateString("en-CA"); 

  async function actualizarHoras() {
    let intervalos = [];
    let cierre = 24 * 60;
    if (fecha.value) {
      const params = new URLSearchParams({ fecha: fecha.value, empleado: empleado.value });
      if (citaId) params.set("excluir", citaId);
      try {
        const resp = await fetch(`${url}?${params}`);
        const datos = await resp.json();
        intervalos = datos.intervalos;
        cierre = datos.cierre;
      } catch (err) {
        console.error("No se pudo consultar la disponibilidad", err);
      }
    }

    const dur = parseInt(duracion.value || "180", 10);

    [...hora.options].forEach((opt) => {
      if (!opt.value) return;
      const ini = aMin(opt.value);
      const fin = ini + dur;
      const noCabe = fin > cierre || intervalos.some((i) => ini < i.fin && fin > i.inicio);
      opt.disabled = noCabe;
      opt.textContent = noCabe ? `${opt.value} (no disponible)` : opt.value;
    });
    if (hora.selectedOptions[0]?.disabled) hora.value = "";
  }

  [fecha, empleado, duracion].forEach((el) => el.addEventListener("change", actualizarHoras));
  actualizarHoras();
});