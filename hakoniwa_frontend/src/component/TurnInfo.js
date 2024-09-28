import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './TurnInfo.css';

const TurnInfo = () => {
    const [turnInfo, setTurnInfo] = useState({
        current_turn: '',
        last_update_time: '',
        next_update_time: '',
        time_remaining: ''
    });

    useEffect(() => {
        // Fetch the turn information from the backend
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/turn_info/`)
            .then(response => {
                setTurnInfo(prevState => ({
                    ...response.data,
                    time_remaining: calculateTimeRemaining(response.data.next_update_time)  // 初回ロード時に残り時間を計算
                }));
            })
            .catch(error => {
                console.error("Error fetching turn info:", error);
            });

        // Set up a timer to refresh the time remaining every second
        const timer = setInterval(() => {
            setTurnInfo(prevState => ({
                ...prevState,
                time_remaining: calculateTimeRemaining(prevState.next_update_time)
            }));
        }, 1000);

        return () => clearInterval(timer); // Clean up the interval on component unmount
    }, [turnInfo.next_update_time]);

    const calculateTimeRemaining = (nextUpdateTime) => {
        const now = new Date();
        const nextUpdate = new Date(nextUpdateTime);
        const timeDiff = nextUpdate - now;

        // 時間差がマイナスの場合、「ターン更新時刻になりました！」を返す
        if (timeDiff <= 0) {
            return "ターン更新時刻になりました！";
        }

        const hours = Math.floor(timeDiff / 1000 / 60 / 60);
        const minutes = Math.floor((timeDiff / 1000 / 60) % 60);
        const seconds = Math.floor((timeDiff / 1000) % 60);

        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    };

    return (
        <div className="turn-info-container">
            <h2>ターン {turnInfo.current_turn}</h2>
            <p>最終更新時刻: {turnInfo.last_update_time}</p>
            <p>次回更新時刻: {turnInfo.next_update_time}</p>
            <p className="time-remaining">次回更新まで: {turnInfo.time_remaining}</p>
        </div>
    );
};

export default TurnInfo;
