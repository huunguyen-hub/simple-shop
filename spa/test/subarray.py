# Function to check if an array is sub array of another array
def isSubArray(list_of_parent, list_of_child):
    n = len(list_of_parent)
    m = len(list_of_child)
    # Two pointers to traverse the arrays
    i = 0
    j = 0
    # Traverse both arrays simultaneously
    while i < n and j < m:
        # If element matches
        # increment both pointers
        if list_of_parent[i] == list_of_child[j]:
            i += 1
            j += 1
            # If array B is completely
            # traversed
            if j == m:
                return True
            # If not,
        # increment i and reset j
        else:
            i = i - j + 1
            j = 0
    return False


# Driver Code
if __name__ == '__main__':
    print(__name__, type(__name__))
    A = [12, 1]
    B = [1, 12]

    if isSubArray(A, B):
        print("YES")
    else:
        print("NO")

    # This code is contributed by Rajput-Ji
