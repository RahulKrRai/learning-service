"""
https://www.naukri.com/code360/problems/rod-cutting-problem_800284?source=youtube&campaign=striver_dp_videos&utm_source=youtube&utm_medium=affiliate&utm_campaign=striver_dp_videos
Problem statement
Given a rod of length ‘N’ units. The rod can be cut into different sizes and each size has a cost associated with it. Determine the maximum cost obtained by cutting the rod and selling its pieces.

Note:
1. The sizes will range from 1 to ‘N’ and will be integers.

2. The sum of the pieces cut should be equal to ‘N’.

3. Consider 1-based indexing.

Problem statement
Given a rod of length ‘N’ units. The rod can be cut into different sizes and each size has a cost associated with it. Determine the maximum cost obtained by cutting the rod and selling its pieces.

Note:
1. The sizes will range from 1 to ‘N’ and will be integers.

2. The sum of the pieces cut should be equal to ‘N’.

3. Consider 1-based indexing.
"""
class RodCuttingProblem:
	def rod_cutting_recursive(self, prices, total_length):

		def inner_recur(i, remaining_length):
			if i == 0:
				return remaining_length*prices[0]
			not_take = inner_recur(i-1, remaining_length)
			take = prices[i - 1] + inner_recur(i, remaining_length - i) if i <= remaining_length else 0
			return  max(take, not_take)
		return inner_recur(total_length, total_length)

	def rod_cutting_memoize(self, prices, total_length):
		dp = [[-1]*(total_length+1) for _ in range(total_length)]
		def inner_recur(i, remaining_length):
			if i == 0:
				return remaining_length*prices[0]
			if dp[i][remaining_length] != -1:
				return dp[i][remaining_length]
			not_take = inner_recur(i-1, remaining_length)
			take = prices[i] + inner_recur(i, remaining_length - (i+1)) if (i+1) <= remaining_length else 0
			dp[i][remaining_length] = max(take, not_take)
			return dp[i][remaining_length]
		res = inner_recur(total_length-1, total_length)
		# print(res, dp)
		return res

	def rod_cutting_tabular(self, prices, total_length):
		dp = [[0]*(total_length+1) for _ in range(total_length)]

		for i in range(1,total_length+1):
			dp[0][i] = i*prices[0]

		for i in range(1, total_length):
			for remaining_length in range(total_length+1):
				not_take = dp[i - 1][remaining_length]
				rod_length = i+1
				take = prices[i] + dp[i][remaining_length - rod_length]if rod_length <= remaining_length else 0
				dp[i][remaining_length] = max(take, not_take)

		return dp[total_length-1][total_length]


if __name__ == "__main__":
	prices = [2, 5, 7, 8, 10]
	length = 5
	RC = RodCuttingProblem()
	print(RC.rod_cutting_tabular(prices, length))
	prices = [3, 5, 8, 9, 10, 17, 17, 20]
	length = 8
	print(RC.rod_cutting_tabular(prices, length))
