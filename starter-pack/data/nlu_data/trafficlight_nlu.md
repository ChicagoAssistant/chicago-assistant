## intent:traffic_light_request
- report a problem with a [traffic light](REQUEST_TYPE:traffic_signal)
- there's a problem with a [traffic light](REQUEST_TYPE:traffic_signal)
- noticed a [traffic light](REQUEST_TYPE:traffic_signal) problem
- [traffic light](REQUEST_TYPE:traffic_signal) is broken
- [traffic light](REQUEST_TYPE:traffic_signal) isn't working

<!-- Can you have two slots filled within the same intent?? -->
## intent:crosswalk_light_out
- report a problem with a [crosswalk light](REQUEST_TYPE:traffic_signal)(REQUEST_DETAIL:crosswalk_out)
- there's a problem with a [crosswalk light](REQUEST_TYPE:traffic_signal)(REQUEST_DETAIL:crosswalk_out)
- noticed a [crosswalk light](REQUEST_TYPE:traffic_signal)(REQUEST_DETAIL:crosswalk_out) problem
- [crosswalk light](REQUEST_TYPE:traffic_signal)(REQUEST_DETAIL:crosswalk_out) is broken
- [crosswalk light](REQUEST_TYPE:traffic_signal)(REQUEST_DETAIL:crosswalk_out) isn't working
- the [crosswalk light](REQUEST_TYPE:traffic_signal)(REQUEST_DETAIL:crosswalk_out) is out

## intent:signal_all_out
- traffic light is out
- crosswalk light is out
- [all lights are out](REQUEST_DETAIL)
- all the [lights are out](REQUEST_DETAIL)

## intent:signal_some_out
- some of the lights are out
- the light is [stuck](REQUEST_DETAIL)
- the light is [frozen](REQUEST_DETAIL)
- the [red](LIGHT_COLOR) [light is out](REQUEST_DETAIL)
- the [yellow](LIGHT_COLOR) [light is out](REQUEST_DETAIL)
- the [green](LIGHT_COLOR) [light is out](REQUEST_DETAIL)

## intent:signal_flashing
- traffic [light is flashing](REQUEST_DETAIL)
- traffic [light is stuck flashing](REQUEST_DETAIL)

## intent: light_color
- the light is [red](LIGHT_COLOR)
- the light is [yellow](LIGHT_COLOR)
- the light is [green](LIGHT_COLOR)
- it's [red](LIGHT_COLOR)
- it's [yellow](LIGHT_COLOR)
- it's [green](LIGHT_COLOR)
- [red](LIGHT_COLOR)
- [yellow](LIGHT_COLOR)
- [green](LIGHT_COLOR)
- [orange](LIGHT_COLOR)
- [amber](LIGHT_COLOR)
- [crimson](LIGHT_COLOR)