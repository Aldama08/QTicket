// register.js
import React from 'react';

function Register({ onRegister }) {
  const handleFormSubmit = (e) => {
    e.preventDefault();
    // Lógica de validación del formulario
    
    // Llama a la función del componente padre para cambiar el estado
    onRegister();
  };

  return (
    <div>
      <h2>Página de Registro</h2>
      <form onSubmit={handleFormSubmit}>
        {/* Tu formulario de registro */}
        <button type="submit">Registrarse</button>
      </form>
    </div>
  );
}

export default Register;