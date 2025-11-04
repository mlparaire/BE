// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.6;

contract VickreyAuction {
    address payable public owner; // We set up the owner of the contract
    uint256 public constant MAX_USERS = 4;  // We set up the max number of users for this contract 
    bool public auctionEnded = false; // We create boolean variables for the proper flow and functionning of the auction bid
    bool public auctionStarted = false;
    bool public ownerWithdrawn = false;

    mapping(address => uint256) public Bid_map; // We create a way to store the bidding in a map

    struct Bid { // Like in C-lang, we create a structure that will allow to store both
        address payable bidder;
        uint256 amount;
    }

    Bid[] public bids; // We create an array of Bids
    address public winner; //We initiate the winner's address
    uint256 public winningBid; //We initiate the winner's bid and second price
    uint256 public secondPrice;

    event AuctionStarted(); // We create an event so that the Auction has started
    event BidPlaced(address indexed bidder, uint256 amount);
    event AuctionEnded(address indexed winner, uint256 winningBid, uint256 secondPrice);
    event OwnerWithdrawn(address indexed owner, uint256 amount);
    event AuctionReset();

    constructor() {
        owner = payable(msg.sender); // We set the owner to the creator of the contract
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner"); // A method so that only the owner is 
        _;
    }

    modifier auctionActive() { // A method so that to prevent a user action when Auction is not Active
        require(auctionStarted, "Auction not started");
        require(!auctionEnded, "Auction ended");
        _;
    }

    function startAuction() external onlyOwner { // an function to start the auction
        require(!auctionStarted, "Already started");
        auctionStarted = true; // We set the environments variables to Auction has begun
        auctionEnded = false;
        emit AuctionStarted(); // We emmit the event
    }

    function hasAlreadyBid(address user) public view returns (bool) { // We check whether the user has already bid
        for (uint256 i = 0; i < bids.length; i++) { 
            if (bids[i].bidder == user) return true; // Inside the bids dictionnary; we seek the user. If bidder has already bid, we return true
        }
        return false;
    }


    function bid() external payable auctionActive { // A function so that the user can bid
        require(msg.value > 0, "Bid must be > 0"); // A minimum threshold of bidding
        require(bids.length < MAX_USERS, "Max bidders reached"); // Here, we check whether the maximum number of bider has been reached
        require(!hasAlreadyBid(msg.sender), "You already placed a bid"); // We check if the user has already bid with the previous function

        bids.push(Bid(payable(msg.sender), msg.value)); // We push into the dictionnary the bid the user
        emit BidPlaced(msg.sender, msg.value); // We broadcast the transaction

        if (bids.length == MAX_USERS) {
            finalizeAuction(); // If the max number of user allowed to bid has been reached, then we finalize the action
        }
    }

    function finalizeAuction() public onlyOwner { // we finalize the auction with this function
        require(auctionStarted, "Auction not started");
        require(!auctionEnded, "Already ended");
        require(bids.length == MAX_USERS, "Not enough bids yet");

        uint256 highest = 0; // We initiate the local variables to zero
        uint256 second = 0;
        uint256 winnerIndex = 0;

        for (uint256 i = 0; i < bids.length; i++) {
            if (bids[i].amount > highest) { // Here, we implement a bubble sort algorithm to find the highest and second highest bid (complexity O(N²))
                second = highest;
                highest = bids[i].amount; 
                winnerIndex = i;
            } else if (bids[i].amount > second) {
                second = bids[i].amount;
            }
        }

        winner = bids[winnerIndex].bidder; // We store the variables from the auction
        winningBid = highest;
        secondPrice = second;
        auctionEnded = true;

        emit AuctionEnded(winner, winningBid, secondPrice); //We emit the event that the auction ended

        for (uint256 i = 0; i < bids.length; i++) {
            if (i != winnerIndex) {
                bids[i].bidder.transfer(bids[i].amount);
            }
        }

        if (highest > second) {
            uint256 refund = highest - second;
            payable(winner).transfer(refund);
        }
    }

    function ownerWithdraw() external onlyOwner { // Here, the user can withdraw the amount from the auction
        require(auctionEnded, "Auction not ended yet");
        require(!ownerWithdrawn, "Already withdrawn");

        ownerWithdrawn = true;
        owner.transfer(secondPrice);
        emit OwnerWithdrawn(owner, secondPrice);
    }

    function resetAuction() external onlyOwner { // We reset the auction with this function
        require(auctionEnded, "Auction must be ended first");

        delete bids; // We reset the bid
        winner = address(0); // The local variables are all reset to zero
        winningBid = 0;
        secondPrice = 0;
        auctionEnded = false;
        auctionStarted = false;
        ownerWithdrawn = false;

        emit AuctionReset();
    }

    // Here, we set up functions to allow the users to follow the bid count and balance during the auction
    function getBidsCount() external view returns (uint256) {
        return bids.length;
    }

    function getBid(uint256 index) external view returns (address, uint256) {
        Bid memory b = bids[index];
        return (b.bidder, b.amount);
    }

    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
