class Solution {
    public int findMinimumOperations(String s1, String s2, String s3) {
        int l1 = s1.length();
        int l2 = s2.length();
        int l3 = s3.length();
        int minLen = Math.min(l1,Math.min(l2,l3));
        for(int i=0;i<minLen;i++){
            if(s1.charAt(i)!=s2.charAt(i) || s1.charAt(i)!=s3.charAt(i) || s2.charAt(i)!=s3.charAt(i)){
                minLen = i;
                break;
            }
        }
        if(minLen == 0){
            return -1;
        }
        return l1-minLen + (l2-minLen) + (l3-minLen);
    }
}