import gym
import numpy as np

from deep_rl import register_trainer
from deep_rl.a2c import A2CTrainer as BaseTrainer
from deep_rl.a2c.model import Flatten, TimeDistributed
from deep_rl.common.env import ScaledFloatFrame, TransposeImage, RewardCollector
from deep_rl.common.vec_env import SubprocVecEnv, DummyVecEnv
from baselines.common.atari_wrappers import ClipRewardEnv, WarpFrame, NoopResetEnv, MaxAndSkipEnv, EpisodicLifeEnv, FrameStack
from torch import nn
from torch.nn import functional as F

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        def init_weights(m):
            if type(m) == nn.Linear:
                nn.init.xavier_uniform_(m.weight)
                m.bias.data.fill_(0)
            
        self.layer = TimeDistributed(nn.Linear(4, 256))
        self.action = TimeDistributed(nn.Linear(256, 2))
        self.critic = TimeDistributed(nn.Linear(256, 1))  
        self.apply(init_weights)

    def forward(self, inputs, masks, states):
        features = self.layer(inputs)
        features = F.relu(features)
        value = self.critic(features)
        policy_logits = self.action(features)
        return policy_logits, value, states
        

@register_trainer(max_time_steps = 10e6, validation_period = None,  episode_log_interval = 10, save = False)
class Trainer(BaseTrainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_processes = 16
        self.num_steps = 5
        self.gamma = .99
        self.allow_gpu = False

    def create_env(self, env):
        class W(gym.ObservationWrapper):
            def observation(self, o):
                return o.astype(np.float32)

        env_kwargs = env
        def _thunk():
            env = gym.make(**env_kwargs)
            env = RewardCollector(env)
            env = ClipRewardEnv(env)
            env = W(env)
            return env

        self.validation_environment = DummyVecEnv([_thunk])
        return SubprocVecEnv([_thunk for _ in range(self.num_processes)])

    def create_model(self):
        return Model()

def default_args():
    return dict(
        env_kwargs = dict(id='CartPole-v0'),
        model_kwargs = dict()
    )