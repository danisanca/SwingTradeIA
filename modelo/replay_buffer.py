"""
replay_buffer.py — Replay Buffer circular para o agente DQN
"""
import numpy as np
from collections import deque
import random
from typing import Dict


class ReplayBuffer:
    """
    Replay Buffer de tamanho fixo com amostragem uniforme aleatória.

    Armazena tuplas (state, action, reward, next_state, done) e
    retorna mini-batches para atualização da rede.

    Attributes:
        capacity: Número máximo de experiências armazenadas
        batch_size: Tamanho do mini-batch retornado pelo sample()
    """

    def __init__(self, capacity: int = 50_000, batch_size: int = 64):
        self.buffer: deque = deque(maxlen=capacity)
        self.batch_size = batch_size

    def push(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ) -> None:
        """Adiciona uma experiência ao buffer"""
        self.buffer.append((
            np.array(state, dtype=np.float32),
            int(action),
            float(reward),
            np.array(next_state, dtype=np.float32),
            bool(done),
        ))

    def sample(self) -> Dict[str, np.ndarray]:
        """
        Amostra um mini-batch aleatório do buffer.

        Returns:
            Dict com arrays numpy: states, actions, rewards, next_states, dones
        """
        assert self.ready(), "Buffer não tem experiências suficientes para amostrar"

        batch = random.sample(self.buffer, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        return {
            "states":      np.array(states,      dtype=np.float32),
            "actions":     np.array(actions,      dtype=np.int64),
            "rewards":     np.array(rewards,      dtype=np.float32),
            "next_states": np.array(next_states,  dtype=np.float32),
            "dones":       np.array(dones,         dtype=bool),
        }

    def ready(self) -> bool:
        """Retorna True se o buffer tem experiências suficientes para um batch"""
        return len(self.buffer) >= self.batch_size

    def __len__(self) -> int:
        return len(self.buffer)

    def __repr__(self) -> str:
        return f"ReplayBuffer(size={len(self.buffer)}/{self.buffer.maxlen}, batch={self.batch_size})"
