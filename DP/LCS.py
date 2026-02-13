"""
https://leetcode.com/problems/longest-common-subsequence/description/

Given two strings text1 and text2, return the length of their longest common subsequence. If there is no common subsequence, return 0.

A subsequence of a string is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.

For example, "ace" is a subsequence of "abcde".
A common subsequence of two strings is a subsequence that is common to both strings.

Example 1:
Input: text1 = "abcde", text2 = "ace"
Output: 3
Explanation: The longest common subsequence is "ace" and its length is 3.

Example 2:
Input: text1 = "abc", text2 = "abc"
Output: 3
Explanation: The longest common subsequence is "abc" and its length is 3.
"""

class LCS:
	def lcs_recursive(self, str1, str2):
		m = len(str1)
		n = len(str2)

		def inner_recur(i,j):
			if i==0 or j ==0:
				return 0
			if str1[i-1] == str2[j-1]:
				return 1+ inner_recur(i-1,j-1)
			else:
				return max(inner_recur(i-1,j), inner_recur(i,j-1))

		return inner_recur(m,n)

	def lcs_memoize(self, str1, str2):
		m = len(str1)
		n = len(str2)
		dp = [[-1]*(n+1) for _ in range(m+1)]
		def inner_recur(i,j):
			if i==0 or j ==0:
				return 0
			if dp[i][j] != -1:
				return dp[i][j]
			if str1[i-1] == str2[j-1]:
				dp[i][j] = 1+ inner_recur(i-1,j-1)
			else:
				dp[i][j] = max(inner_recur(i-1,j), inner_recur(i,j-1))
			return dp[i][j]

		return inner_recur(m,n)

	def lcs_tabular(self,str1, str2):
		m = len(str1)
		n = len(str2)
		dp = [[0]*(n+1) for _ in range(m+1)]

		for i in range(1,m+1):
			for j in range(1,n+1):
				if str1[i - 1] == str2[j - 1]:
					dp[i][j] = 1 + dp[i - 1][j - 1]
				else:
					dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
		for row in dp:
			print(row)
		return dp[m][n]

if __name__ == "__main__":
	lcs = LCS()
	text1 = "abcde"
	text2 = "ace"
	print(lcs.lcs_tabular(text1, text2))