import os

init = """
./tests/user_bench/build.sh bison
./tests/user_bench/run.sh pack bison

./tests/user_bench/run.sh run bison -v

"""

data_path = "/dev/shm/kafl_bison"

path = os.path.dirname(os.path.abspath(__file__))
count = 10

for i in range(count):
    os.system(init)
    os.system('mv ' + data_path + ' ' + path+'/out' + f'{i}'.zfill(3))