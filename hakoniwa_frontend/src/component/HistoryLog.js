import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './HistoryLog.css';

const HistoryLog = () => {
    const [histories, setHistories] = useState([]);

    useEffect(() => {
        const fetchHistories = async () => {
            try {
                const response = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/histories/`);
                setHistories(response.data);
            } catch (error) {
                console.error('Error fetching history records:', error);
            }
        };

        fetchHistories();
    }, []);

    return (
        <div className="history-list">
            <h2>発見の記録</h2>
            {histories.length > 0 ? (
                <ul>
                    {histories.map((history, index) => (
                        <li key={index}>
                            <div dangerouslySetInnerHTML={{ __html: history.message }} />
                        </li>
                    ))}
                </ul>            
            ) : (
                <p>発見の記録はありません。</p>
            )}
        </div>
    );
};

export default HistoryLog;
