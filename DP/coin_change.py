import sys

class CoinChange:

    def min_coin_recursive(self, coins: list[int], amount:int):
        n  = len(coins)
        def inner_recur(i, target):
            if target == 0:
                return 0
            # base case
            if i == 0:
                if target % coins[i] == 0:
                    return target // coins[i]
                else:
                    return sys.maxsize

            take = 1 + inner_recur(i, target-coins[i]) if coins[i] <= target else sys.maxsize
            not_take = inner_recur(i-1, target)
            return min(take, not_take)

        res = inner_recur(n-1, amount)
        if res == sys.maxsize:
            return -1
        return res

    def min_coin_memoization(self, coins: list[int], amount:int):
        n  = len(coins)
        dp = [[-1]*(amount+1) for _ in range(n)]
        def inner_recur(i, target):
            if target == 0:
                return 0
            # base case
            print(i,target, coins[i])
            if i == 0:
                if target % coins[i] == 0:
                    dp[i][target]  = target // coins[i]
                    return dp[i][target]
                else:
                    return sys.maxsize
            if dp[i][target] != -1:
                return dp[i][target]
            take = 1 + inner_recur(i, target-coins[i]) if coins[i] <= target else sys.maxsize
            not_take = inner_recur(i-1, target)
            print(i, target, dp, take, not_take)
            dp[i][target] = min(take, not_take)
            return dp[i][target]

        res = inner_recur(n-1, amount)
        print(dp)
        if res == sys.maxsize:
            return -1
        return dp[n-1][amount]

    def min_coin_tabular(self, coins: list[int], amount):
        n  = len(coins)
        dp = [[0]*(amount+1) for _ in range(n)]

        # base case done
        for i in range(amount+1):
            if i % coins[0] == 0:
                dp[0][i] = i // coins[0]
            else:
                dp[0][i] = sys.maxsize

        for i in range(1, n):
            for target in range(amount+1):
                take = 1 + dp[i][target - coins[i]] if coins[i] <= target else sys.maxsize
                not_take = dp[i - 1][target]
                # print(i, target, dp, take, not_take)
                dp[i][target] = min(take, not_take)
        if dp[n-1][amount] == sys.maxsize:
            return -1
        return dp[n-1][amount]

if __name__ == '__main__':
    cc = CoinChange()

    coins = [3, 5, 6, 7]
    amount = 9
    print(cc.min_coin_tabular(coins, amount))
    coins2 = [3,3,6,8]
    amount2 = 2
    print(cc.min_coin_tabular(coins2, amount2))
    coins2 = [1]
    amount2 = 1
    print(cc.min_coin_tabular(coins2, amount2))





