class Solution {
    public int findChampion(int[][] grid) {
        int n = grid[0].length;
        int champ = 0;
        for(int i=0;i<n;i++){
            if(grid[champ][i]==0){
                champ = i;
            }
        }
        return champ;
    }
}