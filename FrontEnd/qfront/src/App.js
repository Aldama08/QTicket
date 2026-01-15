import React, { useState } from 'react';
import HelpDeskIA from './page';
import Register from './register';

const FASTAPI_BACKEND_URL = 'http://127.0.0.1:8000';

function App() {
  const [userData, setuserData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleRegister = async (datosUsuario) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${FASTAPI_BACKEND_URL}/registrar-o-validar-usuario`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datosUsuario),
      });
      if (!response.ok) throw new Error('Error en el registro');
      const userResponseData = await response.json();
      setuserData(userResponseData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Esta es la función que SÍ existe en App.js
  const handleLogout = () => {
    setuserData(null);
  };

  return (
      <div className="App">
        {!userData ? (
            <Register onRegister={handleRegister} />
        ) : (
            /* REVISA ESTA LÍNEA:
               Propiedad: onLogout
               Valor: {handleLogout}
            */
            <HelpDeskIA userData={userData} onLogout={handleLogout} />
        )}
      </div>
  );
}

export default App;