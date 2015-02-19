__author__ = 'Michael'
from queue import PriorityQueue
from queue import Queue


class PCB:
    def __init__(self, pid: str, priority: int, parent=None):
        self.pid = pid
        self.priority = priority
        self.resources = list()
        self.parent = parent
        self.status = {'type': True, 'list': list()}  # type True = not blocked
        self.children = list()

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)

    def add_resource(self, resource):
        self.resources.append(resource)

    def delete(self):
        del self

    def children_list(self):
        return [child.pid for child in self.children]

class RL:
    """
    Ready list implemented with priority queue using a counter to
        achieve a FIFO priority queue. Therefore, priority comes first, then
        the counter comes second, acting as a time counter.
        """

    def __init__(self):
        self.ready_list = PriorityQueue()
        self.count = 0

    def insert(self, pcb: PCB):
        self.ready_list.put((-pcb.priority, self.count, pcb))
        self.count += 1

    def pop(self) -> PCB:
        if self.ready_list.empty():
            return None
        return self.ready_list.get()[2]

    def peek(self):
        return self.ready_list.queue[0][2]

    def search(self, pid):
        pcb = [pcb_tup[2] for pcb_tup in self.ready_list.queue if pcb_tup[2].pid == pid]
        return pcb[0] if pcb else None

    def delete(self, pid):
         pcb = None
         for pcb_tup in self.ready_list.queue:
             if pcb_tup[2].pid == pid:
                 pcb = pcb_tup

         if not pcb:
             print('error')

         self.ready_list.queue.remove(pcb)

    def show(self):
        print('RL: ', end='')
        for tup in self.ready_list.queue:
            print('({}, {}, {} -> {})->'.format(tup[0],tup[1],tup[2].pid, tup[2].children_list()), end=' ')
        print()


class RCB:
    def __init__(self, rid: int, units: int, waiting_list=Queue()):
        self.rid = rid
        self.units = units
        self.waiting_list = waiting_list
        self.remaining_units = units

    def pop_wl(self) -> PCB:
        return self.waiting_list.get()

    def add_wl(self, pcb: PCB):
        self.waiting_list.put(pcb)


class PRManager:
    def __init__(self):
        self.init()
        self.scheduler()

    def init(self):
        self.ready_list = RL()
        self.ready_list.insert(PCB('init', 0))
        self.resources = list()
        for i in range(1, 5):
            self.resources.append(RCB('R{}'.format(i), i))
        self.running = self.ready_list.peek()

    def create(self, pid: str, priority: int):
        new_pcb = PCB(pid, priority, parent=self.running)
        self.running.add_child(new_pcb)
        self.ready_list.insert(new_pcb)
        return self.scheduler()

    def destroy(self, pid):
        p = self.get_PCB(pid)
        self.kill_tree(p)
        self.running = None
        return self.scheduler()

    def get_PCB(self, pid):
        pcb = self.ready_list.search(pid)
        if not pcb:
            pcb = [pcb for r in self.resources for pcb in r.waiting_list if pcb.pid == pid]

        if not pcb:
            print('error')

        return pcb

    def kill_tree(self, p):
        children = [child for child in p.children]
        for q in children:
            self.kill_tree(q)

        # delete pointer from parent
        p.parent.remove_child(p)


        # TODO: free resources
        # search for all references and destroy
        self.ready_list.delete(p.pid)
        for r in self.resources:
            if p in r.waiting_list.queue:
                r.waiting_list.queue.remove(p)

        # p.delete()

    def request(self, rid, units):
        r = PRManager.get_RCB()
        if r.remaining_units >= units:
            r.remaining_units = r.remaining_units - units
            self.running.add_resource(r)
        else:
            self.running.status['type'] = False
            self.running.status['list'].append(r)
            self.ready_list.pop()
            r.add_wl(self.running)
        self.scheduler()

    def get_RCB(self, rid):
        r = [r for r in self.resources if r.rid == rid]
        return r[0] if r else None

    def scheduler(self):
        p = self.ready_list.peek()
        if (not self.running or
                self.running.priority < p.priority or
                not self.running.status['type']):
            # preempt p
            p.status['type'] = True
            self.running = p
            print(p.pid)
            return p.pid
        else:
            print(self.running.pid)
            return p.pid


if __name__ == '__main__':
    pass




