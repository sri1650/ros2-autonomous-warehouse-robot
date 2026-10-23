# Maps

When mapping mode is complete, save a map here with:

```bash
ros2 run nav2_map_server map_saver_cli -f src/warehouse_robot_bringup/maps/warehouse
```

Then start localisation mode with `use_slam:=false map:=/absolute/path/to/warehouse.yaml`.
