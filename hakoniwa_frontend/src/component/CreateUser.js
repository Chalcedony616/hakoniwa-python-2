import React, { useState } from 'react';
import axios from 'axios';
import './CreateUser.css';  // スタイルシートをインポート

const CreateUser = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');  // パスワード確認用
    const [email, setEmail] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }
        try {
            const response = await axios.post('http://127.0.0.1:8000/accounts/register/', {
                username,
                password,
                email
            });
            setSuccess('User created successfully!');
            setError(null);
        } catch (error) {
            if (error.response && error.response.data && error.response.data.error) {
                setError(error.response.data.error);
            } else {
                setError('Failed to create user.');
            }
            setSuccess(null);
        }
    };

    return (
        <div className="create-user-container">
            <h2>ユーザー登録</h2>
            <form onSubmit={handleSubmit} className="create-user-form">
                <div className="form-group">
                    <label>ユーザ名：</label>
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
                    <label>パスワード確認：</label>
                    <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>メールアドレス：</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">ユーザー登録</button>
            </form>
            {error && (
                <div className="error">
                    {Array.isArray(error) ? (
                        <ul>
                            {error.map((err, index) => (
                                <li key={index}>{err}</li>
                            ))}
                        </ul>
                    ) : (
                        <p>{error}</p>
                    )}
                </div>
            )}
            {success && <p className="success">{success}</p>}
        </div>
    );
};

export default CreateUser;
