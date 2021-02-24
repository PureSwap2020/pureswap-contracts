// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";

// PureBar is the coolest bar in town. You come in with some Pure, and leave with more! The longer you stay, the more Pure you get.
//
// This contract handles swapping to and from xPure, PureSwap's staking token.
contract PureBar is ERC20("PureBar", "xPURE"){
    using SafeMath for uint256;
    IERC20 public pureToken;

    // Define the Pure token contract
    constructor(IERC20 _pureToken) public {
        pureToken = _pureToken;
    }

    // Enter the bar. Pay some PUREs. Earn some shares.
    // Locks Pure and mints xPure
    function enter(uint256 _amount) public {
        // Gets the amount of Pure locked in the contract
        uint256 totalPure = pureToken.balanceOf(address(this));
        // Gets the amount of xPure in existence
        uint256 totalShares = totalSupply();
        // If no xPure exists, mint it 1:1 to the amount put in
        if (totalShares == 0 || totalPure == 0) {
            _mint(msg.sender, _amount);
        } 
        // Calculate and mint the amount of xPure the Pure is worth. The ratio will change overtime, as xPure is burned/minted and Pure deposited + gained from fees / withdrawn.
        else {
            uint256 what = _amount.mul(totalShares).div(totalPure);
            _mint(msg.sender, what);
        }
        // Lock the Pure in the contract
        pureToken.transferFrom(msg.sender, address(this), _amount);
    }

    // Leave the bar. Claim back your PUREs.
    // Unclocks the staked + gained Pure and burns xPure
    function leave(uint256 _share) public {
        // Gets the amount of xPure in existence
        uint256 totalShares = totalSupply();
        // Calculates the amount of Pure the xPure is worth
        uint256 what = _share.mul(pureToken.balanceOf(address(this))).div(totalShares);
        _burn(msg.sender, _share);
        pureToken.transfer(msg.sender, what);
    }
}