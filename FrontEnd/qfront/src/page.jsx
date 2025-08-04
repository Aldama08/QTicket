import React, { useState } from 'react';
// 1. Se importa la función para crear el cliente de Supabase
import { createClient } from '@supabase/supabase-js';
import './page.css';
// --- CONFIGURACIÓN DE SUPABASE INTEGRADA ---
// Datos extraídos de tu backend
const supabaseUrl = 'https://ibecmvmtlndaonohzxce.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImliZWNtdm10bG5kYW9ub2h6eGNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4MTA4NzQsImV4cCI6MjA1MzM4Njg3NH0.XBLqtGUJ3bPjrDgM6ZifZoJGOponRjfhd9YzFJ6yrL0';
// Se crea la instancia del cliente que el resto del código usará
const supabase = createClient(supabaseUrl, supabaseKey);
// --- FIN DE LA CONFIGURACIÓN ---

// 🔴 ¡IMPORTANTE! Reemplaza esto con la URL donde tu backend de FastAPI está corriendo.
const FASTAPI_BACKEND_URL = 'http://localhost:8000'; // O la URL de producción

function HelpDeskIA() {
  const [descripcion, setDescripcion] = useState('');
  const [status, setStatus] = useState('idle'); // idle | creating | processing | success | error
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (descripcion.trim() === '') return;

    // Reiniciar estados
    setStatus('creating');
    setError('');
    setResultado(null);

    try {
      // --- PASO 1: Crear el ticket en Supabase para obtener su ID ---
      console.log('Paso 1: Creando ticket en Supabase...');
      const { data: nuevoTicket, error: insertError } = await supabase
        .from('tickets')
        .insert({ descripcion: descripcion }) // Solo se necesita la descripción para crearlo
        .select('id') // Seleccionamos solo el 'id' que se acaba de generar
        .single();

      if (insertError) {
        throw new Error(`Error en Supabase: ${insertError.message}`);
      }
      
      const ticketId = nuevoTicket.id;
      console.log(`Ticket creado con ID: ${ticketId}`);
      setStatus('processing');

      // --- PASO 2: Llamar a tu backend de FastAPI para procesar el ticket ---
      console.log('Paso 2: Enviando ID al backend de FastAPI para su análisis...');
      const response = await fetch(`${FASTAPI_BACKEND_URL}/procesar-ticket`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ticket_id: ticketId }), // Tu backend espera este formato
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Error del backend: ${errorData.detail || response.statusText}`);
      }
      
      const dataResultado = await response.json();
      console.log('Análisis recibido:', dataResultado);

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

  const renderButtonText = () => {
    switch (status) {
      case 'creating':
        return '🎟️ Creando ticket...';
      case 'processing':
        return '🧠 Analizando con IA...';
      case 'success':
      case 'error':
        return 'Crear otro ticket';
      default:
        return 'Obtener Solución';
    }
  };

  return (
    <div className="container">
      <h2> Help Desk con Agente Experto</h2>
      
      {status !== 'success' && (
        <form onSubmit={handleSubmit}>
          <p>Describe tu problema para obtener ayuda.</p>
          <div className='group-area'>
            <textarea
            rows="5"
            placeholder="Ej: No puedo acceder a mi correo institucional."
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            disabled={status === 'creating' || status === 'processing'}
            required
            
          />
            <button
              type="submit"
              disabled={status === 'creating' || status === 'processing'}
              className='button'
            >
              {renderButtonText()}
            </button>  
          </div>
          
        </form>
      )}

      {status === 'error' && (
        <div style={{ color: 'red', marginTop: '15px' }}>
          <p><strong>Ocurrió un error:</strong> {error}</p>
          <button onClick={resetForm}>Intentar de nuevo</button>
        </div>
      )}

      {status === 'success' && resultado && (
        <div style={{ marginTop: '20px' }}>
          <h3>Análisis Completado</h3>
          <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '5px' }}>
            <h4>Solución Sugerida</h4>
            <p>{resultado.solucion_sugerida}</p>
            <hr />
            <h4>Palabras Clave Detectadas</h4>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {resultado.keywords_extraidas.map(kw => (
                <span key={kw} style={{ background: '#e0e0e0', padding: '4px 8px', borderRadius: '12px', fontSize: '14px' }}>{kw}</span>
              ))}
            </div>
          </div>
          <button onClick={resetForm} style={{ marginTop: '15px' }}>
            Crear otro ticket
          </button>
        </div>
      )}
    </div>
  );
}

export default HelpDeskIA;