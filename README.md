# Boavizta Project - Environmental Footprint Data

This data repository is maintained by [Boavizta](https://www.boavizta.org) and is complementary to Boavizta's environmental footprint evaluation methology. It aims to reference as much data as possible to help organizations to evaluate the environmental footprint of their information systems, applications and digital services.
This data can be freely used for any purpose including without using Boavizta's methodology.

## Data sets
At this time, we provide two CSV files grouping together data collected from manufacturers (mainly Product Carbon Footprint reports) publicly avaiblable :

* `boavizta-data-fr.csv`: French version (`;` used as a delimiter, comma as a decimal separator)
* `boavizta-data-us.csv`: English version (`,` used as a delimiter, dot as a decimal separator)

We encourage all manufacturers to provide us with similar data or to correct potential errors in these files.

Boavizta working group works actively to enrich these files with new data :
* from manufacturers
* resulting from its analyzes and intended to provide ratios or average values that would simplify the evaluation

Please refer to [sources.md](sources.md) for a complete list of sources.

## Contribute
People are encouraged to contribute to these files.

You can easily contribute by :
* forking this repo and submitting PRs
* sending us an email to data@boavizta.org

If any manufacturers wish to share data with us, we will be happy to discuss with them how we can efficiently synchronize this data.

## Data format

* `manufacturer`: Manufacturer name, e.g. "Dell" or "HP"
* `name`: Product name
* `category`:
  * Workplace: product commonly used in a workplace
  * Datacenter: product commonly used in a data center (e.g. server, network switch, etc.)
* `gwp_total`: GHG emissions (estimated as CO2 equivalent, the unit is kgCO2eq) through the total lifecycle of the product (Manufacturing, Transportation, Use phase and Recycling)
* `gwp_use_ratio`: part of the GHG emissions coming from the use phase (the hypothesis for this use phase
  are detailed in the other columns, especially the `lifetime` and the `use_location`)
* `yearly_tec`: Yearly estimated energy demand in kWh
* `lifetime`: Expected lifetime (in years)
* `use_location`: The region of the world in which the device usage footprint has been estimated.
  * US: United States of America
  * EU: Europe
  * DE: Germany
  * CN: China
  * WW: Worldwide
* `report_date`: the date at which the Product Carbon Footprint report of the device was published
* `sources`: the original URLs from which the data for this row was sourced
* `gwp_error_ratio`: the datasheets commonly come with a diagram that shows the error margin for the footprint
* `gwp_manufacturing_ratio` part of the GHG emissions coming from the manufacturing phase
* `weight`: product weight in kg
* `assembly_location`: The region of the world in which the device is assembled
  * US: United States of America
  * EU: Europe
  * CN: China
  * Asia: Asia
* `screen_size`: in inches
* `server_type`: the type of server
* `hard_drive`: the hard drive of the device if any
* `memory`: RAM in GB
* `number_cpu`: number of CPUs
* `height`: the height of the device in a datacenter rack, in U
* `added_date`: the date at which this row was added
* `add_method`: how was the data for this row collected

## About Boavizta.org

Boavizta.org is a working group:

* Working to improve and generalize environmental footprint evaluation in organizations
* Federating and connecting stakeholders of the "environmental footprint evaluation" ecosystem
* Helping members to improve their skills and to carry out their own projects
* Leveraging group members initiatives
