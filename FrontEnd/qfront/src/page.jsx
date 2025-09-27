import React, { useState } from 'react';
import './page.css';

const FASTAPI_BACKEND_URL = 'http://192.168.1.65:8000';

// Recibe los datos del usuario como "props" desde App.js
function Page({ userData }) {
  const [descripcion, setDescripcion] = useState('');
  const [status, setStatus] = useState('idle'); // idle | submitting | success | error
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (descripcion.trim() === '') return;

    setStatus('submitting');
    setError('');
    setResultado(null);

    // Combina los datos del usuario (de props) con la descripción (de state)
    const fullTicketData = {
      ...userData,
      descripcion: descripcion,
    };

    try {
      // Llama al backend UNIFICADO con TODOS los datos
      const response = await fetch(`${FASTAPI_BACKEND_URL}/crear-y-procesar-ticket`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fullTicketData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ocurrió un error');
      }

      const dataResultado = await response.json();
      setResultado(dataResultado);
      setStatus('success');

    } catch (err) {
      console.error(err);
      setError(err.message);
      setStatus('error');
    }
  };

  const resetForm = () => {
    setDescripcion('');
    setStatus('idle');
    setResultado(null);
    setError('');
  };

  // El resto de tu JSX para mostrar el formulario, los resultados y los errores
  // puede permanecer casi igual.
  return (
    <div className="container">
      <h2>Help Desk con Agente Experto</h2>
      <p>Bienvenido, <strong>{userData.nombre}</strong>. Describe tu problema para obtener ayuda.</p>
      
      {status !== 'success' && (
        <form onSubmit={handleSubmit}>
          <div className='group-area'>
            <textarea
              rows="5"
              placeholder="Ej: No puedo acceder a mi correo institucional."
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              disabled={status === 'submitting'}
              required
            />
            <button type="submit" disabled={status === 'submitting'} className='button'>
              {status === 'submitting' ? 'Analizando...' : 'Obtener Solución'}
            </button>  
          </div>
        </form>
      )}

      {status === 'error' && (
        <div className="error-display">
          <p><strong>Ocurrió un error:</strong> {error}</p>
          <button onClick={resetForm}>Intentar de nuevo</button>
        </div>
      )}

      {status === 'success' && resultado && (
        <div className="success-display">
           {/* ... Tu JSX para mostrar la solución y keywords (sin cambios)... */}
           <h3>Análisis Completado</h3>
           <div>
             <h4>Solución Sugerida</h4>
             <p>{resultado.solucion_sugerida}</p>
             <hr />
             <h4>Palabras Clave Detectadas</h4>
             <div>
               {resultado.keywords_extraidas.map(kw => <span key={kw}>{kw}</span>)}
             </div>
           </div>
           <button onClick={resetForm}>Crear otro ticket</button>
        </div>
      )}
    </div>
  );
}

export default Page;