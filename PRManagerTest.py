__author__ = 'Michael'

import unittest
import PRManager
from PRManager import *
from queue import PriorityQueue


class PRManagerTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_RCB_PQ_order(self):
        print('\n\n **** Testing test_RCB_PQ_order ****')
        rl = RL()
        PCB1 = PCB('A', 1)
        PCB2 = PCB('B', 1)
        PCB3 = PCB('C', 2)

        verify_l = ['C', 'A', 'B']


        rl.insert(PCB1)
        rl.insert(PCB2)
        rl.insert(PCB3)
        pcb = 1
        pos = 0
        while pcb:
            pcb = rl.pop()
            if pcb:
                self.assertEquals(verify_l[pos], pcb.pid)
                print(pcb.pid, end=' ')
            pos += 1

    def test_tree_kill(self):
        print('\n\n **** Testing test_tree_kill ****')
        m = PRManager()
        m.init()
        self.assertEquals('x', m.create('x', 1))
        self.assertEquals('x', m.create('y', 1))
        self.assertEquals('z', m.create('z', 2))
        # m.ready_list.show()
        self.assertEquals('init', m.destroy('x'))
        # m.ready_list.show()

        self.assertEquals('x', m.create('x', 1))
        self.assertEquals('x', m.create('y', 1))
        self.assertEquals('z', m.create('z', 2))

        self.assertEquals('z', m.destroy('y'))
        self.assertEquals('x', m.destroy('z'))
        # m.ready_list.show()

        self.assertEquals('init', m.destroy('x'))

    def test_request(self):
        print('\n\n **** Testing test_request ****')
        m = PRManager()
        m.init()
        self.assertEquals('x', m.create('x', 1))
        self.assertEquals('x', m.request('R1', 1))
        self.assertEquals('z', m.create('z', 2))
        self.assertEquals('x', m.request('R1', 1))
        self.assertEquals('y', m.create('y', 2))
        self.assertEquals('y', m.request('R2', 2))
        self.assertEquals('x', m.request('R1', 1))
        self.assertEquals('init', m.request('R2', 1))



    def test_release(self):
        print('\n\n **** Testing test_release ****')
        m = PRManager()
        m.init()
        self.assertEquals('x', m.create('x', 1))
        self.assertEquals('x', m.request('R1', 1))
        self.assertEquals('x', m.release('R1', 1))
        self.assertEquals('x', m.request('R1', 1))
        self.assertEquals('z', m.create('z', 2))
        m.ready_list.show()

        self.assertEquals('x', m.request('R1', 1))
        self.assertEquals('z', m.release('R1', 1))

    def test_time_out(self):
        print('\n\n **** Testing test_time_out ****')
        m = PRManager()
        m.init()
        self.assertEquals('x', m.create('x', 2))
        self.assertEquals('x', m.create('y', 1))
        self.assertEquals('x', m.time_out())
        self.assertEquals('x', m.create('z', 2))
        self.assertEquals('z', m.time_out())





