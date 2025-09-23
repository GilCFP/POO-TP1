import React from 'react';
import './LoadingSpinner.css';

/**
 * Componente de loading spinner reutilizável
 */
const LoadingSpinner = ({ 
  size = 'medium', 
  message = 'Carregando...', 
  center = true,
  variant = 'primary' 
}) => {
  const sizeClasses = {
    small: 'spinner-sm',
    medium: 'spinner-md',
    large: 'spinner-lg'
  };

  const variantClasses = {
    primary: 'spinner-primary',
    secondary: 'spinner-secondary',
    white: 'spinner-white'
  };

  return (
    <div className={`loading-spinner ${center ? 'center' : ''}`}>
      <div className={`spinner ${sizeClasses[size]} ${variantClasses[variant]}`}>
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Carregando...</span>
        </div>
      </div>
      {message && (
        <div className="loading-message">
          {message}
        </div>
      )}
    </div>
  );
};

export default LoadingSpinner;