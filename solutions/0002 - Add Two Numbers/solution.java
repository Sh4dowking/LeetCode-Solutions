/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     int val;
 *     ListNode next;
 *     ListNode() {}
 *     ListNode(int val) { this.val = val; }
 *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
 * }
 */
class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        ListNode res = new ListNode();
        ListNode curr = res;
        int sum = 0;
        int overflow = 0;
        while(l1 != null && l2 != null){
            sum = l1.val + l2.val + overflow;
            overflow = sum/10;
            sum %= 10;
            curr.val = sum;
            if(l1.next != null && l2.next!=null){
                curr.next = new ListNode();
                curr = curr.next;
            }
            l1 = l1.next;
            l2 = l2.next;
        }
        if(l1!=null || l2!=null){
            curr.next = new ListNode();
            curr = curr.next;
        }
        while(l1!=null){
            sum = l1.val + overflow;
            overflow = sum/10;
            sum %= 10;
            curr.val = sum;
            if(l1.next != null){
                curr.next = new ListNode();
                curr = curr.next;
            }
            l1 = l1.next;
        }
        while(l2!=null){
            sum = l2.val + overflow;
            overflow = sum/10;
            sum %= 10;
            curr.val = sum;
            if(l2.next != null){
                curr.next = new ListNode();
                curr = curr.next;
            }
            l2 = l2.next;
        }
        if(overflow>0){
            curr.next = new ListNode(overflow);
        }
        return res;
    }
}