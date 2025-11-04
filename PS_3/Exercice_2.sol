// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.6;


contract Faucet_with_limited_users {
    address payable public owner;
    uint256 private constant MAX_AMOUNT = 50 wei; // We set the max amount to 50 Wei, and we set it to private so that no one can access it outside this class 
    uint256 private constant MAX_USERS = 4;          // Here, we set up the variable to define the maximum amount of the users

    mapping(address => bool) public isUser; // We set up an array to store the information about the user
    address[] private userList;
    uint256 public userCount; // We initiate the user count

    constructor() {
        owner = payable(msg.sender); // We set up the inital owner of the contract, that is only one able to  
    }

    receive() external payable {} // We initiate the method to receive payment

    function withdraw(uint256 amount) external {  // Here, we set up the function to withdraw funds from the contract, with the predicate
        require(amount <= MAX_AMOUNT, "Exceeds max withdrawal amount"); // We set up a verification if the amount demanded exceed MAX_AMOUNT
        require(address(this).balance >= amount, "Insufficient faucet balance"); // // We check whether the amount remaining inside the balance contract is sufficient to cover the transaction

        // We check if the maximum  amount of Users has alrready been reached
        if (!isUser[msg.sender]) {
            require(userCount < MAX_USERS, "Max users reached");
            isUser[msg.sender] = true;
            userList.push(msg.sender);
            userCount++;
        }

        payable(msg.sender).transfer(amount);
    }

    // Only owner can reset the user list
    function resetUsers() internal  { // We set the function to internal, so that the method can be only called inside the function
        require(msg.sender == owner, "Only owner can reset"); // Only the owner can reset the user
        userCount = 0;

        for (uint256 i = 0; i < MAX_USERS; i++) {
            isUser[userList[i]] = false;
        }
    }

    // Check faucet balance
    function getBalance(address account) external view returns (uint256) {
        if (account == address(this)){
           return address(this).balance;
        }
        return account.balance;
    }
}
