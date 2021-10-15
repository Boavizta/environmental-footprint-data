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

* Manufacturer: manufacturer name
* Name: product name
* Category:
  * Workplace: product commonly used in a workplace
  * Datacenter: product commonly used in a data center (e.g. server, network switch, etc.)
* kgCO2eq (total): GHG emissions (estimated as CO2 equivalent) through the total lifecycle of the product (Manufacturing, Transportation, Use phase and Recycling)
* Use (%): percentage of the GHG emissions coming from the use phase (the hypothesis for this use phase
  are detailed in the other columns, especially the Lifetime and the Use Location)
* Yearly TEC (kWh): Yearly estimated energy demand
* Lifetime: expected lifetime (in years)
* Use Location:
  * US: United States of America
  * EU: Europe
  * DE: Germany
  * CN: China
  * WW: Worldwide

* Error: the datasheets commonly come with a diagram that shows the error margin for the footprint
* Weight: product weight in kg
* Assembly Location:
  * US: United States of America
  * EU: Europe
  * CN: China
  * Asia: Asia

* Screen size: in inches
* RAM: in GB
* CPU: number of CPUs

## About Boavizta.org

Boavizta.org is a working group:

* Working to improve and generalize environmental footprint evaluation in organizations
* Federating and connecting stakeholders of the "environmental footprint evaluation" ecosystem
* Helping members to improve their skills and to carry out their own projects
* Leveraging group members initiatives
