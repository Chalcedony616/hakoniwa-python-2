import React from 'react';
import { useNavigate } from 'react-router-dom';
import RecentlyLog from './RecentlyLog';
import './AllCountryLog.css';

const AllCountryLog = () => {
    const navigate = useNavigate();
    return (
        <div className="all-country-log">
            <h1>最近の出来事</h1>
            <button className="back-button" onClick={() => navigate('/')}>トップへ戻る</button>
            <RecentlyLog mode="global" />
        </div>
    );
};

export default AllCountryLog;