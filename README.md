The purpose of this work is to delve into what seen in class about the optimization of network routing, solving a Linear Programming problem of the kind of Unsplittable Multicommodity Min-Cost Flow (UMMCF). In particular, it focuses on OSPF traffic engineering.  
The report attached (Italian) aims to collect ideas around the topic and the Python model attemps to implement the model described in equation n. 3.

_Discalimer: this work makes no claims to be correct or complete. For a formal dissertation, it is suggested to read the papers indicated in the bibliography of the report attached. As for the Python model, it was the first experience of the author with an LP solver._

## Build and run

Due to the lack of prebuilt Windows binaries at the time of writing, I used Docker.

```sh
docker compose run pyomo
cd workdir/
python3 UMMCF.py
```
