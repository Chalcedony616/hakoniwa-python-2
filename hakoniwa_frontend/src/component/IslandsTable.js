import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import units from '../units';
import './IslandsTable.css';
import prizeData from '../prizeData';

const IslandsTable = () => {
    const [islands, setIslands] = useState([]);

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/islands/`)
            .then(response => {
                setIslands(response.data);
            })
            .catch(error => console.error('Error fetching islands:', error));
    }, []);

    const renderPrizes = (island) => {
        const prizes = [];
        Object.keys(prizeData).forEach((key) => {
            if (island[key]) {  // islandオブジェクトに該当する賞があるかどうかを確認
                prizes.push(
                    <img
                        key={key}
                        src={prizeData[key].image}
                        alt={prizeData[key].name}
                        title={prizeData[key].name}
                        className="prize-image"
                    />
                );
            }
        });
        return prizes;
    };

    return (
        <div className="islands-table">
            <h2>島の一覧</h2>
            <table border="1">
                <thead>
                    <tr>
                        <th>順位</th>
                        <th>島</th>
                        <th>人口</th>
                        <th>資金</th>
                        <th>食料</th>
                        <th>面積</th>
                        <th>農場規模</th>
                        <th>工場規模</th>
                        <th>採掘場規模</th>
                    </tr>
                </thead>
                <tbody>
                    {islands.map((island, index) => (
                        <React.Fragment key={island.id}>
                            <tr>
                                <td rowSpan="2"><strong>{index + 1}</strong></td>
                                <td rowSpan="2">
                                    <Link 
                                        to={`/island/${island.id}`} 
                                        className={island.absent !== 0 ? 'absent-link' : 'active-link'}
                                    >
                                        {island.name}{island.absent !== 0 ? ` (${island.absent})` : ''}
                                    </Link>
                                    <div className="prizes">
                                        {renderPrizes(island)}
                                    </div>
                                </td>
                                <td>{`${island.population}${units.population}`}</td>
                                <td>{`${island.funds}${units.funds}`}</td>
                                <td>{`${island.food}${units.food}`}</td>
                                <td>{`${island.area}${units.area}`}</td>
                                <td>{`${island.farm_size}${units.farm_size}`}</td>
                                <td>{`${island.factory_size}${units.factory_size}`}</td>
                                <td>{`${island.mine_size}${units.mine_size}`}</td>
                            </tr>
                            <tr>
                                <td colSpan="7"><strong>{island.owner}</strong>：{island.comment}</td>
                            </tr>
                        </React.Fragment>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default IslandsTable;