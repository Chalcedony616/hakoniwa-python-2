import React, { createContext, useState } from 'react';

export const LoginContext = createContext();

export const LoginProvider = ({ children }) => {
    const [loggedIn, setLoggedIn] = useState(false);
    const [currentIsland, setCurrentIsland] = useState(null);

    const login = (island) => {
        setLoggedIn(true);
        setCurrentIsland(island);
    };

    const logout = () => {
        setLoggedIn(false);
        setCurrentIsland(null);
    };

    return (
        <LoginContext.Provider value={{ loggedIn, currentIsland, login, logout }}>
            {children}
        </LoginContext.Provider>
    );
};
