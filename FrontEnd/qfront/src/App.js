// App.js
import React, { useState } from 'react';

import HelpDeskIA from './page';
import Register from './register';

const FASTAPI_BACKEND_URL = 'http://127.0.0.1:8000'

function App() {
  // null ya que no hay ningun usuario, hace que sea un objeto que guarde los datos del usuario como objeto. Siendo userData email, nombre, rol
  const [userData, setuserData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false)

  const handleRegister = async (datosUsuario) => {
    setLoading(true);
    setError(null);


  try {
  const response = await fetch(`${FASTAPI_BACKEND_URL}/registrar-o-validar-usuario`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  // Envía los datos del formulario (email, nombre, rol)
  body: JSON.stringify(datosUsuario),
  });

  if (!response.ok) {
  const errorData = await response.json();
  throw new Error(errorData.detail || 'Fallo en la validación/registro del usuario.');
  }

  // 3. Guardar le respuesta del backend (que contiene el 'id')
  const userResponseData = await response.json();
  setuserData(userResponseData); // userResponseData ahora tiene el 'id'
  } catch (err) {
    console.error("Error en registro/login:", err);
    setError(err.message);
    setuserData(null); // Asegurar que no se muestre el HelpDesk si falla
  } finally {
    setLoading(false);
  } 
};

  return (
    <div className="App">
      {
        // 3. La condición ahora es: si NO hay datos de usuario (`userData` es `null`)...
        !userData ? (
          // ...muestra el componente de registro y pásale la función.
          <Register onRegister={handleRegister} />
        ) : (
          // 4. Si SÍ hay datos de usuario, muestra el componente del Help Desk
          <HelpDeskIA userData={userData} />
        )
      }
    </div>
  );
}

export default App;