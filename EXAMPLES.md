# Oplaadpalen Integration Example Configurations

## Example 1: Basic Configuration

```yaml
# In Home Assistant Developer Tools > Services
# Or create an automation to add the integration
```

Through the Home Assistant UI:
1. Settings → Devices & Services
2. Create Integration
3. Search for "Oplaadpalen.nl"
4. Fill in:
   - Name: "My Home Charger Monitor"
   - Address: Your location or coordinates
   - Radius: 5 km
   - Update interval: 300 seconds

## Example 2: Automation - Notify on EVSE Availability

```yaml
automation:
  - alias: Notify when EV charger available
    description: Sends notification when an EVSE becomes available
    trigger:
      - platform: state
        entity_id: binary_sensor.my_home_charger_monitor_evse_0
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "{{ trigger.entity_id }} at {{ state_attr(trigger.entity_id, 'address') }} is now available!"
          title: "Charging Available"
          data:
            tag: "evse_available"
```

## Example 3: Template Sensor - Count Available EVSEs

```yaml
template:
  - sensor:
      - name: "Available Chargers Nearby"
        unique_id: available_chargers_count
        unit_of_measurement: "chargers"
        state: |
          {{ expand('group.all_binary_sensors')
             | selectattr('entity_id', 'search', 'oplaadpalen.*evse')
             | selectattr('state', 'eq', 'on')
             | list | length }}
```

## Example 4: Get Station Details

```yaml
automation:
  - alias: Log charging station details
    trigger:
      - platform: state
        entity_id: binary_sensor.amsterdam_charger_evse_0
        to: "on"
    action:
      - service: logbook.log
        data:
          name: "Charger Available"
          message: |
            Station: {{ state_attr(trigger.entity_id, 'address') }}, {{ state_attr(trigger.entity_id, 'city') }}
            Operator: {{ state_attr(trigger.entity_id, 'operator') }}
            Connector: {{ state_attr(trigger.entity_id, 'connector_standard') }}
            Max Power: {{ state_attr(trigger.entity_id, 'max_power') }} W
            Phone: {{ state_attr(trigger.entity_id, 'support_phone') }}
```

## Example 5: Multiple Locations

You can add multiple oplaadpalen devices for different locations:

1. Home Location
   - Address: Your home
   - Radius: 3 km
   - Update interval: 600 seconds (10 minutes)

2. Work Location
   - Address: Your workplace
   - Radius: 5 km
   - Update interval: 300 seconds (5 minutes)

3. Frequent Destination
   - Coordinates: 52.37403, 4.88969 (Centraal Amsterdam)
   - Radius: 2 km
   - Update interval: 900 seconds (15 minutes)

Each will maintain separate sensors with their own unique IDs.

## Example 6: Availability Dashboard Card

```yaml
type: entities
title: EV Chargers Nearby
entities:
  - entity: binary_sensor.my_location_evse_0
    name: EVSE 1
    icon: mdi:ev-station
  - entity: binary_sensor.my_location_evse_1
    name: EVSE 2
    icon: mdi:ev-station
  - entity: binary_sensor.my_location_evse_2
    name: EVSE 3
    icon: mdi:ev-station
```

## Example 7: Conditional Notification

```yaml
automation:
  - alias: Alert for high power chargers available
    description: Only notify for chargers with 22kW or more
    trigger:
      - platform: state
        entity_id: binary_sensor.my_location_evse_0
        to: "on"
    condition:
      - condition: template
        value_template: "{{ state_attr(trigger.entity_id, 'max_power') | int(0) >= 22000 }}"
    action:
      - service: notify.mobile_app
        data:
          message: "High-power charger available!"
```

## Example 8: Group Sensors by Location

```yaml
group:
  home_chargers:
    name: "Home Chargers"
    entities:
      - binary_sensor.home_location_evse_0
      - binary_sensor.home_location_evse_1

  work_chargers:
    name: "Work Chargers"
    entities:
      - binary_sensor.work_location_evse_0
      - binary_sensor.work_location_evse_1

automation:
  - alias: Check home charger availability
    trigger:
      - platform: state
        entity_id: group.home_chargers
        to: "on"
    action:
      - service: logbook.log
        data:
          name: "Home Charger Alert"
          message: "One or more home chargers are available!"
```

## Tips

- Start with a 5 km radius and adjust based on your needs
- Use separate devices for frequently visited locations
- Consider setting update interval to match your usage patterns
- 5 minutes (300s) for frequently checked locations
- 15 minutes (900s) for less frequently used areas
- Filter by power in automations if you need specific charger types
- Use template conditions to only notify for available chargers near you
- Combine with other entities (location, time) for smart automations

## API Response Structure

The integration processes this data structure:

```json
{
  "address": "Jacob Cnodestraat 23",
  "city": "'s-Hertogenbosch",
  "postal_code": "5223 HS",
  "country": "NLD",
  "evses": [
    {
      "status": "AVAILABLE",
      "connectors": [
        {
          "standard": "IEC_62196_T2",
          "format": "SOCKET",
          "max_power": 11000
        }
      ]
    }
  ],
  "operator": {
    "name": "Vattenfall InCharge",
    "website": "http://vattenfall.nl"
  },
  "access_type": "Public",
  "support_phone_number": "+(31)-(88)-3637991"
}
```

