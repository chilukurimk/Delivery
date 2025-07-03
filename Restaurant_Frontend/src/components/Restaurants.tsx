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
        <div>
            <h1>Restaurants</h1>
            <ul>
                {restaurants.map((restaurant) => (
                    <li key={restaurant.id}>
                        {restaurant.name}, {restaurant.location}
                        {restaurant.items && (
                            <ul>
                                {restaurant.items.map(item => (
                                    <li key={item.id}>{item.name} - ${item.price}</li>
                                ))}
                            </ul>
                        )}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Restaurants;