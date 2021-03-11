# Boavizta Project - Environmental Footprint Data

The CSV files provided in this project put together some environmental footprint data of digital
devices such as laptops or servers:

* `boavizta-data-fr.csv`: French version (`;` used as a delimiter, coma as a decimal separator, French date)
* `boavizta-data-us.csv`: English version (`,` used as a delimiter, coma as a decimal separator, US date)

They data has been collected from the manufacturer datasheets publicly available on their Web sites.
They can be freely used for any purpose.

Please refer to [sources.md](sources.md) for a complete list of sources.

People are encouraged to contribute to these files.

## Data format

* Manufacturer: manufacturer name
* Name: product name
* Category:
  * Workplace: product commonly used in a workplace
  * Datacenter: product commonly used in a data center (e.g. server, network switch, etc.)

* Use (%): percentage of the footprint coming from the use phase (the hypothesis for this use phase
  are detailed in the other columns, especially the Lifetime and the Use Location)
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
* CPU: number of CPU
