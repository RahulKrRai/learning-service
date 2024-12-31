"""
https://leetcode.com/problems/coin-change-ii/submissions/1493567249/

You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money.
Return the number of combinations that make up that amount. If that amount of money cannot be made up by any combination of the coins, return 0.
You may assume that you have an infinite number of each kind of coin.
The answer is guaranteed to fit into a signed 32-bit integer.
Example 1:

Input: amount = 5, coins = [1,2,5]
Output: 4
Explanation: there are four ways to make up the amount:
5=5
5=2+2+1
5=2+1+1+1
5=1+1+1+1+1

Constraints:

1 <= coins.length <= 300
1 <= coins[i] <= 5000
All the values of coins are unique.
0 <= amount <= 5000
"""

class CoinChangeII:
    def no_of_ways_coin_change_tabular(self, nums, amount):
        # refer coin change
        n = len(nums)
        # base case all the first coin and its multiple
        dp = [[0]*(amount+1) for _ in range(n)]
        # dp[0][0] = 1
        for i in range(amount+1):
            if i % nums[0] == 0:
                dp[0][i] = 1
        print(dp)

        for i in range(1, n):
            for target in range(amount+1):
                not_take = dp[i-1][target]
                take = dp[i][target-nums[i]] if nums[i] <= target else 0
                dp[i][target] = take + not_take
        print(dp)
        return  dp[n-1][amount]

if __name__ == "__main__":
    coins = [1,2,5]
    amount = 5
    cc = CoinChangeII()
    print(cc.no_of_ways_coin_change_tabular(coins, amount))
