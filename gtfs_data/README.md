TFI = Transport for Ireland
Place the GTFS files here such as agency.txt, calendar.txt, routes.txt, shapes.txt, stops.txt, stop_times.txt, trips.txt etc.

To support other sets of GTFS data create a seperate folder for each set of data and place the files in the folder.
Then call the importer with the -dir option and point it at the folder you created

```
./gtfs_data/TFI/agency.txt
./gtfs_data/SomeOtherDataset/agency.txt
./gtfs_data/AnotherDataset/agency.txt
```
