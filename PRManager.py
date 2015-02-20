__author__ = 'Michael'
from queue import PriorityQueue
from queue import Queue
import heapq


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

    def add_resource(self, resource, units):
        self.resources.append(
            [resource, units])  # resources is a list of lists, where l[0] = resource block, l[1] = units

    def remove_resources(self, resource, units):
        units_left = None
        for l in self.resources:
            if l[0] == resource:
                if l[1] - units < 0:
                    return 'error(release too many units: {}/{}:{})'.format(units, resource.rid, resource.units)
                l[1] -= units
                units_left = l[1]

        if units_left is None:
            # print('error', resource.rid)
            return 'error(not holding resource: {})'.format(resource.rid[1])

        elif units_left == 0:
            self.resources.remove([resource, units_left])

        return True

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

    def remove(self, pcb):
        if not self.search(pcb.pid):
            print('error, {} not in ready list'.format(pcb.pid))
            return False

        tup_to_remove = None
        for pcb_tup in self.ready_list.queue:
            if pcb_tup[2].pid == pcb.pid:
                tup_to_remove = pcb_tup

        self.ready_list.queue.remove(tup_to_remove)
        heapq.heapify(self.ready_list.queue)
        return True

    def peek(self):
        return self.ready_list.queue[0][2]

    def search(self, pid):
        """
        Searches ready list using pid
        :param pid: pid int
        :return: the pcb if found else None
        """
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
            print('({}, {}, {} ch: {}, r: {})->'.format(tup[0], tup[1], tup[2].pid, tup[2].children_list(),
                                                        tup[2].resources), end=' ')
        print()


class RCB:
    def __init__(self, rid: int, units: int, waiting_list=Queue()):
        self.rid = rid
        self.units = units
        self.waiting_list = waiting_list  # list of tuples where t[0] = pcb, t[1] = units requested for pcb
        self.remaining_units = units

    def peek_wl_units(self):
        return self.waiting_list.queue[0][1]

    def pop_wl(self) -> PCB:
        """
        :return: tup where t[0] = pcb on waiting list, t[1] = units requested
        """
        return self.waiting_list.get()

    def add_wl(self, pcb: PCB, units):
        self.waiting_list.put((pcb, units))

    def waiting_list_safe_remove(self, pcb):
        tup_to_remove = None
        for tup in self.waiting_list.queue:
            if tup[0] == pcb:
                tup_to_remove = tup

        if tup_to_remove:
            self.waiting_list.queue.remove(tup_to_remove)


class PRManager:
    def __init__(self):
        pass

    def init(self):
        self.ready_list = RL()
        self.ready_list.insert(PCB('init', 0))
        self.resources = list()
        for i in range(1, 5):
            self.resources.append(RCB('R{}'.format(i), i))
        self.running = self.ready_list.peek()
        self.processes = set()
        return self.scheduler()

    def create(self, pid: str, priority: int):
        """
        Creates a new PCB using resources, then adds it to ready list
            Also creates a bidirectional link to parent
        :param pid: id of the process
        :param priority: priority of process
        :return: currently running process ID
        """
        if pid in self.processes:
            return 'error(duplicate process name: {})'.format(pid)

        new_pcb = PCB(pid, priority, parent=self.running)
        self.running.add_child(new_pcb)
        self.ready_list.insert(new_pcb)
        self.processes.add(pid)
        return self.scheduler()

    def destroy(self, pid):
        if pid not in self.processes:
            return 'error(non-existent process: {})'.format(pid)
        self.processes.remove(pid)

        p = self.get_PCB(pid)
        self.kill_tree(p)
        self.running = None
        return self.scheduler()

    def get_PCB(self, pid):
        pcb = [self.ready_list.search(pid)]
        if not pcb[0]:
            pcb = [pcb for r in self.resources for pcb in r.waiting_list.queue if pcb[0].pid == pid][0]

        if not pcb:
            print('error')
        return pcb[0]

    def kill_tree(self, p):
        children = [child for child in p.children]
        for q in children:
            if q.pid in self.processes:
                self.processes.remove(q.pid)
            self.kill_tree(q)

        # delete pointer from parent
        p.parent.remove_child(p)

        # TODO: free resources
        for r_list in p.resources:
            r = r_list[0]
            units = r_list[1]
            self.release_p(p, r.rid, units)

        # search for all references and destroy
        if self.ready_list.search(p.pid):
            self.ready_list.remove(p)
        else:
            for r in self.resources:
                r.waiting_list_safe_remove(p)


    def request(self, rid, units_req):
        if rid not in ['R1', 'R2', 'R3', 'R4']:
            return 'error(non-existent resource: {})'.format(rid[1])

        r = self.get_RCB(rid)
        if units_req > r.units:
            return 'error(request too many units: {}/{})'.format(units_req, rid)

        if r.remaining_units >= units_req:
            r.remaining_units = r.remaining_units - units_req
            self.running.add_resource(r, units_req)
        else:
            self.running.status['type'] = False
            self.running.status['list'] = r
            self.ready_list.remove(self.running)
            # self.ready_list.pop()

            r.add_wl(self.running, units_req)
        return self.scheduler()

    def release_p(self, pcb, rid, units):
        r = self.get_RCB(rid)

        message = pcb.remove_resources(r, units)

        if message is not True:
            return message

        r.remaining_units += units

        while r.remaining_units > 0 and r.waiting_list.queue:

            units_requested = r.peek_wl_units()
            if units_requested <= r.remaining_units:
                p_tup = r.pop_wl()
                p = p_tup[0]
                p_units_req = p_tup[1]
                r.remaining_units = r.remaining_units - p_units_req
                p.add_resource(r, units)
                p.status['type'] = True
                p.status['list'] = self.ready_list
                self.ready_list.insert(p)
            else:
                break
        return None


    def release(self, rid, units):
        failure = self.release_p(self.running, rid, units)
        if not failure:
            return self.scheduler()
        else:
            return failure

    def get_RCB(self, rid):
        r = [r for r in self.resources if r.rid == rid]
        return r[0] if r else None

    def time_out(self):
        success = self.ready_list.remove(self.running)
        if not success:
            print("running process {} wasn't in readylist".format(self.running))

        self.running.status['type'] = True
        self.ready_list.insert(self.running)
        return self.scheduler()


    def scheduler(self):
        p = self.ready_list.peek()
        if (not self.running or
                    self.running.priority < p.priority or
                not self.running.status['type']):
            # preempt p
            p.status['type'] = True
            self.running = p
            # print(p.pid, end=' ')
            return p.pid
        else:
            self.running = p
            # print(self.running.pid, end=' ')
            return self.running.pid


def main(read_file=None, out_file=None):
    read_file = read_file
    out_file = out_file

    ops = dict()
    m = PRManager()
    ops['cr'] = m.create
    ops['de'] = m.destroy
    ops['req'] = m.request
    ops['rel'] = m.release
    ops['to'] = m.time_out
    ops['init'] = m.init

    g = open(out_file, 'w+')
    a = open(read_file)
    comment = a.readline().startswith('#')

    with open(read_file) as f:
        g.write('{} '.format(ops['init']()))
        for line in f:
            if (line == '\n' or line.startswith('#')) and not comment:
                g.write('\n')
            comment = False
            tokens = line.strip().split(' ')
            op = tokens[0]
            if op in ['to', 'init']:
                g.write(ops[op]() + ' ')
            elif op in ['de']:
                out = ops[op](tokens[1])
                # print(out)
                g.write(out + ' ')
                # g.write(ops[op](tokens[1]) + ' ')
            elif op in ['cr', 'req', 'rel']:
                g.write(ops[op](tokens[1], int(tokens[2])) + ' ')

    g.close()
    # m.ready_list.show()


if __name__ == '__main__':

    # for i in range(1, 4):
    i = 4
    read_file = 'tests/input/input{}.txt'.format(i)
    out_file = 'tests/my_out/out{}.txt'.format(i)
    main(read_file, out_file)

    for i in range(1, 4):
        out_file = 'tests/my_out/out{}.txt'.format(i)
        verify_file = 'tests/output/output{}.txt'.format(i)
        out = enumerate(open(out_file))
        ver = enumerate(open(verify_file))
        out_iter = iter(out)
        ver_iter = iter(ver)
        for line in range(0, len(list(enumerate(open(verify_file))))):
            out_line = next(out_iter)
            ver_line = next(ver_iter)
            if out_line[1].strip() != ver_line[1].strip():
                print(out_file, out_line, ver_line)







