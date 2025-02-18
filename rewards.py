from reporting import net_profit, sharpe, max_drawdown
import logging
import traceback
import numpy as np

def calculate_short_term_reward(self, action):
    try:
        current_prices = self.data_matrix[self.current_step, :, self.mapping['close']]
        reward = 0

        # Initialize arrays for pnl and return_on_investment
        pnl = [0] * self.num_symbols
        return_on_investment = [0] * self.num_symbols

        for i in range(self.num_symbols):
            position = self.positions[i]
            if position:
                entry_price = position['entry_price']
                position_size = position['position_size']
                leverage = position['leverage']
                collateral = position['collateral']
                
                pnl[i] = (current_prices[i] - entry_price) * position_size * leverage
                if position['type'] == 'short':
                    pnl[i] = -pnl[i]  # Reverse PnL for short positions

                # Calculate return
                return_on_investment[i] = pnl[i] / collateral if collateral != 0 else 0

        # Calculate metrics
        net_profit_value = net_profit(np.array(pnl))
        sharpe_ratio_value = sharpe(np.array(return_on_investment))
        drawdown_value = max_drawdown(np.array(return_on_investment))

        # Hyperparameters
        alpha = self.params.get('alpha', 1.0)
        beta = self.params.get('beta', 1.0)
        gamma = self.params.get('gamma', 1.0)

        # Calculate transaction costs
        transaction_costs = sum(1 for action_value in action if action_value != 0) * float(self.params['trading_penalty'])

        # Calculate reward
        reward = (net_profit_value +
                  alpha * sharpe_ratio_value -
                  beta * drawdown_value -
                  gamma * transaction_costs)

        logging.debug(f"Computing short-term reward: {reward} with net profit {net_profit_value}, sharpe ratio {sharpe_ratio_value}, drawdown {drawdown_value}, and transaction costs {transaction_costs}")

        return reward

    except Exception as e:
        logging.error("An error occurred in calculate_short_term_reward")
        logging.error(traceback.format_exc())
        return None

def calculate_combined_reward(self, action):
    try:
        current_prices = self.data_matrix[self.current_step, :, self.mapping['close']]
        reward = 0

        # Define weights
        weight_net_profit = 0.3
        weight_sharpe_ratio = 0.35
        weight_max_drawdown = 0.35

        # Initialize arrays for pnl and return_on_investment
        pnl = [0] * self.num_symbols
        return_on_investment = [0] * self.num_symbols

        for i in range(self.num_symbols):
            position = self.positions[i]
            if position:
                entry_price = position['entry_price']
                position_size = position['position_size']
                leverage = position['leverage']
                collateral = position['collateral']
                
                pnl[i] = (current_prices[i] - entry_price) * position_size * leverage
                if position['type'] == 'short':
                    pnl[i] = -pnl[i]  # Reverse PnL for short positions

                # Calculate return
                return_on_investment[i] = pnl[i] / collateral if collateral != 0 else 0
                
        # Calculate metrics
        net_profit_value = net_profit(np.array(pnl))
        sharpe_ratio_value = sharpe(np.array(return_on_investment))
        max_drawdown_value = max_drawdown(np.array(return_on_investment))

        # Update min and max values for normalization
        self.min_max_values['net_profit'] = [min(self.min_max_values['net_profit'][0], net_profit_value),
                                             max(self.min_max_values['net_profit'][1], net_profit_value)]
        self.min_max_values['sharpe_ratio'] = [min(self.min_max_values['sharpe_ratio'][0], sharpe_ratio_value),
                                               max(self.min_max_values['sharpe_ratio'][1], sharpe_ratio_value)]
        self.min_max_values['max_drawdown'] = [min(self.min_max_values['max_drawdown'][0], max_drawdown_value),
                                               max(self.min_max_values['max_drawdown'][1], max_drawdown_value)]

        # Normalize metrics between -1 and 1
        def normalize(value, min_value, max_value):
            if min_value == max_value:
                return 0  # or some other default value
            return 2 * ((value - min_value) / (max_value - min_value)) - 1

        # Normalize each metric
        normalized_net_profit = normalize(net_profit_value, *self.min_max_values['net_profit'])
        normalized_sharpe_ratio = normalize(sharpe_ratio_value, *self.min_max_values['sharpe_ratio'])
        normalized_max_drawdown = normalize(max_drawdown_value, *self.min_max_values['max_drawdown'])

        # Combine normalized metrics into reward
        reward = (weight_net_profit * normalized_net_profit +
                  weight_sharpe_ratio * normalized_sharpe_ratio -
                  weight_max_drawdown * normalized_max_drawdown)
        
        logging.debug(f"Computing reward: {reward} using a combination of net profit {net_profit_value}, sharpe ratio {sharpe_ratio_value}, and max drawdown {max_drawdown_value}")

        return reward

    except Exception as e:
        logging.error("An error occurred in calculate_combined_reward")
        logging.error(traceback.format_exc())
        return None

def calculate_consecutive_pnl_reward(self, action):
    try:
        current_prices = self.data_matrix[self.current_step, :, self.mapping['close']]
        reward = 0

        # Initialize arrays for pnl, consecutive positive PnLs, and previous returns
        pnl = [0] * self.num_symbols
        consecutive_positive_pnls = [0] * self.num_symbols  # Track consecutive positive PnLs
        previous_returns = self.previous_returns if hasattr(self, 'previous_returns') else [0] * self.num_symbols

        # Initialize rate_of_change
        rate_of_change = 0

        # Initialize holding duration
        holding_duration = self.holding_duration if hasattr(self, 'holding_duration') else [0] * self.num_symbols

        for i in range(self.num_symbols):
            position = self.positions[i]
            if position:
                entry_price = position['entry_price']
                position_size = position['position_size']
                leverage = position['leverage']
                collateral = position['collateral']
                
                pnl[i] = (current_prices[i] - entry_price) * position_size * leverage
                if position['type'] == 'short':
                    pnl[i] = -pnl[i]  # Reverse PnL for short positions

                # Calculate return
                current_return = pnl[i] / collateral if collateral != 0 else 0

                # Calculate rate of change of return
                rate_of_change = current_return - previous_returns[i]

                # Update consecutive positive PnL count
                if pnl[i] > 0:
                    consecutive_positive_pnls[i] += 1 * rate_of_change
                    holding_duration[i] += 1  # Increase holding duration for profitable trades
                else:
                    consecutive_positive_pnls[i] = 0
                    holding_duration[i] = 0  # Reset holding duration for non-profitable trades

                # Reward based on rate of change
                # reward += rate_of_change

                # Update previous return
                previous_returns[i] = current_return

        # Calculate reward based on consecutive positive PnLs and holding duration
        # Increase the multiplier for holding duration to further encourage holding
        reward += sum(consecutive_positive_pnls[i] * (1 + holding_duration[i] * float(self.params['holding_bonus'])) for i in range(self.num_symbols))  # Increase reward for longer holding

        # Introduce a penalty for trading activity
        trading_penalty = sum(1 for action_value in action if action_value != 0) * float(self.params['trading_penalty'])
        reward -= trading_penalty

        # Store previous returns and holding duration for the next step
        self.previous_returns = previous_returns
        self.holding_duration = holding_duration

        logging.debug(f"Computing consecutive PnL reward: {reward} with streaks {consecutive_positive_pnls}, rate of change {rate_of_change}, and holding duration {holding_duration}")

        return reward

    except Exception as e:
        logging.error("An error occurred in calculate_consecutive_pnl_reward")
        logging.error(traceback.format_exc())
        return None

calculate_reward = calculate_consecutive_pnl_reward