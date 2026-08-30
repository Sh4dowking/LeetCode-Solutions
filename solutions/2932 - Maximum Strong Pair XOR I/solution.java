class Solution {
    public int maximumStrongPairXor(int[] nums) {
        int max = 0;
        int len = nums.length;
        for(int i=0;i<len;i++){
            for(int j=i+1;j<len;j++){
                int x = nums[i];
                int y = nums[j];
                int xORy = x^y;
                if(xORy > max && Math.abs(x-y) <= Math.min(x,y)){
                    max = xORy;
                }
            }
        }
        return max;
    }
}