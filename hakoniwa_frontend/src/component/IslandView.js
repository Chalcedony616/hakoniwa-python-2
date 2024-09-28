import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import units from '../units';
import Spinner from './Spinner';
import terrainData from '../terrainData';
import './IslandView.css';
import RecentlyLog from './RecentlyLog';

const IslandView = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [island, setIsland] = useState(null);
    const [images, setImages] = useState({});
    const [allImagesLoaded, setAllImagesLoaded] = useState(false);
    const canvasRef = useRef(null);
    const tooltipRef = useRef(null);

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/islands/${id}/`)
            .then(response => {
                setIsland(response.data);
            })
            .catch(error => console.error('Error fetching island data:', error));
    }, [id]);

    useEffect(() => {
        const loadImages = async () => {
            const images = {};
            const promises = [];

            for (const [key, { imageList }] of Object.entries(terrainData)) {
                imageList.forEach((imageSrc, index) => {
                    const img = new Image();
                    img.src = imageSrc;
                    const promise = new Promise((resolve, reject) => {
                        img.onload = () => {
                            images[`${key}-${index}`] = img; // terrain IDとindexで一意に識別
                            resolve();
                        };
                        img.onerror = () => {
                            console.error(`Failed to load image ${imageSrc} for terrain ID ${key}`);
                            reject();
                        };
                    });
                    promises.push(promise);
                });
            }

            const xbar = new Image();
            xbar.src = `${process.env.PUBLIC_URL}/images/xbar.gif`;
            const xbarPromise = new Promise((resolve, reject) => {
                xbar.onload = () => {
                    images['xbar'] = xbar;
                    resolve();
                };
                xbar.onerror = () => {
                    console.error('Failed to load xbar image');
                    reject();
                };
            });
            promises.push(xbarPromise);

            for (let i = 0; i < 12; i++) {
                const space = new Image();
                space.src = `${process.env.PUBLIC_URL}/images/space${i}.gif`;
                const spacePromise = new Promise((resolve, reject) => {
                    space.onload = () => {
                        images[`space${i}`] = space;
                        resolve();
                    };
                    space.onerror = () => {
                        console.error(`Failed to load space${i} image`);
                        reject();
                    };
                });
                promises.push(spacePromise);
            }

            try {
                await Promise.all(promises);
                setImages(images);
                setAllImagesLoaded(true);
            } catch (error) {
                console.error('Failed to load one or more images');
                setAllImagesLoaded(false); // 読み込み失敗時のフォールバック
            }
        };

        loadImages();
    }, []);

    useEffect(() => {
        if (island && allImagesLoaded) {
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');
            const tileSize = 32;
            const spaceSize = { width: 16, height: 32 };
            const xbarHeight = 16;

            const drawMap = () => {
                ctx.drawImage(images['xbar'], 0, 0, 400, xbarHeight);

                for (let y = 0; y < island.map_data.length; y++) {
                    if (y % 2 === 0) {
                        ctx.drawImage(images[`space${y}`], 0, xbarHeight + y * spaceSize.height, spaceSize.width, spaceSize.height);
                        for (let x = 0; x < island.map_data[y].length; x++) {
                            const terrainId = island.map_data[y][x].terrain;
                            const landvalue = island.map_data[y][x].landvalue;
                            const terrainImageFunc = terrainData[terrainId].touristImage; 
                            const terrainImage = terrainImageFunc(landvalue);
                
                            // 画像を取得する際にキーを正しく指定
                            const terrainImageObj = Object.values(images).find(img => img.src.includes(terrainImage));
                
                            if (terrainImageObj) {
                                const posX = spaceSize.width + x * tileSize;
                                const posY = xbarHeight + y * tileSize;
                                ctx.drawImage(terrainImageObj, posX, posY, tileSize, tileSize);
                            }
                        }
                    } else {
                        for (let x = 0; x < island.map_data[y].length; x++) {
                            const terrainId = island.map_data[y][x].terrain;
                            const landvalue = island.map_data[y][x].landvalue;
                            const terrainImageFunc = terrainData[terrainId].touristImage; 
                            const terrainImage = terrainImageFunc(landvalue);
                
                            // 画像を取得する際にキーを正しく指定
                            const terrainImageObj = Object.values(images).find(img => img.src.includes(terrainImage));
                
                            if (terrainImageObj) {
                                const posX = x * tileSize;
                                const posY = xbarHeight + y * tileSize;
                                ctx.drawImage(terrainImageObj, posX, posY, tileSize, tileSize);
                            }
                        }
                        ctx.drawImage(images[`space${y}`], 400 - spaceSize.width, xbarHeight + y * spaceSize.height, spaceSize.width, spaceSize.height);
                    }
                }            
            };

            drawMap();

            const handleMouseMove = (event) => {
                const rect = canvas.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;

                // y座標をタイルサイズで割って行を取得
                const row = Math.floor((y - xbarHeight) / tileSize);

                // 行が偶数か奇数かでx座標の計算方法を分ける
                let col;
                if (row % 2 === 0) {
                    // 偶数行の場合、spaceSize.widthを引いてからタイルサイズで割る
                    col = Math.floor((x - spaceSize.width) / tileSize);
                } else {
                    // 奇数行の場合、spaceSize.widthを引かずにタイルサイズで割る
                    col = Math.floor(x / tileSize);
                }

                if (row >= 0 && row < island.map_data.length && col >= 0 && col < island.map_data[0].length) {
                    const cell = island.map_data[row][col];
                    const { terrain, landvalue } = cell;
                    const tooltipContent = `(${col},${row}) ${typeof terrainData[terrain].touristTooltip === 'function'
                        ? terrainData[terrain].touristTooltip(landvalue)
                        : terrainData[terrain].touristTooltip}`;

                    const tooltip = tooltipRef.current;
                    tooltip.style.left = `${event.clientX + 10}px`;
                    tooltip.style.top = `${event.clientY + 10}px`;
                    tooltip.innerHTML = tooltipContent;
                    tooltip.style.display = 'block';
                } else {
                    tooltipRef.current.style.display = 'none';
                }
            };

            const handleMouseLeave = () => {
                const tooltip = tooltipRef.current;
                if (tooltip) {
                    tooltip.style.display = 'none';
                }
            };

            canvas.addEventListener('mousemove', handleMouseMove);
            canvas.addEventListener('mouseleave', handleMouseLeave);

            return () => {
                canvas.removeEventListener('mousemove', handleMouseMove);
                canvas.removeEventListener('mouseleave', handleMouseLeave);
            };
        }
    }, [island, images, allImagesLoaded]);
    
    if (!island) {
        return (
            <div className="island-view-failed">
                <h1>島がありません！</h1>
                <button className="back-button" onClick={() => navigate('/')}>トップへ戻る</button>
            </div>
        );
    }

    return (
        <div className="island-view">
            <h1>{island.name}へようこそ！！</h1>
            <button className="back-button" onClick={() => navigate('/')}>トップへ戻る</button>
            <table border="1" className="status-table">
                <thead>
                    <tr>
                        <th>順位</th>
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
                    <tr>
                        <td>1</td>
                        <td>{`${island.population}${units.population}`}</td>
                        <td>{`${island.funds}${units.funds}`}</td>
                        <td>{`${island.food}${units.food}`}</td>
                        <td>{`${island.area}${units.area}`}</td>
                        <td>{`${island.farm_size}${units.farm_size}`}</td>
                        <td>{`${island.factory_size}${units.factory_size}`}</td>
                        <td>{`${island.mine_size}${units.mine_size}`}</td>
                    </tr>
                </tbody>
            </table>
            <canvas ref={canvasRef} width={400} height={400} />
            <div ref={tooltipRef} className="tooltip"></div>
            <RecentlyLog mode="island" islandId={island.id} includeConfidential={false} />
        </div>
    );
};

export default IslandView;
