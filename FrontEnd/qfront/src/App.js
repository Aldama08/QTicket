// App.js
import React, { useState } from 'react';

import HelpDeskIA from './page';
import Register from './register';

function App() {
  // Estado para saber si el usuario se ha registrado.
  const [isRegistered, setIsRegistered] = useState(false);

  const handleRegister = () => {
    // Al llamar a esta función, el estado cambia a `true`
    setIsRegistered(true);
  };

  return (
    <div>
      {/* Si `isRegistered` es `false`, muestra el componente de registro. */}
      {!isRegistered ? (
        <Register onRegister={handleRegister} />
      ) : (
        // Si `isRegistered` es `true`, muestra el componente principal.
        <HelpDeskIA />
      )}
    </div>
  );
}

export default App;