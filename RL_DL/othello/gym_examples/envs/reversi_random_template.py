import gymnasium as gym
from gymnasium import spaces
import numpy as np


class ReversiEnv(gym.Env):
    metadata = {"render_modes": ["text"], "render_fps": 4}

    def __init__(self, render_mode=None, size=8):
        self.size = size  # The size of the square grid

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        # Observation: for each cell in size x size matrix, three states involving
        # { empty (0), agent player 1 (1), gym layer 2 (2) }
        self.observation_space = spaces.Box(low=0, high=255, shape=(size, size, 1), dtype=np.uint8)

        # We have size x size actions, (row, column) index to shoot
        self.action_space = spaces.MultiDiscrete([size, size])

    # Defines all possible movements on the board.
    def possible_moves(self, player, state):
        ret = list()
        opponent = 3 - player

        for i in range(8):
            for j in range(8):
                # if occupied, skip
                if state[i, j] > 0:
                    continue

                # if there is any adjacent cell occupied by oppenent
                # (u, v) is the relative position of eight adjacent cells
                # and also the direction to examine if any opponent piece
                # flipped over
                # (u, v) is
                # (-1, -1) ( -1,  0) (-1,  1)
                # ( 0, -1) (  0,  0) ( 0,  1)
                # ( 1, -1) (  1,  0) ( 1,  1)
                # e.g.,
                #          (i-1, j+1) -> opponent
                #    (i, j) -> player
                # -> examine diagonal direction of up and right
                #    (i-1,j+1), (i-2,j+2), (i-3,j+3), ...
                for u in [-1, 0, 1]:
                    for v in [-1, 0, 1]:
                        if (u != 0 or v != 0) and \
                            (i+u>=0 and i+u<8) and \
                                (j+v>=0 and j+v<8) and \
                                    state[i+u,j+v] == opponent:

                            # examine if there is a player's piece
                            # and thus the opponent's pieces between
                            # (i,j) and (i+d*u,j+d*v) can be
                            # flipped over
                            for d in range(1,8):
                                if (i+d*u<0 or i+d*u>=8) or \
                                    (j+d*v<0 or j+d*v>=8):
                                    break

                                if state[i+d*u,j+d*v] == player:
                                    ret.append((i, j))
                                elif state[i+d*u,j+d*v] == opponent:
                                    continue
                                else:
                                    break
        return list(dict.fromkeys(ret))

    def scoring(self, _state, _player):
        _enemy = 3 - _player
        ptr1 = np.sum([
            1 if _state[i, j] == _player else 0
            for i in range(8) for j in range(8) ])

        ptr2 = np.sum([
            1 if _state[i, j] == _enemy else 0
            for i in range(8) for j in range(8) ])

        return ptr1 - ptr2

    # flip pieces between the new piece placed and the piece with the same color
    # vertically, horizontally and diagonally
    def flip_piece(self, _state, _pos, _player):
        # assume that the cell of pos is empty
        assert _state[_pos] == 0
        _state[_pos] = _player

        n_flipped = 0

        # find target vertical toward top
        for i in range (-1, -8, -1):
            # out of board
            if _pos[0] + i < 0:
                break

            # if empty, stop proving
            if _state[_pos[0] + i, _pos[1]] == 0:
                break

            # found
            if _state[_pos[0] + i, _pos[1]] == _player:
                for j in range (-1, i, -1):
                    _state[_pos[0] + j, _pos[1]] = _player
                    n_flipped += 1
                break

        # find target vertical toward bottom
        for i in range (1, 8):
            # out of board
            if _pos[0] + i >= 8:
                break

            # if empty, stop proving
            if _state[_pos[0] + i, _pos[1]] == 0:
                break

            # found
            if _state[_pos[0] + i, _pos[1]] == _player:
                for j in range (1, i):
                    _state[_pos[0] + j, _pos[1]] = _player
                    n_flipped += 1
                break

        # find target horizon toward left
        for i in range (-1, -8, -1):
            # out of board
            if _pos[1] + i < 0:
                break

            # if empty, stop proving
            if _state[_pos[0], _pos[1] + i] == 0:
                break

            # found
            if _state[_pos[0], _pos[1] + i] == _player:
                for j in range (-1, i, -1):
                    _state[_pos[0], _pos[1] + j] = _player
                    n_flipped += 1
                break

        # find target horizon toward right
        for i in range (1, 8):
            # out of board
            if _pos[1] + i >= 8:
                break

            # if empty, stop proving
            if _state[_pos[0], _pos[1] + i] == 0:
                break

            # found
            if _state[_pos[0], _pos[1] + i] == _player:
                for j in range (1, i):
                    _state[_pos[0], _pos[1] + j] = _player
                    n_flipped += 1
                break

        # find target diagonal toward top & left
        for i in range (-1, -8, -1):
            # out of board
            if _pos[0] + i < 0 or _pos[1] + i < 0:
                break

            # if empty, stop proving
            if _state[_pos[0] + i, _pos[1] + i] == 0:
                break

            # found
            if _state[_pos[0] + i, _pos[1] + i] == _player:
                for j in range (-1, i, -1):
                    _state[_pos[0] + j, _pos[1] + j] = _player
                    n_flipped += 1
                break

        # find target diagonal toward bottom & right
        for i in range (1, 8):
            # out of board
            if _pos[0] + i >= 8 or _pos[1] + i >= 8:
                break

            # if empty, stop proving
            if _state[_pos[0] + i, _pos[1] + i] == 0:
                break

            # found
            if _state[_pos[0] + i, _pos[1] + i] == _player:
                for j in range (1, i):
                    _state[_pos[0] + j, _pos[1] + j] = _player
                    n_flipped += 1
                break

        # find target diagonal toward top & right
        for i in range (-1, -8, -1):
            # out of board
            if _pos[0] + i < 0 or _pos[1] - i >= 8:
                break

            # if empty, stop proving
            if _state[_pos[0] + i, _pos[1] - i] == 0:
                break

            # found
            if _state[_pos[0] + i, _pos[1] - i] == _player:
                for j in range (-1, i, -1):
                    _state[_pos[0] + j, _pos[1] - j] = _player
                    n_flipped += 1
                break

        # find target diagonal toward bottom & right
        for i in range (1, 8):
            # out of board
            if _pos[0] + i >= 8 or _pos[1] - i < 0:
                break

            # if empty, stop proving
            if _state[_pos[0] + i, _pos[1] - i] == 0:
                break

            # found
            if _state[_pos[0] + i, _pos[1] - i] == _player:
                for j in range (1, i):
                    _state[_pos[0] + j, _pos[1] - j] = _player
                    n_flipped += 1
                break

        return n_flipped

    def _get_obs(self):
        return self.state

    def _get_info(self):
        action_mask = np.zeros(shape=(self.size,self.size),dtype=np.int32)
        for idx in self.possible_moves(self.AGENT_PLAYER, self.state):
            action_mask[idx] = 1
        return {'action_mask': action_mask}

    def reset(self, seed=None, options={'gym_player_id': 2}):
        # Define the board to use for the game.
        self.state = np.array([
            [  0,  0,  0,  0,  0,  0,  0,  0 ],
            [  0,  0,  0,  0,  0,  0,  0,  0 ],
            [  0,  0,  0,  0,  0,  0,  0,  0 ],
            [  0,  0,  0,  1,  2,  0,  0,  0 ],
            [  0,  0,  0,  2,  1,  0,  0,  0 ],
            [  0,  0,  0,  0,  0,  0,  0,  0 ],
            [  0,  0,  0,  0,  0,  0,  0,  0 ],
            [  0,  0,  0,  0,  0,  0,  0,  0 ]
        ], dtype=np.int16)

        # if env takes the first move
        if options['gym_player_id'] == 1:
            self.AGENT_PLAYER = 2
            self.GYM_PLAYER = 1
            self.step(self.choose_action())
        else:                           
            self.AGENT_PLAYER = 1
            self.GYM_PLAYER = 2

        return self._get_obs(), self._get_info()

    # select & return a random action
    def choose_action(self):
        moves = self.possible_moves(self.GYM_PLAYER, self.state)
        if not moves:
            return False
        else:
            return moves[np.random.randint(low=0, high=len(moves))]

    def is_over(self):
        # if no more empty cell
        if self.state.min() > 0:
            return True

        # if no more possible moves for both players
        if len(self.possible_moves(self.GYM_PLAYER, self.state)) == 0 and \
                len(self.possible_moves(self.AGENT_PLAYER, self.state)) == 0:
            return True
        return False

    def step(self, action):
        assert action[0] >= 0 and action[0] < self.size
        assert action[1] >= 0 and action[1] < self.size
        assert action in self.possible_moves(self.AGENT_PLAYER, self.state)
        # -------------- fill here --------------------
        # flip_piece가 뒤집힌 개수를 리턴해줌
        flipped = self.flip_piece(self.state, action, self.AGENT_PLAYER)
        # 뒤집힌 개수를 보상으로 준다~
        reward = flipped
        terminated = self.is_over()
        # 게임이 끝낫는지 확인한다~ 100으로 이길때 줘
        if terminated:
            final_score = self.scoring(self.state, self.AGENT_PLAYER)
            if final_score > 0:
                reward += 100  # Winning bonus
            elif final_score < 0:
                reward -= 100  # Losing penalty
            else:
                reward += 50  # Tie bonus

        # Make the gym player's move if the game is not over
        if not terminated:
            gym_action = self.choose_action()
            if gym_action:
                self.flip_piece(self.state, gym_action, self.GYM_PLAYER)
                terminated = self.is_over()
            else:
                terminated = True
        observation = self._get_obs()
        info = self._get_info()

        # observation, reward, if terminated, if truncated, info
        # truncated: true if episode truncates due to a time limit
        return observation, reward, terminated, False, info

    def render(self):
        if self.render_mode == "text":
            return self._render_board()

    def _render_board(self):
        print("Current state of the board:")
        print("    0 1 2 3 4 5 6 7")
        print("-------------------")
        for j in range(8):
            print('{} | {}'.format(j, ' '.join([".12"[self.state[j, i]] for i in range(8)])))

        if self.is_over():
            score = self.scoring(self.state, self.AGENT_PLAYER)
            if score > 0:
                print("Game over! - Winner {}".format(self.AGENT_PLAYER))
            elif score  < 0:
                print("Game over! - Winner {}".format(3 - self.AGENT_PLAYER))
            else:
                print("Tie")
        print(str)
