import random
from datetime import datetime, timedelta
from tabulate import tabulate
import pandas as pd

def log_parameters(params):
    if 'end_time' in params and params['end_time'] is not None:
        params['end_time'] = pd.to_datetime(params['end_time']).strftime('%Y-%m-%d')
    table = [[key, value] for key, value in params.items() if key != 'symbols']
    print("Parameters:\n" + tabulate(table, headers=["Parameter", "Value"], tablefmt="pretty"))

# Generate a random date between two dates
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

financial_params = {
    'initial_balance': 150,
    'leverage_min': 1,
    'leverage_max': 150,
    'collateral_min': 5,
    'collateral_max': 5_000_000,
    'stop_loss_min': 0.01,
    'stop_loss_max': 0.5,
    'take_profit_min': 0.1,
    'take_profit_max': 9,
    'risk_per_trade_min': 0.025,
    'risk_per_trade_max': 0.1,
    'tp_mult_perc': 0.35,
    'sl_mult_perc': 0.2,
    'cooldown_period': 1,
    'trading_penalty': 0.5,
    'kelly_fraction': 0.5,
}

constant_params = {
    'adjust_leverage': True,
    'risk_mgmt': 'fractals',
    'reverse_actions': False,
    'trading_fee': 0.008,  # 0.1% trading fee
    'slippage': 0.0005,    # 0.05% slippage 
    'bid_ask_spread': 0.0002,  # 0.02% bid-ask spread
    'borrowing_fee_per_hour': 0.0001,  # 0.01% per hour
}


# Define the range for the random date
start_date = datetime(2020, 1, 1)
end_date = datetime(2024, 12, 31)

# choose one of the following
granularity_params_1 = {
    'market_data': 'original', # 'original' or 'random' or 'synthetic'
    'symbols': sorted(['ADA', 'BNB', 'EOS', 'ETH', 'IOTA', 'LTC', 'NEO', 'QTUM', 'XLM', 'XRP']),
    'end_time': '2021-08-31',
    'limit': 100, # 240,
    'interval': '1d',
    'boost_factor': 3.5,
    'model_name': 'model_ppo_crypto_trading_slow',
    'basic_risk_mgmt': False
}

granularity_params_2 = {
    'market_data': 'original', # 'original' or 'random' or 'synthetic'
    'symbols': sorted({'BTC', 'ETC', 'ICX', 'LINK', 'NULS', 'ONT', 'TRX', 'TUSD', 'USDC', 'VET'}),
    'end_time': '2021-04-15',
    'limit': 100,
    'interval': '1d',
    'boost_factor': 3.5,
    'model_name': 'model_ppo_crypto_trading_slow',
    'basic_risk_mgmt': False
}

trailing_stop_params = {
    'market_data': 'original', # 'original' or 'random' or 'synthetic'
    'symbols': sorted(['ADA', 'BNB', 'EOS', 'ETH', 'IOTA', 'LTC', 'NEO', 'QTUM', 'XLM', 'XRP']),
    # 'symbols': sorted({'BTC', 'ETC', 'ICX', 'LINK', 'NULS', 'ONT', 'TRX', 'TUSD', 'USDC', 'VET'}),
    'end_time': '2021-05-31',
    'limit': 100, # 240,
    'interval': '1d',
    'boost_factor': 3.5,
    'model_name': 'model_ppo_crypto_trading_slow_trailing_stop',
    'basic_risk_mgmt': False
}

basic_params = {
    'market_data': 'random', # 'original' or 'random' or 'synthetic'
    'interval': '1d',
    'limit': 365,
    'end_time': random_date(start_date, end_date).strftime('%Y-%m-%d'),
    'boost_factor': 3.5,
    'model_name': 'model_ppo_crypto_trading_fast',
    'basic_risk_mgmt': True
}

unittest_params = {
    'market_data': 'original', # 'original' or 'random' or 'synthetic'
    'synth_mode': 'testing', # 'training' or 'testing'
    'symbols': sorted(['ADA', 'BNB', 'EOS', 'ETH', 'IOTA', 'LTC', 'NEO', 'QTUM', 'XLM', 'XRP']),
    # 'symbols': sorted(['BTC', 'ETC', 'ICX', 'LINK', 'NULS', 'ONT', 'TRX', 'LTC', 'NEO', 'VET']),
    # 'symbols': sorted(['LTC', 'DOGE', 'SHIB', 'PEOPLE', 'FLOKI', 'PEPE', 'MEME', 'BONK', 'WIF', 'BOME']),
    'end_time': '2021-06-30', #'2021-08-31', #random_date(start_date, end_date).strftime('%Y-%m-%d'),
    'limit': 175, # 240,
    'interval': '1d',
    'boost_factor': 30,
    'model_name': 'model_ppo_crypto_trading_plex', #'model_ppo_crypto_trading_unit_12h',
    'basic_risk_mgmt': False
}

optim_params = {
    'market_data': 'original', # 'original' or 'random' or 'synthetic'
    # 'symbols': sorted(['ADA', 'BNB', 'EOS', 'ETH', 'IOTA', 'LTC', 'NEO', 'QTUM', 'XLM', 'XRP']),
    # 'symbols': sorted({'BTC', 'ETC', 'ICX', 'LINK', 'NULS', 'ONT', 'TRX', 'TUSD', 'USDC', 'VET'}),
    'symbols': sorted(['LTC', 'DOGE', 'SHIB', 'PEOPLE', 'FLOKI', 'PEPE', 'MEME', 'BONK', 'WIF', 'BOME']),
    'end_time': '2024-11-20',
    'limit': 100, # 240,
    'interval': '1d',
    'boost_factor': 25,
    'model_name': 'model_ppo_crypto_trading_prod', #'model_ppo_crypto_trading_unit_12h',
    'basic_risk_mgmt': False
}

synth_params = {
    'market_data': 'synthetic', # 'original' or 'random' or 'synthetic'
    'synth_mode': 'training', # 'training' or 'testing'
    'end_time': '2024-10-30',
    'limit': 100, # 240,
    'interval': '1d',
    'boost_factor': 22,
    'model_name': 'model_ppo_crypto_trading_synth',
    'basic_risk_mgmt': False
}

live_params = {
    'market_data': 'random', # 'original' or 'random' or 'synthetic'
    'symbols': sorted(['LTC', 'DOGE', 'SHIB', 'PEOPLE', 'FLOKI', 'PEPE', 'MEME', 'BONK', 'WIF', 'BOME']),
    'end_time': None, #'2021-05-31',
    'limit': 100, # 240,
    'interval': '1d',
    'boost_factor': 25,
    'model_name': 'model_ppo_crypto_trading_killbill', #'model_ppo_crypto_trading_synth_wo_trail', #'model_ppo_crypto_trading_unit_12h',
    'basic_risk_mgmt': True # complex risk management is done using web socket
}

training_params = {
    'train_model': False,
    'timesteps': 25_000,
    'num_episodes': 10
}

specific_params = unittest_params

# Create a new dictionary that combines constant_params with the selected params
selected_params = financial_params.copy()  # Start with a copy of constant_params
selected_params.update(constant_params)   # Update with the selected params
selected_params.update(specific_params)   # Update with the selected params

# log_parameters(selected_params)




# params_1 = {'target': 15326.126815563985, 'params': {'batch_size': 256, 'boost_factor': 37.723268797905156, 'clip_range': 0.3448045164184047, 'clip_range_schedule': 'exponential', 'collateral_max': 239351.4797023058, 'collateral_min': 927.4646048755571, 'cooldown_period': 10.349143666135008, 'ent_coef': 0.06363225806792717, 'gae_lambda': 0.9941276807224645, 'initial_balance': 3955.7953470221264, 'interval': '12h', 'kelly_fraction': 0.5870617860755815, 'learning_rate': 0.009999781673471228, 'learning_rate_schedule': 'exponential', 'leverage_max': 142.1301722662317, 'leverage_min': 14.860751255529122, 'limit': 517.7120078580024, 'max_grad_norm': 0.7247566642326536, 'n_epochs': 21.047073565786057, 'n_steps': 1024, 'num_episodes': 18.53474086988722, 'risk_per_trade': 0.1654790858483852, 'sl_mult_perc': 0.7094427943850085, 'timesteps': 44373.27409746959, 'tp_mult_perc': 0.2992831774041858, 'trading_penalty': 3.707350405670074, 'vf_coef': 0.9029303926816543}, 'output_dir': 'N/A'}
# params_2 = {'target': 3637.983691529709, 'params': {'batch_size': 256, 'boost_factor': 37.73468116216042, 'clip_range': 0.3455922619451837, 'clip_range_schedule': 'exponential', 'collateral_max': 239351.48974206502, 'collateral_min': 927.4749832535688, 'cooldown_period': 10.360415635187064, 'ent_coef': 0.06374352418263508, 'gae_lambda': 0.9940583043205065, 'initial_balance': 3955.8047374367825, 'interval': '12h', 'kelly_fraction': 0.587228338884889, 'learning_rate': 0.01, 'learning_rate_schedule': 'exponential', 'leverage_max': 142.14101344801497, 'leverage_min': 14.86776688565866, 'limit': 517.7215385360851, 'max_grad_norm': 0.7250797298127555, 'n_epochs': 21.05848925572844, 'n_steps': 1024, 'num_episodes': 18.55437047537436, 'risk_per_trade': 0.16550624199967884, 'sl_mult_perc': 0.7097963031359721, 'timesteps': 44373.28386361396, 'tp_mult_perc': 0.3012772186199685, 'trading_penalty': 3.7090327191846133, 'vf_coef': 0.903003735776594}, 'output_dir': 'N/A'}
# params_3 = {'target': 945.6100435454418, 'params': {'batch_size': 256, 'boost_factor': 37.73265527495268, 'clip_range': 0.3001830560444592, 'clip_range_schedule': 'exponential', 'collateral_max': 239351.53472428964, 'collateral_min': 927.5092115228115, 'cooldown_period': 10.357019601141479, 'ent_coef': 0.05535113006090066, 'gae_lambda': 0.9935792769889629, 'initial_balance': 3955.8564767581206, 'interval': '12h', 'kelly_fraction': 0.5856603791268618, 'learning_rate': 0.008855558227276942, 'learning_rate_schedule': 'linear', 'leverage_max': 142.13531686203387, 'leverage_min': 14.86590332497829, 'limit': 517.7727168122015, 'max_grad_norm': 0.7233552572839339, 'n_epochs': 21.054439496491625, 'n_steps': 1024, 'num_episodes': 18.28743342444037, 'risk_per_trade': 0.16171411826268317, 'sl_mult_perc': 0.7075737148979527, 'timesteps': 44373.33540887255, 'tp_mult_perc': 0.23780722424771544, 'trading_penalty': 3.7095731401209466, 'vf_coef': 0.9015289857329346}, 'output_dir': 'N/A'}
# params_4 = {'target': 569.4157117177845, 'params': {'batch_size': 256, 'boost_factor': 37.77000108059525, 'clip_range': 0.30615166912198133, 'clip_range_schedule': 'exponential', 'collateral_max': 239351.74840529513, 'collateral_min': 927.6674773653078, 'cooldown_period': 10.388844210944054, 'ent_coef': 0.061203683085175084, 'gae_lambda': 0.9935796805044891, 'initial_balance': 3956.070410410571, 'interval': '12h', 'kelly_fraction': 0.585660782642388, 'learning_rate': 0.01, 'learning_rate_schedule': 'linear', 'leverage_max': 142.1576213092895, 'leverage_min': 14.888242089024748, 'limit': 517.9866477951477, 'max_grad_norm': 0.7233556607994601, 'n_epochs': 21.084796878287765, 'n_steps': 1024, 'num_episodes': 18.365688382219695, 'risk_per_trade': 0.16755326831288245, 'sl_mult_perc': 0.707574118413479, 'timesteps': 44373.54940091472, 'tp_mult_perc': 0.24516935963403394, 'trading_penalty': 3.7238255332740864, 'vf_coef': 0.9015293892484608}, 'output_dir': 'N/A'}
# params_5 = {'target': 21.374123800280383, 'params': {'batch_size': 64, 'boost_factor': 9.108963017076968, 'clip_range': 0.11058560374967809, 'clip_range_schedule': 'linear', 'collateral_max': 149792.7082207011, 'collateral_min': 806.3296773719082, 'cooldown_period': 13.457090777313327, 'ent_coef': 0.03415518655614726, 'gae_lambda': 0.8354394450560254, 'initial_balance': 2529.559775198755, 'interval': '12h', 'kelly_fraction': 0.42867401289232565, 'learning_rate': 0.004624012538046314, 'learning_rate_schedule': 'linear', 'leverage_max': 135.14225771237798, 'leverage_min': 1.8820757052880182, 'limit': 480.675361683711, 'max_grad_norm': 0.40974169001792127, 'n_epochs': 10.350397077202683, 'n_steps': 1024, 'num_episodes': 44.358161606815585, 'risk_per_trade': 0.15240294200915078, 'sl_mult_perc': 0.45922387997657566, 'timesteps': 48244.909728465325, 'tp_mult_perc': 0.4453740979743197, 'trading_penalty': 3.4251342247914556, 'vf_coef': 0.16036154728462787}, 'output_dir': 'N/A'}
# params_6 = {'target': 2.102995659997883, 'params': {'batch_size': 64, 'boost_factor': 11.927424131511449, 'clip_range': 0.32059209010358325, 'clip_range_schedule': 'step', 'collateral_max': 243782.4970147584, 'collateral_min': 335.48627807841217, 'cooldown_period': 9.021747263425505, 'ent_coef': 0.07666956523344381, 'gae_lambda': 0.8900469457489464, 'initial_balance': 2010.6216162974847, 'interval': '5m', 'kelly_fraction': 0.32998481969940596, 'learning_rate': 0.003531371620915724, 'learning_rate_schedule': 'step', 'leverage_max': 78.77902924642693, 'leverage_min': 8.20196124876598, 'limit': 991.2013288209316, 'max_grad_norm': 0.7281310703693529, 'n_epochs': 11.673824385426926, 'n_steps': 2048, 'num_episodes': 47.266311067854616, 'risk_per_trade': 0.18866743395586236, 'sl_mult_perc': 0.76909807474909, 'timesteps': 47277.426327198205, 'tp_mult_perc': 0.2998627888673755, 'trading_penalty': 0.8084252269520469, 'vf_coef': 0.42462447175802875}, 'output_dir': 'N/A'}
# params_7 = {'target': 0.0, 'params': {'batch_size': 64, 'boost_factor': 3.6147647107369387, 'clip_range': 0.27223528164760397, 'clip_range_schedule': 'linear', 'collateral_max': 589716.2313663809, 'collateral_min': 714.7704420198846, 'cooldown_period': 6.535016432417388, 'ent_coef': 0.041405598781956834, 'gae_lambda': 0.938880031545549, 'initial_balance': 2656.7170781076106, 'interval': '3m', 'kelly_fraction': 0.4483326638450825, 'learning_rate': 0.00664130850574569, 'learning_rate_schedule': 'exponential', 'leverage_max': 144.45947559908132, 'leverage_min': 12.144545769537865, 'limit': 927.5514364659126, 'max_grad_norm': 0.3962322929023663, 'n_epochs': 6.760461375770481, 'n_steps': 2048, 'num_episodes': 25.907073479421342, 'risk_per_trade': 0.04141729745221723, 'sl_mult_perc': 0.9347577223564305, 'timesteps': 30432.975792365196, 'tp_mult_perc': 0.7757308928225399, 'trading_penalty': 3.6327299468987526, 'vf_coef': 0.8949754820852288}, 'output_dir': 'N/A'}
# params_8 = {'target': 0.0, 'params': {'batch_size': 32, 'boost_factor': 42.19349809033431, 'clip_range': 0.2828213893265432, 'clip_range_schedule': 'exponential', 'collateral_max': 716290.8374277797, 'collateral_min': 760.5306692313666, 'cooldown_period': 17.55619307767458, 'ent_coef': 0.0462214316930602, 'gae_lambda': 0.9266462799135226, 'initial_balance': 2924.991169134423, 'interval': '3m', 'kelly_fraction': 0.1623048311556194, 'learning_rate': 0.005882696463824781, 'learning_rate_schedule': 'exponential', 'leverage_max': 59.741653599412274, 'leverage_min': 16.776344599061964, 'limit': 623.7324295319028, 'max_grad_norm': 0.7960155108078342, 'n_epochs': 18.66032865458405, 'n_steps': 1024, 'num_episodes': 34.471103401023846, 'risk_per_trade': 0.09777376377655914, 'sl_mult_perc': 0.4829254463412185, 'timesteps': 36856.46272072072, 'tp_mult_perc': 0.34647860781299455, 'trading_penalty': 0.47403874585839484, 'vf_coef': 0.4579947584118913}, 'output_dir': 'N/A'}
# params_9 = {'target': -1.555190192237315, 'params': {'batch_size': 128, 'boost_factor': 39.38292410182589, 'clip_range': 0.1729970766186643, 'clip_range_schedule': 'step', 'collateral_max': 92254.47410701064, 'collateral_min': 831.6178163389774, 'cooldown_period': 6.360279484475213, 'ent_coef': 0.05027144274670854, 'gae_lambda': 0.8485743363491773, 'initial_balance': 4223.450631440122, 'interval': '30m', 'kelly_fraction': 0.25371517202952876, 'learning_rate': 0.0002469549387066683, 'learning_rate_schedule': 'linear', 'leverage_max': 109.57656427415706, 'leverage_min': 4.989282253905992, 'limit': 489.3727768413753, 'max_grad_norm': 0.9413925248956772, 'n_epochs': 7.416630068745856, 'n_steps': 4096, 'num_episodes': 44.099769649758265, 'risk_per_trade': 0.06496688936380668, 'sl_mult_perc': 0.5534831045803988, 'timesteps': 22460.653295637007, 'tp_mult_perc': 0.12737828482163388, 'trading_penalty': 4.6913558259270545, 'vf_coef': 0.8411595111389265}, 'output_dir': 'N/A'}
# params_10 = {'target': -9.97828705744087, 'params': {'batch_size': 64, 'boost_factor': 9.635243970415882, 'clip_range': 0.38275171706828603, 'clip_range_schedule': 'linear', 'collateral_max': 768636.967258197, 'collateral_min': 957.6301576576375, 'cooldown_period': 14.082643349723957, 'ent_coef': 0.005594495696309221, 'gae_lambda': 0.9018127138547087, 'initial_balance': 2269.404439845252, 'interval': '1h', 'kelly_fraction': 0.315324211636388, 'learning_rate': 0.0009184483401840932, 'learning_rate_schedule': 'linear', 'leverage_max': 149.43315639346463, 'leverage_min': 2.3656024856739144, 'limit': 538.6066671555782, 'max_grad_norm': 0.9115105770552601, 'n_epochs': 15.153232425918468, 'n_steps': 4096, 'num_episodes': 45.51548016127665, 'risk_per_trade': 0.16441676147260378, 'sl_mult_perc': 0.12074737491144633, 'timesteps': 33967.56919160856, 'tp_mult_perc': 0.970098254955513, 'trading_penalty': 3.5106740826642393, 'vf_coef': 0.760404624612112}, 'output_dir': 'N/A'}

# find . -type d -name "optim*" -exec grep -H "37.723268797905156" {}/output_recap.log \;

# best_param = {
#     'target': 15326.126815563985,
#     'params': {
#         'batch_size': 256,
#         'boost_factor': 37.723268797905156,
#         'clip_range': 0.3448045164184047,
#         'clip_range_schedule': 'exponential',
#         'collateral_max': 239351.4797023058,
#         'collateral_min': 927.4646048755571,
#         'cooldown_period': 10.349143666135008,
#         'ent_coef': 0.06363225806792717,
#         'gae_lambda': 0.9941276807224645,
#         'initial_balance': 3955.7953470221264,
#         'interval': '12h',
#         'kelly_fraction': 0.5870617860755815,
#         'learning_rate': 0.009999781673471228,
#         'learning_rate_schedule': 'exponential',
#         'leverage_max': 142.1301722662317,
#         'leverage_min': 14.860751255529122,
#         'limit': 400, # 517.7120078580024,
#         'max_grad_norm': 0.7247566642326536,
#         'n_epochs': 21.047073565786057,
#         'n_steps': 1024,
#         'num_episodes': 18.53474086988722,
#         'risk_per_trade': 0.1654790858483852,
#         'sl_mult_perc': 0.7094427943850085,
#         'timesteps': 44373.27409746959,
#         'tp_mult_perc': 0.2992831774041858,
#         'trading_penalty': 3.707350405670074,
#         'vf_coef': 0.9029303926816543
#     },
#     'output_dir': 'N/A'
# }

# financial_params = {
#     'initial_balance': round(best_param['params']['initial_balance']),
#     'leverage_min': round(best_param['params']['leverage_min']),
#     'leverage_max': round(best_param['params']['leverage_max']),
#     'collateral_min': round(best_param['params']['collateral_min']),
#     'collateral_max': round(best_param['params']['collateral_max']),
#     'risk_per_trade': round(best_param['params']['risk_per_trade'], 2),
#     'tp_mult_perc': round(best_param['params']['tp_mult_perc'], 2),
#     'sl_mult_perc': round(best_param['params']['sl_mult_perc'], 2),
#     'cooldown_period': round(best_param['params']['cooldown_period']),
#     'trading_penalty': round(best_param['params']['trading_penalty'], 2),
#     'kelly_fraction': round(best_param['params']['kelly_fraction'], 2),
# }

# constant_params = {
#     'adjust_leverage': True,
#     'risk_mgmt': 'fractals',
#     'reverse_actions': False,
#     'trading_fee': 0.008,  # 0.1% trading fee
#     'slippage': 0.0005,    # 0.05% slippage 
#     'bid_ask_spread': 0.0002,  # 0.02% bid-ask spread
#     'borrowing_fee_per_hour': 0.0001,  # 0.01% per hour
# }

# training_params = {
#     'train_model': False,
#     'timesteps': 25_000,
#     'num_episodes': 10,
#     'n_steps': best_param['params']['n_steps'],
#     'n_epochs': round(best_param['params']['n_epochs']),
#     'learning_rate': round(best_param['params']['learning_rate'], 4),
#     'learning_rate_schedule': best_param['params']['learning_rate_schedule'],
#     'batch_size': best_param['params']['batch_size'],
#     'clip_range': round(best_param['params']['clip_range'], 3),
#     'clip_range_schedule': best_param['params']['clip_range_schedule'],
#     'max_grad_norm': round(best_param['params']['max_grad_norm'], 3),
#     'vf_coef': round(best_param['params']['vf_coef'], 3),
#     'ent_coef': round(best_param['params']['ent_coef'], 3),
#     'gae_lambda': round(best_param['params']['gae_lambda'], 3),
# }


# # Define the range for the random date
# start_date = datetime(2021, 4, 1)
# end_date = datetime(2024, 12, 31)

# # choose one of the following
# specific_params = {
#     'market_data': 'original', # 'original' or 'random' or 'synthetic'
#     # 'symbols': sorted(['ADA', 'BNB', 'EOS', 'ETH', 'IOTA', 'LTC', 'NEO', 'QTUM', 'XLM', 'XRP']),
#     # 'symbols': sorted({'BTC', 'ETC', 'ICX', 'LINK', 'NULS', 'ONT', 'TRX', 'TUSD', 'USDC', 'VET'}),
#     'symbols': sorted(['LTC', 'DOGE', 'SHIB', 'PEOPLE', 'FLOKI', 'PEPE', 'MEME', 'BONK', 'WIF', 'BOME']),
#     'end_time': '2024-11-20', # random_date(start_date, end_date).strftime('%Y-%m-%d'),
#     'limit': round(best_param['params']['limit']),
#     'interval': best_param['params']['interval'],
#     'boost_factor': round(best_param['params']['boost_factor'], 1),
#     'model_name': 'model_ppo_crypto_trading_best',
#     'basic_risk_mgmt': False
# }

# # Create a new dictionary that combines constant_params with the selected params
# selected_params = financial_params.copy()  # Start with a copy of constant_params
# selected_params.update(constant_params)   # Update with the selected params
# selected_params.update(specific_params)   # Update with the selected params

log_parameters(selected_params)
log_parameters(training_params)



# params_1 = {'target': 12005543.998132827, 'params': {'batch_size': 128, 'boost_factor': 20.245647874935752, 'clip_range': 0.21671354680457017, 'clip_range_schedule': 'linear', 'collateral_max': 773937.4328613839, 'collateral_min': 476.93081234374495, 'cooldown_period': 8.170300005504675, 'ent_coef': 0.028786808351933424, 'gae_lambda': 0.9407626086792249, 'initial_balance': 4026.540752591452, 'interval': '12h', 'kelly_fraction': 0.6930999065540848, 'learning_rate': 0.007281015539479985, 'learning_rate_schedule': 'linear', 'leverage_max': 131.59393914816076, 'leverage_min': 11.881306188658609, 'limit': 554.6825972237737, 'max_grad_norm': 0.5520227863964379, 'n_epochs': 12.05477325502877, 'n_steps': 2048, 'num_episodes': 29.526252496989976, 'risk_per_trade': 0.04804012983570592, 'sl_mult_perc': 0.7566443785142316, 'timesteps': 55560.6441968169, 'tp_mult_perc': 0.5255757926971708, 'trading_penalty': 2.575644026010265, 'vf_coef': 0.7358570790180237}, 'output_dir': 'N/A'}
# params_2 = {'target': 11923728.975701049, 'params': {'batch_size': 128, 'boost_factor': 20.245647927047585, 'clip_range': 0.21671357005629893, 'clip_range_schedule': 'linear', 'collateral_max': 773937.4330820297, 'collateral_min': 476.9308128773113, 'cooldown_period': 8.170300040122797, 'ent_coef': 0.028786831494276247, 'gae_lambda': 0.9407626318098837, 'initial_balance': 4026.5407535645795, 'interval': '12h', 'kelly_fraction': 0.693099929682435, 'learning_rate': 0.007281038614978234, 'learning_rate_schedule': 'linear', 'leverage_max': 131.59393918919716, 'leverage_min': 11.88130621965494, 'limit': 554.6825976814575, 'max_grad_norm': 0.5520228099064777, 'n_epochs': 12.054773295615396, 'n_steps': 2048, 'num_episodes': 29.52625254004433, 'risk_per_trade': 0.04804015305685777, 'sl_mult_perc': 0.756644401824554, 'timesteps': 55560.644240210735, 'tp_mult_perc': 0.5255758162330195, 'trading_penalty': 2.575644051449185, 'vf_coef': 0.7358571023486359}, 'output_dir': 'N/A'}
# params_3 = {'target': 10051175.160516985, 'params': {'batch_size': 128, 'boost_factor': 20.2455337575513, 'clip_range': 0.2165994104319479, 'clip_range_schedule': 'linear', 'collateral_max': 773937.4329527612, 'collateral_min': 476.93069855010316, 'cooldown_period': 8.170185876609155, 'ent_coef': 0.028672671623043135, 'gae_lambda': 0.9406484721624507, 'initial_balance': 4026.540639095689, 'interval': '12h', 'kelly_fraction': 0.692985769911707, 'learning_rate': 0.00716687880155573, 'learning_rate_schedule': 'linear', 'leverage_max': 131.5938250227791, 'leverage_min': 11.881192057599264, 'limit': 554.6824833777807, 'max_grad_norm': 0.5519086498658196, 'n_epochs': 12.054659129974267, 'n_steps': 2048, 'num_episodes': 29.52613837356205, 'risk_per_trade': 0.047925993123470775, 'sl_mult_perc': 0.7565302421526677, 'timesteps': 55560.64411477643, 'tp_mult_perc': 0.5254616562871498, 'trading_penalty': 2.575529890807204, 'vf_coef': 0.7357429425183122}, 'output_dir': 'N/A'}
# params_4 = {'target': 6861222.191753902, 'params': {'batch_size': 64, 'boost_factor': 15.189481855971211, 'clip_range': 0.27847727149257473, 'clip_range_schedule': 'exponential', 'collateral_max': 520974.72058921354, 'collateral_min': 670.6430594391614, 'cooldown_period': 15.788155156860672, 'ent_coef': 0.09061477554461375, 'gae_lambda': 0.852422935082987, 'initial_balance': 3025.6988196896446, 'interval': '1d', 'kelly_fraction': 0.5735046683449311, 'learning_rate': 0.00310447432372111, 'learning_rate_schedule': 'linear', 'leverage_max': 142.10281093710876, 'leverage_min': 15.06602898962919, 'limit': 635.4394434942906, 'max_grad_norm': 0.37196030577233385, 'n_epochs': 24.904053204134442, 'n_steps': 4096, 'num_episodes': 18.63350033907963, 'risk_per_trade': 0.0680779499571007, 'sl_mult_perc': 0.618466603935712, 'timesteps': 29260.922431078972, 'tp_mult_perc': 0.5432756726882527, 'trading_penalty': 2.4090997010312045, 'vf_coef': 0.42651600139001666}, 'output_dir': 'N/A'}
# params_5 = {'target': 1521091.9346725752, 'params': {'batch_size': 64, 'boost_factor': 39.89888156533843, 'clip_range': 0.28360853114993745, 'clip_range_schedule': 'linear', 'collateral_max': 420773.27668716817, 'collateral_min': 682.2781473778124, 'cooldown_period': 18.85580005593308, 'ent_coef': 3.938052559334494e-05, 'gae_lambda': 0.9510892096070414, 'initial_balance': 2506.1733572830935, 'interval': '1d', 'kelly_fraction': 0.4930646436695917, 'learning_rate': 0.008289347658184721, 'learning_rate_schedule': 'exponential', 'leverage_max': 112.80761900877096, 'leverage_min': 6.726205499271132, 'limit': 690.1250046700993, 'max_grad_norm': 0.7911256935526585, 'n_epochs': 26.46942544822091, 'n_steps': 2048, 'num_episodes': 38.215830773189325, 'risk_per_trade': 0.1742502697468311, 'sl_mult_perc': 0.39041207518952903, 'timesteps': 73662.89332387764, 'tp_mult_perc': 0.5374282974563842, 'trading_penalty': 2.199368899806468, 'vf_coef': 0.46972939296642424}, 'output_dir': 'N/A'}
# params_6 = {'target': 1002627.1967130215, 'params': {'batch_size': 256, 'boost_factor': 37.73265527495268, 'clip_range': 0.3001830560444592, 'clip_range_schedule': 'exponential', 'collateral_max': 239351.53472428964, 'collateral_min': 924.4569677974562, 'cooldown_period': 10.357019601141479, 'ent_coef': 0.05535113006090066, 'gae_lambda': 0.9935792769889629, 'initial_balance': 3955.8564767581206, 'interval': '12h', 'kelly_fraction': 0.5856603791268618, 'learning_rate': 0.008855558227276942, 'learning_rate_schedule': 'linear', 'leverage_max': 142.13531686203387, 'leverage_min': 14.86590332497829, 'limit': 517.7727168122015, 'max_grad_norm': 0.7233552572839339, 'n_epochs': 21.054439496491625, 'n_steps': 1024, 'num_episodes': 18.28743342444037, 'risk_per_trade': 0.16171411826268317, 'sl_mult_perc': 0.7075737148979527, 'timesteps': 84995.5610903268, 'tp_mult_perc': 0.23780722424771544, 'trading_penalty': 3.7095731401209466, 'vf_coef': 0.9015289857329346}, 'output_dir': 'N/A'}
# params_7 = {'target': 813116.8571533583, 'params': {'batch_size': 64, 'boost_factor': 39.89888154216192, 'clip_range': 0.28360850460168674, 'clip_range_schedule': 'linear', 'collateral_max': 420773.27688274, 'collateral_min': 682.278147458517, 'cooldown_period': 18.85580002973192, 'ent_coef': 3.9353971794925774e-05, 'gae_lambda': 0.9510891830360075, 'initial_balance': 2506.1733580986484, 'interval': '1d', 'kelly_fraction': 0.49306461716880157, 'learning_rate': 0.008289321071211622, 'learning_rate_schedule': 'exponential', 'leverage_max': 112.80761899474295, 'leverage_min': 6.726205477166024, 'limit': 690.1250047481536, 'max_grad_norm': 0.7911256670356427, 'n_epochs': 26.469425422825605, 'n_steps': 2048, 'num_episodes': 38.21583075058118, 'risk_per_trade': 0.1742502431679718, 'sl_mult_perc': 0.390412048807827, 'timesteps': 73662.89333274486, 'tp_mult_perc': 0.5374282710250401, 'trading_penalty': 2.1993688741646653, 'vf_coef': 0.46972936655793734}, 'output_dir': 'N/A'}
# params_8 = {'target': 472832.14749914204, 'params': {'batch_size': 64, 'boost_factor': 45.66561880998825, 'clip_range': 0.3493362397068962, 'clip_range_schedule': 'exponential', 'collateral_max': 788035.2860117669, 'collateral_min': 380.9933512054453, 'cooldown_period': 14.188940031695525, 'ent_coef': 0.03485862646021325, 'gae_lambda': 0.9834888004710473, 'initial_balance': 1457.1123282194708, 'interval': '8h', 'kelly_fraction': 0.6892473944551231, 'learning_rate': 0.0032991362957617613, 'learning_rate_schedule': 'exponential', 'leverage_max': 107.41991533042076, 'leverage_min': 5.4360680553079055, 'limit': 569.8245419504426, 'max_grad_norm': 0.7440429828261637, 'n_epochs': 20.403087133201655, 'n_steps': 2048, 'num_episodes': 32.56605657872211, 'risk_per_trade': 0.06630539550473546, 'sl_mult_perc': 0.7352893099133841, 'timesteps': 48050.81004022262, 'tp_mult_perc': 0.47505643559335287, 'trading_penalty': 1.2423839016753808, 'vf_coef': 0.8586982946617604}, 'output_dir': 'N/A'}
# params_9 = {'target': 338860.36543646595, 'params': {'batch_size': 64, 'boost_factor': 39.60853245744971, 'clip_range': 0.28360935311348023, 'clip_range_schedule': 'linear', 'collateral_max': 420773.48632113106, 'collateral_min': 682.2781481997753, 'cooldown_period': 18.779026669662887, 'ent_coef': 4.0202489135743315e-05, 'gae_lambda': 0.995351829806212, 'initial_balance': 2506.321258983098, 'interval': '1d', 'kelly_fraction': 0.49306546563313447, 'learning_rate': 0.008290169621727123, 'learning_rate_schedule': 'exponential', 'leverage_max': 112.80761983073504, 'leverage_min': 6.4259493522181845, 'limit': 690.1250054920622, 'max_grad_norm': 0.825015234591862, 'n_epochs': 26.174473583584145, 'n_steps': 2048, 'num_episodes': 37.92228993789212, 'risk_per_trade': 0.17425109171037398, 'sl_mult_perc': 0.3904128971530718, 'timesteps': 73663.10326300698, 'tp_mult_perc': 0.5057865427720143, 'trading_penalty': 1.9166927326372711, 'vf_coef': 0.469730214929967}, 'output_dir': 'N/A'}
# params_10 = {'target': 285953.70640705444, 'params': {'batch_size': 256, 'boost_factor': 47.7440309802318, 'clip_range': 0.20850054649148772, 'clip_range_schedule': 'exponential', 'collateral_max': 909379.422713358, 'collateral_min': 899.7075470117425, 'cooldown_period': 17.149412594785332, 'ent_coef': 0.01566663746338334, 'gae_lambda': 0.8718115683154645, 'initial_balance': 4265.228765952113, 'interval': '12h', 'kelly_fraction': 0.3397698697609294, 'learning_rate': 0.006360507648554692, 'learning_rate_schedule': 'step', 'leverage_max': 78.8108891622498, 'leverage_min': 8.599671263439921, 'limit': 271.6153227685566, 'max_grad_norm': 0.5649429312507143, 'n_epochs': 13.720167841035574, 'n_steps': 2048, 'num_episodes': 23.023463451427432, 'risk_per_trade': 0.09356318319655521, 'sl_mult_perc': 0.6582524438086942, 'timesteps': 92702.71448946245, 'tp_mult_perc': 0.11325210441424624, 'trading_penalty': 0.7091896744861514, 'vf_coef': 0.14046698757144135}, 'output_dir': 'N/A'}



# params_1 = {'target': 1.8522886204704387, 'params': {'batch_size': 64, 'boost_factor': 21.74538605570909, 'clip_range': 0.11630383294746163, 'clip_range_schedule': 'step', 'collateral_max': 666634.040546071, 'collateral_min': 244.98736535568176, 'cooldown_period': 5.091998993089825, 'ent_coef': 0.05160955834490191, 'gae_lambda': 0.8228873840177698, 'initial_balance': 715.6320153235805, 'interval': '4h', 'kelly_fraction': 0.2920552928913409, 'learning_rate': 0.002205765251664654, 'learning_rate_schedule': 'step', 'leverage_max': 122.59387048850178, 'leverage_min': 12.36656550599317, 'limit': 628.3319972112254, 'max_grad_norm': 0.8312921278709549, 'n_epochs': 16.82361313218388, 'n_steps': 512, 'num_episodes': 44.52002007597917, 'risk_per_trade': 0.17511076660151062, 'sl_mult_perc': 0.6619379006634124, 'timesteps': 49963.99006827058, 'tp_mult_perc': 0.8837088176239966, 'trading_penalty': 2.9742368190163586, 'vf_coef': 0.13014971009717455}, 'output_dir': 'N/A'}
# params_2 = {'target': 0.7548125633232016, 'params': {'batch_size': 32, 'boost_factor': 1.0308711370550967, 'clip_range': 0.1, 'clip_range_schedule': 'linear', 'collateral_max': 666700.0353452949, 'collateral_min': 296.91059910364817, 'cooldown_period': 16.092446248980774, 'ent_coef': 0.1, 'gae_lambda': 0.8, 'initial_balance': 705.8344995846579, 'interval': '1d', 'kelly_fraction': 0.75, 'learning_rate': 0.004883550722418027, 'learning_rate_schedule': 'step', 'leverage_max': 50.0, 'leverage_min': 19.051535855327458, 'limit': 481.74497857603006, 'max_grad_norm': 0.3, 'n_epochs': 23.517757713969154, 'n_steps': 512, 'num_episodes': 49.958570295648926, 'risk_per_trade': 0.01, 'sl_mult_perc': 0.1, 'timesteps': 49814.99689729136, 'tp_mult_perc': 0.1, 'trading_penalty': 0.03807764762482925, 'vf_coef': 0.14067815304847808}, 'output_dir': 'N/A'}
# params_3 = {'target': 0.7403741496598639, 'params': {'batch_size': 128, 'boost_factor': 40.8893390272648, 'clip_range': 0.38198807530628454, 'clip_range_schedule': 'exponential', 'collateral_max': 168069.49793137866, 'collateral_min': 357.8921624772749, 'cooldown_period': 14.956381114093425, 'ent_coef': 0.09088741920335296, 'gae_lambda': 0.9451737185839935, 'initial_balance': 980.3476366312086, 'interval': '8h', 'kelly_fraction': 0.4102046875419343, 'learning_rate': 0.00121490796940148, 'learning_rate_schedule': 'step', 'leverage_max': 59.473736761974706, 'leverage_min': 14.579806012081969, 'limit': 364.36031271916096, 'max_grad_norm': 0.3986887573656744, 'n_epochs': 25.269247778537878, 'n_steps': 4096, 'num_episodes': 30.491218116590385, 'risk_per_trade': 0.02269009173293552, 'sl_mult_perc': 0.8728241998849765, 'timesteps': 22066.756135154934, 'tp_mult_perc': 0.28591022113462433, 'trading_penalty': 2.0655331448282332, 'vf_coef': 0.1503202794424623}, 'output_dir': 'N/A'}

