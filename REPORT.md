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
python manage.py importer
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
consumptionのリストでsumをとったり演算をすると計算誤差が起こり，ズレが生じる

SQLiteではREAL（IEEEの8バイトの浮動小数点数），Pythonではdecimalで今回扱っている


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
Samples I created were wrong. A number of comsumptions per day was over 48.


[Similar issue](https://code.djangoproject.com/ticket/26963)

## Q&A
### Why deciaml instead of double?
0.3 - 0.2 -> 0.09999999999999998

### Why test datasets are random?


### Why test random functions are safe?


## What I tried

### Multiprocessing
The import.py uses multiprocessing for making the process little bit faster. Because if current users are scaled to 9 billion users, this import.py will be stuck.


## Future prospects
I sometimes use HLSL / GLSL as a GPU calculation language which make around 100 times faster than CPU calculation although it has some limitation. However I haven't used a GPU based calcuration library with Python yet. So I will try it in the near future.

And also, I found a GPU based calcurating SQL and dataframe library which can run in Python. ([BlazingSQL (GPU accelerated SQL)](https://blazingsql.com/) and [cuDF (GPU DataFrames)](https://github.com/rapidsai/cudf).) These tools will make much more faster storing and calcuration.

I am look foward to use these tools!
