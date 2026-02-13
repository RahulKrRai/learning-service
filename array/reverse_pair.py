"""
Given an integer array nums, return the number of reverse pairs in the array.
A reverse pair is a pair (i, j) where:
0 <= i < j < nums.length and
nums[i] > 2 * nums[j].
"""
def reverse_pair_brute(nums: list[int]):
    count = 0
    for i in range(len(nums)):
        for j in range(i+1,len(nums)):
            if i < j and nums[i] > 2*nums[j]:
                count+=1
    return count

def reverse_pair_optimised(nums: list[int]):
    return mergeSort(nums,0, len(nums)-1)

def mergeSort(nums: list[int], low, high):
    if low >= high:
        return 0

    mid = low+ (high-low)//2
    # print(low,high, mid)
    count = mergeSort(nums, low, mid)
    count += mergeSort(nums, mid+1, high)
    j = mid+1
    for i in range(low, mid + 1):
        print(j, high, nums)
        while j<=high and nums[i] > 2*nums[j]:
            j+=1
        count+=(j-(mid+1))

    # merge it
    i = low
    j = mid+1
    temp = []
    while i <=mid and j<=high:
        if nums[i]<nums[j]:
            temp.append(nums[i])
            i+=1
        else:
            temp.append(nums[j])
            j+=1
    while i <=mid:
        temp.append(nums[i])
        i+=1
    while j <=high:
        temp.append(nums[j])
        j+=1
    nums[low:high + 1] = temp
    print(nums)

    return count








if __name__  == "__main__":
    array = [1,3,2,3,1]
    print(reverse_pair_brute(array))
    array2 = [2,4,3,5,1]
    print(reverse_pair_optimised(array))



