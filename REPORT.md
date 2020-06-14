
## How to

python manage.py makemigrations
python manage.py migrate




## What I tried

### Multiprocessing
The import.py uses multiprocessing for making the process little bit faster. Because if current users are scaled to 9 billion users, this import.py will be stuck.

## Future
GPU based calcurating and storing with [BlazingSQL (GPU accelerated SQL)](https://blazingsql.com/) and [cuDF (GPU DataFrames)](https://github.com/rapidsai/cudf).
