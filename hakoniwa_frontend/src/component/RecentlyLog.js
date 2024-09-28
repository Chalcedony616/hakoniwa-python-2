import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './RecentlyLog.css';

const RecentlyLog = ({ islandId, mode, includeConfidential }) => {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                let response;
                if (mode === 'global') {
                    // グローバルモードの場合、すべての島のログを取得
                    response = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/global-logs/`);
                } else {
                    // 特定の島のログを取得
                    response = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/islands/${islandId}/logs/`);
                }
                
                // 極秘ログのフィルタリング
                const filteredLogs = includeConfidential
                    ? response.data  // 極秘ログを表示する場合、全てのログを表示
                    : response.data.filter(log => !log.is_confidential);  // 極秘ログを表示しない場合、フィルタリング

                setLogs(filteredLogs);
            } catch (error) {
                console.error('Error fetching logs:', error);
            }
        };

        fetchLogs();
    }, [islandId, mode, includeConfidential]);

    return (
        <div className="log-list">
            <h2>最近の出来事</h2>
            <div className="logs">
                {logs.length > 0 ? (
                    Object.entries(
                        logs.reduce((acc, log) => {
                            if (!acc[log.turn]) {
                                acc[log.turn] = [];
                            }
                            acc[log.turn].push(log);
                            return acc;
                        }, {})
                    )
                    .sort(([turnA], [turnB]) => turnB - turnA)
                    .map(([turn, turnLogs], index) => (
                        <div key={turn}>
                            {turnLogs.slice().reverse().map((log, logIndex) => (
                                <div key={logIndex} dangerouslySetInnerHTML={{ __html: log.message }} />
                            ))}
                            {index < logs.length - 1 && <hr />}
                        </div>
                    ))
                ) : (
                    <p>ログがありません</p>
                )}
            </div>
        </div>
    );
};

export default RecentlyLog;
