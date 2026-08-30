class Solution {
    public int distributeCandies(int n, int limit) {
        int res = 0;
        for(int i=0;i<=limit;i++){
            for(int j=0;i+j<=n&&j<=limit;j++){
                if(n-i-j<=limit){
                    res++;
                }
            }
        }
        return res;
    }
}