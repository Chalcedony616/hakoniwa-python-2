import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import Spinner from './Spinner';
import IslandsTable from './IslandsTable';
import HistoryLog from './HistoryLog';
import TurnInfo from './TurnInfo';
import './Home.css';

const Home = () => {
    const [isLoading, setIsLoading] = useState(true);  // ロード中かどうかを管理

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/turn_info/`)  // API エンドポイントが正しいか確認
            .then(response => {
                setIsLoading(false);  // データ取得後にロード完了
            })
            .catch(error => {
                console.error("Error fetching data:", error);
                setIsLoading(false);  // エラー時にもロードを終了
            });
    }, []);

    if (isLoading) {
        return <Spinner />;  // ロード中はスピナーを表示
    }

    return (
        <div>
            <header className="App-header">
                <h1 className="header-title">箱庭諸島２ for Python</h1>
                <nav className="header-links">
                    <Link to="/create-user">ユーザー登録</Link>
                    <Link to="/create-island">島の発見</Link>
                    <Link to="/login">ログイン</Link>
                    <Link to="/all-country-log">最近の出来事</Link>
                </nav>
            </header>
            <TurnInfo />
            <IslandsTable />
            <HistoryLog />
        </div>
    );
};

export default Home;
