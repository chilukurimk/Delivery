import React, { useState, useEffect } from "react";

// Define a type for a single item for better type-safety
interface Item {
    id: number;
    name: string;
    price: number;
    description?: string;
    available_quantity: number;
}

// Define a type for a single restaurant for better type-safety
interface Restaurant {
    id: number;
    name: string;
    location: string;
    items?: Item[];
}

const Restaurants = () => {
    const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
    const [selectedRestaurantId, setSelectedRestaurantId] = useState<number | null>(null);

    useEffect(() => {
        console.log("Fetching restaurant data...");
        // The file is fetched from the public folder
        fetch("http://127.0.0.1:8000/restaurants")
            .then((response) => response.json())
            .then((data) => {  
                console.log("Restaurant data fetched:", data);

                // The restaurant data is nested in the "rest_list" property
                if (data && data.rest_list) {
                    const restaurantPromises = data.rest_list.map((restaurant: Restaurant) => {
                        return fetch(`http://127.0.0.1:8000/items/${restaurant.id}`)
                            .then(response => response.json())
                            .then(itemsData => {
                                return { ...restaurant, items: itemsData.item_list };
                            });
                    });

                    Promise.all(restaurantPromises)
                        .then(restaurantsWithItems => {
                            setRestaurants(restaurantsWithItems);
                        });
                }
            })
            .catch((error) => console.error("Error fetching restaurants:", error));
    }, []); // The empty dependency array ensures this effect runs only once

    return (
        <div className="restaurants">
            <div>
                {restaurants.map((restaurant) => (
                    <div key={restaurant.id}>
                        <div style={{ display: 'flex',flexDirection: 'row', alignItems: 'center', gap: '15px' }}>
                            {/* <h2>{restaurant.name}</h2> */}
                            <button onClick={() => setSelectedRestaurantId(restaurant.id)}>
                                {restaurant.name}
                            </button>
                            <p>{restaurant.location}</p>
                            
                        </div>
                        {/* <p>{restaurant.location}</p> */}
                    </div>
                ))}
            </div>
            <hr/>
            <div>
                {selectedRestaurantId ? (
                    <div>
                        <h3>Items from {restaurants.find(r => r.id === selectedRestaurantId)?.name}</h3>
                        <ul>
                            {restaurants
                                .find(r => r.id === selectedRestaurantId)
                                ?.items?.map(item => (
                                    <li key={item.id}>{item.name} - {item.price} /-</li>
                                )) || <li>No items available</li>}
                        </ul>
                        <button onClick={() => setSelectedRestaurantId(null)} style={{ marginBottom: '10px' }}>
                            Back
                        </button>
                        {/* <ul>
                            {restaurants
                                .find(r => r.id === selectedRestaurantId)
                                ?.items?.map(item => (
                                    <li key={item.id}>{item.name} - {item.price} /-</li>
                                )) || <li>No items available</li>}
                        </ul> */}
                    </div>
                ) : (
                    <p>Click Restaurant to view menu</p>
                )}
            </div>
        </div>
    );
};

export default Restaurants;