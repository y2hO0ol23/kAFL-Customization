from fuzzer.technique.havoc_handler import *
from fuzzer.technique.helper import rand
import time

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
        return rand.int(1000) * 0.001 * v

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

        self.probability_now[tmp_swarm][0] = self.x_now[tmp_swarm][0]

        for i in range(1, PSO.get_handler_num()):
            self.probability_now[tmp_swarm][i] = self.probability_now[tmp_swarm][i - 1] + self.x_now[tmp_swarm][i]


    def __init__(self):
        self.x_now = PSO.list_init()
        self.L_best = PSO.list_init(0.5)
        self.eff_best = PSO.list_init()
        self.G_best = [0.5] * PSO.get_handler_num()
        self.v_now = PSO.list_init(0.1)
        self.probability_now = PSO.list_init()
        self.swarm_fitness = [0] * PSO.swarm_num
        self.fitness = None

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
            for tmp_swarm in range(PSO.get_swarm_num()):
                finds_total[i] += self.finds_total[tmp_swarm][i]
        
        total = sum(finds_total)

        for i in range(PSO.get_handler_num()):
            if finds_total[i]:
                self.G_best[i] = finds_total[i] / total

        for tmp_swarm in range(PSO.swarm_num):
            self.update_probability(tmp_swarm)
            
    def core_fuzz_end(self):
        for i in range(PSO.get_handler_num()):
            self.finds_total[PSO.get_core_num()][i] += self.finds[PSO.get_core_num()][i]

        self.update_global() # pso 글로벌 값들을 바꿈
        self.pilot_fuzz_init()


class ServerPSO:
    pilot = 0
    core = 1

    def __init__(self, statistics):
        self.statistics = statistics
        self.pso = PSO()
        self.wait = 0
        self.state = ServerPSO.pilot
        self.swarm_now = 0
        self.start_time = time.time()

        self.statistics.pso_update({"state": f"pilot 0/{PSO.swarm_num}"})


    def select(self, time):
        if self.state == ServerPSO.core:
            res = self.stage_core_fuzz(time)
        else:
            res = self.stage_pilot_fuzz(time)
        
        if res == None: 
            res = self.stage_assist_fuzz()

        return res
        
    def stage_assist_fuzz(self):
        prob = [i for i in range(PSO.get_handler_num())]
        if self.pso.fitness != None:
            prob = self.pso.probability_now[self.pso.fitness]
        
        return {"info": {"swarm_now": "assist"}, "probability": prob}


    def stage_core_fuzz(self, time):
        if self.pso.time[PSO.get_core_num()] < PSO.period_core: # 실행 목표를 달성하지 못했다면
            self.wait += 1 # 기다리고 있는 slave 갯수를 증가
            self.pso.time[PSO.get_core_num()] += time # 돌아가는 횟수를 미리 계산 후
            self.statistics.pso_update({"progress": f"{self.pso.time[PSO.get_core_num()]}/{PSO.period_core}"})
            return {"info": {"swarm_now": PSO.get_core_num()}, "probability": self.pso.probability_now[self.pso.fitness]}

        else:
            if not self.wait:
                self.to_pilot_fuzz()
                return self.stage_pilot_fuzz()
        
        return None


    def stage_pilot_fuzz(self, time):
        if self.pso.time[self.swarm_now] >= PSO.period_pilot:
            self.swarm_now += 1

            if self.swarm_now != PSO.get_core_num():
                self.statistics.pso_update({"state": f"pilot {self.swarm_now}/{PSO.swarm_num}"})
        
        if self.swarm_now == PSO.get_core_num():
            if self.wait:
                return None
            else:
                self.to_core_fuzz()
                return self.stage_core_fuzz(time)
        else:
            self.wait += 1
            self.pso.time[self.swarm_now] += time
            self.statistics.pso_update({"progress": f"{self.pso.time[self.swarm_now]}/{PSO.period_pilot}"})
            return {"info": {"swarm_now": self.swarm_now}, "probability": self.pso.probability_now[self.swarm_now]}


    def to_core_fuzz(self):
        self.state = ServerPSO.core # 코어 퍼징 상태로 바꿈
        self.pso.core_fuzz_init()
        self.statistics.pso_update({"state": f"core {PSO.swarm_num}/{PSO.swarm_num}"})
    

    def to_pilot_fuzz(self):
        self.state = ServerPSO.pilot # 퍼징 상태를 바꿈
        self.swarm_now = 0
        self.pso.core_fuzz_end()
        self.statistics.pso_update({"state": f"pilot 0/{PSO.swarm_num}", "cycles": 1})


    def update_stats(self, data): # 실행 후 정보를 slave에서 받은 경우우
        swarm_now = data['info']['swarm_now']

        if swarm_now == 'assist':
            for i in range(PSO.get_handler_num()):
                self.pso.finds_total[PSO.get_core_num()][i] += data['state']['finds'][i]
        else:
            self.wait -= 1 # 기다리고 있는 slave 갯수를 감소
            self.pso.update(swarm_now, data['state']) # 해당 정보로 pso 변수들을 업데이트 함


class ClientPSO:
    def __init__(self):
        self.cycles = {}
        self.cycles_old = {}
        self.finds = {}

    
    def init(self, met):
        self.total_hit = 0
        for i in range(PSO.get_handler_num()):
            self.cycles[i] = 0
            self.cycles_old[i] = 0
            self.finds[i] = 0
            
        self.probability_now = met["probability"]
        self.swarm_now = met["info"]["swarm_now"]


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
        self.total_hit += hits
        for i in range(PSO.get_handler_num()):
            if self.cycles[i] > self.cycles_old[i]:
                self.finds[i] += hits
                self.cycles_old[i] = self.cycles[i]


    def result(self):
        return {"info": {"swarm_now": self.swarm_now}, "state": {"total_hit": self.total_hit, "finds": self.finds, "cycles": self.cycles}}

