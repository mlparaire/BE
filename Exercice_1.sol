// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.6;

import "Interfaces/Q1.sol";

contract Faucet is IERC20 { // Similar to Java, we implement in the interface from Q1.sol, where we have defined the functions of this exercice
    address payable public owner; // Here, we set up the owner of the contract
    uint256 private MAX_AMOUNT = 0.1 ether; // Here, we set up a MAX_AMOUNT to 50 WEI, and make it immutable. We also set it to private so that no other method can tamper with the ammount

    constructor() {
        owner = payable(msg.sender); // Like in Javascript, we initiate the class with owner 
    }

    receive() external payable {} // Here, we accept any incoming amount

    function withdraw(address to, uint256 amount) external override returns (bool) { // From the interface, we take the method withdraw so that address can take up etherum from the faucet 
        require(amount <= MAX_AMOUNT, "Exceeds max withdrawal amount"); // We check whether the amount asked is enough to meet the MAX_AMOUNT balance
        require(address(this).balance >= amount, "Insufficient faucet balance"); // We check whether the amount remaining inside the balance contract is sufficient to cover the transaction

        payable(to).transfer(amount); // We pay up the balance
        emit Transfer(address(this), to, amount); // We broadcast the transaction using Transfer
        return true; // We return a bool
    }

    function balanceOf(address account) external view override returns (uint256) { // For user to see the amount, we fetch from the interface up a function to get the balance of
        if (account == address(this)) {
            return address(this).balance;
        }
        return account.balance;
    }
}
