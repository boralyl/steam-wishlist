# Architecture Notes

This document is an attempt to document how the component is structured and
how it functions.

## Files

### `__init__.py`

This file contains methods for initial setup of the component.  It handles
managing config entries created through the UI when adding a new Steam Wishlist
integration.

### `binary_sensor.py`

This file is very simple and should look familiar.  It handles registering each
binary sensor.  A binary sensor is created for each game in the wishlist.  It
retrieves the singleton instance of our `SensorManager` class and defers setting
up the binary_sensors to it.

### `config_flow.py`

This file contains the required class that allows the user to configure the
integration via the UI.

### `const.py`

This file contains some commonly used constants.

### `entities.py`

This file contains the 2 types of entities that this component uses.  One entity
represents our full steam wishlist and the second represents a single game in
the wishlist.

### `sensor_manager.py`

This file contains 2 classes that handle managing our sensors and their state.

#### `SteamWishlistDataUpdateCoordinator`

This class simply sub-classes the [DataUpdateCoordinator](https://developers.home-assistant.io/docs/integration_fetching_data/#coordinated-single-api-poll-for-data-for-all-entities).
It provides a method to asynchronously fetch all data once for all sensors for
this component.

#### `SensorManager`

This class was adapted from the [hue integration](https://github.com/home-assistant/core/blob/master/homeassistant/components/hue/sensor_base.py).
It manages all sensors for the component.  Anytime data for the coordinator is
updated it will call the `async_update_items` callback to determine if we need
to add or remove any of the binary sensors due to the wish list changing (user
added a new game or removed a game).

### `sensor.py`

This file is very simple and should look familiar.  It handles registering the
`sensor.steam_wishlist` sensor.  It retrieves the singleton instance of our
`SensorManager` class and defers setting up the sensor to it.

### `types.py`

This file contains custom types for use as type hints in this component.

### `util.py`

This file contains utility functions used by the component.

## How it works

This component utilizes the [DataUpdateCoordinator](https://developers.home-assistant.io/docs/integration_fetching_data/#coordinated-single-api-poll-for-data-for-all-entities)
to fetch the wishlist data.  This allows us to only have to fetch date once
per scan interval for all sensors.  The other part of this component is the
`SensorManager`.  Because games can be added and removed, I needed a way to also
be able to add new sensors and remove existing ones without having to restart
home assistant.  The SensorManager handles this by taking the `async_add_entites`
functions from each platform (`sensor` and `binary_sensor`) and registers a
callback function on the coordinator.  This function gets called after the
coordinator fetches data each time.
