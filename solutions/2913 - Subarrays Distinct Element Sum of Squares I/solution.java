class Solution {
    public int sumCounts(List<Integer> nums) {
        int len = nums.size();
        int res = 0;
        for(int i=0;i<len;i++){
            boolean[] seen = new boolean[101];
            int count = 0;
            for(int j=i;j<len;j++){
                int num = nums.get(j);
                if(!seen[num]){
                    seen[num] = true;
                    count++;
                }
                res+=count*count;
            }
        }
        return res;
    }
}