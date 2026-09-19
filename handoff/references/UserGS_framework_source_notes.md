# UserGS 原始仿真器：通用教学版改造的源码定位记录

## 范围

本记录基于用户上传的 `UserGS_simulation-main.zip`，关注轨道、拓扑、时间推进、地面站、选路和网页适配。它不是论文算法教学设计，也不表示教育版已实现。未修改原始 ZIP，未执行 `main.py` 或完整论文实验。只单独执行了已检查的 `Topology` 类的小规模结构测试。

ZIP SHA-256: `93bca9f4c25352f3d8320bcb809ad3d593c91bf697b722a4e830a2e24ecdb2dc`

## 小规模拓扑检查

使用只有 `id`、`orbit_idx`、`sat_idx_on_orbit` 的假卫星对象调用原始 `Topology` 类，检查节点、边和自环。没有运行轨道、地面接入、流量或拍卖。

```json
[
  {
    "planes": 1,
    "satellites_per_plane": 1,
    "nodes": 1,
    "edges": 1,
    "self_loops": 1
  },
  {
    "planes": 1,
    "satellites_per_plane": 3,
    "nodes": 3,
    "edges": 6,
    "self_loops": 3
  },
  {
    "planes": 2,
    "satellites_per_plane": 3,
    "nodes": 6,
    "edges": 9,
    "self_loops": 0
  },
  {
    "planes": 4,
    "satellites_per_plane": 6,
    "nodes": 24,
    "edges": 48,
    "self_loops": 0
  }
]
```

这个检查只说明原固定邻接图在单轨道面、小规模配置下需要边界处理，不是对研究默认配置的性能或正确性判决。

## 源码摘录

下面每行的数字是原文件的行号。代码保持原样；目录均相对于 ZIP 内的 `UserGS_simulation-main/`。

### 创建星座与更新卫星位置

源文件：`source/models/constellation.py`，第 9–54 行。

```text
   9: class Constellation:
  10:     def __init__(self, num_orbits, satellites_per_orbit, altitude_m, inclination_angle_deg, name, tf):
  11:         self.id = None
  12:         self.name = name
  13:         self.num_orbits = num_orbits
  14:         self.tf = tf
  15:         self.satellites_per_orbit = satellites_per_orbit
  16:         self.altitude_m = altitude_m
  17:         self.inclination_angle_deg = inclination_angle_deg
  18:         self.universal_epoch = None
  19:         self.satellite_id_counter = 0
  20:         self.satellites = []
  21:         self.generate_satellites()
  22:         # self.export_tles()
  23:         self.topology = Topology(self)
  24: 
  25:     def generate_satellites(self):
  26:         for orbit_id in range(self.num_orbits):
  27:             for satellite_pos in range(self.satellites_per_orbit):
  28:                 sat_id = self.get_sat_id_and_increment()
  29:                 sat = Satellite(
  30:                     id=sat_id, name =self.name + '-sat-{}'.format(sat_id),
  31:                     orbit_idx=orbit_id, sat_idx_on_orbit=satellite_pos, 
  32:                     constellation=self, universal_epoch=self.universal_epoch
  33:                 )
  34:                 self.universal_epoch = sat.universal_epoch
  35:                 self.satellites.append(sat)
  36:     
  37:     def get_sat_id_and_increment(self):
  38:         id = self.satellite_id_counter
  39:         self.satellite_id_counter += 1
  40:         return id
  41: 
  42:     def export_tles(self):
  43:         with open(f"../output/{self.name}_tles.txt", "w") as f:
  44:             f.write("{} {}\n".format(self.num_orbits, self.satellites_per_orbit))
  45:             for sat in self.satellites:
  46:                 f.write("LEO-{} {}\n".format(sat.id, sat.id))
  47:                 f.write("{}\n".format(sat.tle[0]))
  48:                 f.write("{}\n".format(sat.tle[1]))
  49: 
  50:     def update_satellites(self, time_step):
  51:         observer = ephem.Observer()
  52:         observer.date = time_step.current_time
  53:         for satellite in self.satellites:
  54:             satellite.ephem.compute(observer)
```

### 卫星状态与合成轨道入口

源文件：`source/models/satellite.py`，第 9–47 行。

```text
   9: class Satellite:
  10:     def __init__(
  11:             self, id, name, 
  12:             ephem=None, orbit_idx=None, 
  13:             sat_idx_on_orbit=None, constellation=None, universal_epoch=None) -> None:
  14:         self.id = id
  15:         self.name = name
  16:         # bandwidth is set according to
  17:         # Laser Intersatellite Links in a Starlink Constellation: A Classification and Analysis -> 2.5 Gbps
  18:         # Satellite Edge Computing for Real-Time and Very-High Resolution Earth Observation -> 10 Gbps
  19:         self.bandwidth_mbps = 2500.0
  20:         self.ephem = ephem
  21:         self.battery = Battery(random_cycle_life=True)
  22:         self.universal_epoch = universal_epoch
  23:         self.tle = None
  24:         self.orbit_idx = orbit_idx
  25:         self.sat_idx_on_orbit = sat_idx_on_orbit
  26:         self.constellation = constellation
  27:         self.create_ephem()
  28:         self.table_lookup_watt_per_mbps = 0.01
  29:         self.processor_watt_per_mbps = 0.01
  30:         self.sending_watt_per_mbps = 0.05
  31:         self.receiving_watt_per_mbps = 0.01
  32:         self.constant_power_watt = 50
  33:     
  34:     def create_ephem(self):
  35:         if self.constellation is None or self.orbit_idx is None or self.sat_idx_on_orbit is None:
  36:             raise Exception('Cannot create ephem object.')
  37:         tle_line1, tle_line2 = generate_tle_for_sat(
  38:             satellite_id=self.id,
  39:             orbit_index=self.orbit_idx,
  40:             sat_index=self.sat_idx_on_orbit,
  41:             num_orbits=self.constellation.num_orbits,
  42:             num_sats_per_orbit=self.constellation.satellites_per_orbit,
  43:             inclination_deg=self.constellation.inclination_angle_deg,
  44:             altitude_m=self.constellation.altitude_m,
  45:         )
  46:         self.tle = (tle_line1, tle_line2)
  47:         self.ephem, self.universal_epoch = tle_to_ephem(self.tle, self.universal_epoch)
```

### 星间距离与第三方来源注释

源文件：`source/models/satellite.py`，第 119–138 行。

```text
 119:     def distance_from(self, satellite, time_step):
 120:         """
 121:         This code is borrowed from Hypatia distance_tool.py
 122:         """
 123:         # Use a third point observer for computing distance
 124:         observer = ephem.Observer()
 125:         observer.epoch = time_step.current_time
 126:         observer.date = time_step.current_time
 127:         observer.lat = 0
 128:         observer.lon = 0
 129:         observer.elevation = 0
 130: 
 131:         self.ephem.compute(observer)
 132:         satellite.ephem.compute(observer)
 133: 
 134:         # Angle between observer and satellites
 135:         angle_radians = float(repr(ephem.separation(self.ephem,  satellite.ephem)))
 136: 
 137:         # Triangle
 138:         return math.sqrt(self.ephem.range ** 2 +  satellite.ephem.range ** 2 - (2 * self.ephem.range *  satellite.ephem.range * math.cos(angle_radians)))
```

### 合成 TLE 的历元和参数

源文件：`source/helpers/generate_tle.py`，第 17–24 行。

```text
  17: # TODO: Allow users to specify these parameters
  18: GRAVITY_MODEL = WGS72
  19: jd, fr = jday(2000, 1, 1, 0, 0, 0)
  20: EPOCH = (jd + fr) - 2433281.5
  21: DRAG_COEFFICIENT = 0.0  # Ignore it
  22: ECCENTRICITY = 0.0000001  # Circular orbit
  23: ARG_PERIGEE_RAD = math.radians(0.0)
  24: PHASE_DIFF = True
```

### 轨道生成与导出

源文件：`source/helpers/generate_tle.py`，第 63–123 行。

```text
  63: def generate_tle_for_sat(
  64:         satellite_id,
  65:         orbit_index,
  66:         sat_index,
  67:         num_orbits,
  68:         num_sats_per_orbit,
  69:         inclination_deg,
  70:         altitude_m,
  71: ):
  72:     sat = Satrec()
  73: 
  74:     orbit_phasing_shift = orbit_phasing(orbit_index, num_sats_per_orbit)
  75:     mean_anomaly_deg = mean_anomaly_degree(orbit_phasing_shift, sat_index, num_sats_per_orbit)
  76: 
  77:     period_s = get_orbit_period(altitude_m)
  78:     mean_motion_radian_per_minute = mm_radian_per_minute(period_s)
  79:     _raan_deg = raan_deg(orbit_index, num_orbits)
  80: 
  81:     sat.sgp4init(
  82:         GRAVITY_MODEL,        # gravity model
  83:         'i',                  # 'a' = old AFSPC mode, 'i' = improved mode
  84:         satellite_id,         # satnum: Satellite number
  85:         EPOCH,       # epoch: days since 1949 December 31 00:00 UT
  86:         DRAG_COEFFICIENT,     # bstar: drag coefficient (1/earth radii)
  87:         0.0,                  # ndot: ballistic coefficient (revs/day)
  88:         0.0,                  # nddot: mean motion 2nd derivative (revs/day^3)
  89:         ECCENTRICITY,         # ecco: eccentricity
  90:         ARG_PERIGEE_RAD,      # argpo: argument of perigee (radians)
  91:         math.radians(inclination_deg),    # inclo: inclination (radians)
  92:         math.radians(mean_anomaly_deg),   # mo: mean anomaly (radians)
  93:         mean_motion_radian_per_minute,    # no_kozai: mean motion (radians/minute)
  94:         math.radians(_raan_deg),          # nodeo: R.A. of ascending node (radians)
  95:     )
  96: 
  97:     tle_line1, tle_line2 = export_tle(sat)
  98:     tle_line1 = update_tle_international_designator(tle_line1)
  99: 
 100:     return tle_line1, tle_line2
 101: 
 102: 
 103: def orbit_phasing(orbit_index, num_sats_per_orbit):
 104:     """
 105:     Return orbit phasing shift.
 106:     """
 107:     if orbit_index % 2 != 1 or not PHASE_DIFF:
 108:         return 0
 109:     return 360.0 / (num_sats_per_orbit * 2.0)
 110: 
 111: 
 112: def mean_anomaly_degree(orbit_phasing_shift, sat_index, num_sats_per_orbit):
 113:     """
 114:     This is the angular position of the satellite in its orbit.
 115:     """
 116:     return orbit_phasing_shift + (sat_index / num_sats_per_orbit * 360.0)
 117: 
 118: 
 119: def raan_deg(orbit_index, num_orbits):
 120:     """
 121:     Right ascension of the ascending node.
 122:     """
 123:     return orbit_index * 360.0 / num_orbits
```

### TLE 读取的来源注释

源文件：`source/helpers/read_tles.py`，第 6–21 行。

```text
   6: def read_tles(filename_tles, id_start=0):
   7:     """
   8:     Read a constellation of satellites from the TLES file.
   9: 
  10:     :param filename_tles:                    Filename of the TLES (typically /path/to/tles.txt)
  11: 
  12:     :return: Dictionary: {
  13:                     "n_orbits":             Number of orbits
  14:                     "n_sats_per_orbit":     Satellites per orbit
  15:                     "epoch":                Epoch
  16:                     "satellites":           Dictionary of satellite id to
  17:                                             {"ephem_obj_manual": <obj>, "ephem_obj_direct": <obj>}
  18:               }
  19: 
  20:     This code is borrowed from Hypatia simulator
  21:     """
```

### 实际 TLE 到轨道对象转换

源文件：`source/helpers/read_tles.py`，第 62–79 行。

```text
  62: def tle_to_ephem(tle, universal_epoch):
  63:     tles_line_1 = tle[0]
  64:     tles_line_2 = tle[1]
  65:     # Fetch and check the epoch from the TLES data
  66:     # In the TLE, the epoch is given with a Julian data of yyddd.fraction
  67:     # ddd is actually one-based, meaning e.g. 18001 is 1st of January, or 2018-01-01 00:00.
  68:     # As such, to convert it to Astropy Time, we add (ddd - 1) days to it
  69:     # See also: https://www.celestrak.com/columns/v04n03/#FAQ04
  70:     epoch_year = tles_line_1[18:20]
  71:     epoch_day = float(tles_line_1[20:32])
  72:     epoch = Time("20" + epoch_year + "-01-01 00:00:00", scale="tdb") + (epoch_day - 1) * u.day
  73:     if universal_epoch is None:
  74:         universal_epoch = epoch
  75:     if epoch != universal_epoch:
  76:         raise ValueError("The epoch of all TLES must be the same")
  77: 
  78:     # Finally, store the satellite information
  79:     return ephem.readtle(tles_line_1, tles_line_1, tles_line_2), universal_epoch
```

### 固定四邻接逻辑拓扑

源文件：`source/models/topology.py`，第 1–39 行。

```text
   1: import networkx as nx
   2: 
   3: 
   4: class Topology:
   5:     def __init__(self, constellation) -> None:
   6:         self.constellation = constellation
   7:         self.hop_count_graph = nx.Graph()
   8:         self.build_hop_count_graph()
   9:         
  10:     def build_hop_count_graph(self):
  11:         for sat in self.constellation.satellites:
  12:             self.hop_count_graph.add_node(sat.id)
  13:         for sat in self.constellation.satellites:
  14:             t_neighbor_id, b_neighbor_id = self.intra_orbit_neighbor_ids(sat)
  15:             l_neighbor_id, r_neighbor_id = self.inter_orbit_neighbor_ids(sat)
  16:             self.hop_count_graph.add_edge(sat.id, t_neighbor_id, weight=1)
  17:             self.hop_count_graph.add_edge(sat.id, b_neighbor_id, weight=1)
  18:             self.hop_count_graph.add_edge(sat.id, l_neighbor_id, weight=1)
  19:             self.hop_count_graph.add_edge(sat.id, r_neighbor_id, weight=1)
  20:     
  21:     def intra_orbit_neighbor_ids(self, sat):
  22:         sats_per_orbit = self.constellation.satellites_per_orbit
  23:         orbit_id = sat.orbit_idx
  24:         sat_index = sat.id - (orbit_id * sats_per_orbit)
  25:         top_neighbor_id = ((sat_index + 1) % sats_per_orbit) + (orbit_id * sats_per_orbit)
  26:         bottom_neighbor_id = ((sat_index + sats_per_orbit - 1) % sats_per_orbit) + (orbit_id * sats_per_orbit)
  27:         return top_neighbor_id, bottom_neighbor_id
  28:     
  29:     def inter_orbit_neighbor_ids(self, sat):
  30:         num_orbits = self.constellation.num_orbits
  31:         sats_per_orbit = self.constellation.satellites_per_orbit
  32:         orbit_id = sat.orbit_idx
  33:         sat_index = sat.id - (orbit_id * sats_per_orbit)
  34:         left_orbit_id = (orbit_id + num_orbits - 1) % num_orbits
  35:         right_orbit_id = (orbit_id + 1) % num_orbits
  36:         # Assume no orbital seams
  37:         left_neighbor_id = left_orbit_id * sats_per_orbit + sat_index
  38:         right_neighbor_id = right_orbit_id * sats_per_orbit + sat_index
  39:         return left_neighbor_id, right_neighbor_id    
```

### 按跳数选路实际位于任务生成器

源文件：`source/models/task.py`，第 47–56 行。

```text
  47:     def get_path_without_offloading(self, source_sat, dest_sat):
  48:         path = nx.shortest_path(
  49:                 self.constellation.topology.hop_count_graph, 
  50:                 source=source_sat.id, target=dest_sat.id, weight='weight')
  51:         return path
  52:     
  53:     def get_delay_requirement(self, path, traffic_mb):
  54:         delay_without_offloading_ms = self.delay_manager.delay_ms(path, traffic_mb, None, is_offloaded=False)
  55:         margin_delay_percent = 0.1  # TODO: discuss how to set this margin
  56:         return delay_without_offloading_ms * (1 + margin_delay_percent)
```

### 时延组成与固定的 GSL 距离

源文件：`source/models/delay_manager.py`，第 7–35 行。

```text
   7: class DelayManager:
   8:     def __init__(self, constellation, time_step, tf) -> None:
   9:         self.constellation = constellation
  10:         self.time_step = time_step
  11:         # Queueing delay set according to 
  12:         # TLR: A Traffic-Light-Based Intelligent Routing Strategy for NGEO Satellite IP Networks
  13:         self.avg_queueing_delay_ms = 8.0 * 2  # times 2 to simulate congested satellite networks
  14:         self.tf = tf
  15:     
  16:     def delay_ms(self, path_without_offloading, traffic_mb, group, offloading_sat_index=0, is_offloaded=False):
  17:         total_delay_ms = 0
  18:         if not is_offloaded:
  19:             total_delay_ms += self.propagation_delay_ms(path_without_offloading)
  20:             total_delay_ms += self.queueing_delay_ms(path_without_offloading)
  21:             total_delay_ms += self.transmission_delay_ms(path_without_offloading)
  22:         else:
  23:             # If offloaded, count the GSL propagation delay and pop delay
  24:             total_delay_ms += 550000 / c * 1000.0  # 550 km altitude LEO satellites
  25:             max_split_delay_ms = float('-inf')
  26:             for bid in group:
  27:                 bid_offloading_path = path_without_offloading[:offloading_sat_index + 1 + bid.offloading_sat_offset]
  28:                 bid_delay_ms = 0
  29:                 bid_delay_ms += self.propagation_delay_ms(bid_offloading_path)
  30:                 bid_delay_ms += self.queueing_delay_ms(bid_offloading_path)
  31:                 bid_delay_ms += self.transmission_delay_ms(bid_offloading_path)
  32:                 bid_delay_ms += bid.pop_delay_ms
  33:                 if bid_delay_ms > max_split_delay_ms:
  34:                     max_split_delay_ms = bid_delay_ms
  35:             total_delay_ms += max_split_delay_ms
```

### 传播、排队、传输时延实现

源文件：`source/models/delay_manager.py`，第 45–81 行。

```text
  45:     def propagation_delay_ms(self, path):
  46:         total_prop_delay_ms = 0
  47:         for i in range(len(path) - 1):
  48:             sat1 = self.constellation.satellites[path[i]]
  49:             sat2 = self.constellation.satellites[path[i + 1]]
  50:             total_prop_delay_ms += self.propagation_delay_ms_between_sats(sat1, sat2, self.time_step)
  51:         return total_prop_delay_ms
  52: 
  53:     def propagation_delay_ms_between_sats(self, sat1, sat2, time_step):
  54:         distance_m = sat1.distance_from(sat2, time_step)
  55:         return distance_m / c * 1000.0
  56:     
  57:     def queueing_delay_ms(self, path):
  58:         total_queueing_delay_ms = 0
  59:         for i in range(len(path)):
  60:             sat = self.constellation.satellites[path[i]]
  61:             total_queueing_delay_ms += self.queueing_delay_ms_on_sat(sat)
  62:         return total_queueing_delay_ms
  63: 
  64:     def queueing_delay_ms_on_sat(self, sat):
  65:         lat_deg = math.degrees(sat.ephem.sublat)
  66:         lon_deg = math.degrees(sat.ephem.sublong)
  67:         scaled_num_users = local_users_scaled_by_time(lat_deg, lon_deg, self.time_step.current_time, self.tf)
  68:         original_num_users = local_users(lat_deg, lon_deg)
  69:         if original_num_users == 0:
  70:             return 0
  71:         return self.avg_queueing_delay_ms * scaled_num_users / original_num_users
  72: 
  73:     def transmission_delay_ms(self, path):
  74:         total_transmission_delay_ms = 0
  75:         for i in range(len(path)):
  76:             sat = self.constellation.satellites[path[i]]
  77:             total_transmission_delay_ms += self.transmission_delay_ms_on_sat(sat, AVG_PKT_SIZE_MBIT)
  78:         return total_transmission_delay_ms
  79:     
  80:     def transmission_delay_ms_on_sat(self, sat, traffic_mb):
  81:         return traffic_mb / sat.bandwidth_mbps * 1000.0
```

### 地面站对象与投标行为

源文件：`source/models/dish.py`，第 11–48 行。

```text
  11: class Dish:
  12:     def __init__(self, id, lat_deg, long_deg, bandwidth_mbps, row, col, type, avg_failure_rate) -> None:
  13:         self.id = id
  14:         self.lat_deg = lat_deg
  15:         self.long_deg = long_deg
  16:         self.bandwidth_mbps = bandwidth_mbps
  17:         self.avg_failure_rate = avg_failure_rate
  18:         self.empirical_failure_rate = avg_failure_rate
  19:         self.number_of_times_won_bids = 0
  20:         self.row = row
  21:         self.col = col
  22:         self.type: GS_TYPES = type
  23:         
  24:         # Network Characteristics of LEO Satellite Constellations: A Starlink-Based Measurement from End Users
  25:         # Conversion from INFOCOM measurement paper
  26:         # 56.3 Watt, 80Mb/s throughput => 0.704 Watt/ Mbps
  27:         self.epsilon_d = 0.704
  28:         
  29:         # https://aws.amazon.com/ec2/pricing/on-demand/
  30:         # First 10 TB / Month: $0.09 per GB
  31:         self.alpha = 0.09 / 8000.0  # price per Mb
  32:         
  33:         # https://azure.microsoft.com/en-ca/pricing/details/orbital/
  34:         # $10 per min -> 0.17 per second
  35:         self.beta = 0.17
  36:     
  37:     def propose_bid(self, dest_lat_deg, dest_long_deg, cost_margin=0) -> Bid:
  38:         traffic_amount_mb = np.random.choice([50, 100, 200, 400])
  39:         bandwidth_mbps = self.bandwidth_mbps * np.random.uniform(0.8, 1)
  40:         bid = Bid(
  41:             cost=self.get_dish_cost(traffic_amount_mb, bandwidth_mbps, cost_margin),
  42:             traffic_amount_mb=traffic_amount_mb,
  43:             pop_delay_ms=self.delay_ms_between(dest_lat_deg, dest_long_deg),
  44:             bandwidth_mbps=bandwidth_mbps,
  45:             offloading_sat_offset=random.randint(0, 2),
  46:             bidder=self
  47:         )
  48:         return bid
```

### 按地理网格挑选投标者

源文件：`source/models/auction.py`，第 64–79 行。

```text
  64:     def collect_bids(self, task):
  65:         # Collect bids based on location
  66:         source_sat = task.traffic_pair[0]
  67:         source_lat_deg = math.degrees(source_sat.ephem.sublat)
  68:         source_long_deg = math.degrees(source_sat.ephem.sublong)
  69:         
  70:         dest_sat = task.traffic_pair[1]
  71:         dest_lat_deg = math.degrees(dest_sat.ephem.sublat)
  72:         dest_long_deg = math.degrees(dest_sat.ephem.sublong)
  73:         
  74:         row, col = map_lat_long_to_grid(source_lat_deg, source_long_deg)
  75:         dishes = self.dish_generator.dish_grid[row, col]
  76:         bids = []
  77:         for dish in dishes:
  78:             bids.append(dish.propose_bid(dest_lat_deg, dest_long_deg, cost_margin=AUCTION_COST_MARGIN))        
  79:         return bids
```

### 事件调度和时间推进

源文件：`source/simulation.py`，第 6–63 行。

```text
   6: class Simulation:
   7:     def __init__(self, max_steps, time_step, is_verbose=False) -> None:
   8:         self.event_callbacks = []
   9:         self.event_intervals = []
  10:         self.event_starts = []
  11:         self.event_ends = []
  12:         self.event_args = []
  13:         self.event_output = {}
  14:         self.event_input_ids = {}
  15:         self.event_messages = {}
  16:         self.event_ids = []
  17:         self.max_steps = max_steps
  18:         self.is_verbose = is_verbose
  19:         self.time_step = time_step
  20:     
  21:     def start(self):
  22:         for step in range(self.max_steps):
  23:             if self.is_verbose:
  24:                 print('======= Step {} ======='.format(step))
  25:             for i in range(len(self.event_callbacks)):
  26:                 if step > self.event_ends[i] or step < self.event_starts[i]:
  27:                     continue
  28:                 if (step - self.event_starts[i]) % (self.event_intervals[i]) != 0:
  29:                     continue
  30:                 args = self.event_args[i].copy()
  31:                 if self.event_input_ids[self.event_ids[i]] is not None:
  32:                     args.append(self.event_output[self.event_input_ids[self.event_ids[i]]])             
  33:                 output = self.event_callbacks[i](*args)
  34:                 self.event_output[self.event_ids[i]] = output
  35:                 if self.is_verbose:
  36:                     if self.event_messages[self.event_ids[i]] is not None:
  37:                         print(self.event_messages[self.event_ids[i]])
  38:             self.time_step.next()
  39:     
  40:     def register(self, id, event_callback, interval, args=[], start=0, end=float('inf'), input_event_id=None, message=None):
  41:         if start < 0 or end < start:
  42:             raise ValueError('Invalid start and end values.')
  43:         self.event_callbacks.append(event_callback)
  44:         self.event_intervals.append(interval)
  45:         self.event_starts.append(start)
  46:         self.event_ends.append(end)
  47:         self.event_args.append(args)
  48:         self.event_ids.append(id)
  49:         self.event_input_ids[id] = input_event_id
  50:         self.event_output[id] = None
  51:         self.event_messages[id] = message
  52: 
  53: 
  54: class TimeStep:
  55:     def __init__(self, start_time: ephemDate, interval: timedelta) -> None:
  56:         self.start_time: ephemDate = start_time
  57:         self.current_time: ephemDate = self.start_time
  58:         self.interval = interval.total_seconds() / (24 * 60 * 60)
  59:         self.time_step_counter = 0
  60:         
  61:     def next(self):
  62:         self.current_time = ephem.Date(self.current_time + self.interval)
  63:         self.time_step_counter += 1
```

### 研究批处理入口及事件装配

源文件：`source/main.py`，第 30–79 行。

```text
  30: DEBUG = False
  31: seed = 1234
  32: MAX_STEPS = 100
  33: 
  34: START_DATE_STR = '2000/1/2 12:00:00'
  35: INTERVAL = timedelta(seconds=60)
  36: 
  37: IS_VERBOSE = True
  38: 
  39: 
  40: class EXP_NAME(Enum):
  41:     DEBUG = 0
  42:     FIXED_BUDGET = 1
  43:     VARIABLE_BUDGET = 2
  44:     NETWORK_SIZES = 3
  45: 
  46: 
  47: def start(constellation_name, max_budget, avg_failure_rate, bad_dish_prob, failure_rate_fluctuation, algo, tf, experiment_name):
  48:     if SKIP_DEFAULT and algo == Algorithms.DEFAULT:
  49:         return
  50:     if IS_VERBOSE:
  51:         print(f'Running for constellation {constellation_name}')
  52:         print(f'Running for avg failure rate {avg_failure_rate}.')
  53:         print(f'Running for algorithm {algo.name}.')
  54:     START_EPHEM_DATE = ephem.Date(START_DATE_STR)
  55:     TIME_STEP = TimeStep(start_time=START_EPHEM_DATE, interval=INTERVAL)
  56:     np.random.seed(seed)
  57:     random.seed(seed)
  58:     data_manager = DataManager()
  59:     sim = Simulation(max_steps=MAX_STEPS, time_step=TIME_STEP, is_verbose=IS_VERBOSE)
  60:     constellation = get_constellation(constellation_name, tf=tf)
  61:     traffic_generator = TrafficGenerator(constellation=constellation, tf=tf)
  62:     energy = Energy(constellation=constellation)
  63:     delay_manager = DelayManager(constellation=constellation, time_step=TIME_STEP, tf=tf)
  64:     routing = Routing(constellation, data_manager, delay_manager, algo)
  65:     dish_generator = DishManager(TRAFFIC_GRID, avg_failure_rate, bad_dish_prob, failure_rate_fluctuation)
  66:     task_generator = TaskGenerator(constellation=constellation, delay_manager=delay_manager)
  67:     algorithm = Algorithm(max_budget, dish_generator, delay_manager, constellation, data_manager, IS_VERBOSE)
  68:     
  69:     sim.register(id=EVENT_ID.UPDATE_SATELLITES, event_callback=constellation.update_satellites, interval=1, args=[TIME_STEP], message='Updated satellites')
  70:     sim.register(id=EVENT_ID.GENERATE_TRAFFIC, event_callback=traffic_generator.generate_traffic, interval=1, args=[TIME_STEP], message='Generated traffic')
  71:     sim.register(id=EVENT_ID.GENERATE_TASKS, event_callback=task_generator.create_tasks, interval=1, input_event_id=EVENT_ID.GENERATE_TRAFFIC, message='Created tasks')
  72:     sim.register(id=EVENT_ID.CHARGE_SATELLITES, event_callback=energy.charge_satellites, interval=1, message='Charged satellites')
  73:     sim.register(id=EVENT_ID.RANDOMIZE_DOD, event_callback=constellation.randomize_satellite_dod, interval=1, args=[TIME_STEP], message='Randomized DoD to simulate background traffic')
  74:     sim.register(id=EVENT_ID.START_ALGORITHM, event_callback=algorithm.start, interval=1, args=[algo], input_event_id=EVENT_ID.GENERATE_TASKS, message='Started algorithm')
  75:     sim.register(id=EVENT_ID.ROUTE_TRAFFIC, event_callback=routing.route_traffic, interval=1, input_event_id=EVENT_ID.START_ALGORITHM, message='Routed traffic and consumed energy')
  76:     
  77:     sim.start()
  78:     
  79:     data_manager.write_to_csv(constellation_name, max_budget, algo, avg_failure_rate, bad_dish_prob, failure_rate_fluctuation, experiment_name)
```

### 批量多进程实验入口

源文件：`source/main.py`，第 89–135 行。

```text
  89: def run_processes(param_combinations, max_processes=48):
  90:     semaphore = multiprocessing.Semaphore(max_processes)
  91:     processes = []
  92: 
  93:     for params in param_combinations:
  94:         process = multiprocessing.Process(target=start_process, args=(params, semaphore))
  95:         processes.append(process)
  96:         process.start()
  97: 
  98:     for process in processes:
  99:         process.join()
 100: 
 101: 
 102: if __name__ == '__main__':
 103:     
 104:     start_time = time.time()
 105:     if DEBUG:
 106:         
 107:         # Single thread for debugging
 108:         semaphore = multiprocessing.Semaphore(1)
 109:         start_process((CONSTELLATION_NAME.STARLINK_550, MAX_BUDGETS[0], AVG_FAILURE_RATES[0], BAD_DISH_PROBS[0], FAILURE_RATE_FLUCTUATION[0], Algorithms.REVERSE_AUCTION, EXP_NAME.DEBUG.name),  semaphore=semaphore)
 110:     
 111:     else:
 112: 
 113:         # First scenario: fixed max budget
 114:         fixed_max_budget = [MAX_BUDGETS[0]]
 115:         algorithms = [Algorithms.REVERSE_AUCTION, Algorithms.SERVICE, Algorithms.SUSTAINABILITY, Algorithms.FALCON]
 116:         param_combinations = list(itertools.product([CONSTELLATION_NAME.STARLINK_550], fixed_max_budget, AVG_FAILURE_RATES, BAD_DISH_PROBS, FAILURE_RATE_FLUCTUATION, algorithms, [EXP_NAME.FIXED_BUDGET.name]))
 117:         run_processes(param_combinations)
 118:         
 119:         # First scenario with another constellation
 120:         fixed_max_budget = [MAX_BUDGETS[0]]
 121:         algorithms = [Algorithms.REVERSE_AUCTION, Algorithms.SERVICE, Algorithms.SUSTAINABILITY, Algorithms.FALCON]
 122:         param_combinations = list(itertools.product([CONSTELLATION_NAME.ONEWEB_18_40_1200], fixed_max_budget, AVG_FAILURE_RATES, BAD_DISH_PROBS, FAILURE_RATE_FLUCTUATION, algorithms, [EXP_NAME.FIXED_BUDGET.name]))
 123:         run_processes(param_combinations)
 124: 
 125:         # Second scenario: fixed avg failure rate, bad dish probabilities, and failure rate fluctuation
 126:         fixed_avg_failure_rate = [AVG_FAILURE_RATES[0]]
 127:         fixed_bad_dish_probs = [BAD_DISH_PROBS[0]]
 128:         fixed_failure_rate_fluctuation = [FAILURE_RATE_FLUCTUATION[0]]
 129:         algorithms = [Algorithms.REVERSE_AUCTION, Algorithms.SERVICE, Algorithms.SUSTAINABILITY, Algorithms.FALCON]
 130:         param_combinations = list(itertools.product([CONSTELLATION_NAME.STARLINK_550, CONSTELLATION_NAME.ONEWEB_18_40_1200], MAX_BUDGETS, fixed_avg_failure_rate, fixed_bad_dish_probs, fixed_failure_rate_fluctuation, algorithms, [EXP_NAME.VARIABLE_BUDGET.name]))
 131:         run_processes(param_combinations)
 132:         
 133:         # Third scenario: fixed everything, use different constellations for our proposed algorithms
 134:         param_combinations = list(itertools.product(list(CONSTELLATION_NAME), [MAX_BUDGETS[0]], [AVG_FAILURE_RATES[0]], [BAD_DISH_PROBS[0]], [FAILURE_RATE_FLUCTUATION[0]], [Algorithms.REVERSE_AUCTION, Algorithms.SERVICE, Algorithms.SUSTAINABILITY, Algorithms.FALCON], [EXP_NAME.NETWORK_SIZES.name]))
 135:         run_processes(param_combinations)
```

### 按数据流修改卫星能源状态

源文件：`source/models/routing.py`，第 52–89 行。

```text
  52:         for task in tasks:
  53:             source_sat, dest_sat, traffic_mb = task.traffic_pair
  54:             if traffic_mb == 0:
  55:                 continue
  56:             is_failed = False
  57:             is_offloaded = False
  58:             if self.has_winner(task):
  59:                 is_offloaded = True
  60:                 if self.has_failed(task):
  61:                     is_failed = True
  62:                     is_offloaded = False
  63:                     path = task.path_without_offloading
  64:                     self.update_dish_empirical_failure_rate_and_num_wins(task, has_failed=True)
  65:                     self.data_manager.data['per_offloaded_task_is_failed'][-1].append(True)
  66:                 else:
  67:                     path = task.path_with_offloading
  68:                     self.update_dish_empirical_failure_rate_and_num_wins(task, has_failed=False)
  69:                     self.data_manager.data['per_offloaded_task_is_failed'][-1].append(False)
  70:             else:
  71:                 path = task.path_without_offloading
  72: 
  73:             per_task_actual_life_consumption = 0
  74:             per_task_actual_energy_consumption = 0  
  75:             for sat_id in path:
  76:                 life_consumption, energy_consumption = self.constellation.satellites[sat_id].route_traffic(traffic_mb)
  77:                 
  78:                 total_life_consumption += life_consumption
  79:                 total_energy_consumption += energy_consumption
  80:                 
  81:                 per_task_actual_life_consumption += life_consumption
  82:                 per_task_actual_energy_consumption += energy_consumption
  83:             
  84:             # GSL energy consumption is already included
  85:             # because the last satellite hop contains sending energy
  86:             # We do not need to consider dish receiving energy because it is in the dish cost
  87:             task_delay_ms = self.delay_manager.delay_ms(task.path_without_offloading, traffic_mb, task.winner, offloading_sat_index=OFFLOADING_SAT_INDEX, is_offloaded=is_offloaded)
  88:             if task_delay_ms > task.delay_ms_requirement:
  89:                 raise Exception('Task delay exceeds the delay requirement.')
```

### 太阳充电的固定 60 秒假设

源文件：`source/models/energy.py`，第 1–13 行。

```text
   1: class Energy:
   2:     def __init__(self, constellation) -> None:
   3:         self.constellation = constellation
   4:         # Towards Energy-Efficient Routing in Satellite Networks
   5:         # Max solar output is set as 500 Watt from the reference
   6:         # Since our interval is 60 seconds (1 min), so here we set 500 Watt * 1 min = 500 Watt min
   7:         self.energy_source_watt_min = 500
   8: 
   9:     def charge_satellites(self):
  10:         for sat in self.constellation.satellites:
  11:             if sat.ephem.eclipsed:
  12:                 continue
  13:             sat.battery.charge(self.energy_source_watt_min)
```

### 背景流量及随机目的端

源文件：`source/models/traffic.py`，第 8–35 行。

```text
   8: class TrafficGenerator:
   9:     def __init__(self, constellation, tf) -> None:
  10:         self.constellation = constellation
  11:         self.SECONDS_PER_MIN = 60
  12:         self.PER_USER_TRAFFIC_KBPS = 1024 * 300
  13:         self.tf = tf
  14:     
  15:     def generate_traffic(self, time_step):
  16:         traffic_pairs = []
  17:         for sat in self.constellation.satellites:
  18:             traffic_mb = self.generate_traffic_from_sat_mb(sat, time_step)
  19:             dest = self.choose_dest(sat, list(range(20, 25)))
  20:             traffic_pairs.append((sat, dest, traffic_mb))
  21:         return traffic_pairs
  22:     
  23:     def generate_traffic_from_sat_mb(self, sat, time_step):
  24:         lat_deg = math.degrees(sat.ephem.sublat)
  25:         lon_deg = math.degrees(sat.ephem.sublong)
  26:         num_users, local_time = local_users_time(lat_deg, lon_deg, time_step.current_time, self.tf)
  27:         scaled_num_users = local_users_scaled_by_time(lat_deg, lon_deg, time_step.current_time, self.tf)
  28:         if num_users == 0:
  29:             return 0
  30:         users_per_min = self.poisson_distribution(num_users, 1)
  31:         # per_user_traffic_kbps_list = self.normal_distribution(self.PER_USER_TRAFFIC_KBPS, sum(users_per_min), self.PER_USER_TRAFFIC_KBPS)
  32:         # total_traffic_kpbs = sum(per_user_traffic_kbps_list)
  33:         traffic_amount_mb = self.PER_USER_TRAFFIC_KBPS / 1024.0
  34:         traffic_amount_mb = traffic_amount_mb * scaled_num_users / num_users
  35:         return traffic_amount_mb
```

### 原 README 的运行方式

源文件：`README.md`，第 1–34 行。

```text
   1: # INFOCOM 2025: Commercial Dishes Can Be My Ladder: Sustainable and Collaborative Data Offloading in LEO Satellite Networks
   2: 
   3: UserGS_simulation
   4: 
   5: The results were produced by using Python 3.11.
   6: 
   7: To run simulation and produce data, run:
   8: 
   9: ```
  10: cd source
  11: python main.py
  12: ```
  13: 
  14: The simulation data will be stored in the output folder.
  15: 
  16: To debug, make DEBUG = True in main.py. This will change the simulation to be single thread with auction algorithm only. Then, we can place debugger point and run debugger.
  17: 
  18: After the simulation is completed, run this to make plot:
  19: 
  20: ```
  21: cd source
  22: python plot.py
  23: ```
  24: 
  25: The plots will be in the output folder.
  26: 
  27: To get the statistics such as percentage of better performance, run:
  28: 
  29: ```
  30: cd source
  31: python statistics.py
  32: ```
  33: 
  34: Some csv files with statistics will be stored in the output folder.
```
