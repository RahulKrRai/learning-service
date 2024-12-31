from typing import List
"""
You are given an integer array nums and an integer target.

You want to build an expression out of nums by adding one of the symbols '+' and '-' before each integer in nums and then concatenate all the integers.

For example, if nums = [2, 1], you can add a '+' before 2 and a '-' before 1 and concatenate them to build the expression "+2-1".
Return the number of different expressions that you can build, which evaluates to target.

Example 1:
Input: nums = [1,1,1,1,1], target = 3
Output: 5

Explanation: There are 5 ways to assign symbols to make the sum of nums be target 3.
-1 + 1 + 1 + 1 + 1 = 3
+1 - 1 + 1 + 1 + 1 = 3
+1 + 1 - 1 + 1 + 1 = 3
+1 + 1 + 1 - 1 + 1 = 3
+1 + 1 + 1 + 1 - 1 = 3

Solution:
 Sum1 - sum2 = D
 SUm1 + sum2 = T
 SUm1 = (D+T)/2
 if we get no of ways to get sum1 we will get D as well
"""
class CountSubset:
    # https://leetcode.com/problems/target-sum/description/
    def target_sum(self, nums: List[int], target: int):
        total = sum(nums)
        if (total + target) % 2 != 0:
            return 0
        subset_sum = (total + target) // 2
        # print("Recursive", self.count_subset_recursive(nums, subset_sum))
        return  self.count_subset_tabulation(nums, subset_sum)

    def count_subset_recursive(self, nums: List[int], target):
        n = len(nums)
        if target == 0:
            return 1
        def inner_recur(i, remaining_target):
            if remaining_target == 0:
                return 1
            if i == 0:
                return 1 if remaining_target == nums[i] else 0
            take = inner_recur(i-1, remaining_target-nums[i]) if nums[i] <= remaining_target else 0
            not_take = inner_recur(i-1, remaining_target)
            print(i, remaining_target, take, not_take,  nums[i] <= remaining_target)
            return take + not_take
        return  inner_recur(n-1, target)

    def count_subset_memoization(self, nums: List[int], target):
        n = len(nums)
        if target == 0:
            return 1
        dp = [[-1]*(target+1) for _ in range(n)]

        def inner_recur(i, remaining_target):
            if remaining_target == 0:
                return 1
            if i == 0:
                return 1 if remaining_target == nums[i] else 0
            if dp[i][remaining_target] != -1:
                return dp[i][remaining_target]
            take = inner_recur(i-1, remaining_target-nums[i]) if nums[i] <= remaining_target else 0
            not_take = inner_recur(i-1, remaining_target)
            print(i, remaining_target, take, not_take,  nums[i] <= remaining_target)
            dp[i][remaining_target] = take + not_take
            return dp[i][remaining_target]
        return  inner_recur(n-1, target)

    def count_subset_tabulation(self, nums: List[int], target):
        if target == 0:
            return 1
        n = len(nums)
        dp = [[0]*(target+1) for _ in range(n)]
        # base case this got missed
        for i in range(n):
            dp[i][0] = 1
        if nums[0] <= target:
            dp[0][nums[0]] = 1
        for i in range(1,n):
            for remaining_target in range(target+1):
                take = dp[i - 1][remaining_target - nums[i]] if nums[i] <= remaining_target else 0
                not_take = dp[i - 1][remaining_target]
                print(i, remaining_target, take, not_take)
                dp[i][remaining_target]= take+not_take

        return dp[n-1][target]


if __name__ == '__main__':
    print(CountSubset().target_sum([1,1,1,1,1], 3))

