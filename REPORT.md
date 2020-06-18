# Report

## How to install
```
pip install -r requirements.txt
```

## How to run
If you have a make commad, you can run easier and faster. Look at Makefile at `./dashboard/Makefile`.

### 1. Migrate
```
cd ./dashboard/
python manage.py makemigrations
python manage.py migrate
```

### 2. Import datasets
```
python manage.py import
```

### 3. Run a server

```
python manage.py runserver localhost:10000
```

### 4. Test it
```
python manage.py test consumption
```






## Issue
I encoutered an issue which I haven't soloved when I run the test many times. It happended only one time. Therefore it requires enough time to test at a random decimal function I created. Especially rounding method of Decimal is pretty tricky when I
One thing

```
  File "/Users/takahashitasuku/iTask/smap-coding-challenge/dashboard/consumption/tests/test_aggregations.py", line 39, in test_aggregations
    UserEConsumptionDayAggregation.calc_consumptions()
  File "/Users/takahashitasuku/iTask/smap-coding-challenge/dashboard/consumption/models.py", line 67, in calc_consumptions
    for row in data_frame.to_dict('records')
  <....>
  File "/path_to_django/db/backends/utils.py", line 204, in format_number
    value = value.quantize(decimal.Decimal(".1") ** decimal_places, context=context)
decimal.InvalidOperation: [<class 'decimal.InvalidOperation'>]
```

[Similar issue](https://code.djangoproject.com/ticket/26963)

## Q&A
### Why deciaml instead of float?
0.3 - 0.2 -> 0.09999999999999998


## What I tried

### Multiprocessing
The import.py uses multiprocessing for making the process little bit faster. Because if current users are scaled to 9 billion users, this import.py will be stuck.

## Future
GPU based calcurating and storing with [BlazingSQL (GPU accelerated SQL)](https://blazingsql.com/) and [cuDF (GPU DataFrames)](https://github.com/rapidsai/cudf).
