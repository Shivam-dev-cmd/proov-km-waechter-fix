# What I checked, and what the agent got wrong

1.Incorrect MILES_PER_KM value in fleet_util.py
the value was set to 1.609, which is actually the number of kilometer in one mile. for converting kilometeres to miles, the correct value is 0.621371. the bug was easy to miss because 1.609 looks like a reasonable conversation value at first glance.

2.integer division in wear_percentage() in km_wachter.py
The code used // instead of /. For example, 14908 // 15eee gives e, even though the car is at roughly 99% of its service interval. This meant heavily wom cars could incorrectly show ex wear and avoid the service warming

3.Incorrect handling of missing readings in needs service() The code used car.get("last service ka", e). When last service los was missing, it treated the value as e. That made the calculation odometer-6, which could incorrectly mark a car as overdue for service.


## What I checked before I accepted its work

Before accepting the fixes, I checked the following:

Ran python verify.py and all checks passed.
Ran the full pytest test suite. All tests passed, including test_summary_does_not_crash_on_missing_reading.
Confirmed that the values in settings.cfg were unchanged: the service interval is still 15,000 km and the wear threshold is still 80%.
Manually checked the MILES_PER_KM change. Since 1 mile is about 1.60934 km, converting kilometres to miles requires dividing by 1.60934, which gives approximately 0.621.


## What the data actually said

The data did not show much difference in odometer_km or age_years between cars that broke down and cars that did not. So the simple assumption that older cars or cars with higher total mileage were more likely to break down was not supported by this dataset.

The stronger signals were: km_since_service: cars that broke down had an average of about 12,700 km since their last service, compared with about 7,700 km for cars that did not.

load_factor: the average was 0.66 for cars that broke down versus 0.46 for healthy cars.
avg_daily_km: cars that broke down averaged around 176 km per day, compared with about 124 km per day for the others.

The risk score was based on these three values, using weights of 0.45, 0.35, and 0.20, respectively.
