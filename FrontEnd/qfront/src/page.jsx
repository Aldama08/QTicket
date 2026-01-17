import React, { useState } from 'react';
import './page.css';

const FASTAPI_BACKEND_URL = 'http://127.0.0.1:8000';

// Recibe los datos del usuario como "props" desde App.js
function Page({ userData, onLogout}) {
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

    const fullTicketData = {
    usuario_id: userData.id, 
    descripcion: descripcion,
    };

    console.log("Enviando Ticket Data:", fullTicketData); 
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

  const HelpDeskIcon = () => (
      <svg width="800" height="300"  viewBox="0 0 240 180" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ margin: '0 auto', display: 'block' }}>
        {/* Fondo Simple */}
        <rect width="240" height="180" rx="10" fill="#f8faff" />

        {/* Bombilla (Idea) */}
        <path d="M175 60 C175 40, 145 40, 145 60 C145 75, 155 85, 155 100 H165 C165 85, 175 75, 175 60" fill="#FFE082" stroke="#333" strokeWidth="2"/>
        <rect x="155" y="105" width="10" height="4" fill="#90A4AE" stroke="#333" strokeWidth="1.5"/>
        <rect x="156" y="111" width="8" height="4" fill="#90A4AE" stroke="#333" strokeWidth="1.5"/>
        <line x1="145" y1="75" x2="175" y2="75" stroke="#333" strokeWidth="1.5" strokeOpacity="0.3"/>
        <line x1="160" y1="60" x2="160" y2="90" stroke="#333" strokeWidth="1.5" strokeOpacity="0.3"/>

        {/* Cohete (Lanzamiento) */}
        <path d="M85 40 L105 85 L85 110 L65 85 Z" fill="#81D4FA" stroke="#333" strokeWidth="2"/>
        <path d="M65 85 L55 105 L65 100" fill="#42A5F5" stroke="#333" strokeWidth="2"/>
        <path d="M105 85 L115 105 L105 100" fill="#42A5F5" stroke="#333" strokeWidth="2"/>
        <circle cx="85" cy="70" r="6" fill="#E3F2FD" stroke="#333" strokeWidth="1.5"/>

        {/* Humo/Nube del cohete */}
        <path d="M60 130 Q85 110 110 130 Q120 145 85 150 Q50 145 60 130" fill="#FFF9C4" stroke="#FFD54F" strokeWidth="2" strokeDasharray="4 2"/>

        {/* Elementos decorativos (Check y líneas) */}
        <circle cx="130" cy="35" r="12" fill="#B2EBF2" stroke="#333" strokeWidth="2"/>
        <path d="M125 35 L128 38 L135 31" stroke="#333" strokeWidth="2" strokeLinecap="round"/>
        <path d="M40 40 H70 M40 50 H60 M40 60 H70" stroke="#B0BEC5" strokeWidth="2" strokeLinecap="round"/>
        <path d="M190 100 H215 M190 110 H215 M190 120 H205" stroke="#B0BEC5" strokeWidth="2" strokeLinecap="round"/>
      </svg>
  );

  // El resto de tu JSX para mostrar el formulario, los resultados y los errores
  // puede permanecer casi igual.
  return (
    <div className="container">

      <div className="svg-container">
        <HelpDeskIcon />
      </div>


      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button onClick={onLogout} className="btn-secondary">
          ← Regresar a Registro
        </button>
      </div>

      <h2 className="texto-central">Help Desk con Agente Experto</h2>
      <p className=''>Bienvenido, <strong>{userData.nombre}</strong>. Describe tu problema para obtener ayuda.</p>
      
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