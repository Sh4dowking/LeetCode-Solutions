class Solution {
    public List<Integer> findWordsContaining(String[] words, char x) {
        List<Integer> res = new ArrayList<>();
        int len = words.length;
        for(int i=0;i<len;i++){
            if(words[i].indexOf(x)>=0){
                res.add(i);
            }
        }
        return res;
    }
}