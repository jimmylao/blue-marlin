### Count Unique Users
##### Description
> This end-point returns number of unique users for a targeting channel in a time period.
##### Method: POST
##### URL: http://service-domain/imsservice/api/users/count
#####POST Body:
```sh
{
    targeting_channel:<ucdocument>,
    ranges: [ {
        sd:<start-date date in yyyy-mm-dd>,
        ed:<end-date date in yyyy-mm-dd>,
        sh:<start-hour in hh>,
        eh:<end-hour in hh>} …]
    today: <today's date in yyyy-mm-dd> set to today's date if not provided
}

The following attributes are used in targeting channel:
1)	pm: Price Model – CPM/CPC/CPD/CPT
2)	ai: Ad slot - list
3)	ipl: Geo-location – list of city code
4)	r: Resident-location – list of city code
5)	g: Gender - list
6)	a: Age – list
-	0 - (0,18)
-	1 - [18,24]
-	2 - (24,34]
-	3 - (34,44]
-	4 - (44,54]
-	5 - (55,+)
7)	aus: App usage – list of {category?_appusage_state}, state is one of following
a.	active_30days
b.	activated
c.	installed_not_activated
d.	not_instatlled
8)	ais: App interest – list
9)	t: Connection type - list
10)	pdas: Pre-defined audiences – list
11)	exclude_pdas: Excluded pre-defined audiences - list
12)	dms: Device model – list
13)	dpc: Device price category range of [0,4] - list
-	(0-1500] – 0_1500
-	(1500-2500] – 1500_2500
-	(2500-3500] – 2500_3500
-	(3500-4500] – 3500_4500
-	(4500-+) – 4500


Excample:
{
	"targetingChannel": {
		"g":["g_m"]
	},
	"days": [{
		"st": "2018-01-17",
		"ed": "2018-01-18",
		"sh": 0,
		"eh": 23
	}],
	"today":"2018-01-07"
}
```
##### Response:
```sh
{
    "result": {
        "availCount": 14070
    }
}
```