import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Login.css';

const Login = () => {
    const [islands, setIslands] = useState([]);
    const [selectedIsland, setSelectedIsland] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/islands/`)
            .then(response => {
                setIslands(response.data);
            })
            .catch(error => console.error('Error fetching islands:', error));
    }, []);

    const handleLogin = (event) => {
        event.preventDefault();  // フォーム送信を防ぐ
    
        axios.post(`${process.env.REACT_APP_API_BASE_URL}/api/login/`, {
            username: username,
            password: password,
            island_id: selectedIsland,
        })
        .then(response => {
            if (response.data.message === "Login successful.") {
                // island_id がサーバーから正しく返っているか確認
                if (response.data.island_id) {
                    navigate('/development', { state: { loggedIn: true, currentIsland: response.data.island_id } });
                } else {
                    alert('Login failed: Missing island_id in the response.');
                }
            } else {
                alert('Login failed: ' + response.data.error);
            }
        })
        .catch(error => {
            console.error('Login error:', error);
            alert('Login failed: ' + (error.response?.data?.error || 'Unknown error'));
        });
    };
    

    return (
        <div className="login-container">
            <h2>開発画面へログイン</h2>
            <form onSubmit={handleLogin}
            className="login-form">
                <div className="form-group">
                    <label>島名：</label>
                    <select value={selectedIsland} onChange={(e) => setSelectedIsland(e.target.value)}>
                    <option value="">-----島を選択-----</option>
                        {islands.map(island => (
                            <option key={island.id} value={island.id}>{island.name}</option>
                        ))}
                    </select>
                </div>
                <div className="form-group">
                    <label>ユーザー名：</label>
                    <input 
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label>パスワード：</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>
                <button type="submit">ログイン</button>
            </form>
        </div>
    );
};

export default Login;
