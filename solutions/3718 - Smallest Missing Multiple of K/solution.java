class Solution {
    public int missingMultiple(int[] nums, int k) {
        boolean[] set = new boolean[101];
        for(int num:nums){
            set[num] = true;
        }
        
        int multiple = k;
        while(multiple <= 100 && set[multiple]){
            multiple += k;
        }
        
        return multiple;
    }
}