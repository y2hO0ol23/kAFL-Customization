from fuzzer.technique.havoc_handler import *
from fuzzer.communicator import MSG_PSO_RUN
import random

class PSO:
    period_core = 500000
    period_pilot = 50000
    w_init = 0.9
    w_end = 0.3
    g_max = 5000
    v_max = 1
    v_min = 0.05
    swarm_num = 5

    @staticmethod
    def get_handler_num():
        return len(havoc_handler)
    
    @staticmethod
    def get_swarm_num():
        return PSO.swarm_num + 1
    
    @staticmethod
    def get_core_num():
        return PSO.swarm_num

    @staticmethod
    def list_init(v = 0):
        return [[v]*PSO.get_handler_num() for _ in range(PSO.get_swarm_num())]
    
    @staticmethod
    def rand(v = 1):
        return random.random() * v

    @staticmethod
    def sat(val, st, ed):
        if st > ed: 
            return PSO.sat(ed, st)

        if val < st: return st
        if ed < val: return ed

        return val

    def update_probability(self, tmp_swarm):
        w_now = (PSO.w_init - PSO.w_end)*(PSO.g_max - self.g_now) / (PSO.g_max)+PSO.w_end

        for i in range(PSO.get_handler_num()):
            self.v_now[tmp_swarm][i] =  w_now * self.v_now[tmp_swarm][i] + \
                                        PSO.rand() * (self.L_best[tmp_swarm][i] - self.x_now[tmp_swarm][i]) + \
                                        PSO.rand() * (self.G_best[i] - self.x_now[tmp_swarm][i])

            self.x_now[tmp_swarm][i] += self.v_now[tmp_swarm][i]
            self.x_now[tmp_swarm][i] = PSO.sat(self.x_now[tmp_swarm][i], PSO.v_min, PSO.v_max)

        total = sum(self.x_now[tmp_swarm])
        self.x_now[tmp_swarm] = [v / total for v in self.x_now[tmp_swarm]]

        self.probability_now[tmp_swarm] = [0]

        for i in range(PSO.get_handler_num()):
            value = self.probability_now[tmp_swarm][i] + self.x_now[tmp_swarm][i]
            self.probability_now[tmp_swarm].append(value)
    
        del self.probability_now[tmp_swarm][0]


    def __init__(self):
        self.x_now = PSO.list_init()
        self.L_best = PSO.list_init(0.5)
        self.eff_best = PSO.list_init()
        self.G_best = [0.5] * PSO.get_handler_num()
        self.v_now = PSO.list_init(0.1)
        self.probability_now = [[]] * PSO.get_swarm_num()
        self.swarm_fitness = [0] * PSO.swarm_num

        self.finds = PSO.list_init()
        self.cycles = PSO.list_init()
        self.finds_total = PSO.list_init()
        
        self.total_hit = [0] * PSO.get_handler_num()
        self.g_now = 0
        self.time = [0] * PSO.get_handler_num()

        for tmp_swarm in range(PSO.swarm_num):
            rand = [(PSO.rand(0.7) + 0.1) for _ in range(PSO.get_handler_num())]
            total = sum(rand)
            self.x_now[tmp_swarm] = [x / total for x in rand]

            self.update_probability(tmp_swarm)


    def pilot_fuzz_init(self):
        for tmp_swarm in range(PSO.get_swarm_num()):
            for i in range(PSO.get_handler_num()):
                self.finds[tmp_swarm][i] = 0
                self.cycles[tmp_swarm][i] = 0
                
            self.time[tmp_swarm] = 0
            self.total_hit[tmp_swarm] = 0


    def core_fuzz_init(self):
        for tmp_swarm in range(PSO.swarm_num):
            self.swarm_fitness[tmp_swarm] = self.total_hit[tmp_swarm] / self.time[tmp_swarm]

            for i in range(PSO.get_handler_num()):
                eff = 0.0
                if self.cycles[tmp_swarm][i]:
                    eff = self.finds[tmp_swarm][i] / self.cycles[tmp_swarm][i]

                if self.eff_best[tmp_swarm][i] < eff:
                    self.eff_best[tmp_swarm][i] = eff
                    self.L_best[tmp_swarm][i] = self.x_now[tmp_swarm][i]
            
                self.finds_total[tmp_swarm][i] += self.finds[tmp_swarm][i]
            
        self.fitness = 0
        for i in range(1, PSO.swarm_num):
            if self.swarm_fitness[self.fitness] < self.swarm_fitness[i]:
                self.fitness = i
    

    def update(self, swarm_num, state):
        self.total_hit[swarm_num] += state['total_hit']
        new_finds = state['finds']
        new_cycles = state['cycles']
        for i in range(PSO.get_handler_num()):
            self.finds[swarm_num][i] += new_finds[i]
            self.cycles[swarm_num][i] += new_cycles[i]


    def update_global(self):
        self.g_now += 1
        if self.g_now > PSO.g_max:
            self.g_now = 0
        
        finds_total = [0 for _ in range(PSO.get_handler_num())]
        for i in range(PSO.get_handler_num()):
            for tmp_swarm in range(PSO.swarm_num):
                finds_total[i] += self.finds_total[tmp_swarm][i]
        
        total = sum(finds_total)

        for i in range(PSO.get_handler_num()):
            if finds_total[i]:
                self.G_best[i] = finds_total[i] / total

        for tmp_swarm in range(PSO.swarm_num):
            self.update_probability(tmp_swarm)


class ServerPSO:
    pilot = 0
    core = 1

    def __init__(self, comm):
        self.pso = []
        self.wait = []
        self.state = []
        self.done = []
        self.count = 0
        self.main_id = self.make_new()
        self.comm = comm


    def select_main_id(self): # 현재까지 진행한 횟수가 가장 많은 pso space를 선택
        time_total = [sum(pso.time) for pso in self.pso]
        self.main_id = 0
        for i in range(1, len(time_total)):
            if time_total[i] > time_total[self.main_id]:
                self.main_id = i

    
    def next_id(self, id):
        return (id + 1) % self.count


    def make_new(self):
        self.pso.append(PSO())
        self.wait.append(0)
        self.done.append(0)
        self.state.append(ServerPSO.pilot)
        self.count += 1
        #self.debug(self.count - 1)
        return self.count - 1


    def select_and_send(self, client, time, id=None):
        if id == None:
            id = self.main_id
        elif id == self.main_id: # pso 공간이 부족하다면
            id = self.make_new() # 새롭게 생성

        if self.state[id] == ServerPSO.core:
            if self.stage_core_fuzz(client, time, id):
                return
        else:
            if self.stage_pilot_fuzz(client, time, id):
                return
                    
        self.select_and_send(client, time, self.next_id(id)) # slave에 정보를 보내지 못했다면 다음 아이디에서 같은 과정을 반복


    def stage_core_fuzz(self, client, time, id):
        pso:PSO = self.pso[id]

        if pso.time[PSO.get_core_num()] < PSO.period_core: # 실행 목표를 달성하지 못했다면
            self.wait[id] += 1 # 기다리고 있는 slave 갯수를 증가
            pso.time[PSO.get_core_num()] += time # 돌아가는 횟수를 미리 계산 후
            self.comm.send_pso_run(client, id, PSO.get_core_num(), pso.probability_now[pso.fitness]) # slave로 정보를 보넴
            return True

        else:
            if not self.wait[id]:
                self.to_pilot_fuzz(id)
                return self.stage_pilot_fuzz(client, time, id)
        
        return False


    def stage_pilot_fuzz(self, client, time, id):
        pso:PSO = self.pso[id]

        for tmp_swarm in range(PSO.swarm_num): # 모든 swarm을 살펴보며
            if pso.time[tmp_swarm] < PSO.period_pilot: # 만약 실행 목표를 달성하지 못했다면
                self.wait[id] += 1 # 기다리고 있는 slave 갯수를 증가
                pso.time[tmp_swarm] += time # 돌아가는 횟수를 미리 계산 후
                self.comm.send_pso_run(client, id, tmp_swarm, pso.probability_now[tmp_swarm]) # slave로 정보를 보넴
                return True

            else:
                self.done[id] |= 1 << tmp_swarm # 실행 목표를 달성하였다면 done 변수에 해당 swarm이 끝났다는 것을 표시함
                if not self.wait[id] and self.done[id] == (1 << PSO.swarm_num) - 1: # 만약 모든 swarm이 목표를 달성했다면
                    self.to_core_fuzz(id)
                    return self.stage_core_fuzz(client, time, id)
        
        return False


    def to_core_fuzz(self, id):
        self.state[id] = ServerPSO.core # 코어 퍼징 상태로 바꿈
        self.pso[id].core_fuzz_init()
        #self.debug(id)
        print(f'[id {id}] - core fuzz')
    

    def to_pilot_fuzz(self, id):
        self.state[id] = ServerPSO.pilot # 퍼징 상태를 바꿈
        self.done[id] = 0
        self.pso[id].update_global() # pso 글로벌 값들을 바꿈
        #self.debug(id)
        self.pso[id].pilot_fuzz_init()
        self.select_main_id()
        print(f'[id {id}] - pilot fuzz')


    def update_stats(self, info, state): # 실행 후 정보를 slave에서 받은 경우우
        id = info['id']
        swarm_num = info['swarm_num']

        self.wait[id] -= 1 # 기다리고 있는 slave 갯수를 감소
        self.pso[id].update(swarm_num, state) # 해당 정보로 pso 변수들을 업데이트 함
    

    def debug(self, id):
        print(f'id: {id}')
        pso:PSO = self.pso[id]

        for tmp_swarm in range(PSO.swarm_num):
            print(f'swarm{tmp_swarm}:', end=' ')
            prob = [0] + pso.probability_now[tmp_swarm]
            rate = []
            for i in range(1, len(prob)):
                rate.append(((prob[i] - prob[i-1]) / prob[-1]) * 100)
            for r in rate:
                print(('%.2f'%r).rjust(5, ' '), end='% ')
            print()

        for tmp_swarm in range(PSO.get_swarm_num()):
            print(f'swarm{tmp_swarm} time: {pso.time[tmp_swarm]}, total_hit: {pso.total_hit[tmp_swarm]}')
            print(f'swarm{tmp_swarm} finds:'.ljust(15, ' '), end=' ')
            for i in range(PSO.get_handler_num()):
                print('%5d'%pso.finds[tmp_swarm][i], end=' ')
            print()
            print(f'swarm{tmp_swarm} cycles:'.ljust(15, ' '), end=' ')
            for i in range(PSO.get_handler_num()):
                print('%5d'%pso.cycles[tmp_swarm][i], end=' ')
            print()
        print()


class ClientPSO:
    def __init__(self, connection):
        self.conn = connection
        self.cycles = [0]*PSO.get_handler_num()
        self.cycles_old = [0]*PSO.get_handler_num()
        self.finds = [0]*PSO.get_handler_num()
    
    def reset(self):
        self.total_hit = 0
        for i in range(PSO.get_handler_num()):
            self.cycles[i] = 0
            self.cycles_old[i] = 0
            self.finds[i] = 0

    def request_probability(self, time):
        self.conn.send_pso_request(time)
        msg = self.conn.recv()
        
        if msg["type"] == MSG_PSO_RUN:
            self.probability_now = msg["probability"]
            self.id = msg["info"]["id"]
            self.swarm_num = msg["info"]["swarm_num"]
            self.reset()
        else:
            raise ValueError("Unknown message type {}".format(msg))


    def select_and_run_handler(self, data):
        range_sele = self.probability_now[-1]
        sele = PSO.rand() * range_sele
        
        for i in range(PSO.get_handler_num()):
            if sele < self.probability_now[i]:
                handler = havoc_handler[i]
                break
            
        data = handler(data)
        self.cycles[i] += 1
        
        if len(data) >= KAFL_MAX_FILE:
            data = data[:KAFL_MAX_FILE]
        
        return data
    

    def update(self, hits):
        if hits > 0:
            self.total_hit += hits
            for i in range(PSO.get_handler_num()):
                if self.cycles[i] > self.cycles_old[i]:
                    self.finds[i] += hits
                    self.cycles_old[i] = self.cycles[i]


    def done(self):
        self.conn.send_pso_done(self.id, self.swarm_num, self.total_hit, self.finds, self.cycles)
