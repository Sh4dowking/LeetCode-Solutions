class Solution {
    public int lengthOfLongestSubstring(String s) {
        int len = s.length();
        if(len <= 1){
            return len;
        }
        int[] lastSeen = new int[128]; // store index of last seen char
        int l = 0;
        int max = 0;
        for(int r=0;r<len;r++){
            char c = s.charAt(r);
            l = Math.max(l,lastSeen[c]);
            lastSeen[c] = r+1;
            max = Math.max(max,r-l+1);
        }
        return max;
    }
}