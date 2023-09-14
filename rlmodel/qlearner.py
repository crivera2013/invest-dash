import random as rand

import numpy as np


class QLearner(object):
    def __init__(
        self,
        num_states=100,
        num_actions=4,
        alpha=0.9,
        gamma=0.9,
        rar=0.995,
        radr=0.98,
        dyna=0,
        verbose=False,
    ):
        # so its a 10x10 grid = 100 possible states
        # 4 actions representing north, south, east, west

        self.num_states = num_states
        self.num_actions = num_actions
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna
        self.verbose = verbose
        self.s = 0
        self.a = 0

        self.Q = np.zeros((self.num_states, self.num_actions))

        self.Exp = []

        # self.T = 	np.zeros((self.num_states,self.num_actions, self.num_states))
        # self.Tc = np.zeros((self.num_states,self.num_actions, self.num_states))
        # self.Tc[self.Tc == 0] = 0.00001

        # self.R =  np.zeros((self.num_states,self.num_actions))

    def querysetstate(self, state):
        """
        @summary: Update the state without updating the Q-table
        @param s: The new state.  This is an integer
        @returns: The selected action
        """
        self.s = state

        rand_value = np.random.rand()
        if rand_value <= self.rar:
            action = rand.randint(0, self.num_actions - 1)
            if self.verbose:
                print("s =", self.s, "a =", action)
            self.a = action
            return action
        else:
            action = self.Q[self.s].argmax()
            self.a = action
            return action

    def query(self, s_prime, r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """

        # update the Q Table
        immediate_r = (1.0 - self.alpha) * self.Q[self.s, self.a]
        discount_r = self.alpha * (
            r + self.gamma * self.Q[s_prime, self.Q[s_prime].argmax()]
        )
        reward = immediate_r + discount_r
        self.Q[self.s, self.a] = reward

        self.Exp.append((self.s, self.a, r, s_prime))

        for i in range(self.dyna):
            dyna_s, dyna_a, dyna_r, dyna_sp = self.Exp[
                rand.randint(0, len(self.Exp) - 1)
            ]
            dyna_immediate_r = (1 - self.alpha) * self.Q[dyna_s, dyna_a]
            dyna_discount_r = self.alpha * (
                dyna_r + self.gamma * self.Q[dyna_sp, self.Q[dyna_sp].argmax()]
            )
            dyna_reward = dyna_immediate_r + dyna_discount_r
            self.Q[dyna_s, dyna_a] = dyna_reward

        rand_value = np.random.rand()

        if rand_value <= self.rar:
            self.rar = self.rar * self.radr  # self.rar - 0.0001
            action = rand.randint(0, self.num_actions - 1)
            self.s = s_prime
            self.a = action
            return action

        else:
            action = self.Q[s_prime].argmax()
            self.s = s_prime
            self.a = action
            return action
