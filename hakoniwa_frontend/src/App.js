import React from 'react';
import { Route, Routes } from 'react-router-dom';
import './App.css';
import IslandsTable from './component/IslandsTable';
import CreateUser from './component/CreateUser';
import CreateIsland from './component/CreateIsland';
import IslandView from './component/IslandView';
import Home from './component/Home';
import Login from './component/Login';
import DevelopmentView from './component/DevelopmentView';
import { LoginProvider } from './context/LoginContext';  // コンテキストのインポート
import AllCountryLog from './component/AllCountryLog';

function App() {
    return (
        <LoginProvider>
            <div className="App">
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/create-user" element={<CreateUser />} />
                    <Route path="/create-island" element={<CreateIsland />} />
                    <Route path="/island/:id" element={<IslandView />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/development" element={<DevelopmentView />} />
                    <Route path="/all-country-log" element={<AllCountryLog />} />
                </Routes>
            </div>
        </LoginProvider>
    );
}

export default App;
