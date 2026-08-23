class Solution {
    public String longestPalindrome(String s) {
        int len = s.length();
        boolean[][] dp = new boolean[len][len];
        
        int max = 1;
        int startIdx = 0;

        for(int i=0;i<len;i++){
            dp[i][i] = true;
            if(i+1<len && s.charAt(i)==s.charAt(i+1)){
                dp[i][i+1] = true;
                max = 2;
                startIdx = i;
            }
        }

        for(int size=2;size<=len;size++){
            for(int i=0;i<len;i++){
                if(i+size<len){ // check boundary
                    if(dp[i+1][i+size-1]){ // check if smaller is palindrome
                        if(s.charAt(i)==s.charAt(i+size)){ // check is same character
                            dp[i][i+size] = true;
                            if(size + 1> max){
                                max = size+1;
                                startIdx = i;
                            }
                        }
                    }
                }
            }
        }

        return s.substring(startIdx, startIdx+max);
    }
}