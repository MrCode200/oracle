from typing import Callable


def backtest(self, signaler: Callable[[...], float], partition_frequency: int, sell_limit: float, buy_limit: float):
    """
    Conducts a backtest on the provided market data to evaluate the performance of a trading strategy.

    NOTE:
        - It may not work if the df is not the length of the Trading Component series!

    :param df: The DataFrame containing the market data with a 'Close' column.
    :param partition_frequency: The number of partitions to divide the data into for recalculating the Return on Investment (ROI). Must be greater than 0.
    :param sell_limit: The percentage of when to sell, (default is 0.2).
    :param buy_limit: The percentage of when to buy, (default is 0.8).

    :returns: A list of floats representing the ROI for each partition.

    :raises ValueError: If `partition_amount` is less than or equal to 0.
    """
    tc_name = self.__class__.__name__

    base_balance: float = 1_000_000
    balance: float = base_balance
    shares: float = 0
    net_worth_history: list[float] = []

    #partition_frequency: int = ceil((len(df)) / partition_frequency) if partition_frequency > 1 else 1

    is_partition_cap_reached: bool = False
    for i in range(len(df)):
        trade_signal: float = signaler()

        is_partition_cap_reached: bool = (
                (i + 1) % partition_frequency == 0) if partition_frequency > 1 else False

        base_balance, balance, shares = BaseTradingComponent.process_trade_signal(
            base_balance, balance, shares,
            df.iloc[i].Close, df.index[i], trade_signal,
            buy_limit, sell_limit,
            net_worth_history, is_partition_cap_reached,
            tc_name
        )

    if not is_partition_cap_reached:
        total_net_worth = balance + shares * df.iloc[-1].Close
        net_worth_history.append(total_net_worth / base_balance)

    logger.info(f"Backtest completed with Return on Investment of {[str(roi * 100) for roi in net_worth_history]}",
                extra={"Trading Component": tc_name})

    return net_worth_history