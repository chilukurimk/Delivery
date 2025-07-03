import React, { useState, useEffect } from "react";
import "./Restaurant.css";

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
    const [selectedItem, setSelectedItem] = useState<Item | null>(null);

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
        <div className="restaurants-container">
            {/* First column - Restaurants */}
            <div className="restaurants-column">
                <h2 className="restaurants-header">Restaurants</h2>
                {restaurants.map((restaurant) => (
                    <div key={restaurant.id} className="restaurant-item">
                        <div className="restaurant-info">
                            <h3>{restaurant.name}</h3>
                            <p className="restaurant-location">({restaurant.location})</p>
                            <button 
                                className="menu-button"
                                onClick={() => {
                                    setSelectedRestaurantId(restaurant.id);
                                    setSelectedItem(null); // Clear selected item when switching restaurants
                                }}
                            >
                                Menu
                            </button>
                            
                            {/* <p className="restaurant-location">{restaurant.location}</p> */}
                        </div>
                    </div>
                ))}
            </div>

            {/* Second column - Items */}
            <div className="items-column">
                <h2 className="items-header">Menu Items</h2>
                {selectedRestaurantId ? (
                    <div className="items-content">
                        <h3>Items from {restaurants.find(r => r.id === selectedRestaurantId)?.name}</h3>
                        <div className="items-list">
                            {restaurants
                                .find(r => r.id === selectedRestaurantId)
                                ?.items?.map(item => (
                                    <button 
                                        key={item.id} 
                                        className="item-entry"
                                        onClick={() => {
                                            setSelectedItem(item);
                                            console.log(`Selected ${item.name} - Price: ${item.price}`);
                                        }}
                                    >
                                        {item.name}
                                    </button>
                                )) || <div className="item-entry">No items available</div>}
                        </div>
                        <button 
                            className="back-button"
                            onClick={() => setSelectedRestaurantId(null)}
                        >
                            Close
                        </button>
                    </div>
                ) : (
                    <p className="placeholder-text">Click Menu to view</p>
                )}
            </div>

            {/* Third column - Item Details */}
            <div className="empty-column">
                <h2 className="empty-header">Item Details</h2>
                {selectedItem ? (
                    <div className="item-details">
                        <h3 className="item-name">{selectedItem.name}</h3>
                        <div className="item-price">
                            <strong>Price: ₹{selectedItem.price}</strong>
                        </div>
                        <div className="item-description">
                            <p><strong>Description:</strong></p>
                            <p>{selectedItem.description || "No description available"}</p>
                        </div>
                        <div className="item-quantity">
                            <p><strong>Available Quantity:</strong> {selectedItem.available_quantity}</p>
                        </div>
                        <button 
                            className="add-to-cart-button"
                            onClick={() => {
                                console.log(`Added ${selectedItem.name} to cart`);
                                // Add to cart functionality can be implemented here
                            }}
                        >
                            Add to Cart
                        </button>
                    </div>
                ) : (
                    <p className="empty-content">Click on a food item to view details</p>
                )}
            </div>
        </div>
    );
};

export default Restaurants;