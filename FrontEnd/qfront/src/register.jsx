import React, { useState } from 'react';
import './register.css';
import logo from './media/logo.jpg'; // Asegúrate de tener esta imagen

const validateForm = (formData) => {
  const errors = {};
  if (!formData.email) errors.email = 'El email es obligatorio';
  else if (!/\S+@\S+\.\S+/.test(formData.email)) errors.email = "Introduce un correo válido";
  if (!formData.nombre) errors.nombre = 'El nombre es obligatorio';
  if (!formData.rol) errors.rol = 'El rol es obligatorio';
  return errors;
};

// Recibe la función onRegister desde App.js
function Register({ onRegister }) {
  const [formData, setFormData] = useState({ email: '', nombre: '', rol: '' });
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    const validationErrors = validateForm(formData);
    setErrors(validationErrors);

    // Si no hay errores, llama a la función de App.js y le pasa los datos
    if (Object.keys(validationErrors).length === 0) {
      onRegister(formData);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-overlay" />
      <main className="auth-container">
        <section className="auth-card">
          <img src={logo} alt="QTicket" className="brand" />
          <h2 className="auth-title">Crea tu cuenta</h2>
          <p className="auth-subtitle">Completa tus datos para continuar</p>

          <form onSubmit={handleFormSubmit} className="auth-form" noValidate>
            {/* ... Tu JSX para los inputs de nombre, email, rol ... (sin cambios) */}
             <div className="form-group">
               <label htmlFor="nombre">Nombre</label>
               <input className={`input ${errors.nombre ? 'input-error' : ''}`} type="text" id="nombre" name="nombre" value={formData.nombre} onChange={handleChange} />
               {errors.nombre && <p className="error-text">{errors.nombre}</p>}
             </div>
             <div className="form-group">
               <label htmlFor="email">Correo electrónico</label>
               <input className={`input ${errors.email ? 'input-error' : ''}`} type="email" id="email" name="email" value={formData.email} onChange={handleChange} />
               {errors.email && <p className="error-text">{errors.email}</p>}
             </div>
             <div className="form-group">
               <label htmlFor="rol">Rol</label>
               <input className={`input ${errors.rol ? 'input-error' : ''}`} type="text" id="rol" name="rol" value={formData.rol} onChange={handleChange} />
               {errors.rol && <p className="error-text">{errors.rol}</p>}
             </div>
            <button type="submit" className="btn-primary">Continuar</button>
          </form>
        </section>
      </main>
    </div>
  );
}

export default Register;