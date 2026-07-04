"""
dqn_network.py — Arquitetura das redes Policy e Target do agente DQN
"""
import torch
import torch.nn as nn
import numpy as np


class DQNNetwork(nn.Module):
    """
    Rede neural Deep Q-Network.

    Arquitetura: 3 camadas fully-connected com ReLU e Dropout.
    Input:  vetor de estado (features de N dias × features_per_day)
    Output: Q-values para cada ação possível (SELL=0, HOLD=1, BUY=2)
    """

    def __init__(self, state_size: int = 30, action_size: int = 3, hidden_sizes=(256, 128, 64)):
        super().__init__()

        layers = []
        in_size = state_size
        for h_size in hidden_sizes:
            layers.extend([
                nn.Linear(in_size, h_size),
                nn.LayerNorm(h_size),
                nn.ReLU(inplace=True),
                nn.Dropout(p=0.2),
            ])
            in_size = h_size
        layers.append(nn.Linear(in_size, action_size))

        self.net = nn.Sequential(*layers)
        self._init_weights()

    def _init_weights(self):
        """Inicialização He para camadas ReLU"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, nonlinearity='relu')
                nn.init.constant_(m.bias, 0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class DQNAgent:
    """
    Agente DQN completo com Policy Network + Target Network.
    Implementa epsilon-greedy exploration e atualização via Bellman.
    """

    ACTION_NAMES = {0: "SELL", 1: "HOLD", 2: "BUY"}

    def __init__(
        self,
        state_size: int = 30,
        action_size: int = 3,
        lr: float = 1e-4,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995,
        target_update_freq: int = 100,
        device: str = "cpu",
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.target_update_freq = target_update_freq
        self.device = torch.device(device)
        self.steps = 0

        # Policy Network (principal) e Target Network (estável)
        self.policy_net = DQNNetwork(state_size, action_size).to(self.device)
        self.target_net = DQNNetwork(state_size, action_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = torch.optim.Adam(self.policy_net.parameters(), lr=lr)
        self.criterion = nn.SmoothL1Loss()  # Huber Loss — mais estável que MSE

    def act(self, state: np.ndarray, training: bool = True) -> int:
        """
        Seleciona ação via epsilon-greedy durante treinamento.
        Em inferência (training=False), usa argmax dos Q-values.
        """
        if training and np.random.rand() < self.epsilon:
            return np.random.randint(self.action_size)

        self.policy_net.eval()
        with torch.no_grad():
            state_t = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_t)
        self.policy_net.train()
        return int(q_values.argmax().item())

    def learn(self, batch: dict) -> float:
        """
        Atualiza a Policy Network via Bellman equation.
        Retorna o loss do batch.
        """
        states = torch.FloatTensor(batch["states"]).to(self.device)
        actions = torch.LongTensor(batch["actions"]).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(batch["rewards"]).to(self.device)
        next_states = torch.FloatTensor(batch["next_states"]).to(self.device)
        dones = torch.BoolTensor(batch["dones"]).to(self.device)

        # Q-values correntes para as ações tomadas
        current_q = self.policy_net(states).gather(1, actions).squeeze(1)

        # Q-values alvo via Target Network (Double DQN)
        with torch.no_grad():
            next_actions = self.policy_net(next_states).argmax(1, keepdim=True)
            next_q = self.target_net(next_states).gather(1, next_actions).squeeze(1)
            next_q[dones] = 0.0
            target_q = rewards + self.gamma * next_q

        loss = self.criterion(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping para estabilidade
        nn.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=1.0)
        self.optimizer.step()

        # Decaimento do epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # Sincronizar Target Network periodicamente
        self.steps += 1
        if self.steps % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        return float(loss.item())

    def save(self, path: str):
        torch.save({
            "policy_net": self.policy_net.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "epsilon": self.epsilon,
            "steps": self.steps,
        }, path)
        print(f"✅ Modelo salvo em {path}")

    def load(self, path: str):
        ckpt = torch.load(path, map_location=self.device)
        self.policy_net.load_state_dict(ckpt["policy_net"])
        self.target_net.load_state_dict(ckpt["policy_net"])
        self.optimizer.load_state_dict(ckpt["optimizer"])
        self.epsilon = ckpt.get("epsilon", self.epsilon_min)
        self.steps = ckpt.get("steps", 0)
        print(f"✅ Modelo carregado de {path}")
