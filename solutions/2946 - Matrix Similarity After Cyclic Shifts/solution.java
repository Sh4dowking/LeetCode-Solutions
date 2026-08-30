class Solution {
    public boolean areSimilar(int[][] mat, int k) {
        int n = mat[0].length;
        int shift = k%n;
        for(int[] row:mat){
            for(int i=0;i<n;i++){
                if(row[i]!=row[(i+shift)%n]){
                    return false;
                }
            }
        }
        return true;
    }
}