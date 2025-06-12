# 100-line PocketFlow implementation for Hard Gate Assessment
class Node:
    def __init__(self, max_retries=1, wait=0):
        self.max_retries = max_retries
        self.wait = wait
        self.cur_retry = 0
        self.successors = {}
        self.params = {}
    
    def prep(self, shared):
        return None
    
    def exec(self, prep_res):
        return None
    
    def exec_fallback(self, prep_res, exc):
        raise exc
    
    def post(self, shared, prep_res, exec_res):
        return "default"
    
    def set_params(self, params):
        self.params = params
    
    def run(self, shared):
        import time
        
        self.cur_retry = 0
        prep_res = self.prep(shared)
        
        while self.cur_retry < self.max_retries:
            try:
                exec_res = self.exec(prep_res)
                break
            except Exception as e:
                self.cur_retry += 1
                if self.cur_retry >= self.max_retries:
                    exec_res = self.exec_fallback(prep_res, e)
                    break
                if self.wait > 0:
                    time.sleep(self.wait)
        
        return self.post(shared, prep_res, exec_res)
    
    def __rshift__(self, other):
        self.successors["default"] = other
        return other
    
    def __sub__(self, action):
        return ActionHelper(self, action)

class ActionHelper:
    def __init__(self, node, action):
        self.node = node
        self.action = action
    
    def __rshift__(self, other):
        self.node.successors[self.action] = other
        return other

class Flow(Node):
    def __init__(self, start):
        super().__init__()
        self.start = start
    
    def run(self, shared):
        current = self.start
        
        while current:
            action = current.run(shared)
            if action and action in current.successors:
                current = current.successors[action]
            else:
                break
        
        return self.post(shared, None, None)

class BatchNode(Node):
    def run(self, shared):
        import time
        
        self.cur_retry = 0
        prep_res = self.prep(shared)
        
        if not hasattr(prep_res, '__iter__'):
            raise ValueError("BatchNode prep() must return an iterable")
        
        exec_res_list = []
        for item in prep_res:
            while self.cur_retry < self.max_retries:
                try:
                    exec_res = self.exec(item)
                    exec_res_list.append(exec_res)
                    break
                except Exception as e:
                    self.cur_retry += 1
                    if self.cur_retry >= self.max_retries:
                        exec_res = self.exec_fallback(item, e)
                        exec_res_list.append(exec_res)
                        break
                    if self.wait > 0:
                        time.sleep(self.wait)
            self.cur_retry = 0
        
        return self.post(shared, prep_res, exec_res_list) 