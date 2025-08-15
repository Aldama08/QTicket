import React from 'react';
import { useState } from 'react'; 
import { createClient } from '@supabase/supabase-js'; 

// Configuración de Supabase 
const supabaseUrl = 'https://ibecmvmtlndaonohzxce.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImliZWNtdm10bG5kYW9ub2h6eGNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4MTA4NzQsImV4cCI6MjA1MzM4Njg3NH0.XBLqtGUJ3bPjrDgM6ZifZoJGOponRjfhd9YzFJ6yrL0';
// Cliente de Supabase
const supabase = createClient(supabaseUrl, supabaseKey);

const FASTAPI_BACKEND_URL = 'http://192.168.1.65:8000'; 


// Validación del Formulario 
// La función  recibe 'formData' como argumento
const validateForm = (formData) => {
  const errors = {};
  
  // Validar el campo 'email'
  if (!formData.email) { 
    errors.email = 'El email es obligatorio';
  } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
    errors.email = "Introduce un correo electrónico válido";
  }
  
  // Validar el campo 'nombre'
  if (!formData.nombre) { 
    errors.nombre = 'El nombre es obligatorio';
  }
  
  // Validar el campo 'rol'
  if (!formData.rol) { 
    errors.rol = 'El rol es obligatorio';
  }
  
  return errors;
}; 


function Register({ onRegister }) {
  // --- Estados del Componente ---
  // Estado para guardar los valores del formulario
  const [formData, setFormData] = useState({
    email: '',
    nombre: '',
    rol: ''
  });

  // Estado para guardar los errores de cada campo
  const [errors, setErrors] = useState({});

  // Estado para controlar si el formulario se está enviando (cargando)
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Manejo de Cambios en los Campos del Formulario 
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value //De donde viene el nombre del campo y el valor que se ha introducido. Ejemplo: { email: jose@email.com'
    });
  };

  //Envío del Formulario
  // const handleFormSubmit = async (e) => {
  //   e.preventDefault(); // Evita la recarga de la página
  //   setIsSubmitting(true); // Activa el estado de carga del botón

  //   const validationErrors = validateForm(formData);
  //   setErrors(validationErrors);

  //   // Si no hay errores de validación, procede a registrar
  //   if (Object.keys(validationErrors).length === 0) {
  //     try {
  //       const { data, error } = await supabase
  //         .from('usuarios')
  //         .insert([
  //           {
  //             nombre: formData.nombre, 
  //             email: formData.email,
  //             rol: formData.rol
  //           },
  //         ]);

  //       if (error) {
  //         throw error;
  //       }

  //       console.log("Usuario registrado con éxito:", data);
  //       onRegister(); 
  //     } catch (error) {
  //       console.error("Error al registrar el usuario:", error.message);
  //       setErrors({ general: 'Error al registrar. Inténtalo de nuevo.' });
  //     } finally {
  //       setIsSubmitting(false); // Desactiva el estado de carga
  //     }
  //   } else {
  //     setIsSubmitting(false); // Si hay errores, desactiva el estado de carga
  //   }
  // };
 //Envio formulario fastapi
 const handleFormSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const validationErrors = validateForm(formData);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length === 0) {
      try {
        // --- Conexión con tu backend de FastAPI ---
        console.log('Enviando datos a FastAPI para el registro...');
        const response = await fetch(`${FASTAPI_BACKEND_URL}/Register/procesar-datos`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData), // Envía los datos del formulario en formato JSON
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(`Error del backend: ${errorData.detail || 'Ocurrió un error en el servidor.'}`);
        }
        
        const dataResultado = await response.json();
        console.log('Registro exitoso:', dataResultado);
        onRegister(dataResultado);

      } catch (err) {
        console.error("Error al registrar el usuario:", err);
        setErrors({ general: err.message });
      } finally {
        setIsSubmitting(false);
      }
    } else {
      setIsSubmitting(false);
    }
  };
  // --- Renderizado del Componente ---
  return (
    <div>
      <h2>Página de Registro</h2>
      <form onSubmit={handleFormSubmit}>
        <div>
          <label htmlFor="nombre">Nombre:</label>
          <input type="text" id="nombre" name="nombre" value={formData.nombre} onChange={handleChange} />
          {errors.nombre && <p style={{ color: 'red' }}>{errors.nombre}</p>}
        </div>
        
        <div>
          <label htmlFor="email">Correo Electrónico:</label>
          <input type="email" id="email" name="email" value={formData.email} onChange={handleChange} />
          {errors.email && <p style={{ color: 'red' }}>{errors.email}</p>}
        </div>
        
        <div>
          <label htmlFor="rol">Rol:</label>
          <input type="text" id="rol" name="rol" value={formData.rol} onChange={handleChange} />
          {errors.rol && <p style={{ color: 'red' }}>{errors.rol}</p>}
        </div>

        {errors.general && <p style={{ color: 'red' }}>{errors.general}</p>}
        
        {/* El botón está deshabilitado si el formulario se está enviando */}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Registrando...' : 'Registrarse'}
        </button>
      </form>
    </div>
  );
}

export default Register;