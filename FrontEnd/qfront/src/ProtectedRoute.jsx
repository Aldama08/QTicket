import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ isAuth, children }) => {
  if (!isAuth) {
    // Si no está autenticado, lo redirige al registro.
    return <Navigate to="/register" replace />;
  }

  // Si está autenticado, renderiza el componente hijo.
  return children;
};

export default ProtectedRoute;