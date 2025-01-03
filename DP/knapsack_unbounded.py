"""
https://www.naukri.com/code360/problems/unbounded-knapsack_1215029?source=youtube&campaign=striver_dp_videos&utm_source=youtube&utm_medium=affiliate&utm_campaign=striver_dp_videos

Problem statement
You are given ‘n’ items with certain ‘profit’ and ‘weight’ and a knapsack with weight capacity ‘w’.



You need to fill the knapsack with the items in such a way that you get the maximum profit. You are allowed to take one item multiple times.



Example:
Input:
'n' = 3, 'w' = 10,
'profit' = [5, 11, 13]
'weight' = [2, 4, 6]

Output: 27

Explanation:
We can fill the knapsack as:

1 item of weight 6 and 1 item of weight 4.
1 item of weight 6 and 2 items of weight 2.
2 items of weight 4 and 1 item of weight 2.
5 items of weight 2.

The maximum profit will be from case 3 = 11 + 11 + 5 = 27. Therefore maximum profit = 27.


Detailed explanation ( Input/output format, Notes, Images )
Sample Input 1:
3 15
7 2 4
5 10 20


Expected Answer:
21


Output on console:
21


Explanation of Sample Input 1
The given knapsack capacity is 15. We can fill the knapsack as [1, 1, 1] giving us profit 21 and as [1,2] giving us profit 9. Thus maximum profit will be 21.

"""

class UnboundedKnapsack:
    def unbounded_knapsack_recur(self, profits, weights, W):
       n = len(profits)
       # we want to maximise profits

       def inner_recur(i, remaining_w):
           if i == 0:
               return (remaining_w // weights[i]) * profits[i]

           take = profits[i] + inner_recur(i, remaining_w-weights[i]) if weights[i] <= remaining_w else 0
           not_take = inner_recur(i-1, remaining_w)
           return  max(take, not_take)
       return inner_recur(n-1,W)

    def unbounded_knapsack_memoize(self, profits, weights, W):
       n = len(profits)
       # we want to maximise profits
       dp = [[-1]*(W+1) for _ in range(n)]

       def inner_recur(i, remaining_w):
           if i == 0:
               return (remaining_w // weights[i]) * profits[i]
           if dp[i][remaining_w] != -1:
               return dp[i][remaining_w]
           take = profits[i] + inner_recur(i, remaining_w-weights[i]) if weights[i] <= remaining_w else 0
           not_take = inner_recur(i-1, remaining_w)
           dp[i][remaining_w] = max(take, not_take)
           return dp[i][remaining_w]
       res = inner_recur(n-1,W)
       print(res)
       return res

    def unbounded_knapsack_tabular(self, profits, weights, W):
        n = len(profits)
        # we want to maximise profits
        dp = [[0] * (W + 1) for _ in range(n)]
        for i in range(W+1):
            dp[0][i] = (i // weights[0]) * profits[0]

        for i in range(1,n):
            for remaining_w in range(W+1):
                take = profits[i] + dp[i][remaining_w - weights[i]] if weights[i] <= remaining_w else 0
                not_take = dp[i - 1][remaining_w]
                dp[i][remaining_w] = max(take, not_take)
        # print(dp)
        return dp[n-1][W]



if __name__ == "__main__":
    uk = UnboundedKnapsack()
    profits = [5, 11, 13]
    weights = [2, 4, 6]
    W = 10
    print(uk.unbounded_knapsack_tabular(profits, weights, W))
    print(uk.unbounded_knapsack_memoize(profits, weights, W))
    profits = [7, 2, 4]
    weights = [5, 10, 20]
    W = 15
    print(uk.unbounded_knapsack_tabular(profits, weights, W))















