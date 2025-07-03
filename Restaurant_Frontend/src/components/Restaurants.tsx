import React, { useState, useEffect } from "react";

// Define a type for a single restaurant for better type-safety
interface Restaurant {
    id: number;
    name: string;
    location: string;
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
                    setRestaurants(data.rest_list);
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
                        <h2>{restaurant.name}</h2>
                        <p>{restaurant.location}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Restaurants;