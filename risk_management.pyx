# risk_management.pyx
import numpy as np
cimport numpy as cnp

def handle_risk_management_cython(int symbol_index, int position_type, 
                                  cnp.ndarray[double] low_prices, 
                                  cnp.ndarray[double] high_prices, 
                                  cnp.ndarray[double] sl_prices, 
                                  cnp.ndarray[double] tp_prices, 
                                  cnp.ndarray[double] liq_prices, 
                                  cnp.ndarray[double] max_prices, 
                                  cnp.ndarray timestamps):
    cdef double sl_price = sl_prices[symbol_index]
    cdef double tp_price = tp_prices[symbol_index]
    cdef double liq_price = liq_prices[symbol_index]
    cdef double max_price = max_prices[symbol_index]
    cdef int i, num_candles = low_prices.shape[0]

    for i in range(num_candles):
        if max_price is not None:
            if position_type == 1 and high_prices[i] >= max_price:
                return symbol_index, max_price, "max", timestamps[i]
            elif position_type == 0 and low_prices[i] <= max_price:
                return symbol_index, max_price, "max", timestamps[i]

        if liq_price is not None:
            if position_type == 1 and low_prices[i] <= liq_price:
                return symbol_index, liq_price, "liq", timestamps[i]
            elif position_type == 0 and high_prices[i] >= liq_price:
                return symbol_index, liq_price, "liq", timestamps[i]

        if tp_price is not None:
            if position_type == 1 and high_prices[i] >= tp_price:
                return symbol_index, tp_price, "tp", timestamps[i]
            elif position_type == 0 and low_prices[i] <= tp_price:
                return symbol_index, tp_price, "tp", timestamps[i]

        if sl_price is not None:
            if position_type == 1 and low_prices[i] <= sl_price:
                return symbol_index, sl_price, "sl", timestamps[i]
            elif position_type == 0 and high_prices[i] >= sl_price:
                return symbol_index, sl_price, "sl", timestamps[i]

    return None, None, None, None