import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import units from '../units';
import Spinner from './Spinner';
import terrainData from '../terrainData';
import commandData from '../commandData';
import './DevelopmentView.css';
import RecentlyLog from './RecentlyLog';

const DevelopmentView = () => {
    const [isLoading, setIsLoading] = useState(true);  // ロード中かどうかを管理
    const location = useLocation();
    const navigate = useNavigate();
    const { loggedIn, currentIsland } = location.state || {}; 
    const [island, setIsland] = useState(null);
    const [images, setImages] = useState({});
    const [allImagesLoaded, setAllImagesLoaded] = useState(false);
    const [targetIslandNames, setTargetIslandNames] = useState({}); 
    const canvasRef = useRef(null);
    const tooltipRef = useRef(null);
    const popupRef = useRef(null);
    const [popupVisible, setPopupVisible] = useState(false);
    const [popupPosition, setPopupPosition] = useState({ x: 0, y: 0 });
    const [selectedCommandIndex, setSelectedCommandIndex] = useState(null);
    const [selectedCommand, setSelectedCommand] = useState('');
    const [xCoord, setXCoord] = useState(0);
    const [yCoord, setYCoord] = useState(0);
    const [quantity, setQuantity] = useState(0);
    const [targetIsland, setTargetIsland] = useState(currentIsland);
    const [islands, setIslands] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [isEditing, setIsEditing] = useState(false);
    const [displayedPlans, setDisplayedPlans] = useState(
        Array.from({ length: 30 }, (_, i) => ({
            command: 0,
            coordinates: "0,0",
            quantity: 0,
            target_island_id: null,
        }))
    );
    const [name, setName] = useState('');
    const [owner, setOwner] = useState('');
    const [comment, setComment] = useState('');
    const [isSaveDisabled, setIsSaveDisabled] = useState(true);

    useEffect(() => {
        if (loggedIn && currentIsland) {
            axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/islands/${currentIsland}/`)
                .then(async response => {
                    setIsland(response.data);

                    // すべての島のリストを取得してtargetIslandNamesに設定
                    axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/islands/`)
                        .then(islandsResponse => {
                            const allIslands = islandsResponse.data;
                            setIslands(allIslands);

                            const names = {};
                            allIslands.forEach(island => {
                                names[island.id] = island.name;
                            });
                            setTargetIslandNames(names);

                            setTargetIsland(currentIsland); 
                        })
                        .catch(error => console.error('Error fetching islands:', error));
                    
                    setIsLoading(false);  // データ取得後にロード完了
                })
                .catch(error => console.error('Error fetching island data:', error));

            axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/islands/`)
                .then(response => setIslands(response.data))
                .catch(error => console.error('Error fetching islands:', error));
        }
    }, [loggedIn, currentIsland]);

    useEffect(() => {
        const firstCommand = Object.keys(commandData)[0];
        setSelectedCommand(firstCommand);
    }, []);

    useEffect(() => {
        // 初期データの取得
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/islands/${currentIsland}/`)
            .then(response => {
                const data = response.data;
                setIsland(data);
                setName(data.name);
                setOwner(data.owner);
                setComment(data.comment);
            })
            .catch(error => console.error('Error fetching island data:', error));
    }, [currentIsland]);

    useEffect(() => {
        // フィールドが変更されたら保存ボタンを有効にする
        if (island && (name !== island.name || owner !== island.owner || comment !== island.comment)) {
            setIsSaveDisabled(false);
        } else {
            setIsSaveDisabled(true);
        }
    }, [name, owner, comment, island]);

    const getPlanDescription = (plan) => {
        const command = commandData[plan.command];
        if (!command) {
            return "不明なコマンド";
        }

        const args = {
            coordinates: plan.coordinates,
            target_island: targetIslandNames[plan.target_island_id] || '不明な島',
            quantity: plan.quantity,
        };

        if (plan.quantity === 0) {
            return typeof command.description === 'function'
                ? command.description(args)
                : command.description;
        } else {
            return typeof command.description_q === 'function'
                ? command.description_q(args)
                : command.description_q;
        }
    };

    const generatePopupContent = () => {
        const developmentCommands = Object.keys(commandData).filter(
            (key) => commandData[key].category === 'development'
        );

        const constructionCommands = Object.keys(commandData).filter(
            (key) => commandData[key].category === 'construction'
        );

        return (
            <>
                {developmentCommands.map((command) => (
                    <div
                        key={command}
                        onClick={() => handlePopupCommandSelect(command)}
                    >
                        {commandData[command].name}
                    </div>
                ))}
                <hr />
                {constructionCommands.map((command) => (
                    <div
                        key={command}
                        onClick={() => handlePopupCommandSelect(command)}
                    >
                        {commandData[command].name}
                    </div>
                ))}
            </>
        );
    };

    const handlePopupCommandSelect = (command) => {
        const planNumberElement = document.querySelector('select[name="planNumber"]');
        const currentPlanNumber = parseInt(planNumberElement.value, 10);

        if (currentPlanNumber >= 1 && currentPlanNumber <= 30) {
            const newPlan = {
                command: command,
                coordinates: `${xCoord},${yCoord}`,
                quantity: quantity || 0,
                target_island_id: targetIsland,
            };

            setDisplayedPlans((prevPlans) => {
                const newPlans = [...prevPlans];
                for (let i = 29; i > currentPlanNumber - 1; i--) {
                    newPlans[i] = newPlans[i - 1];
                }
                newPlans[currentPlanNumber - 1] = newPlan;
                return newPlans;
            });

            if (currentPlanNumber < 30) {
                planNumberElement.value = currentPlanNumber + 1;
            }

            setSelectedCommandIndex(currentPlanNumber);
            setIsEditing(true);
        }
        setPopupVisible(false);
    };

    useEffect(() => {
        const handleOutsideClick = (event) => {
            if (popupRef.current && !popupRef.current.contains(event.target)) {
                setPopupVisible(false);
            }
        };

        document.addEventListener('mousedown', handleOutsideClick);

        return () => {
            document.removeEventListener('mousedown', handleOutsideClick);
        };
    }, []);

    const handlePlanClick = (index) => {
        setSelectedCommandIndex(index);
        document.querySelector('select[name="planNumber"]').value = index + 1;
    };    

    const handleInsert = () => {
        const planNumberElement = document.querySelector('select[name="planNumber"]');
        const currentPlanNumber = parseInt(planNumberElement.value, 10);
    
        if (currentPlanNumber >= 1 && currentPlanNumber <= 30) {
            const newPlan = {
                command: selectedCommand,
                coordinates: `${xCoord},${yCoord}`,
                quantity: quantity || 0,
                target_island_id: targetIsland,
            };
    
            setDisplayedPlans((prevPlans) => {
                const newPlans = [...prevPlans];
                for (let i = 29; i > currentPlanNumber - 1; i--) {
                    newPlans[i] = newPlans[i - 1];
                }
                newPlans[currentPlanNumber - 1] = newPlan;
                return newPlans;
            });

            if (currentPlanNumber < 30) {
                planNumberElement.value = currentPlanNumber + 1;
            }

            // 計画一覧でハイライトされている場所を更新
            setSelectedCommandIndex(currentPlanNumber);

            setIsEditing(true);
        }
    };    

    const handleOverwrite = () => {
        const planNumberElement = document.querySelector('select[name="planNumber"]');
        const currentPlanNumber = parseInt(planNumberElement.value, 10);
    
        if (currentPlanNumber >= 1 && currentPlanNumber <= 30) {
            const newPlan = {
                command: selectedCommand,
                coordinates: `${xCoord},${yCoord}`,
                quantity: quantity || 0,
                target_island_id: targetIsland,
            };
    
            setDisplayedPlans((prevPlans) => {
                const newPlans = [...prevPlans];
                newPlans[currentPlanNumber - 1] = newPlan; 
                return newPlans;
            });

            setIsEditing(true);
        }
    };
    
    const handleDelete = () => {
        const planNumberElement = document.querySelector('select[name="planNumber"]');
        const currentPlanNumber = parseInt(planNumberElement.value, 10);
    
        if (currentPlanNumber >= 1 && currentPlanNumber <= 30) {
            setDisplayedPlans((prevPlans) => {
                const newPlans = [...prevPlans];
                for (let i = currentPlanNumber - 1; i < 29; i++) {
                    newPlans[i] = newPlans[i + 1];
                }
                newPlans[29] = {
                    command: 0,
                    coordinates: "0,0",
                    quantity: 0,
                    target_island_id: currentIsland,
                };
                return newPlans;
            });
            setIsEditing(true);
        }
    };

    const handleCommandChange = (event) => {
        setSelectedCommand(event.target.value);
    };

    const handleCoordChange = (event, coordType) => {
        const value = parseInt(event.target.value, 10);
        if (coordType === 'x') {
            setXCoord(value);
        } else if (coordType === 'y') {
            setYCoord(value);
        }
    };

    const handleQuantityChange = (event) => {
        const value = event.target.value;
    
        if (value === "") {
            setQuantity("");
        } else {
            const numericValue = parseInt(value, 10);
            if (numericValue >= 0 && numericValue <= 99) {
                setQuantity(numericValue);
            } else {
                alert('数量は0から99の範囲で入力してください。');
            }
        }
    };    

    const handleMoveUp = () => {
        const planNumberElement = document.querySelector('select[name="planNumber"]');
        const currentPlanNumber = parseInt(planNumberElement.value, 10);
    
        if (currentPlanNumber > 1) {
            const newPlanNumber = currentPlanNumber - 1;
    
            setDisplayedPlans((prevPlans) => {
                const newPlans = [...prevPlans];
                const temp = newPlans[newPlanNumber - 1];
                newPlans[newPlanNumber - 1] = newPlans[currentPlanNumber - 1];
                newPlans[currentPlanNumber - 1] = temp;
                return newPlans;
            });
    
            // 更新後のplanNumberElementの値に合わせてハイライトを変更
            planNumberElement.value = newPlanNumber;
            setSelectedCommandIndex(newPlanNumber - 1);
    
            setIsEditing(true);
        }
    };

    const handleMoveDown = () => {
        const planNumberElement = document.querySelector('select[name="planNumber"]');
        const currentPlanNumber = parseInt(planNumberElement.value, 10);
    
        if (currentPlanNumber < 30) {
            const newPlanNumber = currentPlanNumber + 1;
    
            setDisplayedPlans((prevPlans) => {
                const newPlans = [...prevPlans];
                const temp = newPlans[currentPlanNumber - 1];
                newPlans[currentPlanNumber - 1] = newPlans[newPlanNumber - 1];
                newPlans[newPlanNumber - 1] = temp;
                return newPlans;
            });

            // 更新後のplanNumberElementの値に合わせてハイライトを変更
            planNumberElement.value = newPlanNumber;
            setSelectedCommandIndex(newPlanNumber - 1);

            setIsEditing(true);
        }
    };

    const handleTargetCapture = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/islands/${targetIsland}/`);
            const targetIslandData = response.data;
    
            const touristImages = {};
            const imagePromises = [];
    
            for (const [key, { imageList }] of Object.entries(terrainData)) {
                imageList.forEach((imageSrc, index) => {
                    const img = new Image();
                    img.src = `${process.env.PUBLIC_URL}${imageSrc}`;
                    const promise = new Promise((resolve, reject) => {
                        img.onload = () => {
                            touristImages[`${key}-${index}`] = img;
                            resolve();
                        };
                        img.onerror = () => {
                            console.error(`Failed to load image ${imageSrc} for terrain ID ${key}`);
                            reject();
                        };
                    });
                    imagePromises.push(promise);
                });
            }
    
            const xbar = new Image();
            xbar.src = `${process.env.PUBLIC_URL}/images/xbar.gif`;
            const xbarPromise = new Promise((resolve, reject) => {
                xbar.onload = () => {
                    touristImages['xbar'] = xbar;
                    resolve();
                };
                xbar.onerror = () => {
                    console.error('Failed to load xbar image');
                    reject();
                };
            });
            imagePromises.push(xbarPromise);
    
            for (let i = 0; i < 12; i++) {
                const space = new Image();
                space.src = `${process.env.PUBLIC_URL}/images/space${i}.gif`;
                const spacePromise = new Promise((resolve, reject) => {
                    space.onload = () => {
                        touristImages[`space${i}`] = space;
                        resolve();
                    };
                    space.onerror = () => {
                        console.error(`Failed to load space${i} image`);
                        reject();
                    };
                });
                imagePromises.push(spacePromise);
            }
    
            await Promise.all(imagePromises);
    
            const newWindow = window.open('', '_blank', 'width=600,height=600');
    
            const newDocument = newWindow.document;
            newDocument.write(`
                <html>
                <head>
                    <title>目標捕捉</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; background-color: AliceBlue; }
                        .header { margin-top: 20px; font-size: 20px; }
                        .close-button { margin-top: 20px; padding: 10px 20px; font-size: 16px; cursor: pointer; }
                        .map-container { margin-top: 20px; position: relative; }
                        .tooltip { position: absolute; background-color: #333; color: #fff; padding: 5px; border-radius: 5px; display: none; z-index: 10; }
                    </style>
                </head>
                <body>
                    <div class="header">${targetIslandData.name}のマップ</div>
                    <button class="close-button">ウィンドウを閉じる</button>
                    <div class="map-container">
                        <canvas id="target-map" width="400" height="400"></canvas>
                        <div class="tooltip"></div>
                    </div>
                </body>
                </html>
            `);
    
            const closeButton = newDocument.querySelector('.close-button');
            closeButton.addEventListener('click', () => {
                newWindow.close();
            });
    
            const targetCanvas = newDocument.getElementById('target-map');
            const ctx = targetCanvas.getContext('2d');
            const tooltipRef = newDocument.querySelector('.tooltip');

            const drawMap = () => {
                const tileSize = 32;
                const spaceSize = { width: 16, height: 32 };
                const xbarHeight = 16;

                ctx.drawImage(images['xbar'], 0, 0, 400, xbarHeight);
                
                for (let y = 0; y < targetIslandData.map_data.length; y++) {
                    if (y % 2 === 0) {
                        ctx.drawImage(images[`space${y}`], 0, xbarHeight + y * spaceSize.height, spaceSize.width, spaceSize.height);
                        for (let x = 0; x < targetIslandData.map_data[y].length; x++) {
                            const terrainId = targetIslandData.map_data[y][x].terrain;
                            const landvalue = targetIslandData.map_data[y][x].landvalue;
                            const terrainImageFunc = terrainData[terrainId].touristImage;
                            const terrainImageSrc = terrainImageFunc(landvalue);  // 画像のキーを取得
                            const terrainImageKey = `${terrainId}-${terrainData[terrainId].imageList.indexOf(terrainImageSrc)}`;
                            const terrainImage = images[terrainImageKey];  // 正しいキーで参照
                            if (terrainImage) {
                                const posX = spaceSize.width + x * tileSize;
                                const posY = xbarHeight + y * tileSize;
                                ctx.drawImage(terrainImage, posX, posY, tileSize, tileSize);
                            } else {
                                console.error(`No image found for terrain ID ${terrainId} with landvalue ${landvalue}`);
                            }
                        }
                    } else {
                        for (let x = 0; x < targetIslandData.map_data[y].length; x++) {
                            const terrainId = targetIslandData.map_data[y][x].terrain;
                            const landvalue = targetIslandData.map_data[y][x].landvalue;
                            const terrainImageFunc = terrainData[terrainId].touristImage;
                            const terrainImageSrc = terrainImageFunc(landvalue);  // 画像のキーを取得
                            const terrainImageKey = `${terrainId}-${terrainData[terrainId].imageList.indexOf(terrainImageSrc)}`;
                            const terrainImage = images[terrainImageKey];  // 正しいキーで参照
                            if (terrainImage) {
                                const posX = x * tileSize;
                                const posY = xbarHeight + y * tileSize;
                                ctx.drawImage(terrainImage, posX, posY, tileSize, tileSize);
                            } else {
                                console.error(`No image found for terrain ID ${terrainId} with landvalue ${landvalue}`);
                            }
                        }
                        ctx.drawImage(images[`space${y}`], 400 - spaceSize.width, xbarHeight + y * spaceSize.height, spaceSize.width, spaceSize.height);
                    }
                }
            };
    
            drawMap();
    
            const handleMouseMove = (event) => {
                const rect = targetCanvas.getBoundingClientRect();
                const tileSize = 32;
                const spaceSize = { width: 16, height: 32 };
                const xbarHeight = 16;

                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;
    
                const row = Math.floor((y - xbarHeight) / tileSize);
                let col;
                if (row % 2 === 0) {
                    col = Math.floor((x - spaceSize.width) / tileSize);
                } else {
                    col = Math.floor(x / tileSize);
                }
    
                if (row >= 0 && row < targetIslandData.map_data.length && col >= 0 && col < targetIslandData.map_data[0].length) {
                    const cell = targetIslandData.map_data[row][col];
                    const { terrain, landvalue } = cell;
    
                    const tooltipContent = `(${col},${row}) ${typeof terrainData[terrain].touristTooltip === 'function'
                        ? terrainData[terrain].touristTooltip(landvalue)
                        : terrainData[terrain].touristTooltip}`;
    
                    tooltipRef.style.left = `${event.clientX - rect.left + 10}px`;
                    tooltipRef.style.top = `${event.clientY - rect.top + 10}px`;
                    tooltipRef.innerHTML = tooltipContent;
                    tooltipRef.style.display = 'block';
                } else {
                    tooltipRef.style.display = 'none';
                }
            };
    
            targetCanvas.addEventListener('mousemove', handleMouseMove);
            targetCanvas.addEventListener('mouseleave', () => {
                tooltipRef.style.display = 'none';
            });
    
            targetCanvas.addEventListener('click', (event) => {
                const rect = targetCanvas.getBoundingClientRect();

                const tileSize = 32;
                const spaceSize = { width: 16, height: 32 };
                const xbarHeight = 16;

                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;
    
                const row = Math.floor((y - xbarHeight) / tileSize);
                let col;
                if (row % 2 === 0) {
                    col = Math.floor((x - spaceSize.width) / tileSize);
                } else {
                    col = Math.floor(x / tileSize);
                }
    
                if (row >= 0 && row < targetIslandData.map_data.length && col >= 0 && col < targetIslandData.map_data[0].length) {
                    setXCoord(col);
                    setYCoord(row);
                    newWindow.close();
                }
            });
        } catch (error) {
            console.error('Error fetching target island data:', error);
        }
    };    

    const handleSubmit = () => {
        setIsland(prevIsland => ({
            ...prevIsland,
            plans: displayedPlans,
        }));
    
        axios.put(`${process.env.REACT_APP_API_BASE_URL}/api/islands/${currentIsland}/plans/`, { plans: displayedPlans })
            .then(response => {
                // console.log("Plans updated successfully:", response.data);
            })
            .catch(error => {
                console.error("Error updating plans:", error);
            });

        setIsEditing(false);
    };
    
    const handleCategoryChange = (event) => {
        const newCategory = event.target.value;
        setSelectedCategory(newCategory);
    
        const filteredCommands = Object.keys(commandData).filter(key => {
            const command = commandData[key];
            return newCategory === 'all' || command.category === newCategory;
        });
    
        if (filteredCommands.length > 0) {
            setSelectedCommand(filteredCommands[0]);
        } else {
            setSelectedCommand('');
        }
    };    

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
            }
        };

        loadImages();
    }, []);

    useEffect(() => {
        if (island && allImagesLoaded) {
            const canvas = canvasRef.current;
    
            if (canvas) {
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
                                const terrainImageFunc = terrainData[terrainId].developmentImage;
                                const terrainImageSrc = terrainImageFunc(landvalue);  // 画像のキーを取得
                                const terrainImageKey = `${terrainId}-${terrainData[terrainId].imageList.indexOf(terrainImageSrc)}`;
                                const terrainImage = images[terrainImageKey];  // 正しいキーで参照
                                if (terrainImage) {
                                    const posX = spaceSize.width + x * tileSize;
                                    const posY = xbarHeight + y * tileSize;
                                    ctx.drawImage(terrainImage, posX, posY, tileSize, tileSize);
                                } else {
                                    console.error(`No image found for terrain ID ${terrainId} with landvalue ${landvalue}`);
                                }
                            }
                        } else {
                            for (let x = 0; x < island.map_data[y].length; x++) {
                                const terrainId = island.map_data[y][x].terrain;
                                const landvalue = island.map_data[y][x].landvalue;
                                const terrainImageFunc = terrainData[terrainId].developmentImage;
                                const terrainImageSrc = terrainImageFunc(landvalue);  // 画像のキーを取得
                                const terrainImageKey = `${terrainId}-${terrainData[terrainId].imageList.indexOf(terrainImageSrc)}`;
                                const terrainImage = images[terrainImageKey];  // 正しいキーで参照
                                if (terrainImage) {
                                    const posX = x * tileSize;
                                    const posY = xbarHeight + y * tileSize;
                                    ctx.drawImage(terrainImage, posX, posY, tileSize, tileSize);
                                } else {
                                    console.error(`No image found for terrain ID ${terrainId} with landvalue ${landvalue}`);
                                }
                            }
                            ctx.drawImage(images[`space${y}`], 400 - spaceSize.width, xbarHeight + y * spaceSize.height, spaceSize.width, spaceSize.height);
                        }
                    }
                };
    
                drawMap();
                
                const handleMouseMove = (event) => {
                    if (!canvas || !tooltipRef.current) return;
    
                    const rect = canvas.getBoundingClientRect();
                    const x = event.clientX - rect.left;
                    const y = event.clientY - rect.top;
    
                    const row = Math.floor((y - xbarHeight) / tileSize);

                    let col;
                    if (row % 2 === 0) {
                        col = Math.floor((x - spaceSize.width) / tileSize);
                    } else {
                        col = Math.floor(x / tileSize);
                    }
    
                    if (row >= 0 && row < island.map_data.length && col >= 0 && col < island.map_data[0].length) {
                        const cell = island.map_data[row][col];
                        const { terrain, landvalue } = cell;

                        const tooltipContent = `(${col},${row}) ${typeof terrainData[terrain].developmentTooltip === 'function'
                            ? terrainData[terrain].developmentTooltip(landvalue)
                            : terrainData[terrain].developmentTooltip}`;
    
                        if (tooltipRef.current) {
                            const tooltip = tooltipRef.current;
                            tooltip.style.left = `${event.clientX + 10}px`;
                            tooltip.style.top = `${event.clientY + 10}px`;
                            tooltip.innerHTML = tooltipContent;
                            tooltip.style.display = 'block';
                        }
                    } else {
                        if (tooltipRef.current) {
                            tooltipRef.current.style.display = 'none';
                        }
                    }
                };
    
                const handleMouseLeave = () => {
                    if (tooltipRef.current) {
                        tooltipRef.current.style.display = 'none';
                    }
                };
    
                const handleMapClick = (event) => {
                    const rect = canvasRef.current.getBoundingClientRect();
                    const x = event.clientX - rect.left;
                    const y = event.clientY - rect.top;
                
                    const row = Math.floor((y - xbarHeight) / tileSize);

                    let col;
                    if (row % 2 === 0) {
                        col = Math.floor((x - spaceSize.width) / tileSize);
                    } else {
                        col = Math.floor(x / tileSize);
                    }
                
                    if (row >= 0 && row < island.map_data.length && col >= 0 && col < island.map_data[0].length) {
                        setXCoord(col);
                        setYCoord(row);
                
                        if (!document.getElementById('popupOff').checked) {
                            setPopupPosition({ x: event.clientX, y: event.clientY });
                            setPopupVisible(true);
                        }
                    }
                };                
    
                canvas.addEventListener('mousemove', handleMouseMove);
                canvas.addEventListener('mouseleave', handleMouseLeave);
                canvas.addEventListener('click', handleMapClick);
    
                return () => {
                    canvas.removeEventListener('mousemove', handleMouseMove);
                    canvas.removeEventListener('mouseleave', handleMouseLeave);
                    canvas.removeEventListener('click', handleMapClick);
                };
            }
        }
    }, [island, images, allImagesLoaded]);
    
    useEffect(() => {
        if (island && island.plans) {
            setDisplayedPlans((prevPlans) =>
                prevPlans.map((plan, index) => island.plans[index] || plan)
            );
        } 
    }, [island]);

    const handleSave = () => {
        const updatedData = { name, owner, comment };

        axios.put(`${process.env.REACT_APP_API_BASE_URL}/api/islands/${currentIsland}/`, updatedData)
            .then(response => {
                setIsland(response.data);
                alert("保存が成功しました！");
            })
            .catch(error => console.error('Error saving data:', error));
    };
    
    const filteredCommands = Object.keys(commandData).filter(key => {
        const command = commandData[key];
        if (selectedCategory === 'all') return true;
        return command.category === selectedCategory;
    });

    if (isLoading) {
        return <Spinner />;  // ロード中はスピナーを表示
    }

    if (!loggedIn || !currentIsland) {
        return (
            <div className="error-container">
                <h1>開発画面へのログインに失敗しました。</h1>
                <button className="back-button" onClick={() => navigate('/')}>トップへ戻る</button>
            </div>
        );
    }

    if (!island) {
        return (
            <div className="island-view-failed">
                <h1>島がありません。</h1>
                <button className="back-button" onClick={() => navigate('/')}>トップへ戻る</button>
            </div>
        );
    }

    return (
        <div className="development-view">
            <h1>{island.name}開発計画</h1>
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
                        <th>ミサイル</th>
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
                        <td>{`${island.missile_capacity}${units.missile_capacity}発射可能`}</td>
                    </tr>
                </tbody>
            </table>

            <div className="map-and-commands">
                <div className="command-input-container">
                    <div className="button-group">
                        <button onClick={handleInsert}>挿入</button>
                        <button onClick={handleOverwrite}>上書き</button>
                        <button onClick={handleDelete}>削除</button>
                    </div>
                    <hr />
                    <label>計画番号：</label>
                    <select name="planNumber">
                        {Array.from({ length: 30 }, (_, i) => (
                            <option key={i} value={i + 1}>{i + 1}</option>
                        ))}
                    </select>
                    <hr />
                    <label>開発計画：</label>
                    <input type="checkbox" id="popupOff" />
                    <label htmlFor="popupOff">Popup Off</label>
                    <br />
                    <select value={selectedCategory} onChange={handleCategoryChange}>
                        <option value="all">全種類</option>
                        <option value="development">開発</option>
                        <option value="construction">建設</option>
                        <option value="attack">攻撃</option>
                        <option value="operation">運営</option>
                    </select>
                    <select value={selectedCommand} onChange={handleCommandChange}>
                        {filteredCommands.map(key => (
                            <option key={key} value={key}>{commandData[key].name}（{commandData[key].costdescription}）</option>
                        ))}
                    </select>
                    <hr />
                    <label>座標：</label>
                    <select name="xCoord" value={xCoord} onChange={(e) => handleCoordChange(e, 'x')}>
                        {Array.from({ length: 12 }, (_, i) => (
                            <option key={i} value={i}>{i}</option>
                        ))}
                    </select>
                    <select name="yCoord" value={yCoord} onChange={(e) => handleCoordChange(e, 'y')}>
                        {Array.from({ length: 12 }, (_, i) => (
                            <option key={i} value={i}>{i}</option>
                        ))}
                    </select>
                    <hr />
                    <label>数量：</label>
                    <input
                        type="number"
                        min="0"
                        max="99"
                        value={quantity === "" ? "" : quantity}
                        onChange={handleQuantityChange}
                    />
                    <hr />
                    <label>目標の島：</label>
                    <select value={targetIsland} onChange={(e) => setTargetIsland(e.target.value)}>
                        {islands.map(island => (
                            <option key={island.id} value={island.id}>{island.name}</option>
                        ))}
                    </select>
                    <button onClick={handleTargetCapture}>目標捕捉</button>
                    <hr />
                    <label>コマンド移動：</label>
                    <div className="command-move-group">
                        <button onClick={handleMoveUp}>▲</button>
                        <button onClick={handleMoveDown}>▼</button>
                    </div>
                    <hr />
                    <button 
                        className="submit-button" 
                        onClick={handleSubmit} 
                        disabled={!isEditing}
                    >
                        計画送信
                    </button>
                </div>
                <div className="map-container">
                    <canvas ref={canvasRef} width={400} height={400} />
                    <div ref={tooltipRef} className="tooltip"></div>
                </div>
                {popupVisible && (
                    <div
                        ref={popupRef}
                        className="popup-menu"
                        style={{ top: popupPosition.y, left: popupPosition.x }}
                    >
                        {generatePopupContent()}
                    </div>
                )}
                <div className="command-list">
                    <ul>
                        {displayedPlans && displayedPlans.length > 0 ? (
                            displayedPlans.map((plan, index) => (
                                <li
                                    key={index}
                                    className={`${commandData[plan.command]?.turnExpend ? 'command-expend' : 'command-non-expend'} ${index === selectedCommandIndex ? 'selected' : ''}`}
                                    onClick={() => handlePlanClick(index)}
                                >
                                    {`${index + 1}: ${getPlanDescription(plan)}`}
                                </li>
                            ))
                        ) : (
                            <li>計画がありません。</li>
                        )}
                    </ul>
                </div>
            </div>
            <div className="form-container">
                <h2>設定変更</h2>
                <div className="form-group">
                    <label>名前: </label>
                    <input 
                        type="text" 
                        value={name} 
                        onChange={(e) => setName(e.target.value)} 
                    />
                </div>
                <div className="form-group">
                    <label>オーナー: </label>
                    <input 
                        type="text" 
                        value={owner} 
                        onChange={(e) => setOwner(e.target.value)} 
                    />
                </div>
                <div className="form-group">
                    <label>コメント: </label>
                    <textarea 
                        value={comment} 
                        onChange={(e) => setComment(e.target.value)} 
                    />
                </div>
                <div><p>注：島の名前、オーナー名の変更には<br></br><b>500億円</b>が必要です。</p></div>
                <button 
                    onClick={handleSave} 
                    disabled={isSaveDisabled}
                    className="save-button"
                >
                    保存
                </button>
            </div>
            <RecentlyLog mode="island" islandId={island.id} includeConfidential={true} />
        </div>
    );    
};

export default DevelopmentView;
