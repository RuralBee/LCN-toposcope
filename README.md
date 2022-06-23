
# Quickstart

## First, download the required dataset

__Download AS to Organization Mapping Dataset from CAIDA__

https://www.caida.org/data/as-organizations/

__Download PeeringDB Dataset from CAIDA__

https://publicdata.caida.org/datasets/peeringdb/

__Download Prefix2AS Dataset from CAIDA__

http://data.caida.org/datasets/routing/routeviews-prefix2as/

__Download AS-rank Dataset from ASRank__

https://asrank.caida.org/
   
you can use asrank API download dataset, python script is asrank.py
if you want change dataset time, you can change variable "history_time_list" in script
```sh
python asrnk.py
```
Put the downloaded Organization, PeeringDB, Prefix2AS, ASRank dataset into the 202107data folder.

##Second, Prepare BGP paths from Route Views and RIS`

You can prepare BGP paths from [BGPStream](https://bgpstream.caida.org/) or download rib file from [Route Views](http://archive.routeviews.org/) and [RIS](http://data.ris.ripe.net/).
you can use http_dowload_ripe.py and htto_dowload_routerview.py scripts to download RIS and Route Views datasets, using prefix_process.py script parse BGP path with the prefix.
you need to modify the script's download direction. Put asprefix.txt into 202107date direction.

The ASes on each BGP path should be delimited by '|' on each line, followed by '&' and prefix should be delimited by '%', for example, AS1|AS2|AS3&prefix1%prefix2.


## inference hidden link 

```sh
python hidden_infer.py
```

__Output data format__

\<provider-as\>|\<customer-as\>|-1 

\<peer-as\>|\<peer-as\>|0 

## Critical AS
you can change script's variable to fit your want to deal data
```sh
cd as_path_infer
python path_number_statistic.py
```

## Contact 

You can contact us at <wzeszsfx252@163.com>.

