[![](https://img.shields.io/github/release/boralyl/steam-wishlist/all.svg?style=for-the-badge)](https://github.com/boralyl/steam-wishlist/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![](https://img.shields.io/github/license/boralyl/steam-wishlist?style=for-the-badge)](LICENSE)
[![](https://img.shields.io/github/workflow/status/boralyl/steam-wishlist/Python package?style=for-the-badge)](https://github.com/boralyl/steam-wishlist/actions)

# Steam Wishlist for Home Assistant

A custom component that keeps track of when games on your Steam wishlist are on
sale. This component uses the config flow and can easily be configured via the
Integrations section in the UI.

[![sensor.steam_wishlist](https://github.com/boralyl/steam-wishlist/raw/master/assets/setup.png)](https://github.com/boralyl/steam-wishlist/raw/master/assets/setup.png)

## Pre-Installation

Prior to installing this integration you must first ensure that your wishlist is publicly
viewable. To do this, login to you steam account and edit your profile. Under the
`Privacy Settings` tab, set `Game Details` to `Public`. Without this step, this integration
will not be able to parse your wishlist.

[![steam privacy settings](https://github.com/boralyl/steam-wishlist/raw/master/assets/steam-profile.png)](https://github.com/boralyl/steam-wishlist/raw/master/assets/steam-profile.png)

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

### `sensor.steam_wishlist`

This sensor will report the number of games on sale from your wishlist.

[![sensor.steam_wishlist](https://github.com/boralyl/steam-wishlist/raw/master/assets/sensor.steam_wishlist.png)](https://github.com/boralyl/steam-wishlist/raw/master/assets/sensor.steam_wishlist.png)

#### Attributes

The following state attributes are available for this sensor:

| attribute | description                                 |
| --------- | ------------------------------------------- |
| on_sale   | An array of [games on sale](#attributes-1). |

### `binary_sensor.steam_wishlist_<title>`

A binary sensor will be created for each game on your wishlist. It's state will
indicate if it is on sale or not.

[![sensor.steam_wishlist](https://github.com/boralyl/steam-wishlist/raw/master/assets/binary_sensor.steam_wishlist_terraria.png)](https://github.com/boralyl/steam-wishlist/raw/master/assets/binary_sensor.steam_wishlist_terraria.png)

#### Attributes

The following state attributes are available for this sensor:

| attribute    | description                             |
| ------------ | --------------------------------------- |
| box_art_url  | The URL for the box art of the game.    |
| normal_price | The normal price of the game.           |
| sale_price   | The sale price of the game.             |
| percent_off  | The percentage off of the normal price. |
| steam_id     | The Steam ID of the game.               |
| title        | The title of the game.                  |

## Displaying in Lovelace

You are able to use any card or custom card to show a list of your games that are
on sale by utilizing the `sensor.steam_wishlist`. Additionally you can use the
[nintendo-wishlist-card](https://github.com/custom-cards/nintendo-wishlist-card)
to display the games on sale from your Steam wish list. This is possible because
I maintain this integration as well as the [nintendo-wishlist integration](https://github.com/custom-components/sensor.nintendo_wishlist), and the way they store their attributes
in sensors is identical. So if you install the card you add it to lovelace like so:

```yaml
- type: custom:nintendo-wishlist-card
  entity: sensor.steam_wishlist
  title: Steam Wishlist
  image_style: backgroundart
  max: 10
```

[![wishlist in the nintendo card](https://github.com/boralyl/steam-wishlist/raw/master/assets/custom-card.png)](https://github.com/boralyl/steam-wishlist/raw/master/assets/custom-card.png)
