import React, { useState } from 'react';
import axios from 'axios';
import './CreateIsland.css';  // スタイルシートをインポート

const CreateIsland = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [ownerName, setOwnerName] = useState('');
    const [islandName, setIslandName] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/create_island/', {
                username,
                password,
                owner_name: ownerName,
                island_name: islandName
            });
            setSuccess('Island created successfully!');
            setError(null);
        } catch (error) {
            if (error.response && error.response.data && error.response.data.error) {
                setError(error.response.data.error);
            } else {
                setError('Failed to create island.');
            }
            setSuccess(null);
        }
    };

    return (
        <div className="create-island-container">
            <h2>島の発見</h2>
            <form onSubmit={handleSubmit} className="create-island-form">
                <div className="form-group">
                    <label>ユーザー名：</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>パスワード：</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>所有者名：</label>
                    <input
                        type="text"
                        value={ownerName}
                        onChange={(e) => setOwnerName(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>島名：</label>
                    <input
                        type="text"
                        value={islandName}
                        onChange={(e) => setIslandName(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">島を発見する</button>
            </form>
            {error && <p className="error">{error}</p>}
            {success && <p className="success">{success}</p>}
        </div>
    );
};

export default CreateIsland;
