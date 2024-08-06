from gymnasium.envs.registration import register

register(
    id="gym_examples/Reversi-v0",
    entry_point="gym_examples.envs:ReversiEnv"
)

