class Solution {
    public int findKOr(int[] nums, int k) {
        int len = nums.length;
        int res = 0;
        for(int i=0;i<32;i++){ // since nums[i] < 2^31 we can have at most 32 bits
            int count = 0;
            for(int j=0;j<len;j++){
                count += (nums[j] >> i) & 1;
            }
            if(count >= k){
                res |= (1 << i);
            }
        }
        return res;
    }
}