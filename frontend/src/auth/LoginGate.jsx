import React, { useState, useEffect } from 'react';
import { AuthService } from './AuthService';
import LoginScreen from './LoginScreen';

const LoginGate = ({ children }) => {
    const [authenticated, setAuthenticated] = useState(AuthService.isAuthenticated());

    useEffect(() => {
        const isAuth = AuthService.isAuthenticated();
        console.log('[LoginGate] Initialized, authenticated:', isAuth);
        setAuthenticated(isAuth);
    }, []);

    const handleLogin = (user) => {
        console.log('[LoginGate] Login recognized for:', user);
        setAuthenticated(true);
    };

    if (!authenticated) {
        return <LoginScreen onLogin={handleLogin} />;
    }

    return (
        <div className="auth-gate-success">
            {children}
        </div>
    );
};

export default LoginGate;
