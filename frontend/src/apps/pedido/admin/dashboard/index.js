import React from 'react';
import { createRoot } from 'react-dom/client';
import AdminDashboard from './AdminDashboard';
import './dashboard.css';

// Inicializar o app quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('admin-root');
    
    if (container) {
        // Obter dados do template Django
        const adminDataElement = document.getElementById('admin-data');
        const adminData = adminDataElement ? JSON.parse(adminDataElement.textContent) : {};
        
        console.log('Dados do admin:', adminData);
        
        const root = createRoot(container);
        root.render(<AdminDashboard initialData={adminData} />);
    }
});