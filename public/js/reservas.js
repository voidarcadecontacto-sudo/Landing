/* ==========================================================================
   Void Arcade — formulario de reservas
   Arma un mensaje de WhatsApp con los datos y abre el chat.
   No envía nada a ningún servidor: todo ocurre en el navegador.
   ========================================================================== */
(function () {
  'use strict';

  var TELEFONO = '573103420856';   // <- si cambia el número, cámbialo aquí y en index.html

  var form = document.getElementById('form-reserva');
  if (!form) return;

  var fecha = form.elements.fecha;

  /* No dejar escoger días que ya pasaron, y arrancar en hoy. */
  if (fecha) {
    var hoy = new Date();
    var iso = new Date(hoy.getTime() - hoy.getTimezoneOffset() * 60000)
      .toISOString().slice(0, 10);
    fecha.min = iso;
    if (!fecha.value) fecha.value = iso;
  }

  /* "2026-09-26" -> "26/09/2026", más legible en el chat. */
  function fechaLegible(valor) {
    var p = /^(\d{4})-(\d{2})-(\d{2})$/.exec(valor);
    return p ? p[3] + '/' + p[2] + '/' + p[1] : valor;
  }

  function mensaje() {
    var d = new FormData(form);
    var nombre = (d.get('nombre') || '').toString().trim();
    var f = (d.get('fecha') || '').toString();
    var hora = (d.get('hora') || '').toString();
    var personas = (d.get('personas') || '').toString();
    var servicio = (d.get('servicio') || '').toString();

    return [
      '¡Hola Void Arcade! Quiero reservar.',
      nombre ? 'Nombre: ' + nombre : '',
      servicio ? 'Servicio: ' + servicio : '',
      f ? 'Fecha: ' + fechaLegible(f) : '',
      hora ? 'Hora: ' + hora : '',
      personas ? 'Personas: ' + personas : ''
    ].filter(Boolean).join('\n');
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var url = 'https://wa.me/' + TELEFONO + '?text=' + encodeURIComponent(mensaje());

    /* En móvil el deep link abre la app de WhatsApp; en escritorio, WhatsApp Web.
       Si el navegador bloquea la ventana nueva, navegamos en la misma pestaña. */
    var w = window.open(url, '_blank', 'noopener');
    if (!w) window.location.href = url;
  });
})();
