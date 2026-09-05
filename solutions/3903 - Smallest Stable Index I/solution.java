class Solution {
    public int firstStableIndex(int[] nums, int k) {
        int max = Integer.MIN_VALUE;
        int len = nums.length;
        int[] mins = new int[len]; // mins[i] = min(nums[i..n-1])
        int min = Integer.MAX_VALUE;
        for(int i=len-1;i>=0;i--){
            min = Math.min(min,nums[i]);
            mins[i] = min;
        }
        for(int i=0;i<len;i++){
            max = Math.max(max,nums[i]);
            if(max-mins[i]<=k){
                return i;
            }
        }
        return -1;
    }
}