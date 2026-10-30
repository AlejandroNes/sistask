(() => {
  const abrir = document.getElementById('chat-abrir');
  const cerrar = document.getElementById('chat-cerrar');
  const panel = document.getElementById('chat-panel');
  const form = document.getElementById('chat-form');
  const texto = document.getElementById('chat-texto');
  const lista = document.getElementById('chat-mensajes');
  const enviar = document.getElementById('chat-enviar');
  const historial = [];

  function mostrar(abierto) {
    panel.hidden = !abierto;
    abrir.setAttribute('aria-expanded', String(abierto));
    if (abierto) texto.focus(); else abrir.focus();
  }
  abrir.addEventListener('click', () => mostrar(panel.hidden));
  cerrar.addEventListener('click', () => mostrar(false));
  panel.addEventListener('keydown', (evento) => { if (evento.key === 'Escape') mostrar(false); });
  function agregar(contenido, tipo) {
    const burbuja = document.createElement('div');
    burbuja.className = 'chat-burbuja ' + tipo;
    burbuja.textContent = contenido;
    lista.appendChild(burbuja);
    lista.scrollTop = lista.scrollHeight;
  }
  form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const pregunta = texto.value.trim();
    if (!pregunta || enviar.disabled) return;
    agregar(pregunta, 'usuario');
    texto.value = '';
    enviar.disabled = true;
    enviar.textContent = 'Consultando…';
    const mensajes = [...historial, {role: 'user', content: pregunta}].slice(-11);
    try {
      const respuesta = await fetch('/api/chat', {
        method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': document.getElementById('chat-csrf').value},
        body: JSON.stringify({mensajes})
      });
      if (respuesta.redirected || !respuesta.headers.get('content-type')?.includes('application/json')) {
        throw new Error('Tu sesión pudo haber vencido. Vuelve a iniciar sesión.');
      }
      const datos = await respuesta.json();
      if (!respuesta.ok) throw new Error(datos.error || 'No se pudo completar la consulta.');
      agregar(datos.respuesta, 'asistente');
      historial.push({role: 'user', content: pregunta}, {role: 'assistant', content: datos.respuesta.slice(0, 2000)});
      if (historial.length > 10) historial.splice(0, historial.length - 10);
    } catch (error) {
      agregar(error.message || 'No se pudo conectar con el asistente.', 'error');
    } finally {
      enviar.disabled = false;
      enviar.textContent = 'Enviar';
      texto.focus();
    }
  });
})();
