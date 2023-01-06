from fuzzer.technique.havoc_handler import *
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
    def get_period_time(tmp_swarm):
        if PSO.get_core_num() == tmp_swarm:
            return PSO.period_core
        return PSO.period_pilot
    
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


    def update_swarm(self, tmp_swarm):
        x = self.x_now[tmp_swarm][:]
        w_now = (PSO.w_init - PSO.w_end)*(PSO.g_max - self.g_now) / (PSO.g_max)+PSO.w_end

        for i in range(PSO.get_handler_num()):
            self.v_now[tmp_swarm][i] =  w_now * self.v_now[tmp_swarm][i] + \
                                        PSO.rand() * (self.L_best[tmp_swarm][i] - x[i]) + \
                                        PSO.rand() * (self.G_best[i] - x[i])

            x[i] += self.v_now[tmp_swarm][i]
            x[i] = PSO.sat(x[i], PSO.v_min, PSO.v_max)

        total = sum(x)
        self.x_now[tmp_swarm] = [v / total for v in x]

        self.probability_now[tmp_swarm] = [0]

        for i in range(PSO.get_handler_num()):
            value = self.probability_now[tmp_swarm][i] + self.x_now[tmp_swarm][i]
            self.probability_now[tmp_swarm].append(value)
    
        del self.probability_now[tmp_swarm][0]

        for i in range(PSO.get_handler_num()):
            self.finds_total[tmp_swarm][i] += self.finds[tmp_swarm][i]
            self.finds[tmp_swarm][i] = 0
            self.cycles[tmp_swarm][i] = 0
            self.cycles_old[tmp_swarm][i] = 0


    def __init__(self):
        self.x_now = PSO.list_init()
        self.L_best = PSO.list_init(0.5)
        self.eff_best = PSO.list_init()
        self.G_best = [0.5] * PSO.get_handler_num()
        self.v_now = PSO.list_init(0.1)
        self.probability_now = [[]] * PSO.get_swarm_num()
        self.swarm_fitness = [0] * PSO.swarm_num

        self.finds = PSO.list_init()
        self.finds_total = PSO.list_init()
        self.cycles = PSO.list_init()
        self.cycles_old = PSO.list_init()
        
        self.total_hit = 0
        self.swarm_now = 0
        self.g_now = 0
        self.time = 0

        for tmp_swarm in range(PSO.swarm_num):
            rand = [(PSO.rand(0.7) + 0.1) for _ in range(PSO.get_handler_num())]
            total = sum(rand)
            self.x_now[tmp_swarm] = [x / total for x in rand]

            self.update_swarm(tmp_swarm)
        

    def select_and_run_handler(self, data):
        range_sele = self.probability_now[self.swarm_now][-1]
        sele = PSO.rand() * range_sele
        
        for i in range(PSO.get_handler_num()):
            if sele < self.probability_now[self.swarm_now][i]:
                handler = havoc_handler[i]
                break
            
        data = handler(data)
        self.cycles[self.swarm_now][i] += 1
        
        if len(data) >= KAFL_MAX_FILE:
            data = data[:KAFL_MAX_FILE]
        
        return data


    def update_cycles(self, hit_cnt):
        self.time += 1

        if hit_cnt > 0:
            self.total_hit += hit_cnt
            for i in range(PSO.get_handler_num()):
                if self.cycles[self.swarm_now][i] > self.cycles_old[self.swarm_now][i]:
                    self.finds[self.swarm_now][i] += hit_cnt
                    self.cycles_old[self.swarm_now][i] = self.cycles[self.swarm_now][i]


    def end(self):
        if self.time > PSO.get_period_time(self.swarm_now):
            if self.swarm_now == PSO.get_core_num():
                self.update_global()
                self.swarm_now = 0
            else:
                self.swarm_fitness[self.swarm_now] = self.total_hit / self.time
                self.total_hit = 0

                for i in range(PSO.get_handler_num()):
                    eff = 0.0
                    if self.cycles[self.swarm_now][i]:
                        eff = self.finds[self.swarm_now][i] / self.cycles[self.swarm_now][i]

                    if self.eff_best[self.swarm_now][i] < eff:
                        self.eff_best[self.swarm_now][i] = eff
                        self.L_best[self.swarm_now][i] = self.x_now[self.swarm_now][i]
                
                self.swarm_now += 1
                
                if self.swarm_now == PSO.get_core_num():
                    best_swarm = 0
                    for i in range(1, PSO.swarm_num):
                        if self.swarm_fitness[best_swarm] < self.swarm_fitness[i]:
                            best_swarm = i
                            
                    self.probability_now[self.swarm_now] = self.probability_now[best_swarm][:]

            self.time = 0
                            

    def update_global(self):
        self.g_now += 1
        if self.g_now > PSO.g_max:
            self.g_now = 0
        
        finds_total = [0 for _ in range(PSO.get_handler_num())]
        for i in range(PSO.get_handler_num()):
            for tmp_swarm in range(PSO.swarm_num):
                finds_total[i] += self.finds[tmp_swarm][i] + self.finds_total[tmp_swarm][i]
        
        total = sum(finds_total)

        for i in range(PSO.get_handler_num()):
            if finds_total[i]:
                self.G_best[i] = finds_total[i] / total

        for tmp_swarm in range(PSO.swarm_num):
            self.update_swarm(tmp_swarm)
    
