[![](https://img.shields.io/github/release/boralyl/steam-wishlist/all.svg?style=for-the-badge)](https://github.com/boralyl/steam-wishlist/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![](https://img.shields.io/github/license/boralyl/steam-wishlist?style=for-the-badge)](LICENSE)
[![](https://img.shields.io/github/actions/workflow/status/boralyl/steam-wishlist/pythonpackage.yaml?branch=main&style=for-the-badge)](https://github.com/boralyl/steam-wishlist/actions)

# Steam Wishlist for Home Assistant

A custom component that keeps track of when games on your Steam wishlist are on
sale. This component uses the config flow and can easily be configured via the
Integrations section in the UI.

[![sensor.steam_wishlist](https://github.com/boralyl/steam-wishlist/raw/main/assets/setup.png)](https://github.com/boralyl/steam-wishlist/raw/main/assets/setup.png)

## HACS Installation

1. Search for `Steam Wishlist` under the `Integrations` tab on [HACS](https://hacs.xyz/).
2. Install the integration.
3. In the home assistant configuration screen click on `Integrations`.
4. Click on the `+` icon to add a new integration.
5. Search for `Steam Wishlist` and select it.
6. Enter your steam account name and click `Submit`.

## Manual Installation

1. Download the [latest release](https://github.com/boralyl/steam-wishlist/releases).
2. Extract the files and move the `steam_wishlist` folder into the path to your
   `custom_components`. e.g. `/config/custom_components`.
3. In the home assistant configuration screen click on `Integrations`.
4. Click on the `+` icon to add a new integration.
5. Search for `Steam Wishlist` and select it.
6. Enter your steam account name and click `Submit`.

## Sensors

After you successfully setup the integration a number of sensors will be created.

### `sensor.steam_wishlist_<your-profile-id>`

This sensor will report the number of games on sale from your wishlist.

[![sensor.steam_wishlist](https://github.com/boralyl/steam-wishlist/raw/main/assets/sensor.steam_wishlist.png)](https://github.com/boralyl/steam-wishlist/raw/main/assets/sensor.steam_wishlist.png)

#### Attributes

The following state attributes are available for this sensor:

| attribute | description                                 |
| --------- | ------------------------------------------- |
| on_sale   | An array of [games on sale](#attributes-1). |

### `binary_sensor.steam_wishlist_<title>`

A binary sensor will be created for each game on your wishlist. It's state will
indicate if it is on sale or not.

[![sensor.steam_wishlist](https://github.com/boralyl/steam-wishlist/raw/main/assets/binary_sensor.steam_wishlist_terraria.png)](https://github.com/boralyl/steam-wishlist/raw/main/assets/binary_sensor.steam_wishlist_terraria.png)

#### Attributes

The following state attributes are available for this sensor:

| attribute       | description                                     |
| --------------- | ----------------------------------------------- |
| title           | Title of the game                               |
| rating          | Reviews e.g. `Reviews: 92% (Very Positive)`     |
| price           | Price description of game                       |
| genres          | Genres of game e.g. `FPS, Action, First-Person` |
| release         | Release date of game                            |
| airdate         | Date game was released (Unix timestamp format)  |
| normal_price    | Price                                           |
| percent_off     | Percentage off of the normal price              |
| review_desc     | Review description                              |
| reviews_percent | Percentage of positive reviews                  |
| reviews_total   | Total number of reviews                         |
| sale_price      | Sale price of the game                          |
| steam_id        | Steam ID of the game                            |
| box_art_url     | URL for the background 16:9 aspect ratio image  |
| fanart          | URL for the background 16:9 aspect ratio image  |
| poster          | URL for the background 3:4 image                |
| deep_link       | Clickable hyperlink to game on Steam website    |

## Displaying in Lovelace

You are able to use any Home Assistant card to display a list of your games that are on sale by utilizing the `sensor.steam_wishlist` sensor. Below, are 2 cards that fully support this integration and its sensor attributes:

### I. upcoming-media-card

You can use [upcoming-media-card](https://github.com/custom-cards/upcoming-media-card) to display your Steam wishlist items that are on sale. You can also toggle displaying your non-sale wishlist items via the YAML setting `collapse: price=🎫` _(along with enabling the **Options** integration setting)_ like so:

Example YAML:

```yaml
- type: custom:upcoming-media-card
  entity: sensor.steam_wishlist_978793482343112
  title: Steam Wishlist
  image_style: fanart
  collapse: price=🎫
  max: 10
```

<img src="./assets/collapse_filter.gif" width="430">

##### Enable the Steam Wishlist integration setting below:

<img src="./assets/options.png" width="430">

---

### II. nintendo-wishlist-card

You can use [nintendo-wishlist-card](https://github.com/custom-cards/nintendo-wishlist-card) to display your Steam wishlist items that are on sale. This is possible since I also maintain the [nintendo-wishlist](https://github.com/custom-components/sensor.nintendo_wishlist) integration. You can add this card to Lovelace like so:

Example YAML:

```yaml
- type: custom:nintendo-wishlist-card
  entity: sensor.steam_wishlist_978793482343112
  title: Steam Wishlist
  image_style: backgroundart
  max: 10
```

<img src="./assets/custom-card.png" width="430">
