// App.js
import React, { useState } from 'react';

import HelpDeskIA from './page';
import Register from './register';

function App() {
  // null ya que no hay ningun usuario, hace que sea un objeto que guarde los datos del usuario como objeto. Siendo userData email, nombre, rol
  const [userData, setuserData] = useState(null);

  const handleRegister = (datosUsuario) => {
    setuserData(datosUsuario);
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