
class Knapsack:
    def __init__(self, capacity, weights, values, n):
        self.capacity = capacity
        self.weights = weights
        self.values = values
        self.n = n

    def knapsack_01_recursive(self):
        def knapsack_recur(i, cap):
            # basecase i =0
            if i == 0:
                if self.weights[i] == cap:
                    return self.values[i]
                else:
                    return 0
            take = self.values[i] + knapsack_recur(i-1, cap - self.weights[i]) if self.weights[i]<=cap else 0
            not_take = knapsack_recur(i-1, cap)
            return max(take, not_take)
        return knapsack_recur(self.n-1, self.capacity)

    def knapsack_01_memoization(self):
        # DP [[-1]* #cols for _ in range(rows)]
        dp = [[-1]*(self.capacity+1) for _ in range(self.n)]
        def knapsack_recur(i, cap, dp):
            # basecase i =0
            if i == 0:
                if self.weights[i] <= cap:
                    return self.values[i]
                else:
                    return 0
            if dp[i][cap] != -1:
                return dp[i][cap]
            take = self.values[i] + knapsack_recur(i-1, cap - self.weights[i], dp) if self.weights[i]<=cap else 0
            not_take = knapsack_recur(i-1, cap, dp)
            dp[i][cap] = max(take, not_take)
            return dp[i][cap]
        # print(dp)
        return knapsack_recur(self.n-1, self.capacity, dp)

    def knapsack_01_tabular(self):
        # in case of tabular default values are 0
        dp = [[0]*(self.capacity+1) for _ in range(self.n)]
        #case when 0th element cap >=weight[0]
        for i in range(self.weights[0], self.capacity+1):
            dp[0][i] = self.values[0]

        for i in range(1, self.n):
            for cap in range(self.capacity+1):
                take = self.values[i] + dp[i-1][cap-self.weights[i]] if self.weights[i] <= cap else 0
                not_take = dp[i-1][cap]
                # print(i,cap,take, not_take)
                dp[i][cap] = max(take, not_take)
        # print(dp)
        return dp[self.n-1][self.capacity]




if __name__ == '__main__':
    ks = Knapsack(50, [10, 20, 30], [60, 100, 120], 3)
    print(ks.knapsack_01_tabular())
    ks2 = Knapsack(5, [1, 2, 4, 5], [5,4,8,6], 4)
    print(ks2.knapsack_01_tabular())